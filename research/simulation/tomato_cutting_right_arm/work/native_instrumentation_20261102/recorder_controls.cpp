#include "PhysX/physx/source/lowleveldynamics/src/TomatoDriveTrace.h"
#include <thread>
void produce() {
    const auto p=tomato_trace::recorder().begin();
    for (unsigned i=0;i<131073;++i)
        tomato_trace::recorder().append({p,123,2,i,5,.01,.001,0,.5,1,2,2});
}
int main() { std::thread a(produce), b(produce); a.join(); b.join(); }
