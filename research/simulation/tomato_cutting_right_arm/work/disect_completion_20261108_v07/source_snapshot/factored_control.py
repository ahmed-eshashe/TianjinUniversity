from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));from contact_numerics import ContactBulk
from factored_contact import FactoredContactBulk
# Same unchanged intact operator, nonzero smooth velocity, larger step.
a=ContactBulk();b=FactoredContactBulk();v=-(a.x-a.x.mean(0))*.01;v*=a.free;a.v.copy_(v);b.v.copy_(v);h=.0002
ra=a.implicit(h,maxiter=2048);rb=b.implicit(h,maxiter=2048);pe=(a.x-b.x).abs().max().item();ve=(a.v-b.v).abs().max().item();out=dict(scope='Same force/operator and step, old versus factored preconditioner',position_max_error_m=pe,velocity_max_error_m_s=ve,old_iterations=ra['iterations'],new_iterations=rb['iterations'],old_residual=ra['relative_residual'],new_residual=rb['relative_residual'],passed=bool(pe<1e-10 and ve<1e-8));(W/'factored_control_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
