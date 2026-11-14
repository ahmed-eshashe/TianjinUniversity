#include "PhysX/physx/source/lowleveldynamics/src/TomatoDriveTrace.h"
int main() {
    const auto p=tomato_trace::recorder().begin();
    tomato_trace::recorder().append({p,123,2,1,5,.01,.001,0,.5,1,2,2});
}
