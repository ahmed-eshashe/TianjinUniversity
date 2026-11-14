"""Time-normalized interpretation of legacy DiSECt damage, NOT a calibration.
No live FEM springs or topology are advanced by this module's tests.
"""
from pathlib import Path
import numpy as np,json
W=Path(__file__).resolve().parent
def advance(k,opening,contact,dt,softness_per_call,reference_dt=1e-4):
    if dt<0 or reference_dt<=0:raise ValueError('Time intervals must be nonnegative; reference interval positive')
    return np.maximum(0.,np.asarray(k)-np.asarray(contact,dtype=bool)*np.maximum(opening,0.)*(softness_per_call/reference_dt)*dt)
if __name__=='__main__':
    rows=[];T=.01
    for name,k0,softness in [('bulk',1800.,1600.),('surface',2000.,2000.)]:
        for n in [100,200,400]:
            dt=T/n;k=k0;energy=0.
            for j in range(n):
                old=k;opening=.0001*((j+.5)/n);k=float(advance(k,opening,True,dt,softness));energy+=.5*opening**2*(old-k)
            exact=k0-(softness/1e-4)*.0001*T/2
            rows.append({'name':name,'intervals':n,'dt_s':dt,'stiffness_N_per_m':k,'analytic_stiffness_N_per_m':exact,'absolute_error_N_per_m':abs(k-exact),'damage_dissipation_J':energy,'passed':bool(abs(k-exact)<=1e-8 and energy>=0)})
    controls={'no_contact_unchanged':float(advance(1800.,.001,False,.1,1600.))==1800.,'closed_interface_unchanged':float(advance(1800.,-.001,True,.1,1600.))==1800.,'no_negative_stiffness':float(advance(1800.,.1,True,1.,1600.))==0.}
    old=[max(0.,1800-n*.0001*1600) for n in [100,200,400]]
    out={'scope':'Defined candidate rate interpretation with analytic unit/refinement controls; not live fracture, skin equivalence or experimental validation','law':'k_new=max(0,k-contact*max(opening,0)*(softness_legacy/dt_reference)*dt)','reference_dt_s':1e-4,'reference_choice':'Observed validated prism forward example, solely fixes interpretation of legacy per-call softness; no tomato fracture data fit','stiffness_unit':'N/m','legacy_softness_unit':'N/m^2 per invocation','rate_softness_unit':'N/(m^2 s)','bulk_initial_stiffness_N_m':1800.,'bulk_legacy_softness':1600.,'surface_initial_stiffness_N_m':2000.,'surface_legacy_softness':2000.,'legacy_dt_dependence_control_final_stiffnesses':old,'rows':rows,'controls':controls,'passed':all(controls.values()) and all(r['passed'] for r in rows),'remaining_limits':['Live FEM cut-spring integration not implemented in the double bulk adapter.','Original tomato cohesive/skin fracture energy and path-eligibility law are not reproduced by example coefficients.','Actual time-dependent contact/opening needs refinement with the complete dynamics; unit tests do not establish cut convergence.']}
    (W/'fracture_rate_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
