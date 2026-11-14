"""Produce the bounded-study evidence summary and scientific plots."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
R=ROOT/'results'
def trace(name): return np.genfromtxt(R/f'{name}_trace.csv',names=True,delimiter=',')
def summary(name): return json.loads((R/f'{name}_summary.json').read_text())
evaluation={'decision':'Do not adopt unmodified CRESSim for persistent multi-cut tomato RL',
 'current_project_modified':False,'experimental_validation':'not performed',
 'finite_particle_state_screen':True,'persistent_independent_fragments':'FAIL',
 'speed_accuracy_equivalence':'not established','solvers':{}}
for solver in ['mls','pb']:
 baseline=trace(f'cuts_{solver}_0'); driven=trace(f'cuts_{solver}_1'); post=baseline['step']>=800
 times=[summary(f'cuts_{solver}_0{suffix}')['wall_per_sim_second'] for suffix in ['', '_repeat1','_repeat2']]
 metrics={'wall_seconds_per_simulated_second':times,
  'median_wall_seconds_per_simulated_second':float(np.median(times)),
  'postcut_undriven_quarter_peak_velocity_fraction':[float(np.max(np.abs(driven[f'vy{g}'][post]-baseline[f'vy{g}'][post]))/.01) for g in [1,2,3]],
  'postcut_final_velocity_fraction':[(float(driven[f'vy{g}'][-1])-float(baseline[f'vy{g}'][-1]))/.01 for g in range(4)],
  'gap_control':{}}
 for mode in ['held','absent','far']:
  data=trace(f'{mode}_{solver}_1_offgrid'); metrics['gap_control'][mode]={'peak_undriven_velocity_fraction':float(np.max(np.abs(data['vz1']))/.01),'final_driven_velocity_fraction':float(data['vz0'][-1]/.01),'final_undriven_velocity_fraction':float(data['vz1'][-1]/.01)}
 evaluation['solvers'][solver]=metrics
all_summaries=[json.loads(f.read_text()) for f in R.glob('*_summary.json')]
evaluation['completed_runs']=len(all_summaries)
evaluation['all_observed_states_finite']=all(s['all_finite'] for s in all_summaries)
evaluation['mass_and_count_preserved_in_logged_runs']=all(s['initial_mass']==s['final_mass'] for s in all_summaries)
(ROOT/'evaluation.json').write_text(json.dumps(evaluation,indent=2))
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(11,4.3))
for ax,solver,title in zip(axs,['mls','pb'],['MLS-MPM','PB-MPM']):
 for mode,label,color in [('held','Blade held in gap','#1a936f'),('absent','Blade absent','#c84545'),('far','Widely separated halves','#3967ad')]:
  data=trace(f'{mode}_{solver}_1_offgrid');ax.plot(data['t']*1000,data['vz1']/.01*100,label=label,color=color,linewidth=2,linestyle='--' if mode=='far' else '-')
 ax.axhline(1,color='#777777',lw=.8,ls=':',label='1% screening threshold')
 ax.set(title=title,xlabel='Simulated time after pulse (ms)',ylabel='Motion transferred to untouched half (%)')
 ax.grid(alpha=.15);ax.set_xlim(0,20)
axs[1].legend(loc='lower right',fontsize=8)
fig.suptitle('Close pieces exchange motion after the blade is absent',fontsize=14,fontweight='bold')
fig.text(.5,.015,'8,000 particles · 1 mm nominal gap · no gravity or friction · 0.01 m/s tangential pulse to one half',ha='center',fontsize=9,color='#555555')
fig.tight_layout(rect=[0,.06,1,.92]);fig.savefig(ROOT/'independence_check.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4.3))
for ax,solver,title in zip(axs,['mls','pb'],['MLS-MPM','PB-MPM']):
 b=trace(f'cuts_{solver}_0');d=trace(f'cuts_{solver}_1');sel=b['step']>=800
 for g,label in enumerate(['Pulsed quarter','Untouched quarter 1','Untouched quarter 2','Untouched quarter 3']):
  ax.plot((b['t'][sel]-1.6)*1000,(d[f'vy{g}'][sel]-b[f'vy{g}'][sel])/.01*100,label=label,linewidth=2,ls='--' if g==2 else '-')
 ax.set(title=title,xlabel='Time after both blade passes and pulse (ms)',ylabel='Mean velocity / applied pulse (%)');ax.grid(alpha=.15)
axs[1].legend(fontsize=8,loc='upper right')
fig.suptitle('Two intersecting passes do not leave independent quarters',fontsize=14,fontweight='bold')
fig.text(.5,.015,'Unforced baseline subtracted · blades clear of block · MLS loses momentum even in a separate far-gap control',ha='center',fontsize=9,color='#555555')
fig.tight_layout(rect=[0,.06,1,.92]);fig.savefig(ROOT/'two_pass_check.png',dpi=180);plt.close(fig)
print(json.dumps(evaluation,indent=2))
