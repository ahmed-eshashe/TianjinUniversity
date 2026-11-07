from pathlib import Path
import sys,numpy as np,json
w=Path(__file__).parent;sys.path.insert(0,str(w.parents[1]/'rl'))
from tomato_native_full_model import registry
from tomato_master_frame_live import frame_support
d=registry();pairs,counts,coef,weights,models,supports=frame_support(d)
np.savez(w/'master_frame_definition.npz',pairs=pairs,counts=counts,coefficients=coef,weights=weights,supports=supports)
(w/'master_frame_definition.json').write_text(json.dumps(dict(frame_side='remainder',selection='canonical reference coordinates',model_extension=True,asymmetric=True,original_traction_quadrature=True,original_bilinear_law=True,experimental_validation='pending',fresh_trajectory_required=True,references=[{'url':'https://portal.research.lu.se/en/publications/framework-for-non-coherent-interface-models-at-finite-displacemen/','scope':'Energy depends on gap and surface tangents; retain frame derivatives for objectivity and angular momentum. Does not validate this specific implementation or tomato parameters.'},{'url':'https://mooseframework.inl.gov/source/materials/cohesive_zone_model/CZMComputeGlobalTractionTotalLagrangian.html','scope':'Finite-deformation cohesive rotations require consistent derivatives; MOOSE uses average deformation gradient, not the one-sided choice implemented here.'}]),indent=2))
