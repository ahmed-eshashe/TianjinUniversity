from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1]
corner=json.loads((W/'corner_reference.json').read_text())['rows'];d=json.loads((W/'failure_confirmation.json').read_text())['rows']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(12,5.3));fig.patch.set_facecolor('#f8fafc')
x=np.array([r['offset_m']*1e6 for r in corner])
for key,label,color in [('v17','Preserved reference','#64748b'),('v18','Aggregation candidate','#0d9488')]:
 axes[0].plot(x,[r[key]['linearized_stability_dt_s']*1e6 for r in corner],'o-',label=label,color=color,lw=2)
axes[0].set(xscale='log',yscale='log',xlabel='Cut-plane offset near grid corner (µm)',ylabel='Linearized stability ceiling (µs)',title='Corner stability improved');axes[0].invert_xaxis();axes[0].legend(frameon=False,loc='lower left');axes[0].grid(alpha=.15)
vals=[r['cross_model']['force_relative']*100 for r in d];labels=['24 mm block\n6 mm grid · 20 ms','60 mm block\n6 mm grid · 5 ms','60 mm block\n3 mm grid · 2 ms']
bars=axes[1].bar(range(3),vals,color=['#b45309','#be123c','#be123c'],width=.62)
axes[1].axhline(5,color='#0f172a',ls='--',lw=1.5,label='Allowed discrepancy: 5%')
for b,v in zip(bars,vals):axes[1].text(b.get_x()+b.get_width()/2,v+3,f'{v:.1f}%',ha='center',weight='bold')
axes[1].set(xticks=range(3),xticklabels=labels,ylabel='Internal-force RMS discrepancy (%)',ylim=(0,145),title='Dynamic response failed the accuracy gate');axes[1].legend(frameon=False,loc='upper right');axes[1].grid(axis='y',alpha=.15)
fig.suptitle('Aggregation trial: stability improved; response accuracy failed',fontsize=17,weight='bold',y=.98)
fig.text(.5,.045,'Left: linearized spectrum only, not measured speed. Right: each solver passes timestep refinement.\nGeometric block tests; internal forces are not blade reactions. Durations differ across rows.',ha='center',fontsize=10,color='#475569')
fig.tight_layout(rect=(0,.12,1,.92));fig.savefig(W/'reports/aggregation-result.png',dpi=160,facecolor=fig.get_facecolor());fig.savefig(W/'reports/aggregation-result.pdf',facecolor=fig.get_facecolor());plt.close(fig)
