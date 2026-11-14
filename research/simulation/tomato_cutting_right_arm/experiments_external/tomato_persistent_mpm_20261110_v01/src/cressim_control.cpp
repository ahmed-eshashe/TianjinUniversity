// Isolated evaluation harness. Upstream engine remains unmodified.
// Stock mode follows upstream examples/example_cutting/main.cpp (BSD-3-Clause).
#include <cuda_runtime.h>
#include "simulation_factory.h"
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <sys/resource.h>
using namespace crmpm;
using Clock=std::chrono::steady_clock;
double seconds(Clock::time_point a){return std::chrono::duration<double>(Clock::now()-a).count();}
struct Sample { double mass=0,ke=0,maxSpeed=0,minx=1e30,maxx=-1e30,miny=1e30,maxy=-1e30,minz=1e30,maxz=-1e30; bool finite=true; double vy[4]={},vz[4]={},cx[4]={}; int n[4]={}; };
Sample sample(Scene* s,const std::vector<int>& labels){
 Sample a; auto& p=s->getParticleData();
 for(unsigned i=0;i<s->getNumAllocatedParticles();++i){auto x=p.positionMass[i]; auto v=p.velocity[i]; int g=labels[i]; double vs=v.dot(v);
  a.finite &= std::isfinite(x.x)&&std::isfinite(x.y)&&std::isfinite(x.z)&&std::isfinite(vs); a.mass+=x.w; a.ke+=.5*x.w*vs; a.maxSpeed=std::max(a.maxSpeed,std::sqrt(vs));
  a.minx=std::min(a.minx,double(x.x));a.maxx=std::max(a.maxx,double(x.x));a.miny=std::min(a.miny,double(x.y));a.maxy=std::max(a.maxy,double(x.y));a.minz=std::min(a.minz,double(x.z));a.maxz=std::max(a.maxz,double(x.z));
  a.n[g]++;a.vy[g]+=v.y();a.vz[g]+=v.z();a.cx[g]+=x.x;
 } for(int g=0;g<4;++g)if(a.n[g]){a.vy[g]/=a.n[g];a.vz[g]/=a.n[g];a.cx[g]/=a.n[g];} return a;
}
void snapshot(Scene*s,const std::vector<int>&labels,const std::string& name){
 std::ofstream f(name);f<<"id,group,x,y,z,vx,vy,vz,mass\n"<<std::setprecision(9); auto&p=s->getParticleData();
 for(unsigned i=0;i<s->getNumAllocatedParticles();++i){auto x=p.positionMass[i];auto v=p.velocity[i];f<<i<<','<<labels[i]<<','<<x.x<<','<<x.y<<','<<x.z<<','<<v.x()<<','<<v.y()<<','<<v.z()<<','<<x.w<<'\n';}
}
int main(int argc,char**argv){
 if(argc<5){std::cerr<<"usage: feasibility stock|cuts|held|absent|far mls|pb output_prefix pulse[0|1] [dt]\n";return 2;}
 std::string mode=argv[1],solver=argv[2],out=argv[3];bool pulse=std::stoi(argv[4]);double angle=(argc>6?std::stod(argv[6]):0)*3.141592653589793/180; double ca=std::cos(angle),sa=std::sin(angle);bool stock=mode=="stock",cuts=mode=="cuts",pb=solver=="pb";
 if(stock&&pb)return 2;
 const auto totalStart=Clock::now(); cudaFree(nullptr); size_t free0,total0;cudaMemGetInfo(&free0,&total0);
 auto*f=createFactory(10000,4,4,15000,true);SceneDesc d;
 d.solverType=pb?MpmSolverType::eGpuPbMpmSolver:MpmSolverType::eGpuMlsMpmSolver;d.numMaxParticles=10000;
 d.gravity=stock?Vec3f(0,-9.81,0):Vec3f(0,0,0);d.gridBounds=stock?Bounds3(Vec3f(-5,-.5,-5),Vec3f(5,5,5)):Bounds3(Vec3f(-.12),Vec3f(.12));
 d.gridCellSize=stock?.2f:.006f;d.solverIntegrationStepSize=stock?.002f:(pb?.001f:.0001f);if(argc>5)d.solverIntegrationStepSize=std::stof(argv[5]);d.solverIterations=20;
 auto*s=f->createScene(d);const float E=1e5f,nu=.4f;float4 material=pb?make_float4(100,.9,0,0):make_float4(E*nu/((1+nu)*(1-2*nu)),E/(2*(1+nu)),0,0);
 ParticleObject*obj=nullptr;
 if(stock){auto*g=f->createGeometry(GeometryType::eBox,make_float4(1,1,1,0));ParticleObjectDesc p;p.particleSpacing=.1;p.particleMass=1;p.geometry=g;p.position=Vec3f(0,2,0);p.rotation=Quat();p.invScale=Vec3f(2);p.materialType=ParticleMaterialType::eCoRotational;p.materialParams=material;obj=f->createParticleObject(p);g->release();if(!obj->addToScene(*s))return 3;}
 else {unsigned offset; if(!s->allocateParticles(8000,offset)||offset!=0)return 3;auto&p=s->getParticleData();auto&m=s->getParticleMaterialData();
  int n=0;for(int i=0;i<20;++i)for(int j=0;j<20;++j)for(int k=0;k<20;++k){float x=(i-9.5f)*.003f;if(!cuts)x+=(i<10?-1:1)*(mode=="far"?.012f:.0005f)+.001f;p.positionMass[n]=make_float4(x,(j-9.5f)*.003f,(k-9.5f)*.003f,.000027f);p.velocity[n]=Vec3f();m.type[n]=ParticleMaterialType::eCoRotational;m.params0[n]=material;s->getComputeInitialDataIndices().pushBack(n++);}
  s->setActiveMaskRange(0,8000,1);for(auto flag:{SceneDataDirtyFlags::eNumParticles,SceneDataDirtyFlags::eParticlePositionMass,SceneDataDirtyFlags::eParticleVelocity,SceneDataDirtyFlags::eParticleMaterialParams0,SceneDataDirtyFlags::eParticleMaterialType,SceneDataDirtyFlags::eComputeInitialData})s->markDirty(flag);
 }
 if(!stock&&!cuts){auto&p=s->getParticleData();for(unsigned i=0;i<s->getNumAllocatedParticles();++i){auto a=p.positionMass[i];p.positionMass[i]=make_float4(ca*a.x-sa*a.y,sa*a.x+ca*a.y,a.z,a.w);}s->markDirty(SceneDataDirtyFlags::eParticlePositionMass);}
 std::vector<int> labels;for(unsigned i=0;i<s->getNumAllocatedParticles();++i){auto p=s->getParticleData().positionMass[i];labels.push_back(cuts?2*(p.x>=0)+(p.z>=0):(i>=4000));}
 auto*g=f->createGeometry(GeometryType::eQuadSlicer,stock?make_float4(1,1,0,0):make_float4(.04,.04,0,0));
 ShapeDesc sd;sd.type=stock?ShapeType::eKinematic:ShapeType::eDynamic; // Dynamic flag only enables impulse output under kinematic contact model.
 sd.comInvMass=sd.inertiaInv0=sd.inertiaInv1=make_float4(0,0,0,0);sd.sdfSmoothDistance=0;sd.sdfFatten=stock?.1f:.0005f;sd.drag=stock?.5f:1.f;sd.friction=0;
 Transform pose;pose.rotation=Quat(0,0,.7071068,.7071068);pose.position=Vec3f((!stock&&!cuts)?.001f:0.f,stock?2.f:((mode=="held")?0.f:.08f),0);if(!stock&&!cuts){auto a=pose.position;pose.position=Vec3f(ca*a.x()-sa*a.y(),sa*a.x()+ca*a.y(),a.z());pose.rotation=Quat(0,0,std::sin((angle+1.5707963267948966)/2),std::cos((angle+1.5707963267948966)/2));}sd.transform=pose;auto*blade=f->createShape(*g,sd);g->release();
 if(!stock)s->addShape(blade);
 bool added=!stock;
 float dt=d.solverIntegrationStepSize;float frame=stock?.02f:(cuts?(pb?2.f:20.f)*dt-dt*.001f:dt);
 int substeps=0;float acc=0;while(acc<frame){acc+=dt;substeps++;}double integratedFrame=double(dt)*substeps;
 s->advance(frame);s->fetchResults(); // initialization / warm-up excluded from steady timings
 size_t free1,total1;cudaMemGetInfo(&free1,&total1);
 snapshot(s,labels,out+"_initial.csv");
 if(!stock&&!cuts&&pulse){auto&p=s->getParticleData();for(unsigned i=0;i<labels.size();++i)if(labels[i]==0)p.velocity[i].z()+=.01f;s->markDirty(SceneDataDirtyFlags::eParticleVelocity);}
 auto initial=sample(s,labels);double sim=0,stepWall=0,ioWall=0,maxForce=0,maxSpeed=0;bool allFinite=true;int executed=0;float elapsedStock=0;
 int steps=stock?300:(cuts?int(std::round(1.7/integratedFrame)):int(std::round(.02/integratedFrame)));int firstEnd=cuts?int(std::round(.8/integratedFrame)):-1,secondEnd=cuts?int(std::round(1.6/integratedFrame)):-1;
 std::ofstream csv(out+"_trace.csv");csv<<"step,t,blade_x,blade_y,blade_z,wall_s,impulse_x,impulse_y,impulse_z,impulse_over_dt_norm,ke,max_speed,mass,finite,min_x,max_x,min_y,max_y,min_z,max_z,vy0,vy1,vy2,vy3,vz0,vz1,vz2,vz3,cx0,cx1,cx2,cx3\n"<<std::setprecision(10);
 for(int k=0;k<steps;++k){
  if(stock){elapsedStock+=.02f;if(elapsedStock>2){if(!added){s->addShape(blade);added=true;}pose.position-=Vec3f(0,.01,0);blade->setKinematicTarget(pose,.02);}}
  if(cuts){if(k<firstEnd){pose.rotation=Quat(0,0,.7071068,.7071068);pose.position=Vec3f(0,.08f-.16f*(k+1)/firstEnd,0);}
   else if(k<secondEnd){if(k==firstEnd){pose.rotation=Quat(.7071068,0,0,.7071068);pose.position=Vec3f(0,.08,0);blade->setPose(pose);blade->setVelocity(Vec3f(),Vec3f());}pose.position=Vec3f(0,.08f-.16f*(k-firstEnd+1)/(secondEnd-firstEnd),0);}
   if(k<secondEnd)blade->setKinematicTarget(pose,float(integratedFrame));
   if(k==secondEnd){snapshot(s,labels,out+"_withdrawn.csv");if(pulse){auto&p=s->getParticleData();for(unsigned i=0;i<labels.size();++i)if(labels[i]==0)p.velocity[i].y()+=.01f;s->markDirty(SceneDataDirtyFlags::eParticleVelocity);}}
  }
  auto before=Clock::now();s->advance(frame);s->fetchResults();double wall=seconds(before);stepWall+=wall;sim+=integratedFrame;executed++;
  auto a=sample(s,labels);auto q=blade->getShapeForce();double force=std::sqrt(double(q.x)*q.x+double(q.y)*q.y+double(q.z)*q.z)/integratedFrame;
  allFinite &= a.finite;maxForce=std::max(maxForce,force);maxSpeed=std::max(maxSpeed,a.maxSpeed);
  auto io=Clock::now();csv<<k<<','<<sim<<','<<pose.position.x()<<','<<pose.position.y()<<','<<pose.position.z()<<','<<wall<<','<<q.x<<','<<q.y<<','<<q.z<<','<<force<<','<<a.ke<<','<<a.maxSpeed<<','<<a.mass<<','<<a.finite<<','<<a.minx<<','<<a.maxx<<','<<a.miny<<','<<a.maxy<<','<<a.minz<<','<<a.maxz;
  for(double v:a.vy)csv<<','<<v;for(double v:a.vz)csv<<','<<v;for(double v:a.cx)csv<<','<<v;csv<<'\n';ioWall+=seconds(io);
  if(cuts&&(k+1==firstEnd))snapshot(s,labels,out+"_first_cut.csv");
  if(!a.finite){std::cerr<<"NONFINITE at "<<k<<"\n";break;}
 }
 csv.close();snapshot(s,labels,out+"_final.csv");auto final=sample(s,labels);
 struct rusage usage;getrusage(RUSAGE_SELF,&usage);
 std::ofstream js(out+"_summary.json");js<<std::setprecision(12)<<"{\n\"mode\":\""<<mode<<"\",\"solver\":\""<<solver<<"\",\"pulse\":"<<pulse<<",\"particles\":"<<labels.size()<<",\"dt\":"<<dt<<",\"frame_request\":"<<frame<<",\"substeps_per_frame\":"<<substeps<<",\"frames\":"<<executed<<",\"simulated_seconds\":"<<sim<<",\"synchronized_step_seconds\":"<<stepWall<<",\"wall_per_sim_second\":"<<stepWall/sim<<",\"trace_write_seconds\":"<<ioWall<<",\"total_wall_seconds\":"<<seconds(totalStart)<<",\"peak_rss_mib\":"<<usage.ru_maxrss/1024.0<<",\"harness_version\":2,\"gpu_allocation_delta_mib\":"<<double(free0-free1)/(1024*1024)<<",\"initial_mass\":"<<initial.mass<<",\"final_mass\":"<<final.mass<<",\"all_finite\":"<<(allFinite?"true":"false")<<",\"max_speed\":"<<maxSpeed<<",\"max_impulse_over_frame_dt\":"<<maxForce<<",\"grid_cell_m\":"<<d.gridCellSize<<",\"pb_iterations\":"<<d.solverIterations<<",\"material_params\":["<<material.x<<','<<material.y<<"]}\n";
 std::cout<<out<<" finite="<<allFinite<<" particles="<<labels.size()<<" wall/sim="<<stepWall/sim<<"\n";
 blade->release();if(obj)obj->release();s->release();releaseFactory(f);return allFinite?0:4;
}
