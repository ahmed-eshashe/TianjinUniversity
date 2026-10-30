"""Capped full cut-face grid contact reference with disclosed quadratic supports.

This tests exact finite-triangle contact, not tomato bulk deformation/cutting.
"""
import argparse,fcntl,hashlib,json,resource,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from scipy.sparse import eye
        from tomato_triangle_contact import triangle_geometry
        from tomato_contact_continuation import solve_triangle_continuation as solve_triangle_contact
        from tomato_coupled_contact import cut_pairs
        from tomato_blade_damage import BLADE
        from audit_tomato_triangle_contact import minimum_polygon_gap
        f=args.output;f.mkdir(exist_ok=False)
        d=json.loads((ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());points=np.array([n['position_m'] for n in d['nodes']]);pairs=cut_pairs(d)
        tip=float(points[pairs[:,0],2].max())-.008125;g=triangle_geometry(d,points,pairs,tip);target=points.copy();target[pairs[:,0],0]-=g['widths']/2;target[pairs[:,1],0]+=g['widths']/2
        face=set(pairs.ravel().tolist());fixed={3*i+j:points[i,j] for i in range(len(points)) for j in range(3) if i not in face or j in [1,2]}
        class Quadratic:
            def evaluate(self,x,*,tangent=False):
                v=x-target;r={'energy_j':float(.5*np.sum(v*v)),'gradient_n':v,'min_cell_ratio':1.,'min_length_ratio':1.}
                if tangent:r['tangent_n_m']=eye(x.size,format='csr')
                return r
        before,count=minimum_polygon_gap(d,target,tip,BLADE)
        x,lam,state,trace,ok,*_=solve_triangle_contact(Quadratic(),target,fixed,g)
        after,count=minimum_polygon_gap(d,x,tip,BLADE);gap=g['matrix']@x.ravel()-g['bounds']
        residual=state['gradient_n'].ravel()-g['matrix'].T@lam;free=np.array([3*i for i in sorted(face)]);scale=max(np.linalg.norm(g['matrix'].T@lam),1e-4);force=float(np.linalg.norm(residual[free])/scale)
        np.save(f/'positions.npy',x);np.save(f/'multipliers.npy',lam)
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        s={'passed':ok and after>=-1e-9 and gap.min()>=-1e-9 and lam.min()>=-1e-9 and force<=1e-6,'depth_mm':8.125,'cut_triangles_per_face':448,'face_vertex_pairs':len(pairs),'initial_independent_gap_m':before,'final_independent_gap_m':after,'clipped_polygon_vertices':count,'force_residual':force,'loaded_cap_constraints':int(sum(m['kind']=='cap_edge' and lam[g['base_rows']+j]>1e-9 for j,m in enumerate(g['cap_rows']))),'maximum_correction_m':float(np.max(np.abs(x-target))),'surface_quadratic_supports':True,'bulk_mechanics_validated':False,'runtime_s':time.monotonic()-start,'peak_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,'full_cut':False,'simulator':False,'training':False,'forbidden_imports':forbidden}
        (f/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(s)
if __name__=='__main__':main()
