"""Independent geometry, intact energy, no-fracture, reset and contact controls."""
from pathlib import Path
import sys,json,numpy as np,time
from scipy.optimize import minimize
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from model import lattice
from solver import Solver,knife_normal

@wp.kernel
def query(points:wp.array(dtype=wp.vec3),out:wp.array(dtype=float),normal:wp.array(dtype=wp.vec3)):
 i=wp.tid();n,d=knife_normal(points[i],.06);out[i]=d;normal[i]=n

def geometry():
 rng=np.random.default_rng(73);p=rng.uniform([-.006,-.006,-.07],[.006,.036,.07],(160,3))
 p=np.r_[p,[[0,.015,0],[0,0,0],[0,.03,0],[.0005,.03,.06],[.001,.015,0]]]
 out=wp.zeros(len(p),device='cuda');normal=wp.zeros(len(p),dtype=wp.vec3,device='cuda');wp.launch(query,len(p),[wp.array(p,dtype=wp.vec3,device='cuda'),out,normal]);d=out.numpy()
 # Independent nearest-point convex optimization, coordinates in millimetres.
 A=np.array([[60.,-1,0],[-60,-1,0],[0,1,0],[0,0,1],[0,0,-1]]);b=np.array([0,0,30,60,60]);exact=[]
 for point in p*1000:
  margin=b-A@point
  if margin.min()>=-1e-10:value=-np.min(margin/np.linalg.norm(A,axis=1))
  else:
   result=minimize(lambda z:.5*np.sum((z-point)**2),np.array([0.,15.,0.]),jac=lambda z:z-point,constraints={'type':'ineq','fun':lambda z:b-A@z,'jac':lambda z:-A},method='SLSQP',options={'ftol':1e-11,'maxiter':200})
   assert (b-A@result.x).min()>-1e-6
   value=np.linalg.norm(result.x-point)
  exact.append(value/1000)
 error=np.max(np.abs(d-exact));return {'cases':len(p),'max_error_m':float(error),'pass':bool(error<2e-8)}

def mechanical_energy(g):
 x=g.x.numpy();v=g.v.numpy();m=g.model;delta=x[m['edges'][:,1]]-x[m['edges'][:,0]];stretch=np.linalg.norm(delta,axis=1)-m['length'];return float((.5*m['mass'][:,None]*v*v).sum()+np.sum(m['mass']*9.81*x[:,1])+.5*np.sum(m['stiffness']*stretch*stretch))

def energy(dt):
 m=lattice();g=Solver(m,dt=dt,knife=False,cut=False,support=False);x=m['x'].copy();x[:,0]*=1.01;x[:,1]+=1.;g.x.assign(x);g.save_initial();e0=mechanical_energy(g);n=round(.1/dt);g.step([0,0,0],n);e1=mechanical_energy(g);diss=float(g.ledger.numpy()[0,[0,5,6]].sum());expected_drift=-.5*m['mass_total']*9.81**2*dt*.1
 stretch=np.linalg.norm(x[m['edges'][:,1]]-x[m['edges'][:,0]],axis=1)-m['length'];initial_strain=.5*np.sum(m['stiffness']*stretch**2);relative=abs(e1+diss-e0-expected_drift)/float(initial_strain)
 return {'dt':dt,'energy_initial_J':e0,'energy_final_J':e1,'dissipation_J':diss,'known_symplectic_gravity_drift_J':expected_drift,'strain_energy_J':float(initial_strain),'relative_residual':relative,'bad':g.bad.numpy().tolist(),'pass':bool(relative<.08 and not g.bad.numpy().any())}

def controls():
 m=lattice();g=Solver(m,cut=False);before={k:v.numpy().copy() for k,v in g.initial.items()};g.graph(200)
 for k in range(350):
  if g.step([0,-.005,.1*np.sin(k*.4)]).any():break
 unbroken=bool(np.all(g.alive.numpy()==1) and np.all(g.paid.numpy()==0));stop=g.bad.numpy().tolist();g.reset();exact=all(np.array_equal(getattr(g,k).numpy(),v) for k,v in before.items())
 # Contact between two pieces after all bonds are deliberately disabled in a
 # unit fixture; this does not count as a blade-generated-cut success.
 tiny=dict(m);tiny.update(x=np.array([[-.0015,.02,0],[.0015,.02,0]],np.float32),edges=np.array([[0,1]],np.int32),length=np.array([.003],np.float32),stiffness=np.array([1.],np.float32),mass=np.array([.001,.001],np.float32),fracture_area=np.array([1e-6],np.float32),radius=.0016,mass_total=.002)
 c=Solver(tiny,knife=False,cut=False,support=False);c.alive.zero_();c.v.assign(np.array([[.01,0,0],[-.01,0,0]],np.float32));initial_gap=float(np.linalg.norm(c.x.numpy()[1]-c.x.numpy()[0]));c.step([0,0,0],30);v=c.v.numpy();outward=bool(v[0,0]<0 and v[1,0]>0);momentum=abs(float(np.sum(v[:,0]*tiny['mass'])));
 return {'fracture_disabled_unbroken':unbroken,'disabled_cut_stop':stop,'exact_full_reset':exact,'noncohesive_recontact_outward':outward,'recontact_horizontal_momentum_kg_m_s':momentum,'pass':bool(unbroken and exact and outward and momentum<1e-8)}

if __name__=='__main__':
 results={'geometry':geometry(),'energy':[energy(.0001),energy(.00005)],'controls':controls()};results['pass']=results['geometry']['pass'] and results['controls']['pass'] and all(x['pass'] for x in results['energy']);(W/'reports/mechanics.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
