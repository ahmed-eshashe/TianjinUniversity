"""Final bounded assessment: field resolution and the rejected curved preimage."""
from pathlib import Path
import sys,json,time,numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import brentq
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from fixtures import make,action
from front_system import FrontSystem,prolongation
from multicut import kron3,volume_certificates
from gpu_backend import GPUReference
from planar_chart import axis_coefficients
R=W/'runs/gpu';checks={};result={};start=time.perf_counter();DT=3.90625e-7
def check(k,v):checks[k]=bool(v)
def evaluate(p,X,field='q'):
    X=X.copy()
    # Evaluate each side with one-sided limits at its discontinuity.
    V=[BSpline(t,np.eye(len(t)-3),2)(X[:,i]) for i,t in enumerate(p.knots)]
    return np.einsum('pi,pj,pk->pijk',*V).reshape(len(X),-1)@(p.T@getattr(p,field))

# A comparison on the continuous field around the fine cut, not only sparse
# original observations which miss the new 50-micron tip region.
primary=FrontSystem.restore(R/'primary.npz');half=FrontSystem.restore(R/'half.npz');p,h=primary.pieces['root'],half.pieces['root']
qdiff=p.T@(p.q-h.q);vdiff=p.T@(p.vg-h.vg)
bound=float(np.linalg.norm(qdiff,axis=1).max());vbound=float(np.linalg.norm(vdiff,axis=1).max())
check('halfstep_whole_field_position_bound',bound<.0001)
pts=np.array([[p.plane+sx,y,z] for sx in [-1e-12,1e-12] for y in np.linspace(.0059,.006,25) for z in np.linspace(-.006,.006,17)])
sample_v=float(np.linalg.norm(evaluate(p,pts,'vg')-evaluate(h,pts,'vg'),axis=1).max())
check('halfstep_local_velocity_refinement',vbound<.005)
result['halfstep_continuous_field']={'position_convex_hull_bound_m':bound,'velocity_convex_hull_bound_m_s':vbound,'sampled_near_front_velocity_difference_m_s':sample_v,'note':'Position bound is continuous; velocity reported explicitly because sparse observations underresolve these local modes.'}

# Same geometric 50-micron score, with one additional 25-micron layer behind it.
fine=make();action(fine,.005975);action(fine,.00595);fine.cpu.save(R/'spatial_initial');s=fine.cpu
f=np.zeros_like(s.X);left=s.X[:,0]<.0003;f[left,0]=-.02/left.sum();f[~left,0]=.02/(~left).sum()
x0=s.observations()[0];m0=s.metrics();g=GPUReference(s,f);tic=time.perf_counter();failed=None
try:g.step(256);g.export()
except Exception as e:failed=repr(e)
if failed:
    check('spatial_refined_dynamic_guard',False);result['spatial']={'failed':failed}
else:
    check('spatial_refined_dynamic_guard',True);s.save(R/'spatial_final');q=s.pieces['root'];A=kron3([prolongation(a,b) for a,b in zip(p.knots,q.knots)])
    difference=A@(p.T@p.q)-q.T@q.q;spbound=float(np.linalg.norm(difference,axis=1).max());work=float(np.sum(f*(s.observations()[0]-x0)))
    source=json.loads((W/'gpu_controls.json').read_text())['results']['dynamics']['primary'];relwork=abs(work-source['work_J'])/max(abs(work),1e-12)
    check('spatial_whole_field_position_bound',spbound<.0001);check('spatial_work',relwork<.05)
    check('spatial_volume',all(c['passed'] for c in volume_certificates(q)))
    check('spatial_mass',abs(s.metrics()['mass']-.001728)<1e-12)
    result['spatial']={'position_convex_hull_bound_m':spbound,'work_relative_difference':relwork,'fine_work_J':work,'old_dofs':len(p.q),'fine_dofs':len(q.q),'fine_condition':q.audit['mass_condition'],'wall_s':time.perf_counter()-tic,'sim_s':.0001,'energy_residual_J':s.metrics()['energy']-m0['energy']-work}

# Reproduce and save only the freely evolved field that the mapper rejected.
# No cut is committed and no tolerance is relaxed.
d=make();g=GPUReference(d.cpu);g.step(128);g.export();s=d.cpu;p=s.pieces['root'];s.save(R/'rejected_mapping_field')
knots=p.knots;Q=(p.T@p.q).reshape(*[len(t)-3 for t in knots],3);C=Q[:,:,:,0];axis_c,res=axis_coefficients(C,0)
normal_bs=BSpline(knots[0],axis_c,2);target=.0003;plane=brentq(lambda x:float(normal_bs(x))-target,knots[0][0],knots[0][-1],xtol=1e-15)
N=BSpline(knots[0],np.eye(len(axis_c)),2)(plane);surface=np.tensordot(N,C,axes=(0,0));normal_bound=float(abs(surface-target).max())
grad=[]
for i in range(C.shape[0]-1):grad.extend((2*(C[i+1]-C[i])/(knots[0][i+3]-knots[0][i+1])).ravel())
minimum_gradient=float(min(grad));reference_bound=normal_bound/minimum_gradient if minimum_gradient>0 else None
roots=[]
for y in np.linspace(-.006,.006,17):
    Ny=BSpline(knots[1],np.eye(len(knots[1])-3),2)(y)
    for z in np.linspace(-.006,.006,17):
        Nz=BSpline(knots[2],np.eye(len(knots[2])-3),2)(z);coef=np.einsum('ijk,j,k->i',C,Ny,Nz);bs=BSpline(knots[0],coef,2)
        roots.append(brentq(lambda x:float(bs(x))-target,knots[0][0],knots[0][-1],xtol=1e-15))
result['mapping_diagnosis']={'sim_s':s.time,'normal_axis_coefficient_residual_m':res,'exact_chart_tolerance_m':1e-11,'candidate_mean_reference_plane_m':plane,'whole_plane_world_normal_offset_bound_m':normal_bound,'global_normal_derivative_lower_bound':minimum_gradient,'reference_preimage_offset_bound_m':reference_bound,'sampled_preimage_range_m':[float(min(roots)),float(max(roots))],'frozen_field':str(R/'rejected_mapping_field.npz'),'interpretation':'The exact planar chart is too restrictive for this evolved field. The measured bound is diagnostic, not an adopted geometric error allowance or a contact proof. No cut was committed.'}
out={'status':'assessment_complete' if all(checks.values()) else 'local_velocity_qualification_failed','checks':checks,'results':result,'wall_s':time.perf_counter()-start,'physical_fracture':False}
(W/'spatial_mapping_assessment.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2))
