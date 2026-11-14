from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from fixtures import make,action,assign,world_y
from front_system import FrontSystem
from deformed_sweep import DeformedSweep
from blade_sweep import pose
from gpu_backend import GPUReference
from coupled_sweep import CoupledSweep
from multicut import volume_certificates
from reference import block
from integrated_cut import RejectedEvent
R=W/'runs/gpu';R.mkdir(exist_ok=False);checks={};results={};start=time.perf_counter();DT=3.90625e-7
def progress(s):
    (W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':'GPU_front_tests_running' if s else 'GPU_front_tests_complete','current':s,'simulation_running':bool(s),'production_changed':False},indent=2));print(s,flush=True)
    (W/'gpu.partial.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.perf_counter()-start},indent=2,allow_nan=False))
def check(k,v,detail=None):
    checks[k]=bool(v)
    if not v:progress('FAILED '+k);raise AssertionError((k,detail))
def diff(a,b):
    return {f:max(float(np.max(abs(getattr(p,f)-getattr(b.pieces[k],f)))) for k,p in a.pieces.items()) for f in ['q','vg','x','v','F']}
def equiv(e):return e['q']<1e-7 and e['x']<1e-7 and e['vg']<1e-5 and e['v']<1e-5 and e['F']<1e-6
progress('non-affine loaded shallow-front force comparison')
d=make();action(d,.00595);s=d.cpu;s.save(R/'initial');p=s.pieces['root'];f=np.zeros_like(s.X);left=s.X[:,0]<.0003
f[left,0]=-.02/left.sum();f[~left,0]=.02/(~left).sum();g=GPUReference(s,f)
got=g.field_values();u,force=p.energy_force(p.q);force+=p.O.T@f;acc,reaction=p.acceleration(p.q,f)
err={'force_relative':float(np.linalg.norm(got['force']-force)/np.linalg.norm(force)),'acceleration_relative':float(np.linalg.norm(got['acceleration']-acc)/np.linalg.norm(acc)),'energy_relative':abs(got['strain_energy']-u)/abs(u),'mass_residual':got['mass_residual']}
check('new_basis_GPU_force',err['force_relative']<1e-7,err);check('new_basis_GPU_acceleration',err['acceleration_relative']<1e-7);check('new_basis_GPU_energy',err['energy_relative']<1e-8);check('new_basis_GPU_mass_residual',err['mass_residual']<1e-7);results['same_field']=err
# Independent directional energy-gradient check through the new local modes.
rng=np.random.default_rng(712);direction=rng.normal(size=p.q.shape);direction/=np.linalg.norm(direction);eps=1e-8
grad=(p.energy_force(p.q+eps*direction)[0]-p.energy_force(p.q-eps*direction)[0])/(2*eps);analytic=-np.sum(p.energy_force(p.q)[1]*direction)
check('new_mode_force_energy_gradient',abs(grad-analytic)<2e-5*max(abs(analytic),1e-6),[grad,analytic]);results['gradient']={'finite_difference':grad,'force_contraction':analytic}

# Freely evolve the same loaded partial block, without requesting a new cut.
# No contact/force law changes are made; loads enter the existing adjoint.
outstates={};records={}
for label,dt in [('primary',DT),('half',DT/2)]:
    progress(label+' loaded GPU dynamics');a=FrontSystem.restore(R/'initial.npz');before=a.metrics();x0=a.observations()[0];gpu=GPUReference(a,f,dt=dt);t=time.perf_counter();gpu.step(round(.0001/dt));gpu.export();wall=time.perf_counter()-t
    after=a.metrics();work=float(np.sum(f*(a.observations()[0]-x0)));balance=after['energy']-before['energy']-work
    check(label+'_energy_balance',abs(balance)<max(1e-12,.05*max(abs(before['energy']),abs(work))))
    check(label+'_momentum',np.linalg.norm(after['momentum']-before['momentum'])<1e-9)
    check(label+'_volume',all(c['passed'] for p in a.pieces.values() for c in volume_certificates(p)))
    check(label+'_mass',abs(after['mass']-.001728)<1e-12)
    a.save(R/label);outstates[label]=a;records[label]={'wall_s':wall,'sim_s':.0001,'work_J':work,'energy_residual_J':balance,'energy_initial_J':before['energy'],'GPU_allocated_bytes':gpu.memory(),'basis_dofs':gpu.ng,'quadrature_points':gpu.nq,'inverse_residuals':gpu.inverse_residuals}
e=diff(outstates['primary'],outstates['half']);check('halfstep_position',e['x']<1e-4);check('halfstep_velocity',e['v']<.005)
w0,w1=records['primary']['work_J'],records['half']['work_J'];check('halfstep_work',abs(w0-w1)<.05*max(abs(w1),1e-12));results['dynamics']=records;results['halfstep']=e

progress('matched CPU trajectory');a=FrontSystem.restore(R/'initial.npz');t=time.perf_counter()
for i in range(256):a.step(DT,f,f)
e=diff(a,outstates['primary']);check('matched_CPU_GPU_trajectory',equiv(e),e);results['CPU']={'wall_s':time.perf_counter()-t,'sim_s':.0001,'difference':e}

progress('loaded restart and local-front continuation');a=FrontSystem.restore(R/'primary.npz');b=FrontSystem.restore(R/'primary.npz');ga=GPUReference(a,f);gb=GPUReference(b,f);ga.step(32);ga.export();gb.step(32);gb.export();e=diff(a,b);check('loaded_GPU_restart',equiv(e));results['restart']=e

# New material response is also compared with a higher quadrature order.
progress('independent integration order check');coarse=make();action(coarse,.00595)
fine=FrontSystem(block(8,.0015),order=7);assign(fine.pieces['root']);fine=DeformedSweep(fine,pose([.0003,world_y(.0061),0]));action(fine,.00595)
cg,fg=GPUReference(coarse.cpu,f),GPUReference(fine.cpu,f);cv,fv=cg.field_values(),fg.field_values()
rel=float(np.linalg.norm(cv['force']-fv['force'])/np.linalg.norm(fv['force']));check('integration_force',rel<1e-5);check('integration_energy',abs(cv['strain_energy']-fv['strain_energy'])<max(1e-12,1e-6*abs(fv['strain_energy'])))
cg.step(64);cg.export();fg.step(64);fg.export();e=diff(coarse.cpu,fine.cpu);check('integration_trajectory',equiv(e));results['integration']={'force_relative':rel,'difference':e}

# Actual GPU material motion plus four fine advances: rest/translation case.
# Nonuniform freely evolving capability is probed separately below, never inferred.
progress('GPU coupled 50 micron front advances');translated={};velocity=np.array([.02,-.01,.03])
for label,dt in [('primary',DT),('half',DT/2)]:
    s=FrontSystem(block(8,.0015));s.pieces['root'].vg[:]=velocity;s.pieces['root'].update_state();d=DeformedSweep(s,pose([.0003,.006,0]));coupled=CoupledSweep(d,dt);rows=[]
    for j in range(1,5):
        end=pose(np.array([.0003,.006-j*.00005,0])+velocity*j*.00005);rows.append(coupled.advance(end,round(.00005/dt)))
        check(label+'_fine_advance_'+str(j),len(d.cpu.pieces)==1 and d.cpu.pieces['root'].plane is not None)
        d.save(R/(label+'_coupled_'+str(j)))
    translated[label]=d;results[label+'_coupled']=rows
e=diff(translated['primary'].cpu,translated['half'].cpu);check('coupled_halfstep',equiv(e),e);results['coupled_halfstep']=e
re=DeformedSweep.restore(R/'primary_coupled_2');c=CoupledSweep(re)
for j in [3,4]:c.advance(pose(np.array([.0003,.006-j*.00005,0])+velocity*j*.00005),128)
check('coupled_history_restart',equiv(diff(re.cpu,translated['primary'].cpu)))

# Critical applicability probe: genuine free non-affine relaxation may no longer
# have a planar, separable chart. Report this as an unsupported capability,
# even though correct rejection/rollback is a successful software guard.
progress('freely evolving non-affine cut capability probe');d=make();c=CoupledSweep(d);before=d.fingerprint();reason=None
try:c.advance(pose([.0003,world_y(.00595),0]),128)
except RejectedEvent as e:reason=str(e)
results['free_nonaffine_coupled_cut']={'accepted':reason is None,'reason':reason,'duration_s':128*DT,'scope':'freely relaxing nonuniform block, no contact'}
if reason:
    check('unsupported_free_deformation_rolls_back',before==d.fingerprint() and c.gpu.steps==0)
else:
    check('free_deformation_cut_fields_finite',all(np.isfinite(p.q).all() for p in d.cpu.pieces.values()))
out={'status':'component_tests_complete','checks':checks,'results':results,'wall_s':time.perf_counter()-start,'physical_fracture':False,'actual_blade_contact':False,'production_changed':False}
(W/'gpu_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));progress(None);print(json.dumps({'status':out['status'],'checks':len(checks),'free_nonaffine_probe':results['free_nonaffine_coupled_cut'],'wall_s':out['wall_s']},indent=2))
