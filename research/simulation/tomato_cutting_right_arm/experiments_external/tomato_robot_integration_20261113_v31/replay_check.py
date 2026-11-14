"""Replay saved measured knife poses from a fresh saved material state, no robot."""
from pathlib import Path
import sys,json,argparse,time,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'tomato_approx_rl_20261113_v28/src'));sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from coupled_environment import CuttingEnv
parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args();r=args.run
E=CuttingEnv(1);g=E.g;state=np.load(r/'material_start.npz');rows=json.loads((r/'coupling_trace.json').read_text());original=np.load(r/'material_final.npz')
for key in state.files:getattr(g,key).assign(state[key])
g.save_initial();last_pos=state['tool'][0].astype(float);last_rot=Rotation.from_quat(state['rotation'][0]).as_matrix();t0=0.;start=time.monotonic()
for i,row in enumerate(rows):
 pos=np.array(row['proxy']);rot=np.array(row['rotation']);dt=row['time']-t0
 g.tool.assign(last_pos[None].astype(np.float32));g.rotation.assign(Rotation.from_matrix(last_rot).as_quat()[None].astype(np.float32));action=np.r_[(pos-last_pos)/dt,Rotation.from_matrix(rot@last_rot.T).as_rotvec()/dt];g.linear_impulse.zero_();g.angular_impulse.zero_();g.step(action,round(dt/g.base_dt));last_pos=pos;last_rot=rot;t0=row['time']
 if g.bad.numpy().any():break
_,info=E.observe();diff=np.linalg.norm(g.x.numpy()-original['x'],axis=1);oldpeak=max(row['peak_N']for row in rows);peak=float(g.peak.numpy()[0]);same_bonds=np.array_equal(g.alive.numpy(),original['alive'])
result=dict(replayed_intervals=i+1,total_intervals=len(rows),same_final_bonds=same_bonds,max_position_difference_m=float(diff.max()),rms_position_difference_m=float(np.sqrt(np.mean(diff**2))),peak_force_N=peak,original_peak_force_N=oldpeak,relative_peak_difference=abs(peak-oldpeak)/max(oldpeak,1e-9),bad=int(g.bad.numpy()[0]),parts=int(info['parts'][0]),wall_s=time.monotonic()-start)
result['pass']=bool(i+1==len(rows) and same_bonds and result['bad']==0 and result['max_position_difference_m']<.0001 and result['relative_peak_difference']<.05)
(r/'actual_pose_replay.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
# Restore every material state array and verify the state is intact and unloaded.
E.reset();reset_exact=all(np.array_equal(getattr(g,k).numpy(),state[k]) for k in state.files);(r/'reset_check.json').write_text(json.dumps({'restores_saved_fresh_state_exactly':reset_exact,'scope':'Material and coupling accumulators. Robot reset is a clean relaunch.'},indent=2))
