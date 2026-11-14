from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from fast_aggregation import Aggregate
from constrained_resistance import trial
from resistance_adapter import trial as old_trial
checks={};rows=[]
for label,offset in [('intact',None),('cut',.0001),('weak_contact',1e-7)]:
 b=Body(n=2,h=.003)
 if offset is not None:b.split([1,0,0],offset)
 a=Aggregate(b);marker=np.asarray(a.M.sum(1)).ravel()/a.M.sum();fixed=np.isclose(b.grid[a.masters,1],-.003);normal=np.array([0.,1.,0.]);F=np.array([[1.05,.04,0],[.02,.97,.03],[0,.01,1.02]])
 for mode,speed,eligible in [('stick',1e-6,True),('slip',1.,True),('reverse',-.1,True),('blunt',1.,False)]:
  a.v[:]=0;before=a.v.copy();r=trial(a,marker,normal,F,[0,speed,0],12.5e-6,.006,fixed,eligible);checks[label+'_'+mode+'_work']=abs(r['energy_residual_J'])<1e-12;checks[label+'_'+mode+'_fixed']=not np.any(r['velocity'][fixed]);checks[label+'_'+mode+'_no_mutation']=np.array_equal(a.v,before);free=~fixed;checks[label+'_'+mode+'_free_equation']=np.max(abs(r['support_impulses_Ns'][free]))<1e-14;momentum=np.sum(a.M@(r['velocity']-a.v),axis=0);checks[label+'_'+mode+'_balance']=np.linalg.norm(momentum-r['impulse_vector_Ns']-r['support_impulses_Ns'].sum(0))<1e-13
  if mode!='slip':checks[label+'_'+mode+'_no_fracture']=r['area_m2']==0
  else:checks[label+'_'+mode+'_paid']=r['area_m2']>0 and r['fracture_J']>0
  rows.append({'case':label,'mode':mode,'force_N':r['force_vector_N'].tolist(),'area_m2':r['area_m2'],'fracture_J':r['fracture_J'],'residual_J':r['energy_residual_J'],'aggregated_nodes':a.report['aggregated_nodes']})
 a.v[:]=[0,.001,0];r=trial(a,marker,normal,np.eye(3),[0,1,0],12.5e-6,.006);ref=old_trial(a,marker,normal,[0,1,0],12.5e-6,.006);checks[label+'_previous_operator_equivalence']=np.max(abs(r['velocity']-ref['velocity']))<1e-13 and abs(r['fracture_J']-ref['fracture_J'])<1e-13
result={'checks':{k:bool(v) for k,v in checks.items()},'passed':all(checks.values()),'cases':rows,'physical_cut':False,'scope':'Unchanged ideal Gc resistance with exact reduced inertia and fixed support; no geometric commit'};(W/'reports/resistance_controls.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
