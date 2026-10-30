"""Find an open-thumb placement clear of the original knife, board, and counter."""
import argparse,sys,json,itertools,numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from pxr import UsdGeom
from search_wrap_grasp import ROOT,s,xc,km,meta,geometry
from grasp_scene_geometry import minimum_z_over_counter
p=argparse.ArgumentParser();p.add_argument('--knife-setup-yaw-deg',type=float,default=120);p.add_argument('--preclose-deg',type=float,default=0);p.add_argument('--allow-finger-handle-contact',action='store_true');p.add_argument('--scene-log',default='logs/cooking_trial8.log');p.add_argument('--hand-yaw-deg',type=float,default=0);p.add_argument('--hand-roll-deg',type=float,default=0);p.add_argument('--aligned-board',action='store_true');p.add_argument('--overhang-edge',type=float,default=-.11);p.add_argument('--thumb-yaws',type=float,nargs='+',default=[0]);p.add_argument('--thumb-pitches',type=float,nargs='+',default=[0,2,4,6,8,10,15,20,30,33]);p.add_argument('--approach-sweep-axis',choices=['x','y','z','world-z']);p.add_argument('--approach-sweep-distance',type=float,default=.08);p.add_argument('--output',default='work/cooking_clear_candidates.json');a=p.parse_args()
r=Rotation.from_euler('z',a.hand_yaw_deg,degrees=True).as_matrix()@np.array(json.load(open(ROOT/'work/grasp_stance_cooking_butt.json'))['orientation'])
lines=(ROOT/a.scene_log).read_text().splitlines();settled=json.loads(next(x.removeprefix('SETTLED_SCENE ') for x in lines if x.startswith('SETTLED_SCENE ')));h=np.array(settled['handle']);kr=np.array(settled['knife_rotation_world']);shift=np.array(json.loads(next(x.removeprefix('BOARD_SETUP ') for x in lines if x.startswith('BOARD_SETUP ')))['existing_board_shift_m'])
r=Rotation.from_rotvec(kr[:,0]*np.deg2rad(a.hand_roll_deg)).as_matrix()@r
centers=np.array(list(itertools.product([.020,.022,.025,.027,.030,.035,.040,.045],[-.055,-.045,-.035,-.025,-.015,-.005,.005,.015,.025,.035,.045,.055],[.075,.085,.095,.105,.115,.125])))
mesh=UsdGeom.Mesh(s.GetPrimAtPath(meta['knife_path']));v=np.array(mesh.GetPointsAttr().Get());cnt=np.array(mesh.GetFaceVertexCountsAttr().Get());idx=np.array(mesh.GetFaceVertexIndicesAttr().Get());off=np.r_[0,np.cumsum(cnt)];scale=np.linalg.norm(km[:3,:3],axis=0);parts=[]
for sections in [['Section2'],['Section0','Section1']]:
 faces=np.concatenate([np.array(UsdGeom.Subset(s.GetPrimAtPath(meta['knife_path']+'/'+name)).GetIndicesAttr().Get()) for name in sections]);ids=np.unique(np.concatenate([idx[off[f]:off[f+1]] for f in faces]));kv=((v[ids]-meta['knife_handle_local'])*scale)@kr.T@r;parts.append(kv[ConvexHull(kv).vertices])
board=s.GetPrimAtPath('/Indoor/RZ/SM_kitchen_Board');bm=np.array(xc.GetLocalToWorldTransform(board)).T;bp=np.array(UsdGeom.Mesh(board).GetPointsAttr().Get());authh=km[:3,:3]@meta['knife_handle_local']+km[:3,3];q=Rotation.from_euler('z',a.knife_setup_yaw_deg,degrees=True).as_matrix()
if a.aligned_board:
 from grasp_scene_geometry import align_board
 table=s.GetPrimAtPath('/Indoor/RZ/SM_YZ_CF_10');bm,error=align_board(bp,bm,np.array(UsdGeom.Mesh(table).GetPointsAttr().Get()),np.array(xc.GetLocalToWorldTransform(table)).T)
 ax=km[:3,0]/np.linalg.norm(km[:3,0]);setup_r=q@Rotation.from_rotvec(ax*np.pi).as_matrix()@km[:3,:3]
 faces=np.array(UsdGeom.Subset(s.GetPrimAtPath(meta['knife_path']+'/Section0')).GetIndicesAttr().Get());ids=np.unique(np.concatenate([idx[off[f]:off[f+1]] for f in faces]));direction=-(setup_r@(v[ids].mean(0)-meta['knife_handle_local']));direction[2]=0;direction/=np.linalg.norm(direction)
 inv=np.linalg.inv(bm);hl=inv[:3,:3]@authh+inv[:3,3];dl=inv[:3,:3]@direction;lo=bp.min(0);hi=bp.max(0)
 edge=min((hi[i]-hl[i])/dl[i] if dl[i]>0 else (lo[i]-hl[i])/dl[i] for i in [0,1] if abs(dl[i])>1e-6)
 bm[:3,3]-=direction*max(0.,edge-a.overhang_edge)
 edge_line=next((x for x in lines if x.startswith('COUNTER_EDGE_SETUP ')),None)
 if edge_line:bm[:3,3]+=np.array(json.loads(edge_line.removeprefix('COUNTER_EDGE_SETUP '))['counter_edge_translation_m'])
 bv=(bp@bm[:3,:3].T+bm[:3,3]-h)@r
 print('ALIGNED_BOARD_ERROR_DEG',error,'BOARD_WORLD_MATRIX',bm.tolist(),flush=True)
else:
 bv=bp@bm[:3,:3].T+bm[:3,3];bv=((bv-authh)@q.T+authh+shift-h)@r
bv=bv[ConvexHull(bv).vertices]
counter_prim=s.GetPrimAtPath('/Indoor/RZ/SM_YZ_CF_10');counter_matrix=np.array(xc.GetLocalToWorldTransform(counter_prim)).T;counter_world=np.array(UsdGeom.Mesh(counter_prim).GetPointsAttr().Get())@counter_matrix[:3,:3].T+counter_matrix[:3,3];counter_lo=counter_world.min(0);counter_hi=counter_world.max(0)
results=[]
for yaw,pitch in itertools.product(a.thumb_yaws,a.thumb_pitches):
 kg=[];bg=[];mins=[];required=[];swept_meshes=[]
 for name,vv in geometry(a.preclose_deg,yaw,pitch):
  mins.append((vv@r[2]).min()-centers@r[2])
  if a.approach_sweep_axis:
   shift_axis=-r.T@np.array([0,0,a.approach_sweep_distance]) if a.approach_sweep_axis=='world-z' else np.eye(3)['xyz'.index(a.approach_sweep_axis)]*a.approach_sweep_distance
   vv=np.vstack([vv,vv-shift_axis])
  swept_meshes.append(vv)
  for ti,(target,dest) in enumerate([(parts[0],kg),(parts[1],kg),(bv,bg)]):
   eq=ConvexHull((vv[:,None,:]-target[None,:,:]).reshape(-1,3)).equations;dest.append((centers@eq[:,:3].T+eq[:,3]).max(1))
   if ti<2:required.append(-.003 if a.allow_finger_handle_contact and ti==0 and (name=='right_rh_hand_base_link' or any('_'+f+'_' in name for f in ['index','middle','ring','pinky'])) else .002)
 knife_ok=np.min(np.array(kg)-np.array(required)[:,None],axis=0)>0;knife_gap=np.min(kg,axis=0);board_gap=np.min(bg,axis=0);min_height=np.min(mins,axis=0)+h[2]
 for i,c in enumerate(centers):
  if knife_ok[i] and board_gap[i]>.001:
   if min_height[i]<=counter_hi[2]+.001:
    clipped=[minimum_z_over_counter((vv-c)@r.T+h,counter_lo,counter_hi) for vv in swept_meshes]
    if any(z is not None and z<counter_hi[2]+.001 for z in clipped):continue
   results.append({'pitch':pitch,'yaw':yaw,'center_xyz':c.tolist(),'knife_clearance_m':float(knife_gap[i]),'board_clearance_m':float(board_gap[i]),'min_world_z':float(min_height[i]),'cost':float(np.linalg.norm(c-[.035,0,.085]))})
results.sort(key=lambda x:(x['cost'],-x['knife_clearance_m']));(ROOT/a.output).write_text(json.dumps(results,indent=2));print('COUNT',len(results));print(json.dumps(results[:12],indent=2))
