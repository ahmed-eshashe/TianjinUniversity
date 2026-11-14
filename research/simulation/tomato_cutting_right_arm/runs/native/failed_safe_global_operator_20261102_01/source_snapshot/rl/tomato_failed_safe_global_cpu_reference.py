"""Independent prepared-history full matrix and incremental-energy references."""
import argparse,json
from pathlib import Path
import numpy as np
from tomato_tangent_cpu_reference import reference_action
from tomato_global_energy_cpu_reference import energy

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();source=np.load(a.input);d={k:source[k]for k in source.files};history=d['history'];law=d['law'];expected=np.where(history[:,0]>=law[:,2],1.,np.where(history[:,0]>law[:,1],law[:,2]*(history[:,0]-law[:,1])/(np.maximum(history[:,0],1e-30)*(law[:,2]-law[:,1])),0.))
 if np.any(d['eligible'])or not np.allclose(history[:,1],expected,rtol=0,atol=1e-10):raise ValueError('Valid prepared history with eligibility disabled required')
 active=history[:,1]<1;factor=1-history[active,1]
 for key in ['cohesive_pairs','cohesive_counts','anchors','sign','weights','local_k']:d[key]=d[key][active].copy()
 d['local_k']*=factor[:,None,None];d['history']=np.zeros((int(active.sum()),2));d['eligible']=np.zeros(int(active.sum()),dtype=int);products,count=reference_action(d);actual=source['matrix_products'];errors=[dict(vector=i,absolute_error_n_m=float(abs(x-y).max()),relative_error=float(np.linalg.norm(x-y)/max(np.linalg.norm(x),1e-12)))for i,(x,y)in enumerate(zip(products,actual))];values=energy(d);ee=abs(values['total_j']-float(source['native_energy'][0]));passed=all(e['absolute_error_n_m']<=1e-6 or e['relative_error']<=1e-7 for e in errors)and(ee<=1e-10 or ee/max(abs(values['total_j']),1e-12)<=1e-9);a.output.write_text(json.dumps(dict(passed=bool(passed),active_material_patches=int(active.sum()),failed_material_patches=int((~active).sum()),matrix_errors=errors,incremental_energy_error_j=ee,incremental_energy_cpu_j=values['total_j'],independent_active_contacts=count,scope='Independent CPU full-registry reference: failed material contributes no frame/traction/energy, partial fixed history scales the qualified objective Gram/stored potential, bulk/contact and tensile curvature retain independent NumPy/CPU-autograd references. No stepping/cut claim.'),indent=2)+'\n');return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
