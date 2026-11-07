"""One disposable material-only timing probe; never used as production evidence."""
from pathlib import Path
import sys,cProfile,pstats,io,json,time
import numpy as np
from scipy.spatial.transform import Rotation
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_master_remap_slice_engine import subcycled_engine
checkpoint=w/'robot_cut13/checkpoints/step_005375.npz';z=np.load(checkpoint);scope=json.loads((checkpoint.parent.parent/'coupling_scope.json').read_text());pose=np.r_[z['blade_translation']+[-.0225,0,.0295],Rotation.from_matrix(z['blade_rotation']).as_quat()]
g=subcycled_engine(pose,np.array(scope['tool_com_local']),checkpoint=checkpoint,padding_m=.001);next(g);goal=pose.copy();goal[2]+=.02/2400
profile=cProfile.Profile();start=time.monotonic();profile.enable();state=g.send(dict(pose=goal,dt=1/2400));profile.disable();elapsed=time.monotonic()-start
profile.dump_stats(w/'material_step_profile.pstats');stream=io.StringIO();pstats.Stats(profile,stream=stream).sort_stats('cumtime').print_stats(35);(w/'material_step_profile.txt').write_text(stream.getvalue());report=dict(scope=__doc__,wall_s=elapsed,interval_substeps=state['interval_substeps'],solver_iterations=state['solver_iterations'],source_checkpoint=str(checkpoint),production_state_changed=False);(w/'material_step_profile.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));print(stream.getvalue())
