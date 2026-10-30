"""Bounded offline diagnosis of small-strain tetrahedron inversions."""
import argparse
import fcntl
import itertools
import json
from pathlib import Path
import resource
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh-directory',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(45,45))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Offline diagnostic wall cap')))
    signal.alarm(55);start=time.monotonic()
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        args.output.mkdir(parents=True,exist_ok=False)
        import numpy as np
        from scipy.sparse.linalg import splu
        from tomato_surface_mechanics import stiffness_matrix
        design=json.loads((args.mesh_directory/'surface_design.json').read_text())
        assignments=json.loads((args.mesh_directory/'mass_stiffness_assignments.json').read_text())
        records=[]
        for piece,assign in zip(design['pieces'],assignments):
            ids=assign['global_node_ids'];mapping={g:i for i,g in enumerate(ids)}
            points=np.asarray([design['nodes'][i]['position_m'] for i in ids])
            cells=np.asarray([[mapping[i] for i in c] for c in assign['integration_cells_global_ids']])
            pairs=np.asarray([[mapping[i] for i in design['bonds'][b]['nodes']] for b in assign['bond_ids']])
            bonds={tuple(sorted(pair)) for pair in pairs}
            p=points[cells];v0=np.linalg.det(p[:,1:]-p[:,:1])/6
            heights=np.stack([3*v0/(np.linalg.norm(np.cross(p[:,j]-p[:,i],p[:,k]-p[:,i]),axis=1)/2)
                              for i,j,k in itertools.combinations(range(4),3)],axis=1).min(axis=1)
            longest=np.stack([np.linalg.norm(p[:,i]-p[:,j],axis=1) for i,j in itertools.combinations(range(4),2)],axis=1).max(axis=1)
            surface=set(piece['surface_node_ids'])
            fixed=np.sort((3*np.array([mapping[i] for i in surface])[:,None]+np.arange(3)).reshape(-1))
            free=np.setdiff1d(np.arange(points.size),fixed)
            matrix=stiffness_matrix(points,pairs,np.asarray(assign['bond_stiffness_n_m']))
            lu=splu(matrix[free][:,free].tocsc())
            modes=[]
            for axis in range(3):
                affine=np.zeros_like(points);affine[:,axis]=-.002*(points[:,axis]-points[:,axis].mean())
                u=affine.reshape(-1).copy();u[free]=lu.solve(-(matrix[free][:,fixed]@u[fixed]))
                deformed=points+u.reshape(-1,3);p1=deformed[cells]
                ratios=(np.linalg.det(p1[:,1:]-p1[:,:1])/6)/v0
                worst=[]
                for index in np.argsort(ratios)[:10]:
                    cell=cells[index];gids=[ids[i] for i in cell]
                    worst.append({'cell_index':int(index),'node_ids':gids,'positions_m':points[cell].tolist(),
                                  'fixed_nodes':[g for g in gids if g in surface],
                                  'J':float(ratios[index]),'rest_volume_m3':float(v0[index]),
                                  'minimum_altitude_m':float(heights[index]),
                                  'altitude_over_longest_edge':float(heights[index]/longest[index]),
                                  'missing_cell_edges':[[ids[i],ids[j]] for i,j in itertools.combinations(cell,2) if tuple(sorted((i,j))) not in bonds],
                                  'nonaffine_displacements_m':(u.reshape(-1,3)[cell]-affine[cell]).tolist()})
                modes.append({'axis':axis,'inverted_count':int(np.sum(ratios<=0)),
                              'minimum_J':float(ratios.min()),'worst_cells':worst})
            records.append({'side':piece['side'],'cells':len(cells),
                            'min_altitude_m':float(heights.min()),'min_altitude_over_edge':float(np.min(heights/longest)),
                            'compression':modes})
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
        if forbidden:raise RuntimeError('Forbidden simulator import')
        result={'mesh_directory':str(args.mesh_directory),'pieces':records,'runtime_s':time.monotonic()-start,
                'simulator_imports_or_launches':False,'training':False}
        (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps([{'side':p['side'],'min_altitude_m':p['min_altitude_m'],
                           'inverted_counts':[m['inverted_count'] for m in p['compression']]} for p in records]))


if __name__=='__main__':main()
