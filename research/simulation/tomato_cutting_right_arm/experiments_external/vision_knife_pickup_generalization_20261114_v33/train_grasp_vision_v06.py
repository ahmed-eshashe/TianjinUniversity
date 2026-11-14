"""Supervised grasp selection, not full motion or pickup qualification."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
import torch
from grasp_vision_v02 import GraspVision,prepare_image,coordinates
W=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--data',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--steps',type=int,default=3000);a.add_argument('--resume',type=Path,required=True);args=a.parse_args()
assert not args.output.exists();args.output.mkdir(parents=True)
torch.manual_seed(2026111403);torch.set_num_threads(2);torch.set_float32_matmul_precision('highest');torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
d=dict(np.load(args.data/'labels.npz'));images=prepare_image(d['rgb'],d['depth'],'cuda');truth=torch.tensor(d['points'],device='cuda');height_truth=torch.tensor(d['height'],device='cuda')
train=torch.tensor(np.flatnonzero(d['split']==0),device='cuda');val=torch.tensor(np.flatnonzero(d['split']==1),device='cuda')
model=GraspVision().cuda();prior=torch.load(args.resume,map_location='cuda',weights_only=False);model.load_state_dict(prior['state_dict']);optimizer=torch.optim.AdamW(model.parameters(),lr=.00005,weight_decay=1e-5)
yy,xx=torch.meshgrid(torch.arange(80,device='cuda')*4+96.,torch.arange(112,device='cuda')*4+96.,indexing='ij');grid=torch.stack([xx,yy],-1)[None,None]
cal=json.loads((W/'grasp_calibration_v02.json').read_text());C=torch.tensor(cal['camera_world_matrix'],device='cuda',dtype=torch.float32);K=torch.tensor(cal['intrinsics'],device='cuda',dtype=torch.float32);nom=torch.tensor(cal['nominal_landmarks_world'],device='cuda',dtype=torch.float32);hand=torch.tensor(cal['nominal_hand_target_world'],device='cuda',dtype=torch.float32)[:3,3];camera_rotation=C[:3,:3]@torch.diag(torch.tensor([1.,-1.,-1.],device='cuda'));base_angle=torch.atan2(nom[1,1]-nom[0,1],nom[1,0]-nom[0,0]);lever=hand-nom.mean(0)
def world_target(p,h):
    rays=torch.cat([p,torch.ones_like(p[...,:1])],-1)@torch.linalg.inv(K).T@camera_rotation.T
    world=C[:3,3]+rays*((nom[:,2]+h-C[2,3])/rays[:,:,2])[:,:,None]
    v=world[:,1]-world[:,0];angle=torch.atan2(v[:,1],v[:,0])-base_angle;co=torch.cos(angle);si=torch.sin(angle)
    offset=torch.stack([co*lever[0]-si*lever[1],si*lever[0]+co*lever[1],torch.ones_like(co)*lever[2]],-1)
    return world.mean(1)+offset,angle
truth_world,truth_yaw=world_target(truth,height_truth)
best=float('inf');history=[];start=time.monotonic()
for step in range(args.steps):
    ids=train[torch.randint(len(train),(16,),device='cuda')];im=images[ids].clone();points=truth[ids]
    # Photometric/sensor noise only: moving a depth image in 2D without changing
    # camera geometry would corrupt the learned height supervision.
    im[:,:3]=(im[:,:3]*(.85+.3*torch.rand(16,1,1,1,device='cuda'))+.01*torch.randn_like(im[:,:3])).clamp(0,1)
    im[:,3]+=(.0002/3)*torch.randn_like(im[:,3])*im[:,4]
    target=(-(grid-points[:,:,None,None]).square().sum(-1)/(2*3.**2)).flatten(2).softmax(-1)
    with torch.autocast('cuda',enabled=False):logits,height=model(im)
    prediction,_=coordinates(logits)
    loss=-(target*logits.float().flatten(2).log_softmax(-1)).sum(-1).mean()+.015*(prediction-points).square().mean()+.2*((height.float()-height_truth[ids])/.002).square().mean()
    wt,wy=world_target(prediction,height.float());loss=loss+1.0*((wt-truth_world[ids])/.002).square().mean()+.05*((torch.sin(wy-truth_yaw[ids]))/.03).square().mean()
    optimizer.zero_grad(set_to_none=True);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5.);optimizer.step()
    if step%100==0 or step==args.steps-1:
        model.eval()
        with torch.no_grad():
            logits,h=model(images[val]);pred,conf=coordinates(logits);e=(pred-truth[val]).norm(dim=-1);he=(h-height_truth[val]).abs()
        w,ang=world_target(pred,h);pose_error=(w-truth_world[val]).norm(dim=-1);angle_error=torch.atan2(torch.sin(ang-truth_yaw[val]),torch.cos(ang-truth_yaw[val])).abs();score=float(pose_error.max()*1000+angle_error.max()*10)
        row=dict(step=step,loss=float(loss.detach()),validation_mean_pixel_error=float(e.mean()),validation_max_pixel_error=float(e.max()),validation_mean_height_error_m=float(he.mean()),validation_max_height_error_m=float(he.max()),minimum_confidence=float(conf.min()),score=score,validation_max_target_error_mm=float(pose_error.max()*1000),validation_max_yaw_error_deg=float(torch.rad2deg(angle_error.max())),wall_s=time.monotonic()-start)
        history.append(row);print(json.dumps(row),flush=True);(args.output/'progress.json').write_text(json.dumps(row))
        if score<best:
            best=score
            torch.save(dict(state_dict=model.state_dict(),metrics=row,source_hash=hashlib.sha256((W/'grasp_vision_v02.py').read_bytes()).hexdigest(),data_sha256=hashlib.sha256((args.data/'labels.npz').read_bytes()).hexdigest(),data=str(args.data.resolve()),resume=str(args.resume.resolve()),resume_sha256=hashlib.sha256(args.resume.read_bytes()).hexdigest()),args.output/'best.pt')
            (args.output/'validation_predictions.json').write_text(json.dumps(dict(points=pred.cpu().tolist(),height=h.cpu().tolist(),confidence=conf.cpu().tolist(),truth=truth[val].cpu().tolist()),indent=2))
        model.train()
(args.output/'history.json').write_text(json.dumps(history,indent=2));(args.output/'training_source.py').write_text(Path(__file__).read_text());(args.output/'grasp_vision_v02.py').write_text((W/'grasp_vision_v02.py').read_text())
