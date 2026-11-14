from pathlib import Path
import sys,json,time,datetime,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from backend import Backend,wp
from topology import components
assert json.loads((W/'persistent_cut_controls.json').read_text())['status']=='pass'
R=W/'runs/gate2_supplement';R.mkdir(exist_ok=False);checks={};result={};DT=1.25e-5

def load(name):
 s=dict(np.load(W/f'runs/gate2/{name}.npz'));b=Backend(s['X'],spacing=.0015,h=.003);b.set_state(**{k:s[k] for k in ['x','v','F','codes']});return b

def evolve(b,duration):
 t=time.monotonic();n=round(duration/DT)
 for j in range(0,n,160):
  b.step(DT,min(160,n-j));b.check()
  if time.monotonic()-t>600:raise TimeoutError('supplement')

def probe(b,name,mask):
 state=b.state();other=Backend(b.X,spacing=.0015,h=.003);other.set_state(**{k:state[k] for k in ['x','v','F','codes']});v=state['v'].copy();v[mask,1]+=.01;b.set_state(v=v);labels,_=components(b.X,state['codes'],b.h);groups=np.unique(labels[~mask]);peak=0.;peak_max=0.;rows=[]
 for j in range(10):
  b.step(DT,160);other.step(DT,160);s=b.check();o=other.check();delta=s['v']-o['v'];peak=max(peak,max(float(np.linalg.norm(delta[labels==g].mean(0))/.01) for g in groups));peak_max=max(peak_max,float(np.linalg.norm(delta[~mask],axis=1).max()/.01));rows.append([.002*(j+1),peak,peak_max,float(delta[mask,1].mean()/.01)])
 np.savetxt(R/f'{name}_probe.csv',rows,delimiter=',',header='t,undriven_mean_fraction,undriven_max_fraction,driven_fraction',comments='');b.save(R/f'{name}_probe.npz');other.save(R/f'{name}_baseline.npz');return {'peak_undriven_mean_fraction':peak,'peak_undriven_max_fraction':peak_max,'driven_final_fraction':rows[-1][-1]}

# Particle and occupied-grid mass must agree even after changes in active codes.
masses=[]
for name in ['untouched','partial_withdrawn','full_withdrawn','parallel','intersecting','four_cuts']:
 b=load(name);b.step(DT);b.check();m=float(b.m.numpy()[:b.count].astype(float).sum());expected=b.mass*b.n;masses.append({'case':name,'particle_mass_kg':expected,'active_grid_mass_kg':m,'relative_error':abs(m/expected-1),'active_codes':b.count})
checks['occupied_grid_mass']=all(x['relative_error']<1e-6 for x in masses);result['mass']=masses

# Actual middle-slice isolation after two sequential finite sweeps.
b=load('parallel');x=b.X;middle=abs(x[:,0])<.012;s=b.state();v=s['v'].copy();v[:,0]+=np.where(x[:,0]<-.012,-.02,np.where(x[:,0]>.012,.02,0));b.set_state(v=v);evolve(b,.2);s=b.check();gaps=[float(s['x'][middle,0].min()-s['x'][x[:,0]<-.012,0].max()-.0015),float(s['x'][x[:,0]>.012,0].min()-s['x'][middle,0].max()-.0015)];b.save(R/'parallel_opened.npz');result['middle_slice']={'gaps_m':gaps,'probe':probe(b,'middle_slice',middle)};checks['parallel_gaps']=min(gaps)>=.003;checks['middle_independent']=result['middle_slice']['probe']['peak_undriven_mean_fraction']<=.01 and result['middle_slice']['probe']['peak_undriven_max_fraction']<=.01

# Spin only one already-cut, opened fragment; do not teleport it or alter F/X/history.
b=load('full_opened');mask=b.X[:,0]<0;s=b.state();x0=s['x'].copy();codes=s['codes'].copy();v=s['v'].copy();center=x0[mask].mean(0);v[mask]+=np.cross(np.tile([0,0,1.],(sum(mask),1)),x0[mask]-center);b.set_state(v=v);evolve(b,.02);s=b.check();A=x0[mask]-x0[mask].mean(0);B=s['x'][mask]-s['x'][mask].mean(0);u,sv,vt=np.linalg.svd(A.T@B);rot=vt.T@u.T;angle=float(np.arccos(np.clip((np.trace(rot)-1)/2,-1,1)));gap=float(s['x'][~mask,0].min()-s['x'][mask,0].max()-.0015);b.save(R/'one_fragment_spinning.npz');result['one_fragment_spin']={'fitted_angle_rad':angle,'x_gap_m':gap,'history_unchanged':bool(np.array_equal(codes,s['codes'])),'probe':probe(b,'one_fragment_spin',mask)};checks['one_fragment_rotated']=angle>.005;checks['spin_gap']=gap>.003;checks['spin_history']=result['one_fragment_spin']['history_unchanged'];checks['spin_independent']=result['one_fragment_spin']['probe']['peak_undriven_mean_fraction']<=.01 and result['one_fragment_spin']['probe']['peak_undriven_max_fraction']<=.01
out={'status':'pass' if all(checks.values()) else 'fail','checks':checks,'results':result,'timestamp':datetime.datetime.now().astimezone().isoformat()};(W/'gate2_supplement.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
