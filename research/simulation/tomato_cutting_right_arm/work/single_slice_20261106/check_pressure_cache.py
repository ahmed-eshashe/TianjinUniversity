from pathlib import Path
import sys,json,numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_fast_exact_cad import FastExactCADPressurePacket
from tomato_cached_cad_pressure import CachedCADPressurePacket
wp.init();wp.set_device('cuda:0');z=np.load(w/'live07/checkpoint.npz');ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');b=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());x=z['x'].copy();t=z['blade_translation'].copy();R=z['blade_rotation'];packet={k:z['packet_'+k][::31].copy()for k in ['indices','barycentric','areas']};a=FastExactCADPressurePacket(len(x));c=CachedCADPressurePacket(len(x));q=wp.array(x,dtype=wp.vec3d);rows=[]
def setup():
 for p in [a,c]:p.set_cad(vertices=b['vertices'],triangles=b['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='Cache correctness control')
def check(label):
 ae=a.evaluate(q);ce=c.evaluate(q);fe=float(np.max(abs(a.force.numpy()-c.force.numpy())));ee=abs(ae-ce);assert fe<1e-10 and ee<1e-12;rows.append(dict(case=label,force_error=fe,energy_error=ee))
setup();check('initial');check('identical coordinates cache hit');x[packet['indices'][0,0],0]+=1e-6;q.assign(x);check('same pointer changed coordinates');t[2]-=1e-6
for p in [a,c]:p.pose(R,t)
check('changed pose');packet['areas']*=1.2;setup();check('changed material packet');(w/'pressure_cache_check.json').write_text(json.dumps(dict(passed=True,rows=rows),indent=2));print(rows)
