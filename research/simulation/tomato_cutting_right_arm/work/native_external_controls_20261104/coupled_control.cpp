#include "PxPhysicsAPI.h"
#include <cstdio>
#include <cstdlib>
using namespace physx;
int main(int argc,char**argv){
 if(argc!=2)return 2;
 PxDefaultAllocator allocator;PxDefaultErrorCallback errors;
 auto* foundation=PxCreateFoundation(PX_PHYSICS_VERSION,allocator,errors);
 auto* physics=PxCreatePhysics(PX_PHYSICS_VERSION,*foundation,PxTolerancesScale());
 auto* dispatcher=PxDefaultCpuDispatcherCreate(1);
 PxSceneDesc desc(physics->getTolerancesScale());desc.gravity=PxVec3(0);desc.cpuDispatcher=dispatcher;desc.filterShader=PxDefaultSimulationFilterShader;desc.solverType=PxSolverType::eTGS;desc.flags|=PxSceneFlag::eENABLE_EXTERNAL_FORCES_EVERY_ITERATION_TGS;
 auto* scene=physics->createScene(desc);auto* a=physics->createArticulationReducedCoordinate();a->setArticulationFlag(PxArticulationFlag::eFIX_BASE,true);a->setSolverIterationCounts(32,8);a->setSleepThreshold(0);
 auto* root=a->createLink(nullptr,PxTransform(PxIdentity));auto* link=a->createLink(root,PxTransform(PxIdentity));
 root->setMass(1);root->setMassSpaceInertiaTensor(PxVec3(1));link->setMass(2);link->setMassSpaceInertiaTensor(PxVec3(1));link->setLinearDamping(0);link->setAngularDamping(0);
 auto* tip=a->createLink(link,PxTransform(PxIdentity));tip->setMass(3);tip->setMassSpaceInertiaTensor(PxVec3(1));tip->setLinearDamping(0);tip->setAngularDamping(0);auto* k=tip->getInboundJoint();k->setJointType(PxArticulationJointType::ePRISMATIC);k->setMotion(PxArticulationAxis::eX,PxArticulationMotion::eFREE);
 auto* j=link->getInboundJoint();j->setJointType(PxArticulationJointType::ePRISMATIC);j->setMotion(PxArticulationAxis::eX,PxArticulationMotion::eFREE);scene->addArticulation(*a);
 auto* cache=a->createCache();cache->jointForce[0]=std::atof(argv[1]);cache->jointForce[1]=2*std::atof(argv[1]);a->applyCache(*cache,PxArticulationCacheFlag::eFORCE);
 std::printf("step,q1,v1,q2,v2\n");for(int i=0;i<2;i++){scene->simulate(1.f/240);scene->fetchResults(true);std::printf("%d,%.17g,%.17g,%.17g,%.17g\n",i,j->getJointPosition(PxArticulationAxis::eX),j->getJointVelocity(PxArticulationAxis::eX),k->getJointPosition(PxArticulationAxis::eX),k->getJointVelocity(PxArticulationAxis::eX));}
 cache->release();a->release();scene->release();dispatcher->release();physics->release();foundation->release();return 0;
}
