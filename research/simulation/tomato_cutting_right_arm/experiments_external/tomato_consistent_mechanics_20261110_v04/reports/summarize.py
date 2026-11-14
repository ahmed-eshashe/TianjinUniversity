from pathlib import Path
import sys,json,hashlib,datetime,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from basis_volume_guard import certificate
names=['cpu_controls','gpu_equivalence','mechanics_selected_controls','localized_selected_controls','analytic_wave_controls','checkpoint_controls','basis_volume_controls'];evidence={n:json.loads((W/(n+'.json')).read_text()) for n in names};base=json.loads((W/'mechanics_controls.json').read_text());checks={n:r['status']=='pass' for n,r in evidence.items()};checks['original_affine_checks']=all(v for k,v in base['checks'].items() if k!='compression_refinement');loaded=[]
for name in ['localized','localized_half']:
 with np.load(W/'runs/localized_selected'/(name+'.npz')) as z:c=certificate(z['X'],z['q']);loaded.append(c)
checks['continuous_loaded_endpoint_bounds']=all(c['passed'] for c in loaded)
(W/'loaded_basis_volume_controls.json').write_text(json.dumps({'status':'pass' if checks['continuous_loaded_endpoint_bounds'] else 'fail','cases':loaded,'scope':'Continuous-basis endpoints. Reconstructed-cell volume guard also ran at all 40 shared loading samples in each selected run.'},indent=2))
manifest=json.loads((W/'manifest.json').read_text());mismatches=[]
for name,digest in manifest['protected_sha256'].items():
 p=Path(name)
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:mismatches.append(name)
(W/'preservation_check.json').write_text(json.dumps({'at':datetime.datetime.now().astimezone().isoformat(),'protected_files':len(manifest['protected_sha256']),'mismatches':mismatches,'passed':not mismatches},indent=2));checks['preservation']=not mismatches
out={'status':'pass_intact_block_mechanics_only' if all(checks.values()) else 'fail','checks':checks,'selected_dt':3.90625e-7,'reference_dt':1.953125e-7,'key_result':evidence['mechanics_selected_controls']['results']['compression_refinement'],'material_unchanged':{'E_Pa':100000,'nu':.4,'rho_kg_m3':1000,'Gc_J_m2':80},'limits':{'production_adopted':False,'arbitrary_shape_supported':False,'cut_topology_requalified':False,'blade_contact_requalified':False,'gate3_complete':False,'RL_qualified':False},'original_failed_coarse_pair_preserved':str(W/'mechanics_controls.json')};(W/'qualification.json').write_text(json.dumps(out,indent=2))
old=Path('/home/omen/Documents/Codex/experiments/tomato_apic_repair_20261110_v03');fig,ax=plt.subplots(1,2,figsize=(12,4.3),constrained_layout=True)
for directory,label,color in [(old/'runs/mechanics_refined/compression_half.json','Previous APIC prototype','#b96845'),(W/'runs/mechanics_selected/compression.json','Consistent block mechanics','#267b5c')]:
 r=json.loads(directory.read_text());rows=r['rows'];ax[0].plot([x['t']*1000 for x in rows],[x['energy']/r['result']['initial_energy']*100 for x in rows],label=label,color=color)
ax[0].set(title='Elastic energy retained over 20 ms',xlabel='Simulated time (ms)',ylabel='Mechanical energy / initial energy (%)');ax[0].set_ylim(0,108);ax[0].legend();ax[0].grid(alpha=.2)
r=evidence['mechanics_selected_controls']['results']['compression_refinement'];ax[1].bar(['Old APIC\nfinal sample','New block basis\nmaximum over 20 samples'],[23.129,r['max_shared_time_velocity_m_s']*1000],color=['#b96845','#267b5c']);ax[1].axhline(5,color='#943f37',ls='--',label='5 mm/s acceptance screen');ax[1].set(title='Timestep consistency',ylabel='Velocity difference (mm/s)');ax[1].legend();ax[1].grid(axis='y',alpha=.2)
fig.suptitle('Numerical mechanics repaired in an intact-block candidate',fontsize=14);fig.text(.5,-.055,'Same 64,000 particles and material; different numerical bases. Energy traces: dt = 0.390625 µs.\nRefinement pairs: old 0.78125/0.390625 µs; new 0.390625/0.1953125 µs. Not cutting or RL qualification.',ha='center',fontsize=9);fig.savefig(W/'reports/mechanics_outcome.png',dpi=160,bbox_inches='tight');plt.close(fig)
print(json.dumps({'qualification':out,'loaded_bounds':loaded,'protected_files':len(manifest['protected_sha256'])},indent=2))
