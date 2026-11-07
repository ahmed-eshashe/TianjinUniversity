"""Independent original-rest energy baseline, without cached replay contacts."""
from pathlib import Path
import json,gzip,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];design=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json';mass_path=R/'runs/native/global_gn_operator_20261102_01/rest_reference_inputs.npz';d=json.loads(design.read_text());x=np.array([n['position_m']for n in d['nodes']])+[0,0,.002];mass=np.load(mass_path)['mass'];initial=float(np.sum(mass*9.81*x[:,2]));records=[];pins={}
for name in ['fraction_duration_20261102_01','fraction_screen8_20261102_01','fraction_screen16_20261102_01','fraction_screen32_20261102_01','global_hold_preview_20261102_01']:
 run=R/'runs/native'/name;result=run/'supervisor_result.json'
 if not json.loads(result.read_text())['passed']:raise ValueError('Expected native pass '+name)
 if name.startswith('fraction_duration'):
  p=run/'fraction_preflight_measurements.json';episodes=[e['trace']for e in json.loads(p.read_text())['episodes']];paths=[p]
 else:
  paths=sorted(run.glob('episode*_audit.jsonl.gz'));episodes=[]
  for p in paths:
   with gzip.open(p,'rt')as stream:episodes.append([json.loads(line)for line in stream])
 for ep,rows in enumerate(episodes):
  max_change=max(row['energy']['total_j']-initial for row in rows);cached=np.array([row['energy']['total_j']-row['energy_increase_j']for row in rows]);offset=float(np.max(abs(cached-initial)));spread=float(np.ptp(cached));record=dict(run=name,episode=ep,records=len(rows),independent_original_rest_energy_j=initial,maximum_energy_increase_from_actual_original_rest_j=max_change,maximum_recorded_initial_energy_offset_j=offset,recorded_baseline_spread_j=spread,unchanged_budget_j=1e-5,passed=bool(max_change<=1e-5 and spread<1e-12));records.append(record)
  if not record['passed']:raise ValueError(record)
 for p in paths+[result]:pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
for p in [design,mass_path,Path(__file__)]:pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'runs/offline/original_initial_energy_recheck_20261102_01';out.mkdir(exist_ok=False);(out/'measurements.json').write_text(json.dumps(dict(passed=True,cases=records,source_sha256=pins,scope='Independent baseline and unchanged energy-rise gate recheck on saved accepted traces. Original constitutive rest lengths/volumes, zero gaps, zero velocity and no board penetration give zero original non-gravity potential; independent rest-operator checks establish zero initial self contact. No native rerun or new physical qualification. New prepared-state workers explicitly refresh contact after every reset.'),indent=2)+'\n');print(json.dumps(records,indent=2))
