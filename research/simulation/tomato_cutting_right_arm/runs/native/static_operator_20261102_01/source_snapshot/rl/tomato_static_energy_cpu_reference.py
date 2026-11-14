"""Independent original material/contact potential plus gravity preload value."""
import argparse,json
from pathlib import Path
import numpy as np
from tomato_global_energy_cpu_reference import energy

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=np.load(a.input);values=energy(d);gravity=-float(np.sum(d['mass'][:,None]*d['gravity'][None,:]*(d['x']-d['gravity_reference'])));total=values['total_j']+gravity;error=abs(total-float(d['native_energy'][0]));relative=error/max(abs(total),1e-12);passed=error<=1e-10 or relative<=1e-9;a.output.write_text(json.dumps(dict(passed=bool(passed),material_contact_values=values,gravity_relative_potential_j=gravity,static_total_j=total,absolute_error_j=error,relative_error=relative,scope='Independent CPU static potential value; original bulk/cohesive/contact/board plus gravity, no inertia or damping. No mechanical time advanced.'),indent=2)+'\n');return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
