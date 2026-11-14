from pathlib import Path
import json,shutil,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1];a=json.loads((W/'algebra_controls.json').read_text());d=json.loads((W/'dynamics_controls.json').read_text())
partial=json.loads((W/'runs/dynamics/partial.json').read_text())['rows'];full=json.loads((W/'runs/dynamics/full.json').read_text())['rows']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#394d47','text.color':'#19362f','axes.edgecolor':'#b1beb7','xtick.color':'#52665e','ytick.color':'#52665e'})
fig,ax=plt.subplots(1,3,figsize=(13.5,5.3));fig.set_facecolor('#f5f7f2')
for axis in ax:axis.set_facecolor('white');axis.set_axisbelow(True);axis.grid(axis='y',alpha=.16)
ax[0].bar([0,1],[288,324],color=['#a86c17','#267b5c'],width=.55);ax[0].bar(0,36,bottom=288,color='#f0d5ac',hatch='///',edgecolor='#a86c17',width=.55)
ax[0].text(0,332,'288 / 324',ha='center',weight='bold');ax[0].text(1,332,'324 / 324',ha='center',weight='bold');ax[0].set(xticks=[0,1],xticklabels=['v05 fixed samples','v06 integration'],ylim=(0,380),ylabel='Resolved / required scalar modes',title='The +0.3 mm cut is now resolved')
ax[1].plot([r['t']*1000 for r in partial],[r['behind_m']*1000 for r in partial],color='#267b5c',lw=2.5,label='Released region');ax[1].plot([r['t']*1000 for r in partial],[r['ahead_m']*1000 for r in partial],color='#9a5c18',lw=2,ls='--',label='Intact bridge');ax[1].set(xlabel='Simulated time (ms)',ylabel='Opening across plane (mm)',title='Partial cut keeps its bridge',ylim=(-.003,.06));ax[1].legend(frameon=False,fontsize=9)
ax[2].semilogy([r['t']*1000 for r in full],[max(r['left_speed_m_s'],1e-16) for r in full],color='#267b5c',lw=2.5,label='Untouched piece');ax[2].axhline(.0002,color='#9a5c18',ls='--',label='Allowed leakage limit');ax[2].set(xlabel='Simulated time (ms)',ylabel='Untouched piece speed (m/s)',title='Divided pieces remain independent',ylim=(1e-15,1e-3));ax[2].legend(frameon=False,fontsize=9,loc='center right')
fig.suptitle('Integration repair passed — within a restricted, single-plane block test',fontsize=16,weight='bold',y=.97)
fig.text(.5,.89,'v06 · eight tested cut positions · fresh dynamics at +0.3 mm · prescribed topology, not a physical knife cut',ha='center',fontsize=10,color='#61736b')
fig.text(.05,.079,'Mass, loaded state, refinement and complete cut-history restart checks pass.  •  Existing setup unchanged.',fontsize=10,weight='bold')
fig.text(.05,.034,'The CPU reference remains too slow for RL. Multiple cuts, tomato geometry, blade contact and physical fracture remain open.',fontsize=10,color='#61736b')
fig.subplots_adjust(top=.77,bottom=.23,left=.065,right=.975,wspace=.38)
p=W/'reports/integration_outcome.png';fig.savefig(p,dpi=160,facecolor=fig.get_facecolor());plt.close(fig)
shutil.copy2(p,Path('/home/omen/Documents/Codex/2026-10-31/tomato-project-handoff/outputs/mpm-v06-integration-outcome-20261110.png'));print(p)
