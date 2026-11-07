from pathlib import Path
import sys,json,time,traceback
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'));out=w/'partition_growth01';out.mkdir(exist_ok=True);source=w/'robot_cut08';z=np.load(source/'material_before_failed_microstep.npz');meta=json.loads((source/'material_before_failed_microstep.json').read_text());origin=np.array([-.0225,0,.0295]);x=z['x']+origin;pose=np.array(meta['trial_pose']);com=np.array(json.loads((source/'coupling_scope.json').read_text())['tool_com_local']);start=time.monotonic()
try:
 from tomato_native_full_model import registry
 from tomato_partition_diagnostic_refresh import refresh_packet
 data=registry();reference=data['x']+[0,0,.002];triangles=np.array([t for piece in data['design']['pieces']for t in piece['triangles']]);blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());solid=json.loads((r/'work/exact_blade_cells.json').read_text());packet={k:z['packet_'+k]for k in ['indices','barycentric','areas']}
 packet,value,report=refresh_packet(blade,np.array(solid['cells']),x,triangles,reference,z['blade_rotation'],z['blade_translation']+origin,com,packet,padding_m=.001,lookahead=(x+z['v']*meta['micro_interval'],pose[:3],Rotation.from_quat(pose[3:]).as_matrix()))
 result=dict(passed=True,report=report)
except BaseException as e:result=dict(passed=False,error=str(e),details=e.args,traceback=traceback.format_exc())
result['wall_s']=time.monotonic()-start;(out/'result.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
