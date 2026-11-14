from pathlib import Path
import os,json,numpy as np
W=Path(__file__).resolve().parents[1];os.environ['MPLCONFIGDIR']=str(W/'cache/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':14})
fig,axes=plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
colors=['#3478b8','#e89c39','#37a681','#8e68bb'];cmap=ListedColormap(colors)
R=W/'runs/gate2'
for ax,name,title,ab,sliceaxis in [(axes[0,0],'partial_withdrawn','Partial cut: bridge remains',(0,1),2),(axes[0,1],'full_opened','Full cut: two independent parts',(0,1),2),(axes[1,0],'intersecting_opened','Cross-cut: four independent parts',(0,2),1)]:
 s=np.load(R/f'{name}.npz');x=s['x'];m=abs(x[:,sliceaxis])<.0016
 if name=='partial_withdrawn':c=s['codes']%3;cm=ListedColormap(['#a8b0ba',colors[0],colors[1]])
 elif name=='full_opened':c=(s['X'][:,0]>0).astype(int);cm=cmap
 else:c=2*(s['X'][:,0]>0)+(s['X'][:,2]>0);cm=cmap
 ax.scatter(x[m,ab[0]]*1000,x[m,ab[1]]*1000,c=c[m],cmap=cm,s=7,linewidths=0,vmin=0,vmax=2 if name=='partial_withdrawn' else 3)
 ax.set_aspect('equal');ax.set_xlim(-37,37);ax.set_ylim(-37,37);ax.set_xlabel('x (mm)');ax.set_ylabel(('y' if ab[1]==1 else 'z')+' (mm)');ax.set_title(title,loc='left',fontweight='bold');ax.grid(alpha=.16);ax.set_axisbelow(True)
 if name=='partial_withdrawn':ax.plot([0,0],[30,0],color='#343d49',lw=2,ls='--');ax.text(0,-20,'Intact bridge',ha='center',fontsize=10,color='#333d49')
 else:ax.text(0,-35,'Opened by test impulses after the tool sweep',ha='center',fontsize=8,color='#4a5361')
ax=axes[1,1];p=json.loads((W/'persistent_cut_controls.json').read_text())['results']['performance'];values=[a['wall_per_sim_s'] for a in p]
ax.bar(['0 cuts','1 cut','2 cuts','4 cuts'],values,color=colors,width=.6)
for i,v in enumerate(values):ax.text(i,v+2,f'{v:.1f}',ha='center',fontweight='bold')
ax.set_ylim(0,110);ax.set_ylabel('Wall seconds per simulated second');ax.set_title('Measured physics cost — not RL-ready',loc='left',fontweight='bold');ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True);ax.axhline(1,color='#777',ls='--',lw=1);ax.text(3.4,8,'Real-time target: 1',ha='right',fontsize=9)
fig.suptitle('Persistent-cut prototype: Gates 0–2 component evidence',fontsize=19,fontweight='bold')
fig.supxlabel('64,000 particles • 3 mm grid • Particle-center sections shown • Geometry-driven cuts; no cutting-resistance/contact qualification',fontsize=10)
fig.savefig(W/'reports/phase1_evidence.png',dpi=150)
print(W/'reports/phase1_evidence.png')
