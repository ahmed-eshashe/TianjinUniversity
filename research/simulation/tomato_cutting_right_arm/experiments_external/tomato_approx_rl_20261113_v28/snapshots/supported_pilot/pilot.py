from pathlib import Path
import os,sys,time,json,numpy as np,argparse
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from model import lattice
from solver import Solver
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--shape',default='cube');p.add_argument('--envs',type=int,default=1);p.add_argument('--frames',type=int,default=300);p.add_argument('--dt',type=float,default=.0001);p.add_argument('--no-cut',action='store_true');p.add_argument('--velocity',type=float,default=.01);p.add_argument('--saw',type=float,default=.03);args=p.parse_args();out=W/'runs'/args.name;out.mkdir(exist_ok=False);model=lattice(args.shape);g=Solver(model,args.envs,dt=args.dt,cut=not args.no_cut);n=round(.02/args.dt);g.graph(n);rows=[];snapshots=[];start=time.perf_counter();status='running'
# Settle on the board with the blade away. The subsequent input is supplied
# online at each controller step, not from a precomputed cut surface.
for k in range(args.frames):
 if k<25:action=np.zeros(3)
 else:action=np.array([0.,-args.velocity if g.tool.numpy()[0,1]>.0034 else 0.,args.saw*np.sin((k-25)*.4)])
 bad=g.step(action,n);components,labels=g.components();row=dict(frame=k,time=g.steps*g.dt,bad=bad.tolist(),broken=int((g.alive.numpy()==0).sum()),components=components,peak=float(g.peak.numpy().max()),tool=g.tool.numpy()[0].tolist(),ledger=g.ledger.numpy()[0].tolist());rows.append(row)
 if k%10==0 or bad.any():print(json.dumps(row),flush=True);snapshots.append(g.x.numpy()[:g.n].copy());(out/'progress.json').write_text(json.dumps(row))
 if bad.any():status='stopped';break
else:status='completed'
wall=time.perf_counter()-start;np.savez_compressed(out/'state.npz',x=g.x.numpy(),v=g.v.numpy(),alive=g.alive.numpy(),paid=g.paid.numpy(),labels=labels,original=model['x'],edges=model['edges'],snapshots=snapshots,tool=g.tool.numpy());result=dict(status=status,rows=rows,wall_s=wall,envs=args.envs,n=g.n,bonds=g.nb,dt=args.dt,simulated_s=g.steps*g.dt,components=components,complete_environment_steps_s=len(rows)*args.envs/wall,scope='Initial approximate-network pilot with diagnostic host connected-components each step. No fragment recontact, detailed-reference match or robot qualification.');(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
