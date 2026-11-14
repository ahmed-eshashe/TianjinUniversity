"""Read existing body damping/gravity/clamp properties; never edit them."""
import argparse,json,signal,traceback
from pathlib import Path
from tomato_evidence_snapshot import capture_sources,sources_unchanged
from tomato_isaac_startup_worker import write
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);out=p.parse_args().output;robot=app=None;passed=False;count=0
 def stop(*args):raise InterruptedError('Body parameter capture stopped')
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 try:
  parent=ROOT/'runs/native/joint_recenter_pgs_20261102_01';plan_path=parent/'fixed_mount_recenter_plan.json';snapshot_path=parent/'robot_kinematic_snapshot_recenter.json';proof=ROOT/'runs/offline/recenter_pgs_interface_readback_20261102_01/measurements.json';d=json.loads(proof.read_text());plan=json.loads(plan_path.read_text());snap=json.loads(snapshot_path.read_text())
  if not d['passed']or not sources_unchanged(d['source_sha256']):raise ValueError('Independent physical-coordinate parent required')
  pins=capture_sources(out,[Path(__file__)],inputs=[plan_path,snapshot_path,proof,Path(plan['scene'])]+[Path(x)for x in plan['source_sha256']])
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=True,device='cpu',visualizer=['none']).app
  import numpy as np,torch
  from pxr import PhysxSchema,UsdPhysics
  from tomato_contact_robot_pgs import MovingContactRobotPGS
  torch.set_num_threads(1);robot=MovingContactRobotPGS(out,plan,1/38400,np.zeros(7));robot.reset_contact();r=robot.robot;records=[]
  methods=['GetLinearDampingAttr','GetAngularDampingAttr','GetDisableGravityAttr','GetMaxLinearVelocityAttr','GetMaxAngularVelocityAttr','GetSleepThresholdAttr','GetStabilizationThresholdAttr']
  for name in r.body_names:
   record=next(b for b in snap['body_records']if b['name']==name);prim=robot.sim.stage.GetPrimAtPath(record['path']);api=PhysxSchema.PhysxRigidBodyAPI(prim);values={}
   for method in methods:
    attr=getattr(api,method)();values[method]=dict(value=attr.Get(),authored=attr.HasAuthoredValueOpinion(),property_path=str(attr.GetPath()))
   records.append(dict(body=name,path=record['path'],has_PhysxRigidBodyAPI=prim.HasAPI(PhysxSchema.PhysxRigidBodyAPI),properties=values));count+=1
  scenes=[UsdPhysics.Scene(p)for p in robot.sim.stage.Traverse()if p.IsA(UsdPhysics.Scene)];gravity=np.array(scenes[0].GetGravityDirectionAttr().Get(),dtype=float)*float(scenes[0].GetGravityMagnitudeAttr().Get());write(out,'body_parameters.json',dict(bodies=records,actual_gravity_vector_world=gravity.tolist(),backend_joint_stiffness=r.root_view.get_dof_stiffnesses().numpy().tolist(),backend_joint_damping=r.root_view.get_dof_dampings().numpy().tolist(),scope='Read-only resolved active USD body properties, including schema fallback values; original properties are not changed. Runtime joint gains queried separately. Native link-property damping getters are not exposed by this tensor interface; source configuration is recorded, not mislabelled a measured damping force.'))
  if robot.steps or count!=46 or not sources_unchanged(pins):raise ValueError('Body capture count/step/input failure')
  passed=True
 except BaseException:write(out,'worker_failure.json',dict(traceback=traceback.format_exc()));traceback.print_exc()
 finally:
  write(out,'worker_result.json',dict(shutdown_requested=app is not None,diagnostic_passed=passed,robot_body_parameters_captured=passed,controlled_steps=0 if robot is None else robot.steps,newton_steps=0,deformable_steps=0,cases_completed=count))
  if robot is not None:robot.close()
  if app is not None:app.close(exit_code=0 if passed else 1)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
