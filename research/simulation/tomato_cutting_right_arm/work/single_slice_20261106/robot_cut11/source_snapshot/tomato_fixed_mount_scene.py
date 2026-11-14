"""Prepare an isolated fixed-tool scene and an offset, contact-free dry stroke.

The ideal mount has no compliance or bracket mass. It is an initial simulation
fixture, not a demonstrated finger grasp or hardware mount design.
"""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
from pxr import Gf, Usd, UsdGeom, UsdPhysics
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reach_kinematics import ArmKinematics, PALM_OFFSET


def matrix(xform,t):
    xform.ClearXformOpOrder()
    xform.AddTransformOp(opSuffix='fixedTool').Set(Gf.Matrix4d(t.T.tolist()))


def prepare(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    audit_path=ROOT/'runs/offline/robot_scene_20261101_01/scene_audit.json'
    audit=json.loads(audit_path.read_text())
    source=Usd.Stage.Open(audit['scene']);kin=ArmKinematics(source)
    physics=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text())
    blade=json.loads((ROOT/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text())
    h=np.array(physics['handle_centre_local_m']);verts=np.asarray(blade['vertices'])
    q=np.array([audit['home_rad'][n] for n in kin.names]);_,rh=kin.pose(q)
    rk=np.array([[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]])
    # Knife stays 90 mm laterally away from the intended x=-22.5 mm cut plane.
    # The lowest point remains 12 mm above the board during the dry stroke.
    heights=[.16,.10,.012,.10,.16]
    knife_positions=[];qs=[];records=[]
    previous=q
    for phase in range(4):
        for i in range(121):
            if phase and i==0:continue
            u=i/120;blend=u*u*u*(10+u*(-15+6*u))
            bottom=(1-blend)*heights[phase]+blend*heights[phase+1]
            origin=np.array([.0675,0.,bottom-verts[:,1].min()])-rk@np.array([verts[:,0].mean(),0.,0.])
            handle=origin+rk@h
            palm=handle+np.array([0.,0.,.15])
            solved,error,angle=kin.solve(palm,rh,previous)
            if error>2e-5 or angle>2e-4:raise ValueError(f'Unreachable fixed-mount dry route: {phase=} {i=} {error=} {angle=}')
            records.append(dict(phase=phase,index=i,position_error_m=error,rotation_error_rad=angle))
            qs.append(solved);knife_positions.append(origin);previous=solved
    hand=kin.transforms(qs[0])[kin.hand_path]
    knife=np.eye(4);knife[:3,:3]=rk;knife[:3,3]=knife_positions[0]
    mount=np.linalg.inv(hand)@knife
    path=out/'fixed_mount_scene.usda'
    stage=Usd.Stage.CreateNew(str(path)) if not path.exists() else Usd.Stage.Open(str(path))
    stage.GetRootLayer().Clear();stage.GetRootLayer().subLayerPaths=[audit['scene']]
    old=stage.GetPrimAtPath(audit['knife_path']);old.SetActive(False)
    tool_path='/dual_ar5_o6/MountedKnife'
    prim=stage.DefinePrim(tool_path)
    prim.GetReferences().AddReference(str(ROOT/'rl/scene/phase3.usda'),audit['knife_path'])
    relative=np.linalg.inv(np.asarray(audit['robot_root_world_matrix']))@knife
    matrix(UsdGeom.Xformable(prim),relative)
    joint=UsdPhysics.FixedJoint.Define(stage,'/dual_ar5_o6/Physics/cutting_tool_mount')
    joint.CreateBody0Rel().SetTargets([kin.hand_path]);joint.CreateBody1Rel().SetTargets([tool_path])
    joint.CreateLocalPos0Attr(Gf.Vec3f(*mount[:3,3]))
    quat=Rotation.from_matrix(mount[:3,:3]).as_quat()
    joint.CreateLocalRot0Attr(Gf.Quatf(float(quat[3]),Gf.Vec3f(*quat[:3])))
    joint.CreateLocalPos1Attr(Gf.Vec3f(0.));joint.CreateLocalRot1Attr(Gf.Quatf(1.))
    joint.CreateCollisionEnabledAttr(False)
    # Exclude only the directly connected hand base. Other robot/tool pairs stay enabled.
    UsdPhysics.FilteredPairsAPI.Apply(prim).CreateFilteredPairsRel().AddTarget(kin.hand_path)
    # Author ready drive targets; runtime explicitly writes the same joint state.
    home=audit['home_rad'].copy();home.update(dict(zip(kin.names,qs[0])))
    for name,value in home.items():
        jp=stage.GetPrimAtPath('/dual_ar5_o6/Physics/'+name)
        if jp:UsdPhysics.DriveAPI.Apply(jp,'angular').CreateTargetPositionAttr(float(np.rad2deg(value)))
    if stage.GetCompositionErrors():raise ValueError(stage.GetCompositionErrors())
    stage.GetRootLayer().Save()
    manifest=dict(scene=str(path),tool_path=tool_path,hand_path=kin.hand_path,mount_hand_from_knife=mount.tolist(),
        home_rad={n:float(v) for n,v in home.items()},right_joint_names=kin.names,right_joint_route_rad=np.asarray(qs).tolist(),
        knife_origin_route_m=np.asarray(knife_positions).tolist(),knife_rotation=rk.tolist(),ik_checks=records,
        robot_root_world_matrix=audit['robot_root_world_matrix'],board_path=audit['board_path'],counter_path=audit['counter_path'],
        samples=len(qs),phase_count=4,dt_s=1/240,substeps_per_sample=4,knife_mass_kg=.25,
        minimum_planned_blade_board_clearance_m=.012,lateral_offset_from_cut_plane_m=.09,
        ideal_mount=True,bracket_mass_kg=0.,mount_compliance=0.,finger_grasp=False,
        source_sha256={**audit['source_sha256'],str(audit_path):hashlib.sha256(audit_path.read_bytes()).hexdigest(),
          audit['scene']:hashlib.sha256(Path(audit['scene']).read_bytes()).hexdigest(),
          str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        limitations=['Ideal fixed tool with 150 mm vertical palm-to-handle offset; no physical bracket or finger retention claim.',
          'Dry stroke is offset from the tomato by 90 mm; no cutting is performed.',
          'Actual blade force transfer and target contact must be tested before a cut.'])
    (out/'fixed_mount_plan.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(scene=str(path),samples=len(qs),max_ik_error_m=max(c['position_error_m'] for c in records))))
    return manifest

if __name__=='__main__':prepare(ROOT/'runs/offline/fixed_mount_scene_20261101_01')
