from pathlib import Path
import sys,json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from contact_geometry import Cells
from volume_guard import jacobians
fig,axes=plt.subplots(1,2,figsize=(11,4.5),constrained_layout=True)
for ax,name,title in zip(axes,['paid_cut','paid_cut_refined_guard'],['Initial pilot: stored strain missed collapse','Bounded retest: independent guard stops it']):
 d=json.loads((W/f'runs/{name}/result.json').read_text());f=np.load(W/f'runs/{name}/final.npz');z=np.load(W/f'runs/{name}/trajectory.npz');g=Cells(f['X'],f['codes']);actual=[np.linalg.det(jacobians(g.corners(x),g.spacing)).min() for x in z['x']];stored=[r['minJ'] for r in d['rows']]
 ax.plot(z['t']*1000,stored,color='#3070c3',label='Stored constitutive J',lw=2);ax.plot(z['t']*1000,actual,color='#c84435',label='Reconstructed geometry J',lw=2);ax.axhline(.1,color='#555',ls='--',label='Retained minimum (0.1)');ax.set(xlabel='Simulated time (ms)',ylabel='Minimum local volume ratio J',title=title,ylim=(-.55,1.07));ax.grid(alpha=.2);ax.legend(fontsize=8,loc='lower left')
 if name.endswith('guard'):ax.scatter([1000*(d['sim_time']+d['dt'])],[d['last_volume_certificate']['observed_minJ']],color='#c84435',marker='x',s=70,zorder=6)
fig.suptitle('Gate 3 is unqualified — no physical cut was created',fontweight='bold');fig.savefig(W/'reports/gate3_failure_evidence.png',dpi=170);plt.close(fig)
