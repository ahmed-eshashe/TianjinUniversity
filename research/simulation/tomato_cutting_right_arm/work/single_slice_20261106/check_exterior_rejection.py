from pathlib import Path
import sys,json,time
import numpy as np
import warp as wp

r=Path(__file__).resolve().parents[2]
w=Path(__file__).parent
sys.path.insert(0,str(r/'rl'))
from tomato_cached_cad_pressure import CachedCADPressurePacket
from tomato_exterior_culled_pressure import ExteriorCulledCADPressurePacket
wp.init();wp.set_device('cuda:0')
z=np.load(w/'live16/checkpoint.npz')
blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
kwargs=dict(vertices=blade['vertices'],triangles=blade['triangles'],
    indices=z['packet_indices'],barycentric=z['packet_barycentric'],areas=z['packet_areas'],
    rotation=z['blade_rotation'],translation=z['blade_translation'],com_local=ref['com_local'],source_scope='Exterior rejection comparison only')
old=CachedCADPressurePacket(len(z['x']));new=ExteriorCulledCADPressurePacket(len(z['x']))
for obj in [old,new]:obj.set_cad(**kwargs)
results=[]
for offset in [0.,1/2400,-1/2400]:
    x=wp.array(z['x']+offset*z['v'],dtype=wp.vec3d)
    a=old.evaluate(x);b=new.evaluate(x)
    error=dict(energy_j=abs(a-b),force_n=float(abs(old.force.numpy()-new.force.numpy()).max()),
        sample_hessian=float(abs(old.sample_hessian.numpy()-new.sample_hessian.numpy()).max()),
        reaction=float(abs(old.reaction()-new.reaction()).max()),rejected=int((new.face.numpy()<0).sum()))
    assert error['energy_j']<1e-12 and error['force_n']<1e-10 and error['sample_hessian']<1e-8 and error['reaction']<1e-10,error
    results.append(error)
timings=[[],[]]
for repeat in range(10):
    for index,obj in enumerate([old,new]):
        obj._valid=False;wp.synchronize();start=time.perf_counter();obj.evaluate(x);wp.synchronize();timings[index].append(time.perf_counter()-start)
result=dict(contact_operator_parity_passed=True,checks=results,
    original_median_s=float(np.median(timings[0])),candidate_median_s=float(np.median(timings[1])),
    speed_ratio=float(np.median(timings[0])/np.median(timings[1])),adopted=False)
(w/'exterior_rejection_check.json').write_text(json.dumps(result,indent=2));print(result)
