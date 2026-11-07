from pathlib import Path
import sys,json,time
import numpy as np
import warp as wp
w=Path(__file__).parent;r=w.parents[1];sys.path.insert(0,str(r/'rl'))
from tomato_bvh_cad_query import build_tree,bvh_query
from tomato_fast_exact_cad import fast_query
wp.init();wp.set_device('cuda:0');blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());v=np.array(blade['vertices']);f=np.array(blade['triangles']);rng=np.random.default_rng(613)
random=rng.uniform(v.min(0)-.01,v.max(0)+.01,(50000,3));tri=v[f];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];surf=tri.mean(1);near=np.concatenate([surf+off*n for off in [0,1e-16,-1e-16,1e-12,-1e-12,1e-8,-1e-8]])
z=np.load(w/'robot_cut04/checkpoints/step_001500.npz') if (w/'robot_cut04/checkpoints/step_001500.npz').exists() else np.load(w/'robot_cut03/checkpoints/step_001500.npz')
material=np.einsum('qi,qij->qj',z['packet_barycentric'],z['x'][z['packet_indices']]);local=(material-z['blade_translation'])@z['blade_rotation'];points=np.concatenate([random,near,v,tri[:,[0,1]].mean(1),local]);p=wp.array(points,dtype=wp.vec3d);vertices=wp.array(v,dtype=wp.vec3d);faces=wp.array(f,dtype=wp.vec3i);tree=build_tree(v,f);tree_wp=[wp.array(tree[0],dtype=wp.vec3d),wp.array(tree[1],dtype=wp.vec3d),wp.array(tree[2],dtype=int),wp.array(tree[3],dtype=int),tree[4]]
def out():return [wp.zeros(len(points),dtype=t) for t in [wp.float64,wp.vec3d,wp.vec3d,int,wp.float64]]
a=out();b=out();times={}
for name,kernel,inputs,outputs in [('baseline',fast_query,[vertices,faces,p],a),('bvh',bvh_query,tree_wp+[vertices,faces,p],b)]:
 wp.launch(kernel,dim=len(points),inputs=inputs,outputs=outputs,block_dim=64);wp.synchronize();start=time.monotonic()
 for _ in range(3):wp.launch(kernel,dim=len(points),inputs=inputs,outputs=outputs,block_dim=64)
 wp.synchronize();times[name]=(time.monotonic()-start)/3
errors={};passed=True
for key,aa,bb in zip(['distance','normal','closest_point','face','classification'],a,b):
 aa=aa.numpy();bb=bb.numpy();errors[key]=float(abs(aa-bb).max());passed=passed and np.array_equal(aa,bb)
result=dict(passed=passed,bitwise_equal=passed,points=len(points),errors=errors,seconds=times,global_ambiguous=tree[4],adopted=False);(w/'bvh_query_check.json').write_text(json.dumps(result,indent=2));print(result)
