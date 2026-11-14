from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
W=Path(__file__).resolve().parents[1];a=json.loads((W/'assessment.json').read_text());b=json.loads((W/'bulk_profile.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,(ax,bx)=plt.subplots(1,2,figsize=(12.6,5.8),gridspec_kw={'width_ratios':[1.15,1]});fig.patch.set_facecolor('#f7f8fa')
for x in [ax,bx]:x.set_facecolor('#f7f8fa');x.spines[['top','right','left']].set_visible(False);x.tick_params(axis='y',length=0)
vals=[next(r['optimistic_equivalent_50Hz_transitions_per_wall_s'] for r in b['rows'] if r['fixture']=='one_front' and r['batch']==n) for n in [1,4,8]]+[100,500]
labels=['1 block','4 independent blocks','8 independent blocks','Entry target','Preferred target'];colors=['#64748b','#475569','#2563eb','#15803d','#15803d']
ax.set_xscale('log');ax.set_xlim(.0003,1600);ax.barh(labels,vals,color=colors,height=.58);ax.invert_yaxis();ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True);ax.set_xlabel('Equivalent policy decisions / second (log scale)');ax.set_title('Even the optimistic bulk-only rate is far below target',loc='left',fontsize=12,pad=16)
for y,v in enumerate(vals):ax.text(v*1.3,y,f'{v:.4f}' if v<1 else f'{v:g}',va='center',fontsize=10,fontweight='bold')
ax.text(.02,-.20,'50 Hz control assumed. Fixed-topology microbenchmarks;\nno contact, fracture, robot, rendering or policy overhead.',transform=ax.transAxes,fontsize=9,color='#475569',va='top')
g=a['kernel_time_shares'];names=list(g);values=[100*g[n] for n in names];bx.barh(names,values,color='#64748b',height=.58);bx.invert_yaxis();bx.set_xlim(0,40);bx.set_xlabel('Share of diagnostic kernel time (%)');bx.set_title('The cost is in the mechanics',loc='left',fontsize=12,pad=16)
for y,v in enumerate(values):bx.text(v+.7,y,f'{v:.1f}%',va='center',fontsize=10)
bx.text(.02,-.20,'One partially cut block, 32 profiled microsteps.\nThe verified timestep is 24.4 nanoseconds.',transform=bx.transAxes,fontsize=9,color='#475569',va='top')
fig.suptitle('Performance decision: keep this solver as a reference, not the RL engine',x=.03,ha='left',fontsize=16,fontweight='bold',color='#152238')
fig.text(.03,.885,f'Best tested batch is about {a["shortfall_factor_entry_100_transitions_per_s"]:,.0f}× below the entry target. Existing Isaac/DiSECt setup unchanged.',fontsize=11,color='#475569')
fig.subplots_adjust(left=.15,right=.96,top=.75,bottom=.28,wspace=.80)
fig.savefig(W/'performance-review.png',dpi=170,facecolor=fig.get_facecolor());fig.savefig(W/'performance-review.pdf',facecolor=fig.get_facecolor())
