"""Supervised grasp selection, not full motion or pickup qualification."""
from pathlib import Path
import argparse,hashlib,json,time
import numpy as np
import torch
from grasp_vision_v03 import GraspVision,prepare_image,coordinates
W=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--data',type=Path,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--steps',type=int,default=4000);args=a.parse_args()
assert not args.output.exists();args.output.mkdir(parents=True)
torch.manual_seed(2026111403);torch.set_num_threads(2);torch.set_float32_matmul_precision('high')
d=dict(np.load(args.data/'labels.npz'));images=prepare_image(d['rgb'],d['depth'],'cuda');truth=torch.tensor(d['points'],device='cuda');height_truth=torch.tensor(d['height'],device='cuda');along_truth=torch.tensor(d['along'],device='cuda')
train=torch.tensor(np.flatnonzero(d['split']==0),device='cuda');val=torch.tensor(np.flatnonzero(d['split']==1),device='cuda')
model=GraspVision().cuda();optimizer=torch.optim.AdamW(model.parameters(),lr=.0008,weight_decay=1e-5)
yy,xx=torch.meshgrid(torch.arange(80,device='cuda')*4+96.,torch.arange(112,device='cuda')*4+96.,indexing='ij');grid=torch.stack([xx,yy],-1)[None,None]
best=float('inf');history=[];start=time.monotonic()
for step in range(args.steps):
    ids=train[torch.randint(len(train),(16,),device='cuda')];im=images[ids].clone();points=truth[ids]
    # Photometric/sensor noise only: moving a depth image in 2D without changing
    # camera geometry would corrupt the learned height supervision.
    im[:,:3]=(im[:,:3]*(.85+.3*torch.rand(16,1,1,1,device='cuda'))+.01*torch.randn_like(im[:,:3])).clamp(0,1)
    im[:,3]+=(.0002/3)*torch.randn_like(im[:,3])*im[:,4]
    target=(-(grid-points[:,:,None,None]).square().sum(-1)/(2*3.**2)).flatten(2).softmax(-1)
    with torch.autocast('cuda',dtype=torch.bfloat16):logits,height,along=model(im)
    prediction,_=coordinates(logits)
    loss=-(target*logits.float().flatten(2).log_softmax(-1)).sum(-1).mean()+.015*(prediction-points).square().mean()+.2*((height.float()-height_truth[ids])/.002).square().mean()
    optimizer.zero_grad(set_to_none=True);loss=loss+.2*((along.float()-along_truth[ids])/.005).square().mean();loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5.);optimizer.step()
    if step%100==0 or step==args.steps-1:
        model.eval()
        with torch.no_grad():
            logits,h,along_val=model(images[val]);pred,conf=coordinates(logits);e=(pred-truth[val]).norm(dim=-1);he=(h-height_truth[val]).abs()
        ae=(along_val-along_truth[val]).abs();score=float(e.mean()+300*he.mean()+300*ae.mean())
        row=dict(step=step,loss=float(loss.detach()),validation_mean_pixel_error=float(e.mean()),validation_max_pixel_error=float(e.max()),validation_mean_height_error_m=float(he.mean()),validation_max_height_error_m=float(he.max()),validation_mean_along_error_m=float(ae.mean()),validation_max_along_error_m=float(ae.max()),minimum_confidence=float(conf.min()),score=score,wall_s=time.monotonic()-start)
        history.append(row);print(json.dumps(row),flush=True);(args.output/'progress.json').write_text(json.dumps(row))
        if score<best:
            best=score
            torch.save(dict(state_dict=model.state_dict(),metrics=row,source_hash=hashlib.sha256((W/'grasp_vision_v03.py').read_bytes()).hexdigest(),data_sha256=hashlib.sha256((args.data/'labels.npz').read_bytes()).hexdigest(),data=str(args.data.resolve())),args.output/'best.pt')
            (args.output/'validation_predictions.json').write_text(json.dumps(dict(points=pred.cpu().tolist(),height=h.cpu().tolist(),along=along_val.cpu().tolist(),confidence=conf.cpu().tolist(),truth=truth[val].cpu().tolist()),indent=2))
        model.train()
(args.output/'history.json').write_text(json.dumps(history,indent=2));(args.output/'training_source.py').write_text(Path(__file__).read_text());(args.output/'grasp_vision_v03.py').write_text((W/'grasp_vision_v03.py').read_text())
