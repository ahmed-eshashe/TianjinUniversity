"""Controller-only comparison. Imports the unchanged v28 solver and material."""
from pathlib import Path
import argparse, hashlib, json, sys, time
import numpy as np

W = Path(__file__).resolve().parent
R = W.parent / 'tomato_approx_rl_20261113_v28'
sys.path.insert(0, str(R / 'src'))
import warp as wp
wp.config.kernel_cache_dir = str(W / 'cache/warp')
wp.config.enable_backward = False
from environment import CuttingEnv

CASES = {
    'baseline': dict(kind='original', feed=.0015),
    'feed_2x': dict(kind='original', feed=.003),
    'feed_4x': dict(kind='original', feed=.006),
    'smooth_2x': dict(kind='smooth', feed=.003, frequency=.8, amplitude=.020),
    'smooth_4x': dict(kind='smooth', feed=.006, frequency=.8, amplitude=.020),
    'smooth_sync_2x': dict(kind='smooth_sync', feed=.003, frequency=.8, amplitude=.020),
}

def command(case, k, position, parts, phase):
    action = np.zeros(6)
    if k < 25:
        return action, phase
    if parts >= 2 and position[1] <= .0034:
        phase = 1
    if phase == 1:
        action[2] = .06
        return action, phase
    t = (k-25)*.02
    if case['kind'] == 'original':
        saw = np.sin((k-25)*.4)
        action[2] = .15*saw
        feed = case['feed']*abs(saw)
    else:
        # Smooth position envelope starts at rest and stays within +/-20 mm.
        # Its finite difference is the exact desired control-step velocity.
        def target(s):
            u = np.clip(s/.5, 0., 1.)
            ramp = u*u*u*(10-15*u+6*u*u)
            return case['amplitude']*ramp*np.sin(2*np.pi*case['frequency']*s)
        action[2] = (target(t+.02)-target(t))/.02
        # Match original mean downward feed (2/pi times its stated peak),
        # but do not stop descending at every sliding reversal.
        u = np.clip(t/.5, 0., 1.)
        feed = case['feed']*2/np.pi*u*u*(3-2*u)
        if case['kind'] == 'smooth_sync':
            # Hold the same long-run mean feed, but smoothly stop descent at
            # sliding reversals instead of pushing down with no slicing speed.
            feed *= 2*np.cos(2*np.pi*case['frequency']*(t+.01))**2
    if position[1] > .0034:
        action[1] = -min(feed, (position[1]-.0034)/.02) if case['kind']!='original' else -feed
    assert np.all(np.abs(action) <= CuttingEnv.action_limits+1e-8)
    return action, phase

def run(name, dt, suffix):
    case = CASES[name]
    out = W/'runs'/(name+suffix)
    out.mkdir(exist_ok=False)
    E = CuttingEnv(1, dt=dt, max_steps=5500)
    g = E.g
    g.graph(round(.02/dt))
    initial = {k: v.numpy() for k,v in g.initial.items()}
    m = E.model; edges=m['edges']; mass=m['mass']
    trace=[]; snapshots=[]; snapshot_time=[]; phase=0
    contact_s=None; separated_s=None; max_deform=0.; max_strain=0.
    net_peak=0.; min_height=float('inf'); max_shortening=0.; path=0.
    previous=g.tool.numpy()[0].copy(); settled=None
    started=time.perf_counter()
    for k in range(5500):
        action,phase=command(case,k,g.tool.numpy()[0],E.parts[0],phase)
        obs,reward,terminated,truncated,info=E.step(action)
        elapsed=(k+1)*.02
        x=g.x.numpy(); tool=g.tool.numpy()[0]; reaction=g.reaction.numpy()[0]
        path+=float(np.linalg.norm(tool-previous)); previous=tool.copy()
        net_peak=max(net_peak,float(np.linalg.norm(reaction)))
        if k==24: settled=x.copy()
        if contact_s is None and info['fracture_work_J'][0]>0:contact_s=elapsed
        if separated_s is None and info['separated'][0]:separated_s=elapsed
        deform=0.; strain99=0.
        if settled is not None and not info['separated'][0]:
            displacement=x-settled
            displacement-=np.average(displacement,axis=0,weights=mass)
            deform=float(np.sqrt(np.average(np.sum(displacement**2,axis=1),weights=mass)))
            max_deform=max(max_deform,deform)
            max_shortening=max(max_shortening,float(np.ptp(settled[:,1])-np.ptp(x[:,1])))
        if k%10==0:
            alive=g.alive.numpy().astype(bool)
            strain=np.abs(np.linalg.norm(x[edges[:,1]]-x[edges[:,0]],axis=1)/m['length']-1)
            strain99=float(np.quantile(strain[alive],.99)) if alive.any() else 0.
            max_strain=max(max_strain,strain99)
        min_height=min(min_height,float(x[:,1].min()-m['radius']))
        trace.append([elapsed,*tool,*action,*reaction,float(g.load.numpy()[0]),float(info['peak_force_N'][0]),float(info['peak_penetration_m'][0]),int(info['parts'][0]),int(info['broken'][0]),float(info['fracture_work_J'][0]),deform,phase])
        if k%50==0 or terminated.any() or truncated.any():
            snapshots.append(x.copy());snapshot_time.append(elapsed)
        if k%250==0 or terminated.any() or truncated.any():
            progress={'case':name+suffix,'sim_s':elapsed,'pieces':int(E.parts[0]),'peak_load_N':float(info['peak_force_N'][0]),'bad':int(info['bad'][0]),'wall_s':time.perf_counter()-started}
            (W/'progress.json').write_text(json.dumps(progress)); print(json.dumps(progress),flush=True)
        if terminated.any() or truncated.any():break
    result={'case':name,'config':case,'dt_s':dt,'success':bool(info['success'][0]),'bad':int(info['bad'][0]),'pieces':int(E.parts[0]),'second_mass_fraction':float(info['second_mass_fraction'][0]),'duration_sim_s':elapsed,'first_fracture_work_s':contact_s,'separation_s':separated_s,'peak_sum_load_N':float(g.peak.numpy()[0]),'peak_net_reaction_50Hz_N':net_peak,'peak_penetration_mm':float(info['peak_penetration_m'][0])*1000,'fracture_work_J':float(info['fracture_work_J'][0]),'broken_bonds':int(info['broken'][0]),'max_preseparation_deformation_rms_mm':max_deform*1000,'max_preseparation_height_shortening_mm':max_shortening*1000,'max_surviving_bond_abs_strain_p99_5Hz':max_strain,'min_particle_bottom_mm':min_height*1000,'blade_path_m':path,'refinements':g.refinements,'final_dt_s':g.active_dt,'wall_s':time.perf_counter()-started,'wall_time_scope':'Viewer may render concurrently; not an isolated throughput benchmark.','force_scope':'Safety load is sum of local contact/fracture magnitudes. Net reaction sampled at 50Hz, not an experimentally measured wrist force.'}
    np.savez_compressed(out/'state.npz',**{key:getattr(g,key).numpy() for key in g.initial},labels=E.labels[0],snapshots=np.array(snapshots),snapshot_time=snapshot_time)
    np.savez_compressed(out/'trace.npz',values=np.array(trace),columns=np.array(['time','tool_x','tool_y','tool_z','vx','vy','vz','wx','wy','wz','reaction_x','reaction_y','reaction_z','sampled_load','running_peak_load','running_peak_penetration_m','pieces','broken','fracture_work_J','deformation_rms_m','phase']))
    E.reset()
    result['exact_reset']=all(np.array_equal(getattr(g,key).numpy(),value) for key,value in initial.items())
    (out/'result.json').write_text(json.dumps(result,indent=2))
    print('RESULT '+json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cases',nargs='+',default=list(CASES));parser.add_argument('--dt',type=float,default=.0002);parser.add_argument('--suffix',default='');args=parser.parse_args()
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'src').glob('*.py')}
    results=[run(name,args.dt,args.suffix) for name in args.cases]
    unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    (W/'reports'/('comparison_'+ '-'.join(args.cases)+args.suffix+'.json')).write_text(json.dumps({'results':results,'original_physics_unchanged':unchanged,'original_source_hashes':hashes},indent=2))
    assert unchanged
