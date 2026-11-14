#include "geometry.cpp"
#include <map>
// Convex boundary faces are immutable between events. A clip modifies only
// crossed faces and creates its cap; no new convex hull is needed per event.
struct Surface { Poly v; std::vector<std::vector<int>> f; };
struct Event { std::vector<Surface> s; std::vector<long long> origin,codes; std::vector<double> V,X; int changed=0; };
static Surface initial(const Poly& p){Surface s;s.v=p;for(auto t:faces(p))s.f.push_back({t[0],t[1],t[2]});return s;}
static Surface cutface(const Surface& s,V n,double d){
 std::vector<double> h;double lo=INFINITY,hi=-INFINITY;
 for(auto v:s.v){double z=dot(v,n)-d;h.push_back(z);lo=std::min(lo,z);hi=std::max(hi,z);}
 if(hi<=0)return s;if(lo>=0)return {};
 std::vector<Poly> ff;Poly cap;
 auto crossing=[&](int i,int j){if(i>j)std::swap(i,j);double t=h[i]/(h[i]-h[j]);V x;for(int k=0;k<3;k++)x[k]=s.v[i][k]+t*(s.v[j][k]-s.v[i][k]);return x;};
 for(const auto& face:s.f){
  Poly out;
  for(size_t t=0;t<face.size();t++){
   int i=face[t],j=face[(t+1)%face.size()];
   if(h[i]<=0){out.push_back(s.v[i]);if(h[i]==0)cap.push_back(s.v[i]);}
   if((h[i]<0&&h[j]>0)||(h[j]<0&&h[i]>0)){V x=crossing(i,j);out.push_back(x);cap.push_back(x);}
  }
  out.erase(std::unique(out.begin(),out.end()),out.end());if(out.size()>1&&out.front()==out.back())out.pop_back();
  if(out.size()>=3)ff.push_back(out);
 }
 std::sort(cap.begin(),cap.end());cap.erase(std::unique(cap.begin(),cap.end()),cap.end());
 if(cap.size()<3)throw std::runtime_error("unresolved cap; no material discard");
 V c={0,0,0};for(auto v:cap)for(int k=0;k<3;k++)c[k]+=v[k]/cap.size();
 double nn=std::sqrt(dot(n,n));if(!(nn>0))throw std::runtime_error("invalid cutting normal");for(double& x:n)x/=nn;
 V axis={1,0,0};if(std::abs(n[0])>.8)axis={0,1,0};
 V e1={n[1]*axis[2]-n[2]*axis[1],n[2]*axis[0]-n[0]*axis[2],n[0]*axis[1]-n[1]*axis[0]};double length=std::sqrt(dot(e1,e1));for(double& x:e1)x/=length;
 V e2={n[1]*e1[2]-n[2]*e1[1],n[2]*e1[0]-n[0]*e1[2],n[0]*e1[1]-n[1]*e1[0]};
 std::sort(cap.begin(),cap.end(),[&](V a,V b){V u=sub(a,c),v=sub(b,c);double aa=std::atan2(dot(u,e2),dot(u,e1)),bb=std::atan2(dot(v,e2),dot(v,e1));return aa==bb?dot(u,u)<dot(v,v):aa<bb;});ff.push_back(cap);
 Surface out;for(auto& f:ff)out.v.insert(out.v.end(),f.begin(),f.end());std::sort(out.v.begin(),out.v.end());out.v.erase(std::unique(out.v.begin(),out.v.end()),out.v.end());
 if(out.v.size()<4)throw std::runtime_error("unresolved positive region");
 for(auto& f:ff){std::vector<int> ids;for(auto v:f)ids.push_back(std::lower_bound(out.v.begin(),out.v.end(),v)-out.v.begin());out.f.push_back(ids);}return out;
}
static std::pair<double,V> face_moments(const Surface& s){
 V c={0,0,0},weighted={0,0,0};for(auto v:s.v)for(int k=0;k<3;k++)c[k]+=v[k];for(double& x:c)x/=s.v.size();double total=0;
 for(const auto& f:s.f)for(size_t i=1;i+1<f.size();i++){
  V a=s.v[f[0]],b=s.v[f[i]],z=s.v[f[i+1]];double v=std::abs(det(sub(a,c),sub(b,c),sub(z,c)))/6.;total+=v;for(int k=0;k<3;k++)weighted[k]+=v*(a[k]+b[k]+z[k]+c[k])/4.;
 }
 if(!(total>0)||!std::isfinite(total))throw std::runtime_error("invalid surface volume");for(double& x:weighted)x/=total;return {total,weighted};
}
extern "C" {
void* surface_prepare(int count,const long long* ptr,const double* vertices){
 auto out=new Event;try{for(int i=0;i<count;i++){Poly p;for(long long j=ptr[i];j<ptr[i+1];j++)p.push_back({vertices[3*j],vertices[3*j+1],vertices[3*j+2]});out->s.push_back(initial(p));}return out;}catch(const std::exception& e){error_text=e.what();delete out;return nullptr;}
}
void* surface_event(void* old,const long long* codes,const double* oldvol,const double* oldcent,const double* cn,const double* cd,const double* fn,const double* fd,int cut_id,int use_front){
 auto src=(Event*)old;auto out=new Event;try{
  int digit=1;for(int i=0;i<cut_id;i++)digit*=3;
  for(size_t i=0;i<src->s.size();i++){
   const auto& p=src->s[i];
   auto add=[&](Surface child,int label){if(child.v.empty())return;out->origin.push_back(i);out->codes.push_back(codes[i]+label*digit);
    if(child.v==p.v){out->V.push_back(oldvol[i]);for(int k=0;k<3;k++)out->X.push_back(oldcent[3*i+k]);}
    else{auto [v,x]=face_moments(child);out->V.push_back(v);out->X.insert(out->X.end(),x.begin(),x.end());out->changed++;}out->s.push_back(std::move(child));};
   if((codes[i]/digit)%3){add(p,0);continue;}
   std::vector<std::pair<Surface,bool>> pending;
   if(use_front){V n={fn[3*i],fn[3*i+1],fn[3*i+2]};pending.push_back({cutface(p,n,fd[i]),true});for(double& x:n)x=-x;pending.push_back({cutface(p,n,-fd[i]),false});}else pending.push_back({p,true});
   V n={cn[3*i],cn[3*i+1],cn[3*i+2]},neg={-n[0],-n[1],-n[2]};
   for(auto& [s,active]:pending){if(s.v.empty())continue;if(active){add(cutface(s,n,cd[i]),1);add(cutface(s,neg,-cd[i]),2);}else add(std::move(s),0);}
  }return out;
 }catch(const std::exception& e){error_text=e.what();delete out;return nullptr;}
}
int surface_count(void* h){return ((Event*)h)->s.size();}
int surface_vertex_count(void* h){int n=0;for(auto& s:((Event*)h)->s)n+=s.v.size();return n;}
int surface_changed(void* h){return ((Event*)h)->changed;}
void surface_data(void* h,long long* ptr,double* vertices,long long* origin,long long* codes,double* vol,double* cent){
 auto r=(Event*)h;long long p=0;ptr[0]=0;
 for(size_t i=0;i<r->s.size();i++){for(auto v:r->s[i].v){for(int k=0;k<3;k++)vertices[3*p+k]=v[k];p++;}ptr[i+1]=p;origin[i]=r->origin[i];codes[i]=r->codes[i];vol[i]=r->V[i];for(int k=0;k<3;k++)cent[3*i+k]=r->X[3*i+k];}
}
void surface_free(void* h){delete (Event*)h;}
}
