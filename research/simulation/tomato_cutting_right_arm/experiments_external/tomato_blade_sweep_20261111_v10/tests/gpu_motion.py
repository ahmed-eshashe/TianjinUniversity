from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from blade_sweep import SweepDriver,pose
from coupled_sweep import CoupledSweep
from multicut import MultiCut,volume_certificates,RejectedEvent
from gpu_backend import GPUReference
from reference import block
R=W/'runs/gpu_motion';R.mkdir(exist_ok=False);checks={};results={};start=time.perf_counter();DT=3.90625e-7;X=block(8,.0015);velocity=np.array([.02,-.01,.03])
def progress(label):
    (W/'status.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'status':'GPU_blade_motion_running' if label else 'GPU_blade_motion_complete','current':label,'simulation_running':bool(label),'production_changed':False},indent=2))
    (W/'gpu_motion.partial.json').write_text(json.dumps({'checks':checks,'results':results,'wall_s':time.perf_counter()-start},indent=2,allow_nan=False));print(label,flush=True)
def check(k,v,detail=None):
    checks[k]=bool(v)
    if not v:progress('FAILED '+k);raise AssertionError((k,detail))
def fields(a,b):
    return {f:max(float(np.max(abs(getattr(p,f)-getattr(b.pieces[k],f)),initial=0)) for k,p in a.pieces.items()) for f in ['q','vg','x','v','F']}
def equivalent(e):return e['q']<1e-7 and e['x']<1e-7 and e['vg']<1e-5 and e['v']<1e-5 and e['F']<1e-6
def make():
    s=MultiCut(X)
    for p in s.pieces.values():p.vg[:]=velocity;p.update_state()
    return SweepDriver(s,pose([.0003,.007,0]))

# Repeat the actual moving-edge path at unchanged and halved mechanical steps.
drivers={}
for label,dt in [('primary',DT),('half',DT/2)]:
    progress(label+' GPU cut sweep');d=make();c=CoupledSweep(d,dt);records=[];t0=time.perf_counter()
    for i,y in enumerate(np.linspace(.006,-.007,14),1):
        end=pose(np.array([.0003,y,0])+velocity*(i*.001));r=c.advance(end,round(.001/dt));records.append(r)
        check(label+'_graph_topology_'+str(i),c.gpu.ng==sum(len(p.q) for p in d.cpu.pieces.values()) and c.gpu.keys==list(d.cpu.pieces))
        check(label+'_volume_'+str(i),all(x['passed'] for p in d.cpu.pieces.values() for x in volume_certificates(p)))
        d.save(R/(label+'_frame'+str(i)))
        if i==7:check(label+'_partial_bridge',len(d.cpu.pieces)==1 and d.cpu.pieces['root'].plane is not None)
        if time.perf_counter()-t0>600:raise TimeoutError(label)
    check(label+'_full_cut',len(d.cpu.pieces)==2 and d.cpu.cut_count==1)
    check(label+'_state_carried',max(float(np.max(abs(p.v-velocity))) for p in d.cpu.pieces.values())<1e-6)
    check(label+'_mass',abs(d.cpu.metrics()['mass']-.001728)<1e-12)
    check(label+'_no_teleport_gap',abs(d.cpu.pieces['rootL'].q[:,0].max()-d.cpu.pieces['rootR'].q[:,0].min())<1e-8)
    # Geometric withdrawal/clearance query, not an integrated contact trajectory.
    before=d.cpu.fingerprint();withdraw=d.pose.copy();withdraw[:3,3]+=[0,0,.25];d.commit(d.propose(withdraw))
    check(label+'_withdrawal_no_new_topology',d.cpu.fingerprint()==before)
    check(label+'_whole_CAD_clear',d.whole_blade_clear()['clear'])
    d.save(R/(label+'_withdrawn'));drivers[label]=d
    results[label]={'wall_s':time.perf_counter()-t0,'material_sim_s':d.cpu.time,'cut_count':d.cpu.cut_count,'pieces':len(d.cpu.pieces),'GPU_rebuilds':c.rebuilds,'actions':records,'clearance':d.whole_blade_clear(),'withdrawal_note':'Along-edge pose/clearance checked at fixed material state; no contact forces or physical withdrawal time integrated.'};progress(label+' completed')
diff=fields(drivers['primary'].cpu,drivers['half'].cpu);check('mechanical_halfstep_agreement',equivalent(diff),diff);results['halfstep_differences']=diff

# Restart from material and sweep history during the active incision.
progress('partial-history GPU restart');d=SweepDriver.restore(R/'primary_frame7');c=CoupledSweep(d)
for i,y in enumerate(np.linspace(-.001,-.007,7),8):c.advance(pose(np.array([.0003,y,0])+velocity*(i*.001)),2560)
diff=fields(d.cpu,drivers['primary'].cpu);check('GPU_restart_continuation',equivalent(diff),diff);results['restart_difference']=diff

# Matched CPU/GPU short step exactly where the next full-support basis activates.
progress('short CPU GPU action comparison');a=make()
for y in [.006,.005,.004,.00301]:a.commit(a.propose(pose([.0003,y,0])))
a.save(R/'short_start');b=SweepDriver.restore(R/'short_start');c=CoupledSweep(b);end=pose(np.array([.0003,.003,0])+velocity*(32*DT))
for _ in range(32):a.cpu.step(DT)
a.commit(a.propose(end));c.advance(end,32);diff=fields(a.cpu,b.cpu)
check('CPU_GPU_action_fields',equivalent(diff),diff);check('CPU_GPU_action_topology',list(a.cpu.pieces)==list(b.cpu.pieces) and len(a.cpu.events)==len(b.cpu.events));results['CPU_GPU_action_difference']=diff

# A geometry rejection after GPU motion must roll back the whole action.
progress('coupled action rollback');d=make();c=CoupledSweep(d);before=d.fingerprint();bad=pose([.0003,0,0]);rejected=False
try:c.advance(bad,32)
except RejectedEvent:rejected=True
check('rejected_action_rolls_back_material_and_history',rejected and before==d.fingerprint() and c.gpu.steps==0)
# Non-affine motion is a declared boundary, not an approximate inverse-map fallback.
d=make();f=np.zeros_like(X);f[X[:,1]>.003,0]=.1/(X[:,1]>.003).sum();c=CoupledSweep(d,external=f);before=d.fingerprint();rejected=False
try:c.advance(pose([.0003,.006,0]),256)
except RejectedEvent:rejected=True
check('nonaffine_action_is_rejected_and_restored',rejected and before==d.fingerprint())

# Post-cut opening is generated by explicit balanced material loads, not position edits.
progress('post-withdrawal force-driven opening');opening={}
for label,dt in [('primary',DT),('half',DT/2)]:
    d=SweepDriver.restore(R/(label+'_withdrawn'));s=d.cpu;initial=s.metrics();x0=s.observations()[0].copy();f=np.zeros_like(X)
    f[s.pieces['rootL'].indices,0]=-.4/len(s.pieces['rootL'].indices)
    f[s.pieces['rootR'].indices,0]=.4/len(s.pieces['rootR'].indices)
    gpu=GPUReference(s,f,dt=dt);t0=time.perf_counter();gpu.step(round(.001/dt));s=gpu.export();final=s.metrics();work=float(np.sum(f*(s.observations()[0]-x0)));gap=float(s.pieces['rootR'].q[:,0].min()-s.pieces['rootL'].q[:,0].max())
    check(label+'_opening_gap',gap>.0002,gap)
    check(label+'_opening_energy',abs(final['energy']-initial['energy']-work)<max(1e-12,.05*abs(work)))
    check(label+'_opening_momentum',np.linalg.norm(final['momentum']-initial['momentum'])<1e-9)
    check(label+'_opening_volume',all(c['passed'] for p in s.pieces.values() for c in volume_certificates(p)))
    d.cpu=s;d.save(R/(label+'_opened'));opening[label]={'gap_m':gap,'material_work_J':work,'energy_error_J':final['energy']-initial['energy']-work,'net_load_N':f.sum(0).tolist(),'opposed_load_per_piece_N':.4,'wall_s':time.perf_counter()-t0,'note':'Auxiliary opening load after geometry-only split and kinematic withdrawal. Not fracture work or blade-driven physical separation.'}
results['opening']=opening
a=SweepDriver.restore(R/'primary_opened');b=SweepDriver.restore(R/'half_opened');diff=fields(a.cpu,b.cpu);check('opening_halfstep_position',diff['x']<1e-4);check('opening_halfstep_work',abs(opening['primary']['material_work_J']-opening['half']['material_work_J'])<.05*max(abs(opening['half']['material_work_J']),1e-12));results['opening_halfstep_difference']=diff

# At a resolved gap, a subsequent probe of one piece must not alter the other.
progress('post-cut independent-piece probe');a=SweepDriver.restore(R/'primary_opened');b=SweepDriver.restore(R/'primary_opened');f=np.zeros_like(X);f[a.cpu.pieces['rootL'].indices,0]=-.02/len(a.cpu.pieces['rootL'].indices);ga=GPUReference(a.cpu);gb=GPUReference(b.cpu,f);ga.step(1280);gb.step(1280);sa=ga.export();sb=gb.export();leak=float(np.linalg.norm(sa.pieces['rootR'].v-sb.pieces['rootR'].v,axis=1).max());probe=.02*(1280*DT)/sa.pieces['rootL'].metrics()['mass'];check('independent_neighbor_after_motion_generated_cut',leak/max(probe,1e-12)<.01);results['independence']={'neighbor_velocity_difference_m_s':leak,'nominal_probe_velocity_m_s':probe,'gap_before_probe_m':opening['primary']['gap_m']}
out={'status':'pass_motion_generated_topology_scope','checks':checks,'results':results,'wall_s':time.perf_counter()-start,'physical_fracture':False,'actual_blade_contact':False,'production_changed':False};(W/'gpu_motion_controls.json').write_text(json.dumps(out,indent=2,allow_nan=False));progress(None);print({'status':out['status'],'checks':len(checks),'wall_s':out['wall_s']},flush=True)
