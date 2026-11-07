"""Registered moving-contact energy exits with independent robot channels.

Uses the separately verified canonical initial target energy, target potential
readouts, and CAD-validated contact potentials. Does not claim a fresh host
recalculation of every target constitutive/contact energy at every microstep.
"""
from pathlib import Path
import argparse, gzip, hashlib, json
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--body-readback',type=Path,required=True);p.add_argument('--pressure-readback',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2];run=a.run.resolve();out=a.output.resolve();out.mkdir(exist_ok=False);pins={}
def read(path):
    pins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())
m=read(run/'input_manifest.json');native=read(run/'supervisor_result.json');protocol=read(root/'runs/offline/moving_contact_protocol_20261102_01/plan.json');body=read(a.body_readback.resolve()/'measurements.json');pressure=read(a.pressure_readback.resolve()/'measurements.json');initial=read(root/'runs/native/static_preparation_cached_20261102_01/static_preparation_measurements.json');E0=initial['prestressed_physical_energy']['total_j'];assert native['passed'] and body['body_work_channel_reconstruction_passed'] and pressure['component_readback_passed']
cases=[]
for label in m['cases']:
    robots=read(run/(label+'_robot_audit.json'));brows=read(a.body_readback.resolve()/(label+'_robot_work.json'));bcase=next(c for c in body['cases']if c['case']==label)
    path=run/(label+'_target_audit.jsonl.gz');pins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    with gzip.open(path,'rt')as f:target=[json.loads(l)for l in f]
    signal=target[0]['pressure_energy_before_j'];rawerr=adjusted=berr=contactworkscale=0.;reconstruction=0.;curve=[]
    for i,(row,b)in enumerate(zip(robots,brows)):
        tr=target[(i+1)*m['subcycles']-1]
        defect=tr['target_audit']['energy']['total_j']+row['contact_potential_after_robot_j']+b['actual_robot_kinetic_energy_j']-E0-target[0]['pressure_energy_before_j']-bcase['initial_robot_kinetic_energy_j']-b['cumulative_gravity_work_j']-b['cumulative_actuator_work_j']
        reconstruction=max(reconstruction,abs(defect-row['whole_energy_minus_known_work_j']))
        assert abs(defect-row['whole_energy_minus_known_work_j'])<=1e-12
        signal=max(signal,abs(row['cumulative_target_pressure_work_j']),abs(b['cumulative_applied_contact_work_j']))
        contactworkscale=max(contactworkscale,abs(b['cumulative_applied_contact_work_j']))
        rawerr=max(rawerr,abs(defect));adjusted=max(adjusted,abs(defect-row['cumulative_signed_remap_j'])+row['cumulative_absolute_remap_j']);berr=max(berr,abs(b['cumulative_robot_energy_work_defect_j']))
        assert np.isfinite([rawerr,adjusted,berr,signal]).all()
        curve.append(dict(time_s=row['time_s'],independently_reconstructed_whole_defect_j=defect,robot_energy_work_defect_j=b['cumulative_robot_energy_work_defect_j'],robot_contact_work_j=b['cumulative_applied_contact_work_j'],cumulative_absolute_remap_j=row['cumulative_absolute_remap_j']))
    ebudget=protocol['whole_contact_signal_relative_budget']*signal+protocol['whole_contact_signal_absolute_floor_j'];bbudget=protocol['robot_contact_work_relative_budget']*contactworkscale+protocol['robot_contact_work_absolute_floor_j']
    if label=='clear':ebudget=bbudget=1e-6*bcase['initial_robot_kinetic_energy_j']+1e-15
    criteria=dict(raw_whole_energy=rawerr<=ebudget,remap_accounted_whole_energy=adjusted<=ebudget,robot_energy_work=berr<=bbudget)
    required=label in ('feedback','replay','clear')
    cases.append(dict(case=label,closed_contact_case=required,energy_signal_j=signal,raw_whole_energy_error_j=rawerr,remap_accounted_whole_energy_error_j=adjusted,whole_energy_budget_j=ebudget,robot_contact_work_scale_j=contactworkscale,robot_energy_work_error_j=berr,robot_energy_budget_j=bbudget,independent_whole_reconstruction_error_j=reconstruction,criteria=criteria))
    (out/(label+'_work_curve.json')).write_text(json.dumps(curve,indent=2)+'\n')
energy_passed=all(all(c['criteria'].values())for c in cases if c['closed_contact_case'])
pins[str(Path(__file__).resolve())]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
report=dict(moving_fixture_energy_passed=energy_passed,original_absolute_knife_measurement_gate_passed=body['component_passed'],resolution_aware_knife_measurement_gate_passed=body['moving_measurement_passed'],velocity_resolution_reference=body['velocity_resolution_reference'],pose_velocity_work_consistency_passed=body['pose_velocity_work_consistency_passed'],moving_fixture_combined_work_passed=bool(energy_passed and body['moving_measurement_passed']and body['pose_velocity_work_consistency_passed']),cases=cases,source_sha256=pins,full_23B_qualified=False,scope='Registered bounded coasting-contact fixture only, pending same-source coupling refinement and reversed-motion coverage. Independent full-body work, canonical initial target energy and CAD-validated contact potentials combined with previously verified target energy channels; not a fresh host re-evaluation of every target constitutive/contact potential per fine interval. Complete route/controller/fracture/global-base-momentum qualification remains open.')
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='source_sha256'},indent=2))
