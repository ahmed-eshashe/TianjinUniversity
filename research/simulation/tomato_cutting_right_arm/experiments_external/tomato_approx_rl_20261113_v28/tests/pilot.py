from pathlib import Path
import os,sys,time,json,numpy as np,argparse
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from model import lattice
from solver import Solver
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--shape',default='cube');p.add_argument('--envs',type=int,default=1);p.add_argument('--frames',type=int,default=300);p.add_argument('--dt',type=float,default=.0001);p.add_argument('--no-cut',action='store_true');p.add_argument('--velocity',type=float,default=.01);p.add_argument('--saw',type=float,default=.03);p.add_argument('--offset',type=float,default=0.);p.add_argument('--feedback',action='store_true');p.add_argument('--sync-feed',action='store_true');args=p.parse_args();out=W/'runs'/args.name;out.mkdir(exist_ok=False);model=lattice(args.shape);g=Solver(model,args.envs,dt=args.dt,cut=not args.no_cut);n=round(.02/args.dt);tool=g.tool.numpy();tool[:,0]+=args.offset;g.tool.assign(tool);g.save_initial();g.graph(n);rows=[];snapshots=[];start=time.perf_counter();status='running'
# Settle on the board with the blade away. The subsequent input is supplied
# online at each controller step, not from a precomputed cut surface.
for k in range(args.frames):
 if k<25:action=np.zeros(3)
 else:
  load=float(g.load.numpy().max());feed=1. if not args.feedback else np.clip((1.5-load)/.6,0.,1.)
  if args.sync_feed:feed*=abs(np.sin((k-25)*.4))
  action=np.array([0.,-args.velocity*feed if g.tool.numpy()[0,1]>.0034 else 0.,args.saw*np.sin((k-25)*.4)])
 bad=g.step(action,n);components,labels=g.components();row=dict(frame=k,time=g.steps*g.dt,bad=bad.tolist(),broken=int((g.alive.numpy()==0).sum()),components=components,peak=float(g.peak.numpy().max()),penetration=float(g.penetration_peak.numpy().max()),tool=g.tool.numpy()[0].tolist(),ledger=g.ledger.numpy()[0].tolist());rows.append(row)
 if k%10==0 or bad.any():print(json.dumps(row),flush=True);snapshots.append(g.x.numpy()[:g.n].copy());(out/'progress.json').write_text(json.dumps(row))
 if bad.any():status='stopped';break
else:status='completed'
wall=time.perf_counter()-start;np.savez_compressed(out/'state.npz',x=g.x.numpy(),v=g.v.numpy(),alive=g.alive.numpy(),paid=g.paid.numpy(),labels=labels,original=model['x'],edges=model['edges'],snapshots=snapshots,tool=g.tool.numpy());result=dict(status=status,rows=rows,wall_s=wall,envs=args.envs,n=g.n,bonds=g.nb,dt=args.dt,simulated_s=g.steps*g.dt,components=components,pilot_control_steps_s=len(rows)*args.envs/wall,scope='Approximate-network pilot includes particle recontact and host connected components. No complete RL reward/reset loop, detailed-reference match or robot qualification.');(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
