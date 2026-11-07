from pathlib import Path
import json
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_corrected_contact_exchange import AcceptedContactExchange
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');out=R/'work/corrected_contact_exchange_20261102/operator01';out.mkdir(exist_ok=False);rng=np.random.default_rng(301);maximum=dict(impulse=0.,world_moment=0.,power=0.,rotated_wrench=0.);negative=0
for case in range(100):
 x=rng.normal(size=(12,3))*.005;f=rng.normal(size=(12,3))*1e-5;cp=rng.normal(size=3)*.002;cn=cp+rng.normal(size=3)*1e-6;forces=[];dt=1/76800;wrenches=[]
 e=AcceptedContactExchange(block_id=str(case),time_start_s=0.,robot_dt_s=2*dt,target_dt_s=dt,body_id=45,geometry_com_world=cp,native_com_world=cn)
 for i in range(2):
  ff=f*(i+1);w=np.r_[-ff.sum(0),-np.cross(x-cp,ff).sum(0)];e.accept(time_start_s=i*dt,time_end_s=(i+1)*dt,points_world=x,target_nodal_force=ff,pressure_reaction_at_geometry_com=w,maximum_penetration_m=1e-5);forces.append(ff);wrenches.append(w)
 request=e.finish();native=np.array(request.requested_native_com_wrench);F=-np.mean(forces,axis=0).sum(0);M=-np.cross(x-cn,np.mean(forces,axis=0)).sum(0);maximum['world_moment']=max(maximum['world_moment'],float(abs(native-np.r_[F,M]).max()));maximum['impulse']=max(maximum['impulse'],float(abs(np.array(request.reaction_impulse_world)-dt*np.sum(wrenches,axis=0)).max()))
 omega=rng.normal(size=3);vcn=rng.normal(size=3);vcp=vcn+np.cross(omega,cp-cn);maximum['power']=max(maximum['power'],float(abs(native@np.r_[vcn,omega]-(np.mean(wrenches,axis=0)@np.r_[vcp,omega]))))
 rot=Rotation.random(random_state=rng).as_matrix();shift=rng.normal(size=3);xx=x@rot.T+shift;cc=rot@cp+shift;nn=rot@cn+shift;ff=np.mean(forces,axis=0)@rot.T;rr=np.r_[-ff.sum(0),-np.cross(xx-nn,ff).sum(0)];maximum['rotated_wrench']=max(maximum['rotated_wrench'],float(abs(rr-np.r_[rot@native[:3],rot@native[3:]]).max()))
 calls=[];e.queue_once(lambda req:calls.append(req));assert len(calls)==1
 for action in [lambda:e.queue_once(lambda req:calls.append(req)),lambda:e.finish()]:
  try:action();raise AssertionError('Invalid exchange accepted')
  except ValueError:negative+=1
assert max(maximum.values())<1e-12
for failure in ['incomplete','wrong_clock','wrong_sign','too_deep','too_much_force','callback_error']:
 e=AcceptedContactExchange(block_id=failure,time_start_s=0.,robot_dt_s=1e-4,target_dt_s=1e-4,body_id=45,geometry_com_world=[0,0,0],native_com_world=[0,0,0]);x=np.array([[.001,0,0]]);f=np.array([[0,0,-.001]]);w=np.r_[-f.sum(0),-np.cross(x,f).sum(0)]
 try:
  if failure=='incomplete':e.finish()
  elif failure=='callback_error':
   e.accept(time_start_s=0,time_end_s=1e-4,points_world=x,target_nodal_force=f,pressure_reaction_at_geometry_com=w,maximum_penetration_m=0);e.finish()
   try:e.queue_once(lambda _:(_ for _ in ()).throw(RuntimeError('Simulated queue callback failure')))
   except RuntimeError:pass
   e.queue_once(lambda _:None)
  else:e.accept(time_start_s=1e-6 if failure=='wrong_clock'else 0,time_end_s=1e-4,points_world=x,target_nodal_force=f*100 if failure=='too_much_force'else f,pressure_reaction_at_geometry_com=-w if failure=='wrong_sign'else(w*100 if failure=='too_much_force'else w),maximum_penetration_m=.001 if failure=='too_deep'else 0)
  raise AssertionError('Negative control accepted '+failure)
 except ValueError:negative+=1
result=dict(passed=True,manufactured_cases=100,negative_controls=negative,maximum_errors=maximum,scope='Host operator invariants and at-most-once transaction only; no Native force/work qualification.');(out/'measurements.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
