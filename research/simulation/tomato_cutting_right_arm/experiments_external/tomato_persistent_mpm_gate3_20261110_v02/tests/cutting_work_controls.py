from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from cutting_work import CutLedger
R=W/'runs/cutting_work';R.mkdir(exist_ok=False);checks={};data={};Gc=80.

def run(dt,divisions=1):
 ledgers=[CutLedger((-.003+i*.006/divisions,0,-.003+(i+1)*.006/divisions,.006)) for i in range(divisions)];duration=.06;speed=.1;rows=[];total=0.
 for k in range(round(duration/dt)):
  y=k*dt*speed;new=(k+1)*dt*speed;force=np.zeros(3)
  for l in ledgers:
   t=l.trial(k,[[-.003,y],[.003,y]],[[-.003,new],[.003,new]],'edge',True);f=l.force(t,new-y);work=float(f[1]*(new-y));l.commit(t,work,True);force+=f;total+=work
  rows.append([new,force[1],total])
 return ledgers,np.array(rows)
ls,rows=run(.0001);l=ls[0];checks['area_energy']=abs(l.fracture_work-Gc*.006*.006)<1e-12;data['area_m2']=l.covered.area;data['fracture_J']=l.fracture_work;data['steady_force_N']=float(rows[:,1].mean());np.savetxt(R/'ledger.csv',rows,delimiter=',',header='advance_m,force_N,cumulative_fracture_J',comments='')
for count in [2,4,8]:
 ls2,r=run(.0001,count);checks[f'area_partition_{count}']=abs(sum(x.fracture_work for x in ls2)-l.fracture_work)<1e-12
_,half=run(.00005);checks['half_step_force_work']=abs(half[1::2]-rows).max()<1e-10
# Repeated evaluations, rejected trials and read-only queries cannot advance state.
a=CutLedger((-.003,0,.003,.006));before=a.fingerprint();t=a.trial(0,[[-.003,0],[.003,0]],[[-.003,.001],[.003,.001]],'edge',True)
for _ in range(5):a.trial(0,[[-.003,0],[.003,0]],[[-.003,.001],[.003,.001]],'edge',True);a.state();a.commit(t,t.required_work,False)
checks['rollback_and_queries']=a.fingerprint()==before
try:a.commit(t,t.required_work/2,True);checks['unpaid_rejected']=False
except ValueError:checks['unpaid_rejected']=a.fingerprint()==before
a.commit(t,t.required_work,True);saved=a.state()
try:a.commit(t,t.required_work,True);checks['duplicate_rejected']=False
except ValueError:checks['duplicate_rejected']=a.state()==saved
for kind,old,new,active in [('face',0,.001,True),('spine',0,.001,True),('tip',0,.001,True),('edge',.001,.001,True),('edge',.001,0,True),('edge',0,.001,False),('edge',0,.001,True)]:
 t=a.trial(1,[[-.003,old],[.003,old]],[[-.003,new],[.003,new]],kind,active);checks[f'negative_{kind}_{old}_{new}_{active}']=t.area==0
restored=CutLedger.restore(saved);checks['checkpoint_exact']=a.fingerprint()==restored.fingerprint()
# Objectivity and material-area transformation preserve virtual work.
F=np.array([[1.1,.2,0],[0,.9,.1],[0,0,1.02]]);t=a.trial(2,[[-.003,.001],[.003,.001]],[[-.003,.002],[.003,.002]],'edge',True);force=a.force(t,.001,F);dx=F@np.array([0,.001,0]);checks['material_map_work']=abs(force@dx-t.required_work)<1e-12
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':data,'scope':'Ideal cutting-work constitutive/transaction controls only; geometric area requires actual contact and paid work. Not coupled material cutting qualification.'};(W/'cutting_work_controls.json').write_text(json.dumps(out,indent=2,default=lambda x:x.item()));print(json.dumps(out,indent=2,default=lambda x:x.item()))
