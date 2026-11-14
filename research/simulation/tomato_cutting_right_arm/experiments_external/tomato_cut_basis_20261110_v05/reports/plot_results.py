from pathlib import Path
import json,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1]
partial=json.loads((W/'runs/dynamics/partial.json').read_text())['rows']
full=json.loads((W/'runs/dynamics/full.json').read_text())['rows']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#394d47','text.color':'#19362f','axes.edgecolor':'#b1beb7','xtick.color':'#52665e','ytick.color':'#52665e'})
fig,ax=plt.subplots(1,3,figsize=(13.5,5.2));fig.set_facecolor('#f5f7f2')
for a in ax:a.set_facecolor('#ffffff');a.grid(axis='y',alpha=.16);a.set_axisbelow(True)
ax[0].plot([r['t']*1000 for r in partial],[r['behind_jump']*1000 for r in partial],color='#267b5c',lw=2.5,label='Released region')
ax[0].plot([r['t']*1000 for r in partial],[r['ahead_jump']*1000 for r in partial],color='#9a5c18',lw=2,ls='--',label='Intact bridge')
ax[0].set(xlabel='Simulated time (ms)',ylabel='Opening across plane (mm)',title='Partial cut retains its bridge',ylim=(-.003,.06));ax[0].legend(frameon=False,loc='upper left',fontsize=9)
ax[1].semilogy([r['t']*1000 for r in full],[max(r['left_speed'],1e-16) for r in full],color='#267b5c',lw=2.5,label='Untouched piece')
ax[1].axhline(.02*.01,color='#9a5c18',ls='--',lw=1.6,label='Allowed leakage limit')
ax[1].set(xlabel='Simulated time (ms)',ylabel='Untouched piece speed (m/s)',title='Divided pieces are independent',ylim=(1e-15,1e-3));ax[1].legend(frameon=False,loc='center right',fontsize=9)
required=np.array([288,324,324]);resolved=np.array([288,288,324]);labels=['Aligned\nunit cut','Shifted\n0.3 mm','Integration\ndiagnostic']
ax[2].bar(np.arange(3),resolved,color=['#267b5c','#a86c17','#6d8580'],width=.58)
ax[2].bar(np.arange(3),required-resolved,bottom=resolved,color='#f0d5ac',width=.58,hatch='///',edgecolor='#a86c17')
for i,(r,n) in enumerate(zip(resolved,required)):ax[2].text(i,n+7,f'{r}/{n}',ha='center',fontsize=10,fontweight='bold')
ax[2].set(xticks=np.arange(3),xticklabels=labels,ylabel='Resolved / required scalar modes',title='Off-grid sampling blocks progress',ylim=(0,375))
fig.suptitle('Cut-state proof: useful component passes, freely positioned cuts still blocked',fontsize=16,fontweight='bold',y=.97)
fig.text(.5,.89,'v05 · 12 mm block · prescribed topology fixtures · no physical knife cut',ha='center',fontsize=11,color='#61736b')
fig.text(.05,.075,'Partial/full motion and state-history checks passed.  •  All 883 protected files unchanged.',fontsize=10,fontweight='bold')
fig.text(.05,.032,'Integration diagnostic restores rank only; it is not yet a validated solver. Contact, fracture, tomato geometry and RL speed remain open.',fontsize=9,color='#61736b')
fig.subplots_adjust(top=.77,bottom=.22,left=.065,right=.975,wspace=.38)
path=W/'reports/cut_basis_outcome.png';fig.savefig(path,dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
shutil.copy2(path,Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/mpm-v05-cut-basis-outcome-20261110.png'))
print(path)
