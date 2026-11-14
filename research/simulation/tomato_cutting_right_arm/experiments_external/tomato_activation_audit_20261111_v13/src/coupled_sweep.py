"""Transactional GPU mechanics plus CPU current-sweep topology preparation."""
import time,numpy as np
from gpu_backend import GPUReference

class CoupledSweep:
    def __init__(self,driver,dt=3.90625e-7,external=None):
        self.driver=driver;self.dt=dt;self.external=external;self.gpu=GPUReference(driver.cpu,external,dt=dt)
        self.rebuilds=1;self.records=[]

    def advance(self,new_pose,steps):
        cpu=self.driver.cpu;start=time.perf_counter();snapshot={key:{f:getattr(p,f).copy() if isinstance(getattr(p,f),np.ndarray) else getattr(p,f) for f in ['q','vg','time','steps','support_impulse','support_moment']} for key,p in cpu.pieces.items()};clock=(cpu.time,cpu.steps)
        try:
            t=time.perf_counter();self.gpu.step(steps);self.gpu.export();step_s=time.perf_counter()-t
            t=time.perf_counter();proposal=self.driver.propose(new_pose);prepare_s=time.perf_counter()-t
            # Prepare replacement before committing, so failed upload cannot half-commit a cut.
            t=time.perf_counter();replacement=GPUReference(proposal['cpu'],self.external,dt=self.dt) if proposal['topology_changed'] else None;upload_s=time.perf_counter()-t
            self.driver.commit(proposal)
            if replacement is not None:self.gpu=replacement;self.rebuilds+=1
            else:self.gpu.cpu=self.driver.cpu
        except Exception:
            for key,p in cpu.pieces.items():
                for f,value in snapshot[key].items():setattr(p,f,value)
                p.update_state()
            cpu.time,cpu.steps=clock;self.gpu=GPUReference(cpu,self.external,dt=self.dt)
            raise
        r={'time':self.driver.cpu.time,'pieces':len(self.driver.cpu.pieces),'topology_changed':proposal['topology_changed'],'GPU_checked_and_export_s':step_s,'CPU_motion_topology_s':prepare_s,'GPU_rebuild_s':upload_s,'total_wall_s':time.perf_counter()-start,'new_area_m2':proposal['command']['new_reference_area_m2']};self.records.append(r);return r
