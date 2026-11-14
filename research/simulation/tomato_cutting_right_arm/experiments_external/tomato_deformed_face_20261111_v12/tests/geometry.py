from pathlib import Path
import sys,json,time,numpy as np
from scipy.interpolate import BSpline
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from fixtures import make,action,assign,analytic,world_y
from front_system import FrontSystem
from deformed_sweep import DeformedSweep,field_snapshot
from blade_sweep import pose
from face_chart import edge_rectangle
from integrated_cut import RejectedEvent
from rectangle_union import covered,union_area
start=time.perf_counter();checks={};results={}
def check(k,v):
    checks[k]=bool(v)
    if not v:raise AssertionError(k)
def evaluate(p,X):
    V=[BSpline(t,np.eye(len(t)-3),2)(X[:,i]) for i,t in enumerate(p.knots)]
    return np.einsum('pi,pj,pk->pijk',*V).reshape(len(X),-1)@(p.T@p.q)
def point_crossing(old,new,op,np_,chart,blade):
    rng=np.random.default_rng(342);rect=chart['rectangle'];X=np.empty((500,3));X[:,chart['axis']]=chart['plane'];other=[i for i in range(3) if i!=chart['axis']]
    for j,a in enumerate(other):X[:,a]=rng.uniform(rect[2*j],rect[2*j+1],len(X))
    a=(evaluate(old,X)-op[:3,3])@op[:3,:3];b=(evaluate(new,X)-np_[:3,3])@np_[:3,:3];t=-a[:,1]/(b[:,1]-a[:,1]);hit=a+t[:,None]*(b-a);lo,hi,half=edge_rectangle(blade)
    return bool(np.all((t>=-1e-9)&(t<=1+1e-9)) and hit[:,0].min()>=lo-1e-10 and hit[:,0].max()<=hi+1e-10 and abs(hit[:,2]).max()<=half+1e-10),{'crossing_fraction_range':[float(t.min()),float(t.max())],'normal_offset_max_m':float(abs(hit[:,2]).max())}
d=make();check('CAD_face_is_original',edge_rectangle(d.blade)[2]>.0004)
old=d.cpu.pieces['root'];op=d.pose.copy();p=d.propose(pose([.0003,world_y(.00595),0]));c=p['command']['charts'][0];ok,proof=point_crossing(old,old,op,p['pose'],c,d.blade);check('independent_static_crossing',ok);d.commit(p)
check('front_is_shallow',d.cpu.pieces['root'].plane is not None and len(d.cpu.pieces)==1)
results['static']=proof

# The exact v11 rejected freely evolved field is accepted only with the actual
# finite edge-face containment certificate, never by relaxing its plane-fit test.
d=make();old=d.cpu.pieces['root'];op=d.pose.copy();b=W.parent/'tomato_deformed_front_20261111_v11'
d.cpu=FrontSystem.restore(b/'runs/gpu/rejected_mapping_field.npz');new=d.cpu.pieces['root'];before=d.cpu.observations();p=d.propose(pose([.0003,world_y(.00595),0]));c=p['command']['charts'][0]
ok,proof=point_crossing(old,new,op,p['pose'],c,d.blade);check('independent_curved_field_crossing',ok);d.commit(p)
check('curved_field_carried',max(np.max(abs(x-y)) for x,y in zip(before,d.cpu.observations()))<1e-10)
check('curved_field_conservative_bounds',c['normal_offset_bound_m']<1e-5 and c['front_spread_bound_m']<1e-5)
results['curved_field']={'chart':c,'sample_crossing':proof};d.save(W/'runs/curved_field');check('checkpoint',DeformedSweep.restore(W/'runs/curved_field').fingerprint()==d.fingerprint())

# Monotone history may accumulate a score, but withdrawal/outside repositioning
# breaks that proof chain and cannot turn disjoint strokes into a full strip.
d=make();action(d,.00595);first=d.cpu.fingerprint();area=union_area(d.histories['root']['rectangles']);action(d,.006);action(d,.00595)
check('reverse_reentry_no_extra_area',first==d.cpu.fingerprint() and abs(union_area(d.histories['root']['rectangles'])-area)<1e-18)
for q in [pose([.0003,world_y(.00595),.25]),pose([.0003,world_y(.0058),.25]),pose([.0003,world_y(.0058),0]),pose([.0003,world_y(.00575),0])]:d.commit(d.propose(q))
check('disjoint_stroke_gap_not_filled',not covered([.00575,.006,-.006,.006],d.histories['root']['rectangles']))
p=d.cpu.pieces['root'];q=p.q.copy();p.q[p.base_ng:,0]+=1e-9;p.update_state();check('disjoint_bridge',np.max(abs(p.face_jump(np.array([[.005875,0]]))))<1e-11);p.q=q;p.update_state()

def rejected(d,end):
    fp=d.fingerprint()
    try:d.propose(end)
    except RejectedEvent:return fp==d.fingerprint()
    return False
d=make();check('large_step_rejected',rejected(d,pose([.0003,0,0])))
d=make();check('sideways_accuracy_rejected',rejected(d,pose([.00032,world_y(.00595),0])))
d=make();assign(d.cpu.pieces['root'],lambda X:analytic(X)+np.c_[10*X[:,1]**2,np.zeros(len(X)),np.zeros(len(X))]);d.previous=field_snapshot(d.cpu);check('excess_curvature_rejected',rejected(d,pose([.0003,world_y(.00595),0])))
d=make();d.pose=pose([.02,world_y(.0061),0]);d.commit(d.propose(pose([.02,world_y(.00595),0])));check('near_miss',not d.histories)
d=make();fp=d.cpu.fingerprint();d.commit(d.propose(d.pose.copy()));check('held_no_cut',fp==d.cpu.fingerprint() and not d.histories)
d=make();d.pose=pose([.0003,world_y(.0061),.055253]);d.commit(d.propose(pose([.0003,world_y(.00595),.055253])));check('finite_edge_retained',0<union_area(d.histories['root']['rectangles'])<.00005*.006)
out={'status':'pass_finite_face_geometry','checks':checks,'results':results,'wall_s':time.perf_counter()-start,'physical_fracture':False};(W/'geometry_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print(json.dumps(out,indent=2))
