"""Energy ledgers for bounded unloading/reclosure; no dynamics or simulator."""
import math


def ledger(energy,dissipation,work,*,initial_energy,initial_dissipation,peak_energy=0.):
    """A new boundary-work experiment retains all previously spent fracture loss.

    Scale by this experiment's recoverable energy/work and NEW fracture loss,
    not total historical dissipation. Thus a small reclosure loop cannot hide
    behind a large energy from the earlier insertion.
    """
    values=(energy,dissipation,work,initial_energy,initial_dissipation,peak_energy)
    if not all(math.isfinite(v) for v in values):raise ValueError('Nonfinite energy')
    if min(energy,dissipation,initial_energy,initial_dissipation,peak_energy)<-1e-12:raise ValueError('Negative energy')
    new_loss=dissipation-initial_dissipation
    if new_loss < -1e-12:raise ValueError('Fracture dissipation cannot heal')
    change=energy-initial_energy;error=work-change-new_loss
    peak=max(peak_energy,initial_energy,energy)
    scale=max(peak,abs(work),abs(change)+max(new_loss,0.),1e-12)
    return {'work_j':work,'initial_energy_j':initial_energy,'initial_dissipation_j':initial_dissipation,
            'stored_energy_change_j':change,'new_fracture_dissipation_j':new_loss,'peak_energy_j':peak,
            'residual_j':error,'scale_j':scale,'relative_residual':abs(error)/scale,
            'passed':abs(error)<=.01*scale+1e-12}


def damage_changes(old,new):
    if len(old)!=len(new):raise ValueError('Changed patch registry')
    return {'healed_patches':sum(b.damage<a.damage for a,b in zip(old,new)),
            'decreased_histories':sum(b.kappa_m<a.kappa_m for a,b in zip(old,new)),
            'max_absolute_damage_change':max(abs(b.damage-a.damage) for a,b in zip(old,new)),
            'max_absolute_history_change_m':max(abs(b.kappa_m-a.kappa_m) for a,b in zip(old,new))}


def withdrawal_guess(initial,pairs,old_multipliers,widths,cut_x):
    """Uncommitted predictor following previously loaded blade contacts.

    Moving only an optimization guess keeps a loaded body's Newton system near
    its constrained branch. Neither the accepted path origin nor damage/history
    changes here. The final solve must still pass every independent check.
    """
    x=initial.copy();n=len(pairs)
    for i,(s,r) in enumerate(pairs):
        if old_multipliers[n+2*i]>1e-9:x[s,0]=cut_x-widths[i]/2
        if old_multipliers[n+2*i+1]>1e-9:x[r,0]=cut_x+widths[i]/2
    return x
