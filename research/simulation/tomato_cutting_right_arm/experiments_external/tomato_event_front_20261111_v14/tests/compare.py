from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from event_sweep import EventSweep
from rectangle_union import union_area
from front_system import prolongation
from multicut import kron3
names=sys.argv[1:];checks={};results={}
def check(k,v,detail=None):
    checks[k]=bool(v)
    if not v:print('FAIL',k,detail,flush=True)
def compare(a,b):
    # Same band, normal plane and final active keys: coefficient hull bounds hold everywhere.
    check('identical_knots_'+a+'_'+b,all(np.array_equal(x,y) for x,y in zip(states[a].knots,states[b].knots)))
    pa,pb=states[a],states[b]
    return {f:float(np.linalg.norm(pa.T@getattr(pa,f)-pb.T@getattr(pb,f),axis=1).max()) for f in ['q','vg']}
allnames=names or ['half_action','half_probe','half_dt','half_event','restart','heldout_half_action']
for name in allnames:
    base='heldout' if name.startswith('heldout_') else 'primary';results[name]={}
    for frame in ['frame1','frame2']:
        da=EventSweep.restore(W/'runs'/base/frame);db=EventSweep.restore(W/'runs'/name/frame);states={base:da.cpu.pieces['root'],name:db.cpu.pieces['root']};pa,pb=states.values();e=compare(base,name)
        check(name+'_'+frame+'_topology',pa.keys==pb.keys and np.max(abs(pa.T.toarray()-pb.T.toarray()))<1e-12)
        check(name+'_'+frame+'_position',e['q']<=1e-4,e);check(name+'_'+frame+'_velocity',e['vg']<=.005,e)
        ma,mb=da.cpu.metrics(),db.cpu.metrics();e['energy_difference_relative']=abs(ma['energy']-mb['energy'])/max(abs(ma['energy']),1e-12)
        check(name+'_'+frame+'_energy',e['energy_difference_relative']<=.05)
        _,fa=pa.energy_force(pa.q);_,fb=pb.energy_force(pb.q);e['internal_generalized_force_relative']=float(np.linalg.norm(fa-fb)/max(np.linalg.norm(fb),1e-12));check(name+'_'+frame+'_internal_force',e['internal_generalized_force_relative']<=.05)
        ha,hb=da.histories['root'],db.histories['root'];e['coverage_area_delta_m2']=abs(union_area(ha['rectangles'])-union_area(hb['rectangles']))
        e['activation_times_delta_s']=[abs(a['time_s']-b['time_s']) for a,b in zip(da.activations,db.activations)]
        e['activation_count']=[len(da.activations),len(db.activations)];check(name+'_'+frame+'_activation_count',len(da.activations)==len(db.activations))
        results[name][frame]=e
out={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'results':results};(W/('comparison_'+('_'.join(allnames))+'.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));sys.exit(0 if all(checks.values()) else 1)
