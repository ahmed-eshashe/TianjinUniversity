#include <libqhull_r/qhull_ra.h>
#include <array>
#include <vector>
#include <set>
#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string>
#include <cstdio>
#include <cstring>
using V=std::array<double,3>;
using Poly=std::vector<V>;
static thread_local std::string error_text;
static V sub(V a,V b){return {a[0]-b[0],a[1]-b[1],a[2]-b[2]};}
static double dot(V a,V b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
static double det(V a,V b,V c){return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);}
static std::vector<std::array<int,3>> faces(const Poly& p){
 V c={0,0,0},lo=p[0],hi=p[0];for(auto v:p)for(int k=0;k<3;k++){c[k]+=v[k];lo[k]=std::min(lo[k],v[k]);hi[k]=std::max(hi[k],v[k]);}
 double scale=0;for(int k=0;k<3;k++){c[k]/=p.size();scale=std::max(scale,hi[k]-lo[k]);}
 if(!(scale>0))throw std::runtime_error("zero scale; no material discard");
 std::vector<double> x;for(auto v:p)for(int k=0;k<3;k++)x.push_back((v[k]-c[k])/scale);
 qhT state;qhT *qh=&state;FILE* err=stderr;qh_zero(qh,err);char flags[]="qhull Qt";
 int status=qh_new_qhull(qh,3,(int)p.size(),x.data(),False,flags,nullptr,err);
 std::vector<std::array<int,3>> out;
 if(!status){facetT *facet;vertexT *vertex,**vertexp;FORALLfacets{std::array<int,3> f;int j=0;FOREACHvertex_(facet->vertices){if(j<3)f[j]=qh_pointid(qh,vertex->point);j++;}if(j!=3){status=-1;break;}out.push_back(f);}}
 qh_freeqhull(qh,!qh_ALL);int n,bytes;qh_memfreeshort(qh,&n,&bytes);
 if(status||out.empty())throw std::runtime_error("Qhull failure; ambiguous geometry rejected");return out;
}
static Poly clip(const Poly& p,V n,double d){
 std::vector<double>s;double lo=INFINITY,hi=-INFINITY;
 for(auto v:p){double z=dot(v,n)-d;s.push_back(z);lo=std::min(lo,z);hi=std::max(hi,z);}
 if(hi<=0)return p;if(lo>=0)return {};
 auto ff=faces(p);std::set<std::pair<int,int>> edges;
 for(auto f:ff)for(int i=0;i<3;i++)for(int j=i+1;j<3;j++)edges.emplace(std::min(f[i],f[j]),std::max(f[i],f[j]));
 Poly out;for(size_t i=0;i<p.size();i++)if(s[i]<=0)out.push_back(p[i]);
 for(auto [i,j]:edges)if((s[i]<0&&s[j]>0)||(s[j]<0&&s[i]>0)){V x;double t=s[i]/(s[i]-s[j]);for(int k=0;k<3;k++)x[k]=p[i][k]+t*(p[j][k]-p[i][k]);out.push_back(x);}
 std::sort(out.begin(),out.end());out.erase(std::unique(out.begin(),out.end()),out.end());
 if(out.size()<4)throw std::runtime_error("unresolved clipped region; no silent discard");return out;
}
static std::pair<double,V> moments(const Poly& p){
 V c={0,0,0},weighted={0,0,0};for(auto v:p)for(int k=0;k<3;k++)c[k]+=v[k];for(int k=0;k<3;k++)c[k]/=p.size();
 double total=0;for(auto f:faces(p)){double vol=std::abs(det(sub(p[f[0]],c),sub(p[f[1]],c),sub(p[f[2]],c)))/6.;total+=vol;for(int k=0;k<3;k++)weighted[k]+=vol*(p[f[0]][k]+p[f[1]][k]+p[f[2]][k]+c[k])/4.;}
 if(!(total>0)||!std::isfinite(total))throw std::runtime_error("invalid material volume");for(int k=0;k<3;k++)weighted[k]/=total;return {total,weighted};
}
struct Result{std::vector<long long> ptr{0},origin,codes;std::vector<double> vertices,vol,cent;int changed=0;};
extern "C" {
const char* geometry_error(){return error_text.c_str();}
void* geometry_event(int count,const long long* ptr,const double* vertices,const long long* codes,const double* oldvol,const double* oldcent,const double* cn,const double* cd,const double* fn,const double* fd,int cut_id,int use_front){
 Result* out=new Result;try{
  int digit=1;for(int i=0;i<cut_id;i++)digit*=3;
  for(int i=0;i<count;i++){
   Poly p;for(long long j=ptr[i];j<ptr[i+1];j++)p.push_back({vertices[3*j],vertices[3*j+1],vertices[3*j+2]});
   auto add=[&](const Poly& child,int label){if(child.empty())return;out->origin.push_back(i);out->codes.push_back(codes[i]+label*digit);for(auto v:child)for(double x:v)out->vertices.push_back(x);out->ptr.push_back(out->vertices.size()/3);
    if(child==p){out->vol.push_back(oldvol[i]);for(int k=0;k<3;k++)out->cent.push_back(oldcent[3*i+k]);}
    else{auto [vol,cent]=moments(child);out->vol.push_back(vol);for(double x:cent)out->cent.push_back(x);out->changed++;}};
   if((codes[i]/digit)%3){add(p,0);continue;}
   std::vector<std::pair<Poly,bool>> pending;
   if(use_front){V n={fn[3*i],fn[3*i+1],fn[3*i+2]};pending.push_back({clip(p,n,fd[i]),true});for(double& x:n)x=-x;pending.push_back({clip(p,n,-fd[i]),false});}
   else pending.push_back({p,true});
   V n={cn[3*i],cn[3*i+1],cn[3*i+2]},neg={-n[0],-n[1],-n[2]};
   for(auto& [poly,active]:pending){if(poly.empty())continue;if(!active)add(poly,0);else{add(clip(poly,n,cd[i]),1);add(clip(poly,neg,-cd[i]),2);}}
  }return out;
 }catch(const std::exception& e){error_text=e.what();delete out;return nullptr;}
}
int result_regions(void* h){return ((Result*)h)->vol.size();}
int result_vertices(void* h){return ((Result*)h)->vertices.size()/3;}
int result_changed(void* h){return ((Result*)h)->changed;}
const long long* result_ptr(void* h){return ((Result*)h)->ptr.data();}
const long long* result_origin(void* h){return ((Result*)h)->origin.data();}
const long long* result_codes(void* h){return ((Result*)h)->codes.data();}
const double* result_xyz(void* h){return ((Result*)h)->vertices.data();}
const double* result_volume(void* h){return ((Result*)h)->vol.data();}
const double* result_centroid(void* h){return ((Result*)h)->cent.data();}
void result_free(void* h){delete (Result*)h;}
}
