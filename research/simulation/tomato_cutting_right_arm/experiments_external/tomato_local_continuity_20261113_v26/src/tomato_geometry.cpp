#include "facet_geometry.cpp"
// Reset-time intersection with the verified convex source exterior. All
// positive material is kept; an empty intersection alone is omitted.
extern "C" void* surface_crop(void* old,int nplanes,const double* planes){
 auto src=(Event*)old;auto out=new Event;
 try{
  for(size_t i=0;i<src->s.size();++i){
   Surface p=src->s[i];bool empty=false;std::vector<int> crossing;
   for(int j=0;j<nplanes;j++){
    V n={planes[4*j],planes[4*j+1],planes[4*j+2]};double d=-planes[4*j+3],lo=INFINITY,hi=-INFINITY;
    for(auto v:p.v){double s=dot(n,v)-d;lo=std::min(lo,s);hi=std::max(hi,s);}
    if(lo>=0){empty=true;break;}if(hi>0)crossing.push_back(j);
   }
   if(empty)continue;
   for(int j:crossing){V n={planes[4*j],planes[4*j+1],planes[4*j+2]};p=cutface(p,n,-planes[4*j+3]);if(p.v.empty()){empty=true;break;}}
   if(empty)continue;
   // Hundreds of coplanar source clips can leave redundant boundary loops.
   // Vertices remain exact, but summing those loops can double-count volume.
   // Reset construction therefore rebuilds the convex boundary and moments;
   // this is never a volume correction, threshold or vertex deletion.
   auto [vol,cent]=moments(p.v);p=initial(p.v);out->s.push_back(std::move(p));out->origin.push_back(i);out->codes.push_back(0);out->V.push_back(vol);out->X.insert(out->X.end(),cent.begin(),cent.end());out->changed++;
  }
  return out;
 }catch(const std::exception& e){error_text=e.what();delete out;return nullptr;}
}
