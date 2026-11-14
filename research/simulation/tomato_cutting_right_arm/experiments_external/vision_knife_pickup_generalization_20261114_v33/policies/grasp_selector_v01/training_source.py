from pathlib import Path
import json,hashlib,time
import numpy as np,torch
from grasp_vision_v02 import prepare_image
from grasp_selector_v01 import GraspSelector
W=Path(__file__).resolve().parent;out=W/'policies/grasp_selector_v01';assert not out.exists();out.mkdir()
torch.manual_seed(2026111409);torch.set_num_threads(2);torch.set_float32_matmul_precision('highest')
new=W/'grasp_data_v10';old=W/'grasp_data_v05';data=dict(np.load(new/'labels.npz'));meta=json.loads((new/'metadata.json').read_text())['samples'];oldmeta={x['id']:x for x in json.loads((old/'metadata.json').read_text())['samples']}
classes=[(f,r) for f in ['short','wide','medium'] for r in [0,180]];labels=torch.tensor([classes.index((x['family'],x['face'])) for x in meta],device='cuda');images=prepare_image(data['rgb'],data['depth'],'cuda');train=torch.tensor(np.flatnonzero(data['split']==0),device='cuda');val=torch.tensor(np.flatnonzero(data['split']==1),device='cuda');offsets=[]
for family,face in classes:
 ds=[]
 for x in meta:
  if x['split']=='train' and (x['family'],x['face'])==(family,face):
   A=np.array(oldmeta[x['id']]['hand_target_world']);B=np.array(x['hand_target_world']);ds.append(A[:3,:3].T@(B[:3,3]-A[:3,3]))
 assert np.max(np.std(ds,axis=0))<1e-7
 offsets.append(np.mean(ds,axis=0).tolist())
model=GraspSelector().cuda();opt=torch.optim.AdamW(model.parameters(),lr=.0004,weight_decay=1e-4);start=time.monotonic();best=float('inf');history=[]
for step in range(3000):
 ids=train[torch.randint(len(train),(32,),device='cuda')];im=images[ids].clone();im[:,:3]=(im[:,:3]*(.8+.4*torch.rand(32,1,1,1,device='cuda'))+.01*torch.randn_like(im[:,:3])).clamp(0,1)
 logits=model(im);loss=torch.nn.functional.cross_entropy(logits,labels[ids]);opt.zero_grad(set_to_none=True);loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5.);opt.step()
 if step%100==0 or step==2999:
  model.eval()
  with torch.no_grad():p=model(images[val]).softmax(-1);pred=p.argmax(-1);vl=torch.nn.functional.nll_loss(p.clamp_min(1e-20).log(),labels[val]);correct=int((pred==labels[val]).sum())
  row=dict(step=step,training_loss=float(loss),validation_loss=float(vl),correct=correct,count=len(val),minimum_confidence=float(p.max(-1).values.min()),wall_s=time.monotonic()-start);history.append(row);print(json.dumps(row),flush=True)
  if float(vl)<best:
   best=float(vl);base=W/'policies/grasp_vision_v02_expanded/best.pt';torch.save(dict(selector_state_dict=model.state_dict(),classes=classes,hand_frame_offsets=offsets,metrics=row,selector_source_hash=hashlib.sha256((W/'grasp_selector_v01.py').read_bytes()).hexdigest(),base_checkpoint=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),data=str(new),data_sha256=hashlib.sha256((new/'labels.npz').read_bytes()).hexdigest(),scope='Known-family two-face visual grasp selector; not arbitrary knife recognition'),out/'best.pt')
  model.train()
(out/'history.json').write_text(json.dumps(history,indent=2));(out/'training_source.py').write_text(Path(__file__).read_text())
