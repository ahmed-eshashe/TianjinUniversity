"""Capped contact virtual-work reference on guided quadratic triangles only."""
import argparse,fcntl,json,resource,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--steps',type=int,choices=[180,360],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from scipy.sparse import eye
        from tomato_triangle_contact import triangle_geometry,blade_resistance,swept_triangle_gap
        from tomato_contact_continuation import solve_triangle_continuation as solve_triangle_contact
        from tomato_linear_contact import solve_linear_contact
        class Quadratic:
            def evaluate(self,x,*,tangent=False):
                g=x-points;r={'energy_j':float(.5*np.sum(g*g)),'gradient_n':g,'min_cell_ratio':1.,'min_length_ratio':1.}
                if tangent:r['tangent_n_m']=eye(x.size,format='csr')
                return r
        points=np.array([[0.,-.001,0.],[0.,.001,.001],[0.,0.,.001]]*2)
        design={'cut_x_m':0.,'pieces':[{'triangles':[[0,1,2]],'face_tags':['cut']}]};pairs=np.array([[0,3],[1,4],[2,5]])
        fixed={3*i+j:points[i,j] for i in range(6) for j in [1,2]};model=Quadratic();x=points.copy();oldR=0.;old_depth=0.;work=0.;peak=0.;min_gap=0.;max_error=0.;records=[]
        path=list(np.linspace(0.,.009,a.steps+1))+list(np.linspace(.009,0.,a.steps+1))[1:]
        from collections import deque
        pending=deque((float(d),0) for d in path);rejected=0;attempts=0
        while pending:
            depth,level=pending.popleft();attempts+=1
            if attempts>8000:raise ValueError('Adaptive reference call budget exceeded')
            tip=.001-depth;g=triangle_geometry(design,points,pairs,tip)
            new,lam,state,trace,ok,*_=solve_triangle_contact(model,x,fixed,g)
            if not ok:raise ValueError('Reference equilibrium failed')
            gap=swept_triangle_gap(design,points,pairs,x,new,.001-old_depth,tip)
            if gap < -1e-9:
                if level>=14:raise ValueError('Swept path refinement exhausted')
                pending.appendleft((depth,level+1));pending.appendleft(((depth+old_depth)/2,level+1));rejected+=1;continue
            R=blade_resistance(g,new,lam);work+=.5*(oldR+R)*(depth-old_depth);E=state['energy_j'];peak=max(peak,E)
            min_gap=min(min_gap,gap);err=work-E;max_error=max(max_error,abs(err));records.append({'depth_m':float(depth),'energy_j':E,'work_j':work,'blade_resistance_n':R,'residual_j':err,'swept_gap_m':gap})
            x=new;oldR=R;old_depth=depth
        result={'passed':max_error<=.01*peak+1e-12 and min_gap>=-1e-9,'steps_per_direction':a.steps,'states':len(records),'discarded_uncommitted_candidates':rejected,'attempts':attempts,'peak_energy_j':peak,'maximum_energy_residual_j':max_error,'relative_peak_energy_error':max_error/peak,'net_cycle_work_j':work,'final_energy_j':state['energy_j'],'minimum_swept_gap_m':min_gap,'records':records,'runtime_s':time.monotonic()-start,'simulator':False,'training':False,'full_cut':False,'is_full_tomato':False}
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        result['forbidden_imports']=forbidden
        a.output.write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='records'})
if __name__=='__main__':main()
