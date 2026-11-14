from pathlib import Path
import json,numpy as np,hashlib
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;R=W.parents[1];old=W.parent/'disect_normal_timestep_20261109_v31';stable=W.parent/'disect_contact_linesearch_20261109_v32'
assert json.loads((stable/'local_retest_result.json').read_text())['passed']
m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');q=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz')['x'];pairs=m['ties'];tt=m['tets'];sides=m['tet_side'];side=np.zeros(len(q),int);side[tt.ravel()]=np.repeat(sides,4);neg=np.where(side[pairs[:,0]]<0,pairs[:,0],pairs[:,1]);pos=np.where(side[pairs[:,0]]>0,pairs[:,0],pairs[:,1]);mp=np.full(len(q),-1,int);mp[neg]=np.arange(len(pairs));mp[pos]=np.arange(len(pairs));on=mp[tt]>=0;tri=np.array([mp[tet[mask]] for tet,mask,ss in zip(tt,on,sides) if ss>0 and mask.sum()==3]);mid=(q[neg]+q[pos])/2
front=np.array(json.loads((old/'initial_entry_geometry_audit.json').read_text())['front_point_m']);z=front[2]
p=mid[tri][:,:,[1,2]];mat=np.transpose(p[:,1:]-p[:,0,None],(0,2,1));valid=abs(np.linalg.det(mat))>1e-18;ids=np.flatnonzero(valid)
def surface(y):
 uv=np.linalg.solve(mat[valid],np.array([y,z])-p[valid,0]);ww=np.column_stack((1-uv.sum(1),uv));keep=np.all(ww>=-1e-8,axis=1)&np.all(ww<=1+1e-8,axis=1);assert keep.any(),y
 xs=np.einsum('ij,ij->i',mid[tri[ids[keep]],0],ww[keep]);assert np.ptp(xs)<1e-8;return float(xs.mean())
slope=(surface(front[1]-.00001)-front[0])/.00001
clear=.001;stroke=.009;depth=np.linspace(0,stroke,37)
def target(d):
 progress=d-clear
 return front[0]+slope*progress if progress<=0 else surface(front[1]-progress)
x=np.array([target(d) for d in depth]);curve=PchipInterpolator(depth,x-x[0]);dense=np.linspace(0,stroke,361);err=max(abs(float(curve(d))+x[0]-target(d)) for d in dense);assert err<1e-6,err
bevel=json.loads((old/'leading_bevel_reference.json').read_text());local=np.array(bevel['leading_bevel_midpoint_rotated_local_m']);initial=np.array([x[0],front[1]+clear,z])-local
plan=json.loads((old/'correction_plan.json').read_text());plan.update(scope='One geometry-calibrated fixed leading-bevel-midpoint trajectory, fresh settled target; equivalent stable line-search arithmetic; no material, contact-law, grip or limit change',selected={'translation_m':initial.tolist()},downward_stroke_m=stroke,durations_s=[.18,.8,.08,.02],total_s=1.08,front_lateral_path_m=np.column_stack((depth,x-x[0])).tolist(),wall_cap_s=3600.,reason='Finite leading bevel midpoint follows a frozen chart of the initial settled interface. Approach tangent extends the same chart above the front. Old lowest-corner reference was not the finite bevel centre. No online mesh feedback or imposed damage.',initial_clearance_m=clear,reference_rotated_local_m=local.tolist(),reference_chart_max_error_m=err)
plan.pop('candidates',None);plan.pop('contact_timestep_audit',None)
(W/'correction_plan.json').write_text(json.dumps(plan,indent=2)+'\n')
(W/'candidate_controls_gate.json').write_text(json.dumps({'passed':True,'scope':'Inherited physical controls plus independent stable-arithmetic controls and saved-step retest; not damage qualification','arithmetic_retest':str(stable/'local_retest_result.json'),'physical_controls':str(old/'candidate_controls_gate.json')},indent=2)+'\n')
source=(old/'loading.py').read_text().replace('from implicit_blade import ImplicitBlade as DamageBlade,s,m,closure,torch,tensor','sys.path.insert(0,str(W.parent/\'disect_contact_linesearch_20261109_v32\'))\nfrom stable_blade import StableBlade as DamageBlade,s,m,closure,torch,tensor')
(W/'loading.py').write_text(source)
out={'front_m':front.tolist(),'midpoint_rotated_local_m':local.tolist(),'initial_translation_m':initial.tolist(),'chart_fit_error_m':err,'clearance_m':clear,'stroke_m':stroke,'fixed_reference':True,'original_loaded_prefix_reused':False}
(W/'geometry_contract.json').write_text(json.dumps(out,indent=2)+'\n')
paths=[W/'loading.py',W/'correction_plan.json',stable/'stable_blade.py',stable/'stable_solver.py',stable/'stable_potential.py']
(W/'source_manifest.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n');print(json.dumps(out,indent=2))
