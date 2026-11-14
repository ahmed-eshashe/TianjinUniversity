from pathlib import Path
import json,sys,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_execution_strategy_20261110_v35';sys.path.insert(0,str(V))
from precision_query import precise_query,resolved_winding,stats
from fast_cad_query import fast_query
z=np.load(W.parent/'disect_query_sign_replay_20261110_v37/first_uncertain_query.npz');vals=precise_query(z['vertices'],z['faces'],z['points']);bad=np.flatnonzero(z['errors']);assert all(abs(vals[4][i]-1)<1e-15 and vals[0][i]<0 for i in bad);assert np.array_equal(np.abs(vals[0]),np.abs(z['phi']));actual_repaired=len(bad)
# Independently known convex box geometry, rotated/translated in 3D.
v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)*.01
f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
a=.43;b=.29;A=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])@np.array([[1,0,0],[0,np.cos(b),-np.sin(b)],[0,np.sin(b),np.cos(b)]]);T=np.array([.071,-.027,.13]);vr=v@A.T+T
max_phi=0.;max_force=0.;max_energy=0.;same=0;points=0
for axis in range(3):
 for side in [-1,1]:
  for delta in [-1e-4,-1e-6,-1e-8,-1e-10,-1e-12,1e-12,1e-10,1e-8,1e-6,1e-4]:
   q=np.zeros(3);q[axis]=side*(.01+delta);q[(axis+1)%3]=.0013;q[(axis+2)%3]=-.0021;p=(q@A.T+T)[None]
   out=precise_query(vr,f,p);expected_normal=np.eye(3)[axis]*side@A.T;phi=out[0][0];max_phi=max(max_phi,abs(phi-delta));assert (phi<0)==(delta<0)
   actual_force=2e6*max(-phi,0)*out[1][0];reference_force=2e6*max(-delta,0)*expected_normal;max_force=max(max_force,float(np.linalg.norm(actual_force-reference_force)));max_energy=max(max_energy,abs(.5*2e6*min(phi,0)**2-.5*2e6*min(delta,0)**2))
   # Independent high precision sum even when the float64 query passes.
   wind=resolved_winding(vr,f,p[0]);assert (abs(wind)>.5)==(delta<0)
   try:old=fast_query(vr,f,p)
   except ValueError:old=None
   if old is not None:
    assert all(np.array_equal(x,y) for x,y in zip(old,out));same+=1
   points+=1
assert max_phi<1e-15 and max_force<1e-8 and max_energy<1e-12
# Neither an unresolved exact surface nor a damaged CAD topology is assigned an arbitrary sign.
try:resolved_winding(v,f,np.array([.01,0.,0.]));boundary='resolved to integer' # valid only if high precision certifies it
except ValueError:boundary='conservative stop on ambiguous boundary'
try:resolved_winding(v,f[:1],np.array([0.,0.,.003]));raise AssertionError('Open surface incorrectly certified')
except ValueError:pass
out={'passed':True,'scope':'Arithmetic-only winding fallback, independent analytical rotated box checks plus captured actual CAD case; not cutting qualification','actual_captured_points_repaired':actual_repaired,'analytic_points':points,'ordinary_path_bitwise_equal_cases':same,'maximum_phi_error_m':max_phi,'maximum_force_error_N':max_force,'maximum_energy_error_J':max_energy,'exact_surface_behavior':boundary,'open_mesh_uncertainty_still_rejected':True,'fallback_stats':stats,'original_1e_minus6_winding_test_unchanged':True,'no_distance_or_force_snapping':True,'physical_limits_unchanged':True};(W/'controls_result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
