from pathlib import Path
import sys,json,time,numpy as np
from scipy.spatial.transform import Rotation
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from blade_sweep import SweepDriver,pose,material_map
from multicut import MultiCut,RejectedEvent
from reference import block
from rectangle_union import covered,union_area
R=W/'runs/geometry';R.mkdir(exist_ok=False);checks={};results={};tic=time.perf_counter()
def check(k,v):
    checks[k]=bool(v)
    if not v:raise AssertionError(k)
def make(x=.0003,z=0):return SweepDriver(MultiCut(block(8,.0015)),pose([x,.007,z]))
def action(d,p):
    fingerprint=d.fingerprint();proposal=d.propose(p);check('preview_queries_do_not_mutate',d.fingerprint()==fingerprint);d.commit(proposal);return proposal
def scan(d,end=-.007,step=.001,transform=lambda p:p,x=.0003,z=0):
    start=.007
    for y in np.arange(start-step,end-step/2,-step):action(d,transform(pose([x,float(y),z])))

# Independent union geometry controls: area cannot fill an unvisited gap.
check('rectangle_gap_not_filled',not covered([0,3,0,1],[[0,1,0,1],[2,3,0,1]]))
check('rectangle_tiling_covers',covered([0,3,0,1],[[0,1,0,1],[1,2,0,1],[2,3,0,1]]))
check('overlap_area_once',abs(union_area([[0,2,0,1],[1,3,0,1]])-3)<1e-14)
d=make();check('CAD_not_rescaled',np.linalg.norm(d.blade.edge[1]-d.blade.edge[0])>.1)
d=make(x=.02);scan(d,x=.02);check('near_miss_no_cut',not d.histories and not d.cpu.events)
d=make();before=d.cpu.fingerprint();action(d,d.pose.copy());check('held_tool_no_cut',before==d.cpu.fingerprint() and not d.histories)
# Spine-only movement through the block while the cutting edge stays far below it.
d=SweepDriver(MultiCut(block(8,.0015)),pose([.0003,-.04,0]));action(d,pose([.0003,-.041,0]));check('spine_only_no_edge_cut',not d.histories)
d=make()
for y in [.006,.005]:action(d,pose([.0003,y,0]))
check('early_coverage_before_activation',bool(d.histories) and not d.cpu.events)
d.save(R/'early');restored=SweepDriver.restore(R/'early');check('early_coverage_checkpoint',restored.fingerprint()==d.fingerprint())
for y in [.004,.003,.002,.001,0]:action(d,pose([.0003,y,0]));action(restored,pose([.0003,y,0]))
check('partial_connected',len(d.cpu.pieces)==1 and d.cpu.pieces['root'].plane is not None)
check('early_checkpoint_continuation',restored.cpu.fingerprint()==d.cpu.fingerprint() and restored.histories==d.histories)
p=d.cpu.pieces['root'];q=p.q.copy();p.q[p.base_ng:,0]+=1e-7;p.update_state();pts=np.stack(np.meshgrid(np.linspace(-.006,.006,49),np.linspace(-.006,.006,9),indexing='ij'),axis=-1).reshape(-1,2);jump=np.linalg.norm(p.face_jump(pts),axis=1)
check('intact_bridge_ahead',float(jump[pts[:,0]<=0].max())<1e-11);check('opening_enabled_only_behind',float(jump[pts[:,0]>.001].max())>1e-9);p.q=q;p.update_state()
old_area=sum(union_area(h['rectangles']) for h in d.histories.values());old_events=len(d.cpu.events)
for y in [.001,.002,.003,.002,.001,0]:action(d,pose([.0003,y,0]))
check('reverse_reentry_no_new_cut',len(d.cpu.events)==old_events and abs(sum(union_area(h['rectangles']) for h in d.histories.values())-old_area)<1e-18)
for y in [-.001,-.002,-.003,-.004,-.005,-.006,-.007]:action(d,pose([.0003,y,0]))
check('full_sweep_two_fragments',len(d.cpu.pieces)==2)
check('full_area',abs(union_area(d.histories['root']['rectangles'])-.012**2)<1e-15)
check('mass_preserved',abs(d.cpu.metrics()['mass']-.001728)<1e-12)
check('no_artificial_gap',abs(d.cpu.pieces['rootL'].q[:,0].max()-d.cpu.pieces['rootR'].q[:,0].min())<1e-11)
check('blade_not_yet_clear',not d.whole_blade_clear()['clear'])
action(d,pose([.0003,-.007,.25]));check('full_CAD_withdrawal_clear',d.whole_blade_clear()['clear'])
d.save(R/'full');check('full_checkpoint',SweepDriver.restore(R/'full').fingerprint()==d.fingerprint())
results['full']={'events':d.commands,'clearance':d.whole_blade_clear()}
# Pose subdivision and translation of the plane do not require a future path.
fine=make();scan(fine,step=.0005);coarse=make();scan(coarse)
check('pose_subdivision_topology',list(fine.cpu.pieces)==list(coarse.cpu.pieces) and fine.cpu.cut_count==coarse.cpu.cut_count)
check('pose_subdivision_area',abs(union_area(fine.histories['root']['rectangles'])-union_area(coarse.histories['root']['rectangles']))<1e-15)
off=make(x=-.0012);scan(off,x=-.0012);check('motion_selects_new_plane',abs(off.histories['root']['plane']+.0012)<1e-10 and len(off.cpu.pieces)==2)
# Use the actual finite CAD edge endpoint to cover only the last 3 mm of width.
finite=make(z=.055253);scan(finite,z=.055253);check('finite_edge_remains_partial',len(finite.cpu.pieces)==1 and finite.cpu.pieces['root'].plane is not None)
check('finite_edge_area_not_infinite',union_area(finite.histories['root']['rectangles'])<.5*.012**2)
results['finite_area_m2']=union_area(finite.histories['root']['rectangles'])
# Two disjoint strokes with clear/along-edge repositioning: never fill their gap.
gap=make()
for y in [.006,.005,.004,.003]:action(gap,pose([.0003,y,0]))
action(gap,pose([.0003,.003,.25]));action(gap,pose([.0003,-.003,.25]));action(gap,pose([.0003,-.003,0]))
for y in [-.004,-.005,-.006,-.007]:action(gap,pose([.0003,y,0]))
check('disjoint_strokes_keep_bridge',len(gap.cpu.pieces)==1 and not covered([-.006,.006,-.006,.006],gap.histories['root']['rectangles']))
results['disjoint_area_m2']=union_area(gap.histories['root']['rectangles'])
# Loaded affine state: geometry insertion must not reset strain or inject energy.
loaded=MultiCut(block(8,.0015));p=loaded.pieces['root'];p.q=p.q@np.diag([1,.99,1]);p.update_state();ld=SweepDriver(loaded,pose([.0003,.007*.99,0]));U=ld.cpu.metrics()['energy'];old=ld.cpu.observations()
for y in np.linspace(.006,-.007,14):action(ld,pose([.0003,y*.99,0]))
check('loaded_energy_preserved',abs(ld.cpu.metrics()['energy']-U)<max(1e-12,abs(U)*1e-8));check('loaded_fields_preserved',max(float(np.max(abs(a-b))) for a,b in zip(old,ld.cpu.observations()))<1e-10)
# Reference history persists under a rigid change of world frame after a partial cut.
rot=make()
for y in [.006,.005,.004,.003,0]:
    # Retain the declared maximum normal advance.
    current=rot.pose[1,3]
    for yy in np.arange(current-.001,y-.0005,-.001):action(rot,pose([.0003,float(yy),0]))
Rb=Rotation.from_rotvec([.2,.3,-.15]).as_matrix();t=np.array([.12,-.03,.04]);T=np.eye(4);T[:3,:3]=Rb;T[:3,3]=t
for p in rot.cpu.pieces.values():p.q=p.q@Rb.T+p.translation[:,None]*t;p.vg=p.vg@Rb.T;p.update_state()
rot.pose=T@rot.pose;rot.maps={key:{'F':Rb@m['F'],'t':Rb@m['t']+t,'residual':m['residual']} for key,m in rot.maps.items()}
for y in np.linspace(-.001,-.007,7):action(rot,T@pose([.0003,y,0]))
check('rotated_history_full_cut',len(rot.cpu.pieces)==2 and abs(rot.histories['root']['plane']-.0003)<1e-10)
results['rigid_frame_note']='Coordinate/frame covariance fixture after partial history; not a torque-driven rotation during cutting.'
# Unsupported actions reject atomically; they cannot invent an alternative plane.
for label,initial,new in [('too_large',pose([.0003,.007,0]),pose([.0003,0,0])),('sideways',pose([.0003,0,0]),pose([.0013,0,0])),('oblique',pose([.0003,.001,0]),pose([.0005,0,0]))]:
    d=SweepDriver(MultiCut(block(8,.0015)),initial);fp=d.fingerprint();rejected=False
    try:d.propose(new)
    except RejectedEvent:rejected=True
    check(label+'_rejected',rejected and fp==d.fingerprint())
d=make();stale=d.propose(pose([.0003,.006,0]));d.commit(d.propose(pose([.0003,.0061,0])));fp=d.fingerprint();rejected=False
try:d.commit(stale)
except RejectedEvent:rejected=True
check('stale_rejected',rejected and fp==d.fingerprint())
d=make();d.cpu.pieces['root'].q[0,0]+=1e-6;fp=d.fingerprint();rejected=False
try:d.propose(pose([.0003,.006,0]))
except RejectedEvent:rejected=True
check('nonaffine_not_approximated',rejected and fp==d.fingerprint())
out={'status':'pass_geometry_scope','checks':checks,'results':results,'wall_s':time.perf_counter()-tic,'physical_fracture':False};(W/'geometry_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));print({'status':out['status'],'checks':len(checks),'wall_s':out['wall_s']})
