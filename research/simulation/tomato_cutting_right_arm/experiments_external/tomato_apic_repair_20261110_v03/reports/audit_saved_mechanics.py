from pathlib import Path
import json,numpy as np,hashlib,datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1]
rows=[]
for folder,prefix,dt in [('mechanics','initial',12.5e-6),('mechanics_refined','refined',.78125e-6)]:
 pair=[]
 for name,factor in [('compression',1),('compression_half',.5)]:
  z=np.load(W/'runs'/folder/(name+'.npz'));r=json.loads((W/'runs'/folder/(name+'.json')).read_text());q=r['rows'][-1];e=r['result']['initial_energy'];pair.append(z)
  rows.append({'name':prefix+'_'+name,'dt_s':dt*factor,'particles':len(z['x']),'sim_s':.02,'wall_s':r['result']['wall_s'],'wall_per_sim_second':r['result']['wall_s']/.02,'initial_energy_J':e,'final_mechanical_energy_J':q['energy'],'recorded_numerical_loss_J':q['transfer_and_support_loss'],'numerical_loss_fraction':q['transfer_and_support_loss']/e,'max_accounted_energy_residual_fraction':r['result']['max_energy_residual']/e,'peak_final_speed_m_s':float(np.linalg.norm(z['v'],axis=1).max()),'tracked_array_bytes':r['result']['memory']['array_bytes']})
 dv=np.linalg.norm(pair[0]['v']-pair[1]['v'],axis=1);dx=np.linalg.norm(pair[0]['x']-pair[1]['x'],axis=1);i=int(dv.argmax())
 out={'max_velocity_difference_m_s':float(dv.max()),'rms_velocity_difference_m_s':float(np.sqrt(np.mean(dv**2))),'velocity_difference_p95_m_s':float(np.quantile(dv,.95)),'fraction_particles_above_5mm_s':float(np.mean(dv>.005)),'max_position_difference_m':float(dx.max()),'worst_particle_index':i,'reference_position_m':pair[0]['X'][i].tolist(),'coarse_velocity_m_s':pair[0]['v'][i].tolist(),'fine_velocity_m_s':pair[1]['v'][i].tolist()}
 (W/'reports'/f'{prefix}_pair_saved_audit.json').write_text(json.dumps(out,indent=2))
(W/'reports/saved_damping_audit.json').write_text(json.dumps({'cases':rows,'interpretation':'Numerical dissipation is explicitly recorded, not material viscosity or fracture. Converged accounted energy alone does not establish converged motion. Strong timestep sensitivity and substantial numerical damping remain; no universal claim about APIC or official CRESSim.','new_simulation':False},indent=2))
fig,axs=plt.subplots(1,2,figsize=(12,4.4),constrained_layout=True)
colors=['#5e7c94','#9db9c5','#b9693e','#e1ad72']
for row,color in zip(rows,colors):
 folder='mechanics_refined' if row['name'].startswith('refined') else 'mechanics';name='compression_half' if row['name'].endswith('half') else 'compression';r=json.loads((W/'runs'/folder/(name+'.json')).read_text());ts=np.array([x['t'] for x in r['rows']])*1e3;loss=np.array([x['transfer_and_support_loss'] for x in r['rows']])/row['initial_energy_J']*100
 axs[0].plot(ts,loss,label=f"{row['dt_s']*1e6:g} µs",color=color)
axs[0].set(title='Numerical energy removal during elastic release',xlabel='Simulated time (ms)',ylabel='Recorded loss / initial energy (%)');axs[0].legend(title='Timestep');axs[0].grid(alpha=.2)
a=json.loads((W/'reports/initial_pair_saved_audit.json').read_text());b=json.loads((W/'reports/refined_pair_saved_audit.json').read_text());axs[1].bar(['12.5 / 6.25 µs','0.78125 / 0.390625 µs'],[a['max_velocity_difference_m_s']*1e3,b['max_velocity_difference_m_s']*1e3],color=['#5e7c94','#b9693e']);axs[1].axhline(5,color='#a43f3f',ls='--',label='Predeclared 5 mm/s screen');axs[1].set(title='Motion still depends on timestep',ylabel='Maximum final velocity difference (mm/s)');axs[1].legend();axs[1].grid(axis='y',alpha=.2)
fig.suptitle('Isolated v03 repair: null-mode treatment passes; mechanics qualification fails',fontsize=13);fig.savefig(W/'reports/repair_outcome.png',dpi=160);plt.close(fig)
manifest=json.loads((W/'manifest.json').read_text());bad=[]
for name,digest in manifest['protected_sha256'].items():
 p=Path(name)
 if not p.is_file():bad.append({'path':name,'reason':'missing'})
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:bad.append({'path':name,'reason':'changed'})
proof={'at':datetime.datetime.now().astimezone().isoformat(),'protected_files':len(manifest['protected_sha256']),'mismatches':bad,'passed':not bad,'scope':'Frozen production/evidence files listed in manifest, including v01/v02; not a hash of every filesystem file.'};(W/'preservation_check.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'refined_pair':b,'cases':rows,'preservation':proof},indent=2))
