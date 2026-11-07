from pathlib import Path
import sys,json,numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_cached_cad_pressure import CachedCADPressurePacket
wp.init();wp.set_device('cuda:0');z=np.load(w/'live08/checkpoint.npz');b=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');p=CachedCADPressurePacket(len(z['x']));packet={k:z['packet_'+k][::7]for k in ['indices','barycentric','areas']};p.set_cad(vertices=b['vertices'],triangles=b['triangles'],**packet,rotation=z['blade_rotation'],translation=z['blade_translation'],com_local=ref['com_local'],source_scope='Read-only pressure feature audit');p.evaluate(wp.array(z['x'],dtype=wp.vec3d));inside=p.phi.numpy()<0;ids,n=np.unique(p.face.numpy()[inside],return_counts=True);print(sorted(zip(ids.tolist(),n.tolist()),key=lambda a:-a[1]));print('inside fraction',inside.mean())
