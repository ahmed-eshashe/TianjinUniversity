from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parent
fig,axes=plt.subplots(2,2,figsize=(12,8),constrained_layout=True)
for file,label,color in [('settle_result.json','Explicit board friction (failed)','#ba5b45'),('settle_contact_result.json','Implicit board friction','#267658'),('settle_contact_refined_result.json','Implicit, half timestep','#6286a4')]:
    p=W/file
    if not p.exists():continue
    d=json.loads(p.read_text());axes[0,0].semilogy([r['sim_s'] for r in d['rows']],[r['maximum_speed_m_s']*1000 for r in d['rows']],label=label,color=color,lw=1.3)
axes[0,0].axhline(1,color='#6d6250',ls='--',lw=1,label='Late settling limit');axes[0,0].axvspan(.9,1,color='#d4e6d5',alpha=.4);axes[0,0].set(xlabel='Simulated time (s)',ylabel='Maximum nodal speed (mm/s)',title='Intact-target settling: preserved failure and correction');axes[0,0].legend(fontsize=8)
d=json.loads((W/'settle_contact_result.json').read_text());late=[r for r in d['rows'] if r['sim_s']>=.9];t=[r['sim_s'] for r in late];ground=[r['ground_force_N'][1] for r in late];fixture=[r['fixed_reaction_N'][1] for r in late];axes[0,1].plot(t,ground,label='Board normal reaction',color='#267658');axes[0,1].plot(t,fixture,label='Fixed-support normal reaction',color='#b47e43');axes[0,1].plot(t,np.array(ground)+fixture,label='Combined support',color='#48565a');axes[0,1].axhline(.12167126547965468*9.80665,color='#6d6250',ls='--',lw=1,label='Physical total weight');axes[0,1].set(xlabel='Simulated time (s)',ylabel='Normal force (N)',title='Late support load paths (1 mm contact-offset model)');axes[0,1].legend(fontsize=8)
if (W/'indent_result.json').exists():
    for file,label,col in [('indent_result.json','CAD probe','#267658'),('indent_refined_result.json','Half timestep','#6286a4')]:
        p=W/file
        if p.exists():
            d=json.loads(p.read_text());axes[1,0].plot([r['sim_s']*1000 for r in d['rows']],[r['force_norm_N'] for r in d['rows']],label=label,color=col)
    axes[1,0].set(xlabel='Probe time (ms)',ylabel='Resultant contact-law force (N)',title='CAD probe: force refinement FAILED (10.1% > 5%)');axes[1,0].legend(fontsize=8)
else:
    old=json.loads((W/'preflight_result.json').read_text());new=json.loads((W/'corrected_preflight_result.json').read_text());ang=[r['rotation_deg'] for r in old['rows']];axes[1,0].semilogy(ang,[r['rest_force_norm_N'] for r in old['rows']],'o-',label='Preserved diagonal-only invariant',color='#ba5b45');axes[1,0].semilogy(ang,[r['rest_force_norm_N'] for r in new['rows']],'o-',label='Corrected full invariant',color='#267658');axes[1,0].set(xlabel='Static rigid rotation (degrees)',ylabel='Global nodal force norm (N)',title='Independent material preflight');axes[1,0].legend(fontsize=8)
mesh=np.load(W/'conforming_split.npz');x=mesh['x'];f=mesh['cut_minus'];axes[1,1].triplot(x[:,2]*1000,x[:,1]*1000,f,color='#507a64',lw=.35);axes[1,1].set(xlabel='Interface tangent z (mm)',ylabel='Height y (mm)',title='Paired cutting-interface geometry — static input only');axes[1,1].set_aspect('equal');axes[1,1].text(.02,.02,'No physical slice or live cohesive-assembly pass',transform=axes[1,1].transAxes,fontsize=8,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'})
for ax in axes.flat:ax.grid(alpha=.16)
fig.suptitle('Section 3 prerequisite evidence — uncalibrated FEM candidate',fontsize=14);fig.savefig(W/'precontact_evidence.png',dpi=160);fig.savefig(W/'precontact_evidence.pdf');plt.close(fig)
