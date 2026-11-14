from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parent;R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(W/'src'),str(R/'rl')]
from frames import average_wrench,ExchangeClock
from tomato_wrench_contract import to_world
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
import instrumented_solver as s
def array(v,dtype):return wp.array(v,dtype=dtype,device='cuda')
Q=Rotation.from_rotvec([.3,-.4,.2]).as_matrix();anchor=np.array([.2,-.1,.4]);com=np.array([-.2,.1,.3]);f=np.array([.7,-.3,1.1]);point=np.array([.1,.02,-.04]);moment=np.cross(point,f)+[.01,.02,.03];dt=.002
observed=average_wrench(f*dt,moment*dt,dt,Q,anchor,com);ff,mm=to_world(f,moment,Q,anchor,com);frame_error=float(np.max(np.abs(observed-np.r_[ff,mm])))
omega=np.array([.2,-.1,.3]);velocity=np.array([.04,-.02,.01]);world_w=Q@omega;world_v_at_com=Q@velocity+np.cross(world_w,com-anchor)
power_error=abs(float(observed@np.r_[world_v_at_com,world_w]-np.r_[f,moment]@np.r_[velocity,omega]))
clock=ExchangeClock();clock.accept(0,0,.002);clock.queue_once(0);rejected=0
for fn in [lambda:clock.queue_once(0),lambda:clock.accept(0,.002,.002),lambda:clock.accept(1,.003,.002)]:
 try:fn()
 except ValueError:rejected+=1
clock.reset();clock.accept(0,0,.002)
# Single unstretched bond: an analytic force/moment fixture, no body gravity or elasticity.
x=array([[-.001,.015,.01],[.001,.015,.01]],wp.vec3);v=array([[0,0,0]]*2,wp.vec3);force=array([[0,0,0]]*2,wp.vec3);edge=array([[0,1]],wp.vec2i)
rest=array([.002],float);stiff=array([1000.],float);mass=array([.001,.001],float);area=array([1e-6],float);alive=array([1],int);paid=array([0.],float)
tool=array([[0,0,0]],wp.vec3);vel=array([[0,-.001,.01]],wp.vec3);angular=array([[0,0,0]],wp.vec3);rot=array([[0,0,0,1]],wp.quat);reaction=array([[0,0,0]],wp.vec3);momentarr=array([[0,0,0]],wp.vec3);load=array([0.],float);ledger=wp.zeros((1,7),dtype=float,device='cuda');bad=array([0],int)
wp.launch(s.bonds,1,[x,v,force,edge,rest,stiff,mass,area,alive,paid,tool,vel,angular,rot,reaction,momentarr,load,ledger,bad,.0035,.0001,2,1,.06,1]);wp.synchronize()
fmeas=reaction.numpy()[0].astype(float);mmeas=momentarr.numpy()[0].astype(float);dwork=80e-6/.0035*(.001+.25*.01)*.0001;expected=-dwork/(np.linalg.norm([0,-.001,.01])**2*.0001)*np.array([0,-.001,.01]);fixture_force_error=float(np.max(abs(expected-fmeas)));fixture_moment_error=float(np.max(abs(np.cross([0,.015,.01],fmeas)-mmeas)));conservation=float(np.linalg.norm(force.numpy().sum(0)+fmeas));work_error=abs(float(-fmeas@np.array([0,-.001,.01])*.0001-ledger.numpy()[0,2]))
# Exercise all instrumented kernel bindings with a zero-contact complete step.
sys.path.insert(0,str(W.parent/'tomato_approx_rl_20261113_v28/src'));from model import lattice
g=s.Solver(lattice('tomato'),dt=.0001,adaptive=True);g.step([0,0,0],20);zero=bool(np.array_equal(g.linear_impulse.numpy(),np.zeros((1,3))) and np.array_equal(g.angular_impulse.numpy(),np.zeros((1,3))) and not g.bad.numpy().any())
result={'frame_error':frame_error,'power_error_W':power_error,'bad_clock_cases_rejected':rejected,'fixture_force_error_N':fixture_force_error,'fixture_moment_error_Nm':fixture_moment_error,'force_conservation_error_N':conservation,'contact_work_identity_error_J':work_error,'zero_contact_pass':zero,'pass':bool(frame_error<1e-12 and power_error<1e-12 and rejected==3 and fixture_force_error<1e-7 and fixture_moment_error<1e-9 and conservation<1e-8 and work_error<1e-10 and zero),'scope':'Analytic frame/clock and isolated GPU force-moment telemetry fixtures only. Native robot transfer and full integration still require tests.'}
(W/'reports/interface_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert result['pass']
