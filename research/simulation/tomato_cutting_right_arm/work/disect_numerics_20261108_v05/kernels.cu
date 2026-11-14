#include <torch/extension.h>
#include <ATen/cuda/CUDAContext.h>
#include <c10/cuda/CUDAException.h>
using torch::Tensor;
__device__ void cross3(const double*a,const double*b,double*c){c[0]=a[1]*b[2]-a[2]*b[1];c[1]=a[2]*b[0]-a[0]*b[2];c[2]=a[0]*b[1]-a[1]*b[0];}
// egrad stores shape gradients and dJ/dx at CURRENT geometry, never frozen at rest.
__global__ void geom_k(const double*x,const int64_t*t,const double*dm,const double*mu,const double*la,const double*kd,const double*act,double*f,double*gout,double*jout,double*diag,int E){
 int e=blockIdx.x*blockDim.x+threadIdx.x;if(e>=E)return;
 double D[9],F[9]={},g[12],j[12],cr[9],H[9]={};const double*A=dm+9*e;
 for(int b=0;b<3;b++)for(int a=0;a<3;a++)D[a*3+b]=x[3*t[4*e+b+1]+a]-x[3*t[4*e]+a];
 double det=A[0]*(A[4]*A[8]-A[5]*A[7])-A[1]*(A[3]*A[8]-A[5]*A[6])+A[2]*(A[3]*A[7]-A[4]*A[6]);double V=1/(6*det);
 for(int a=0;a<3;a++){g[a]=0;for(int b=0;b<3;b++){g[(b+1)*3+a]=A[b*3+a];g[a]-=A[b*3+a];}}
 double c0[3],c1[3],c2[3];for(int a=0;a<3;a++){c0[a]=D[a*3];c1[a]=D[a*3+1];c2[a]=D[a*3+2];}
 cross3(c1,c2,cr);cross3(c2,c0,cr+3);cross3(c0,c1,cr+6);
 for(int a=0;a<3;a++){j[a]=0;for(int b=0;b<3;b++){j[(b+1)*3+a]=cr[b*3+a]*det;j[a]-=j[(b+1)*3+a];}}
 for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)F[a*3+b]+=D[a*3+c]*A[c*3+b];
 // Preserve the current DiSECt executable's diagonal-only Ic expression exactly.
 double Ic=F[0]*F[0]+F[4]*F[4]+F[8]*F[8];
 double J=(c0[0]*cr[0]+c0[1]*cr[1]+c0[2]*cr[2])*det;
 double alpha=1+0.75*mu[e]/la[e];double volf=(J-alpha+act[e])*la[e]*V;
 for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)H[a*3+b]+=F[a*3+c]*mu[e]*V*(1-1/(Ic+1))*A[b*3+c];
 double lf[12]={};for(int a=0;a<3;a++)for(int b=0;b<3;b++){lf[(b+1)*3+a]=-H[a*3+b]-j[(b+1)*3+a]*volf;lf[a]-=lf[(b+1)*3+a];}
 for(int i=0;i<4;i++)for(int a=0;a<3;a++){
  int p=3*t[4*e+i]+a;atomicAdd(f+p,lf[3*i+a]);gout[e*12+3*i+a]=g[3*i+a];jout[e*12+3*i+a]=j[3*i+a];
  double gg=0;for(int b=0;b<3;b++)gg+=g[3*i+b]*g[3*i+b];atomicAdd(diag+p,kd[e]*V*(gg+j[3*i+a]*j[3*i+a]));
 }
}
__global__ void damp_k(const double*v,const int64_t*t,const double*g,const double*j,const double*weight,double*out,int E){
 int e=blockIdx.x*blockDim.x+threadIdx.x;if(e>=E)return;double B[9]={},s=0;
 // Relative velocity form is essential also in float64: exact common translation nullspace.
 for(int i=1;i<4;i++)for(int a=0;a<3;a++){double va=v[3*t[4*e+i]+a]-v[3*t[4*e]+a];s+=j[e*12+3*i+a]*va;for(int b=0;b<3;b++)B[3*a+b]+=va*g[e*12+3*i+b];}
 double sum[3]={};for(int i=1;i<4;i++)for(int a=0;a<3;a++){double z=j[e*12+3*i+a]*s;for(int b=0;b<3;b++)z+=B[3*a+b]*g[e*12+3*i+b];z*=weight[e];atomicAdd(out+3*t[4*e+i]+a,z);sum[a]+=z;}
 for(int a=0;a<3;a++)atomicAdd(out+3*t[4*e]+a,-sum[a]);
}
__global__ void ground_k(const double*x,const double*v,const double*mask,double*f,int N){int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=N)return;double c=fmin(x[3*i+1]-.001,0.);if(c<0){double upper=-.2*c*1000.;f[3*i+1]-=c*1000.*mask[i];f[3*i]-=fmin(fmax(1000.*v[3*i],-upper),upper)*mask[i];f[3*i+2]-=fmin(fmax(1000.*v[3*i+2],-upper),upper)*mask[i];}}
__global__ void step_k(double*x,double*v,const double*f,const double*im,const double*g,double h,int N){int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=N)return;if(im[i]==0){for(int a=0;a<3;a++)v[3*i+a]=0;return;}for(int a=0;a<3;a++){v[3*i+a]+=h*(f[3*i+a]*im[i]+g[a]);x[3*i+a]+=h*v[3*i+a];}}
void geom(Tensor x,Tensor t,Tensor dm,Tensor mu,Tensor la,Tensor kd,Tensor act,Tensor f,Tensor g,Tensor j,Tensor diag){int E=t.size(0);geom_k<<<(E+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(x.data_ptr<double>(),t.data_ptr<int64_t>(),dm.data_ptr<double>(),mu.data_ptr<double>(),la.data_ptr<double>(),kd.data_ptr<double>(),act.data_ptr<double>(),f.data_ptr<double>(),g.data_ptr<double>(),j.data_ptr<double>(),diag.data_ptr<double>(),E);C10_CUDA_KERNEL_LAUNCH_CHECK();}
void damp(Tensor v,Tensor t,Tensor g,Tensor j,Tensor weight,Tensor out){int E=t.size(0);damp_k<<<(E+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(v.data_ptr<double>(),t.data_ptr<int64_t>(),g.data_ptr<double>(),j.data_ptr<double>(),weight.data_ptr<double>(),out.data_ptr<double>(),E);C10_CUDA_KERNEL_LAUNCH_CHECK();}
void ground(Tensor x,Tensor v,Tensor mask,Tensor f){int N=x.size(0);ground_k<<<(N+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(x.data_ptr<double>(),v.data_ptr<double>(),mask.data_ptr<double>(),f.data_ptr<double>(),N);C10_CUDA_KERNEL_LAUNCH_CHECK();}
void step(Tensor x,Tensor v,Tensor f,Tensor im,Tensor gravity,double h){int N=x.size(0);step_k<<<(N+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(x.data_ptr<double>(),v.data_ptr<double>(),f.data_ptr<double>(),im.data_ptr<double>(),gravity.data_ptr<double>(),h,N);C10_CUDA_KERNEL_LAUNCH_CHECK();}
__global__ void rate_k(const double*v,const int64_t*t,const double*j,double*rate,int E){int e=blockIdx.x*blockDim.x+threadIdx.x;if(e>=E)return;double s=0;for(int i=1;i<4;i++)for(int a=0;a<3;a++)s+=j[e*12+3*i+a]*(v[3*t[e*4+i]+a]-v[3*t[e*4]+a]);rate[e]=s;}
__global__ void gather_k(const double*v,const int64_t*row,const int64_t*col,const double*val,const int64_t*ir,const int64_t*inc,const double*j,const double*w,const double*rate,double*out,int N){
 int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=N)return;double o[3]={};
 for(int64_t k=row[i];k<row[i+1];k++){int q=col[k];if(q!=i)for(int a=0;a<3;a++)o[a]+=val[k]*(v[3*q+a]-v[3*i+a]);}
 for(int64_t k=ir[i];k<ir[i+1];k++){int id=inc[k],e=id/4,local=id%4;for(int a=0;a<3;a++)o[a]+=w[e]*j[e*12+3*local+a]*rate[e];}
 for(int a=0;a<3;a++)out[3*i+a]=o[a];
}
void gathered_damp(Tensor v,Tensor t,Tensor j,Tensor weight,Tensor row,Tensor col,Tensor val,Tensor ir,Tensor inc,Tensor rate,Tensor out){int E=t.size(0),N=v.size(0);rate_k<<<(E+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(v.data_ptr<double>(),t.data_ptr<int64_t>(),j.data_ptr<double>(),rate.data_ptr<double>(),E);gather_k<<<(N+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(v.data_ptr<double>(),row.data_ptr<int64_t>(),col.data_ptr<int64_t>(),val.data_ptr<double>(),ir.data_ptr<int64_t>(),inc.data_ptr<int64_t>(),j.data_ptr<double>(),weight.data_ptr<double>(),rate.data_ptr<double>(),out.data_ptr<double>(),N);C10_CUDA_KERNEL_LAUNCH_CHECK();}
__global__ void op_rate_k(const double*p,const double*scale,const int64_t*t,const double*j,double*rate,int E){int e=blockIdx.x*blockDim.x+threadIdx.x;if(e>=E)return;double s=0;int q0=t[4*e];for(int i=1;i<4;i++)for(int a=0;a<3;a++){int q=t[4*e+i];s+=j[e*12+3*i+a]*(scale[3*q+a]*p[3*q+a]-scale[3*q0+a]*p[3*q0+a]);}rate[e]=s;}
__global__ void op_gather_k(const double*p,const double*scale,const int64_t*row,const int64_t*col,const double*val,const int64_t*ir,const int64_t*inc,const double*j,const double*w,const double*rate,double*out,double h,int N){
 int i=blockIdx.x*blockDim.x+threadIdx.x;if(i>=N)return;double o[3]={};
 for(int64_t k=row[i];k<row[i+1];k++){int q=col[k];if(q!=i)for(int a=0;a<3;a++)o[a]+=val[k]*(scale[3*q+a]*p[3*q+a]-scale[3*i+a]*p[3*i+a]);}
 for(int64_t k=ir[i];k<ir[i+1];k++){int id=inc[k],e=id/4,local=id%4;for(int a=0;a<3;a++)o[a]+=w[e]*j[e*12+3*local+a]*rate[e];}
 for(int a=0;a<3;a++)out[3*i+a]=p[3*i+a]+h*scale[3*i+a]*o[a];
}
__global__ void dot_k(const double*p,const double*ap,double*s,int N){__shared__ double q[512];int a=threadIdx.x;double v=0;for(int k=a;k<N;k+=512)v+=p[k]*ap[k];q[a]=v;__syncthreads();for(int d=256;d;d/=2){if(a<d)q[a]+=q[a+d];__syncthreads();}if(a==0)s[1]=q[0];}
__global__ void update_k(double*y,double*r,const double*p,const double*ap,const double*d,double*z,double*s,int N){__shared__ double q[256];int a=threadIdx.x,k=blockIdx.x*256+a;double v=0;if(k<N){double alpha=s[0]/fmax(s[1],1e-300);y[k]+=alpha*p[k];r[k]-=alpha*ap[k];z[k]=r[k]/d[k];v=r[k]*z[k];}q[a]=v;__syncthreads();for(int d0=128;d0;d0/=2){if(a<d0)q[a]+=q[a+d0];__syncthreads();}if(a==0)s[4+blockIdx.x]=q[0];}
__global__ void finalize_k(double*s,int blocks){__shared__ double q[256];int a=threadIdx.x;double v=0;for(int k=a;k<blocks;k+=256)v+=s[4+k];q[a]=v;__syncthreads();for(int d=128;d;d/=2){if(a<d)q[a]+=q[a+d];__syncthreads();}if(a==0){s[3]=q[0]/fmax(s[0],1e-300);s[0]=q[0];}}
__global__ void direction_k(double*p,const double*z,const double*s,int N){int a=blockIdx.x*blockDim.x+threadIdx.x;if(a<N)p[a]=z[a]+s[3]*p[a];}
void pcg_op(Tensor p,Tensor scale,Tensor t,Tensor j,Tensor weight,Tensor row,Tensor col,Tensor val,Tensor ir,Tensor inc,Tensor rate,Tensor out,double h){int E=t.size(0),N=p.size(0);op_rate_k<<<(E+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(p.data_ptr<double>(),scale.data_ptr<double>(),t.data_ptr<int64_t>(),j.data_ptr<double>(),rate.data_ptr<double>(),E);op_gather_k<<<(N+127)/128,128,0,at::cuda::getCurrentCUDAStream()>>>(p.data_ptr<double>(),scale.data_ptr<double>(),row.data_ptr<int64_t>(),col.data_ptr<int64_t>(),val.data_ptr<double>(),ir.data_ptr<int64_t>(),inc.data_ptr<int64_t>(),j.data_ptr<double>(),weight.data_ptr<double>(),rate.data_ptr<double>(),out.data_ptr<double>(),h,N);C10_CUDA_KERNEL_LAUNCH_CHECK();}
void pcg_iteration(Tensor y,Tensor r,Tensor p,Tensor ap,Tensor d,Tensor z,Tensor s){int N=p.numel();dot_k<<<1,512,0,at::cuda::getCurrentCUDAStream()>>>(p.data_ptr<double>(),ap.data_ptr<double>(),s.data_ptr<double>(),N);update_k<<<(N+255)/256,256,0,at::cuda::getCurrentCUDAStream()>>>(y.data_ptr<double>(),r.data_ptr<double>(),p.data_ptr<double>(),ap.data_ptr<double>(),d.data_ptr<double>(),z.data_ptr<double>(),s.data_ptr<double>(),N);finalize_k<<<1,256,0,at::cuda::getCurrentCUDAStream()>>>(s.data_ptr<double>(),(N+255)/256);direction_k<<<(N+255)/256,256,0,at::cuda::getCurrentCUDAStream()>>>(p.data_ptr<double>(),z.data_ptr<double>(),s.data_ptr<double>(),N);C10_CUDA_KERNEL_LAUNCH_CHECK();}
