from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_normal_contact_20261109_v30'))
from implicit_blade import ImplicitBlade,s,tensor
from legacy_trace_solver import LegacyTraceBulk

class Probe(ImplicitBlade):
    def implicit(self,h,**kw):
        self.contact_step=h
        try:return LegacyTraceBulk.implicit(self,h,**kw)
        finally:self.contact_step=None

z=np.load(W.parent/'disect_normal_timestep_20261109_v31/loading0080_final.npz')
b=Probe();b.x.copy_(tensor(z['x']));b.v.copy_(tensor(z['v']))
b.fracture.load_state_dict({'history':z['history']})
b.blade_enabled=True;b.blade_translation=z['blade_translation'].copy();b.blade_velocity=z['blade_velocity'].copy()
oldq=b.x.clone();oldv=b.v.clone();hist=b.fracture.state_dict()['history'].copy()
b.eligibility_override=None;traces=[];start=time.perf_counter();status='trial_solved'
for coupling in range(4):
    try:
        info=b.implicit(float(z['dt']))
        actual=b.blade_sample['force']+b.last_blade_dashpot.cpu().numpy()
        eligible=s.eligibility_from_contact(actual)
        traces.append(dict(coupling=coupling,info=info,newton=b.contact_trace,line_search=b.line_search_trace,eligible=eligible.tolist()))
        if np.array_equal(eligible,b.eligibility):break
        b.x.copy_(oldq);b.v.copy_(oldv);b.eligibility_override=eligible
    except Exception as error:
        status='exception: '+str(error)
        traces.append(dict(coupling=coupling,newton=getattr(b,'contact_trace',[]),line_search=getattr(b,'line_search_trace',[])))
        break
else:status='eligibility_fixed_point_failed'
pure=bool(np.array_equal(hist,b.fracture.state_dict()['history']))
out=dict(scope='One uncommitted reproduction of the original saved-state solve; no cut or qualification',status=status,source_time_s=float(z['step'])*float(z['dt']),dt_s=float(z['dt']),fracture_history_unmodified=pure,wall_s=time.perf_counter()-start,traces=traces)
(W/'legacy_reproduction_result.json').write_text(json.dumps(out,indent=2)+'\n')
np.savez_compressed(W/'legacy_uncommitted_trial.npz',x=b.x.cpu().numpy(),v=b.v.cpu().numpy(),history=b.fracture.state_dict()['history'])
print(json.dumps({k:v for k,v in out.items() if k!='traces'},indent=2))
print('Last Newton:',traces[-1]['newton'][-1] if traces[-1]['newton'] else None)
print('Last line search:',traces[-1]['line_search'][-1] if traces[-1]['line_search'] else None)
assert pure
