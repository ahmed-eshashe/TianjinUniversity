from pathlib import Path
import sys,json,time,numpy as np
from scipy.interpolate import BSpline
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from fixtures import make,analytic,assign,action,world_y
from front_system import FrontSystem,prolongation
from multicut import kron3,volume_certificates
from blade_sweep import pose,material_map
from deformed_sweep import DeformedSweep,field_snapshot
from planar_chart import PlanarChart,Monotone
from reference import block
from integrated_cut import RejectedEvent
from rectangle_union import union_area,covered
start=time.perf_counter();checks={};results={}
def check(k,v):
    checks[k]=bool(v)
    if not v:raise AssertionError(k)
def reject(label,d,new):
    before=d.fingerprint();why=None
    try:d.propose(new)
    except RejectedEvent as e:why=str(e)
    check(label,why is not None and before==d.fingerprint());return why
def evalfield(p,X):
    V=[BSpline(t,np.eye(len(t)-3),2)(X[:,i]) for i,t in enumerate(p.knots)]
    return np.einsum('pi,pj,pk->pijk',*V).reshape(len(X),-1)@(p.T@p.q)

d=make();p=d.cpu.pieces['root'];rng=np.random.default_rng(2301);X=rng.uniform(-.006,.006,(100,3))
check('analytic_nonaffine_field_reproduction',np.max(abs(evalfield(p,X)-analytic(X)))<1e-11)
try:material_map(p);oldreject=False
except RejectedEvent:oldreject=True
check('field_is_outside_old_affine_scope',oldreject)
old=p;oldfields=d.cpu.observations();action(d,.00595);p=d.cpu.pieces['root']
A=kron3([prolongation(a,b) for a,b in zip(old.knots,p.knots)])
P=np.linalg.lstsq(p.T.toarray(),(A@old.T).toarray(),rcond=None)[0]
masserr=float(np.linalg.norm(P.T@p.M@P-old.M.toarray())/np.linalg.norm(old.M.toarray()))
fold=old.energy_force(old.q)[1];fnew=p.energy_force(p.q)[1];forceerr=float(np.linalg.norm(P.T@fnew-fold)/np.linalg.norm(fold))
check('full_inertia_pullback',masserr<1e-10);check('virtual_work_pullback',forceerr<1e-7)
results['pullback']={'mass_relative':masserr,'internal_force_relative':forceerr,'old_dofs':len(old.q),'new_dofs':len(p.q)}
conditions=[]
for depth in [.00010,.00020,.00030]:
    before=d.cpu.observations();E=d.cpu.metrics()['energy'];action(d,.006-depth);p=d.cpu.pieces['root']
    check('carried_fields_'+str(depth),max(np.max(abs(a-b)) for a,b in zip(before,d.cpu.observations()))<1e-10)
    check('carried_energy_'+str(depth),abs(d.cpu.metrics()['energy']-E)<max(1e-12,abs(E)*1e-8))
    check('volume_'+str(depth),all(c['passed'] for c in volume_certificates(p)));conditions.append(p.audit)
    q=p.q.copy();p.q[p.base_ng:,0]+=1e-9;p.update_state()
    pts=np.array([[.006-depth-1e-6,0],[.006-depth,0],[.006-depth+1e-6,0]])
    jump=p.face_jump(pts);check('bridge_'+str(depth),np.max(abs(jump[:2]))<1e-11)
    check('resolved_front_'+str(depth),np.linalg.norm(jump[2])>1e-13);p.q=q;p.update_state()
check('partial_remains_one_piece',len(d.cpu.pieces)==1)
results['advancing_front_conditions']=conditions
d.save(W/'runs/geometry_partial');r=DeformedSweep.restore(W/'runs/geometry_partial');check('loaded_restart',r.fingerprint()==d.fingerprint())
action(d,.0056);action(r,.0056);check('restart_continuation',r.fingerprint()==d.fingerprint())
before=d.cpu.fingerprint();area=union_area(d.histories['root']['rectangles']);action(d,.0058);action(d,.0056)
check('reverse_reentry_no_new_area',before==d.cpu.fingerprint() and abs(union_area(d.histories['root']['rectangles'])-area)<1e-18)

# Halved pose increments preserve the geometric front/coverage. Different new
# approximation spaces are compared as fields, not by coefficient-array identity.
a=make();b=make();action(a,.0059)
for y in [.005975,.00595,.005925,.0059]:action(b,y)
check('subdivision_same_area',abs(union_area(a.histories['root']['rectangles'])-union_area(b.histories['root']['rectangles']))<1e-15)
check('subdivision_same_carried_fields',max(np.max(abs(x-y)) for x,y in zip(a.cpu.observations(),b.cpu.observations()))<1e-10)
check('subdivision_same_front',abs(a.commands[-1]['charts'][0]['front']-b.commands[-1]['charts'][0]['front'])<1e-11)

# State/chart covariance under a rigid world-frame rotation and translation.
d=make();action(d,.00595);R=Rotation.from_rotvec([.2,-.3,.15]).as_matrix();t=np.array([.07,.03,-.04]);T=np.eye(4);T[:3,:3]=R;T[:3,3]=t
for p in d.cpu.pieces.values():p.q=p.q@R.T+p.translation[:,None]*t;p.vg=p.vg@R.T;p.update_state()
d.pose=T@d.pose;d.previous=field_snapshot(d.cpu);pp=d.propose(T@pose([.0003,world_y(.0059),0]));d.commit(pp)
check('rotated_nonaffine_history',abs(d.histories['root']['plane']-.0003)<1e-10 and abs(d.commands[-1]['charts'][0]['front']-.0059)<1e-11)

# A changing analytic compression state is accepted only when the endpoint
# spline fields certify a monotone linear-in-time preimage of this same plane.
d=make();p=d.cpu.pieces['root'];assign(p,lambda X:analytic(X,.989,1.5))
endpoint=.989*.00595+2*.00595**2+1.5*.0003**2
q=d.propose(pose([.0003,endpoint,0]));d.commit(q)
check('changing_nonuniform_compression_chart',abs(d.commands[-1]['charts'][0]['front']-.00595)<1e-11)
results['temporal_note']='Analytic endpoint-field fixture, not freely evolved GPU or contact trajectory.'

# Near misses and finite footprint: whole support cannot be released past the
# actual edge endpoint. Disjoint coverage must never fill a skipped band.
d=make();d.pose=pose([.02,world_y(.0061),0]);q=d.propose(pose([.02,world_y(.00595),0]));d.commit(q);check('near_miss',not d.histories and not d.cpu.events)
d=make();fp=d.cpu.fingerprint();q=d.propose(d.pose.copy());d.commit(q);check('held_tool',fp==d.cpu.fingerprint() and not d.histories)
d=make();d.pose=pose([.0003,world_y(.0061),.055253]);q=d.propose(pose([.0003,world_y(.00595),.055253]));d.commit(q)
check('finite_edge_partial_area',0<union_area(d.histories['root']['rectangles'])<.00005*.006)
check('finite_edge_intact_gap',not covered([.00595,.006,-.006,.006],d.histories['root']['rectangles']))
d=make();action(d,.00595);p=d.cpu.pieces['root'];rects=d.histories['root']['rectangles']+[[.0058,.00585,-.006,.006]]
d.cpu.commit(d.cpu.propose('root',0,p.plane,rects));p=d.cpu.pieces['root'];q=p.q.copy();p.q[p.base_ng:,0]+=1e-9;p.update_state()
check('disjoint_prescribed_gap_stays_connected',np.max(abs(p.face_jump(np.array([[.0059,0]]))))<1e-11 and len(d.cpu.pieces)==1)
p.q=q;p.update_state()
results['disjoint_note']='Direct prescribed union isolates refinement/bridge algebra; not a blade trajectory.'

# Explicit unsupported/ambiguous cases: retain state instead of fitting a plane.
d=make();results['too_large_reason']=reject('too_large_rejected',d,pose([.0003,0,0]))
d=make();results['sideways_reason']=reject('changing_plane_rejected',d,pose([.0013,world_y(.00595),0]))
d=make();assign(d.cpu.pieces['root'],lambda X:analytic(X)+np.c_[2*X[:,1]**2,np.zeros(len(X)),np.zeros(len(X))]);d.previous=field_snapshot(d.cpu)
results['curved_preimage_reason']=reject('curved_preimage_rejected',d,pose([.0003,world_y(.00595),0]))
d=make();assign(d.cpu.pieces['root'],lambda X:analytic(X)+np.c_[np.zeros(len(X)),2*X[:,2]**2,np.zeros(len(X))]);d.previous=field_snapshot(d.cpu)
results['curved_edge_reason']=reject('curved_edge_footprint_rejected',d,pose([.0003,world_y(.00595),0]))
d=make();stale=d.propose(pose([.0003,world_y(.00595),0]));action(d,.005975);fp=d.fingerprint();ok=False
try:d.commit(stale)
except RejectedEvent:ok=True
check('stale_commit_rejected',ok and fp==d.fingerprint())

# Direct full-plane completion is an algebra regression only.
d=make();action(d,.00595);before=d.cpu.observations();p=d.cpu.pieces['root'];d.cpu.commit(d.cpu.propose('root',0,p.plane,[[-.006,.006,-.006,.006]]))
check('prescribed_completion_partition',len(d.cpu.pieces)==2)
check('completion_fields_preserved',max(np.max(abs(x-y)) for x,y in zip(before,d.cpu.observations()))<1e-10)
check('completion_mass',abs(d.cpu.metrics()['mass']-.001728)<1e-12)
out={'status':'pass_restricted_nonaffine_front_geometry','checks':checks,'results':results,'wall_s':time.perf_counter()-start,'physical_fracture':False}
(W/'geometry_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2))
