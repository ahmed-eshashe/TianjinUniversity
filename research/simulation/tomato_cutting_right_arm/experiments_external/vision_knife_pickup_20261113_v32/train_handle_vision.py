"""Dense supervised perception trial; it is not motor-policy qualification."""
from pathlib import Path
import argparse,json,hashlib,time
import numpy as np
import torch
import torch.nn.functional as F
from handle_vision import HandleVision,prepare_image,coordinates

W=Path(__file__).resolve().parent
a=argparse.ArgumentParser()
a.add_argument('--data',type=Path,default=W/'perception_data_v02_settled')
a.add_argument('--output',type=Path,required=True)
a.add_argument('--steps',type=int,default=1500)
args=a.parse_args()
assert not args.output.exists()
args.output.mkdir(parents=True)
torch.manual_seed(20261113);torch.set_num_threads(4);torch.set_float32_matmul_precision('high')
d=dict(np.load(args.data/'labels.npz'))
images=prepare_image(d['rgb'],d['depth'],'cuda')
truth=torch.tensor(d['points'],device='cuda')
train_ids=torch.tensor(np.flatnonzero(d['split']==0),device='cuda')
val_ids=torch.tensor(np.flatnonzero(d['split']==1),device='cuda')
model=HandleVision().cuda();optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=1e-5)
yy,xx=torch.meshgrid(torch.arange(40,device='cuda')*4.+48.,torch.arange(56,device='cuda')*4.+48.,indexing='ij')
gridpoints=torch.stack([xx,yy],-1)[None,None]
best=float('inf');history=[];started=time.monotonic()
for step in range(args.steps):
    ids=train_ids[torch.randint(len(train_ids),(24,),device='cuda')]
    im=images[ids].clone();points=truth[ids].clone()
    # Consistent 2D image/landmark augmentation, used only for perception.
    theta=(torch.rand(24,device='cuda')-.5)*.20
    rotation=torch.stack([theta.cos(),-theta.sin(),theta.sin(),theta.cos()],-1).reshape(-1,2,2)
    translation=(torch.rand(24,2,device='cuda')-.5)*.16
    affine=torch.cat([rotation,translation[:,:,None]],-1)
    sample_grid=F.affine_grid(affine,im.shape,align_corners=True)
    im=F.grid_sample(im,sample_grid,align_corners=True,padding_mode='zeros')
    norm=(points-torch.tensor([48.,48.],device='cuda'))/torch.tensor([223.,159.],device='cuda')*2.-1.
    norm=torch.einsum('bij,bkj->bki',rotation.transpose(1,2),norm-translation[:,None])
    points=(norm+1.)/2.*torch.tensor([223.,159.],device='cuda')+48.
    im[:,:3]=(im[:,:3]*(.8+.4*torch.rand(24,1,1,1,device='cuda'))).clamp(0.,1.)
    target=(-(gridpoints-points[:,:,None,None]).square().sum(-1)/(2.*3.**2)).flatten(2).softmax(-1)
    with torch.autocast('cuda',dtype=torch.bfloat16):logits=model(im)
    prediction,_=coordinates(logits)
    cross_entropy=-(target*logits.float().flatten(2).log_softmax(-1)).sum(-1).mean()
    loss=cross_entropy+.015*(prediction-points).square().mean()
    optimizer.zero_grad(set_to_none=True);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5.);optimizer.step()
    if step%50==0 or step==args.steps-1:
        model.eval()
        with torch.no_grad():
            pred,conf=coordinates(model(images[val_ids]));error=(pred-truth[val_ids]).norm(dim=-1)
        row=dict(step=step,train_loss=float(loss.detach()),validation_mean_pixel_error=float(error.mean()),validation_max_pixel_error=float(error.max()),wall_s=time.monotonic()-started)
        history.append(row);print(json.dumps(row),flush=True);(args.output/'progress.json').write_text(json.dumps(row))
        if row['validation_mean_pixel_error']<best:
            best=row['validation_mean_pixel_error']
            torch.save(dict(state_dict=model.state_dict(),metrics=row,source_hash=hashlib.sha256((W/'handle_vision.py').read_bytes()).hexdigest(),data=str(args.data.resolve())),args.output/'best.pt')
            (args.output/'validation_predictions.json').write_text(json.dumps(dict(points=pred.cpu().tolist(),truth=truth[val_ids].cpu().tolist(),confidence=conf.cpu().tolist()),indent=2))
        model.train()
(args.output/'history.json').write_text(json.dumps(history,indent=2))
(args.output/'training_source.py').write_text(Path(__file__).read_text())
(args.output/'handle_vision.py').write_text((W/'handle_vision.py').read_text())
(args.output/'scope.txt').write_text('Perception only: two handle landmarks learned from actual settled head RGB-D images. Whole episodes held out; simulator poses are training labels only. This is not a demonstrated learned pickup, geometry-generalization result or physical calibration.\n')
