"""Plot recorded physical measurements; this is not rendered camera evidence."""
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('run',type=Path);a=p.parse_args()
r=json.loads((a.run/'trajectory.json').read_text());r=[s for s in r if s['control_step']>=30]
t=np.array([s['sim_s'] for s in r]);height=np.array([s['handle_height_m'] for s in r]);initial=height[0]
fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True,layout='constrained')
axes[0].plot(t,(height-initial)*1000,color='#2776a3');axes[0].axhline(50,color='#b65037',ls='--',label='Final lift requirement (also requires unsupported wrap)')
axes[0].set_ylabel('Handle rise (mm)');axes[0].legend(fontsize=8,loc='upper left')
axes[1].plot(t,[s.get('in_place_motion',{}).get('centre_xy_shift_m',0)*1000 for s in r],color='#7552a5')
axes[1].axhline(30,color='#b65037',ls='--');axes[1].set_ylabel('Knife centre drift (mm)')
for part,color in zip(['thumb','index','middle','ring','pinky','palm'],['#d08925','#2776a3','#3e975e','#b74866','#7d6cb5','#222222']):
 force=[sum(c['force_n'] for c in s['contacts'] if c['part']==part and c['on_handle']) for s in r]
 axes[2].plot(t,force,label=part,color=color,linewidth=1.1)
axes[2].set_ylabel('Handle contact force (N)');axes[2].set_xlabel('Simulated time (s)');axes[2].legend(ncol=3,fontsize=8)
seating=[s['sim_s'] for s in r if s['phase'] in ['coordinated_palm_seating','mesh_guided_palm_seating']]
for ax in axes:
 ax.grid(alpha=.18)
 if seating:ax.axvspan(min(seating),max(seating),color='#d7e6c9',alpha=.45)
fig.suptitle(a.run.name+' — recorded physical diagnostic\nShading: palm seating attempt | no learned policy or camera observation',fontsize=12)
fig.savefig(a.run/'seating_progress.png',dpi=150);plt.close(fig);print(a.run/'seating_progress.png')
