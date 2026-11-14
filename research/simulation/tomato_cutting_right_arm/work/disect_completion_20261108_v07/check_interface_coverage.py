from cohesive_transfer import Transfer
import numpy as np,json
from pathlib import Path
s=Transfer();m=s.mesh;a=s.mapping;ids=a['used_pairs'];nonzero=abs(a['barycentric_weights'][ids])>1e-12;touched=np.unique(a['left_indices'][ids][nonzero]);missing=np.setdiff1d(m['ties'][:,0],touched)
# Directly move an entirely unsampled interface vertex, retaining all other nodes.
# Bulk resistance is intentionally outside this cohesion-coverage test.
node=int(missing[len(missing)//2]);x=m['x'].copy();x[node,0]-=1e-5;r=s.evaluate(x,np.ones(47,bool));baseline=s.evaluate(m['x']);delta=r['force']-baseline['force']
out=dict(scope='Negative control of interface quadrature coverage, independent of bulk stiffness',interface_nodes_per_side=len(m['ties']),nodes_with_nonzero_original_quadrature_weight=len(touched),unsampled_interface_nodes=len(missing),test_node=node,test_opening_m=1e-5,cohesive_force_change_norm_N=float(np.linalg.norm(delta)),cohesive_energy_change_J=float(r['stored_energy_j']-baseline['stored_energy_j']),maximum_damage=float(r['trial_history'][:,1].max()),coverage_passed=False,interpretation='Original quadrature transfer alone cannot resist every resolved interface opening mode. A constant-gap coupon does not qualify this full discretization. New surface quadrature or kinematic constraints are required; either changes the discrete model.')
Path(__file__).with_name('interface_coverage_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
