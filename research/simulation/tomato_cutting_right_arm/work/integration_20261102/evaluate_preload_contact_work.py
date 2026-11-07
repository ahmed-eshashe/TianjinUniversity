"""Apply the registered signal-relative work gates without hiding remap errors."""
from pathlib import Path
import argparse, gzip, hashlib, json
import numpy as np

p=argparse.ArgumentParser()
p.add_argument('--run',type=Path,required=True)
p.add_argument('--body-readback',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
root=Path(__file__).resolve().parents[2]
out=a.output.resolve();out.mkdir(exist_ok=False)
run=a.run.resolve();body_dir=a.body_readback.resolve()
plan_path=root/'runs/offline/preload_contact_work_plan_20261102_01/plan.json'
plan=json.loads(plan_path.read_text());pins={}
def read(path):
    pins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())
read(plan_path);pins[str(Path(__file__).resolve())]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
native=read(run/'supervisor_result.json');manifest=read(run/'input_manifest.json');body=read(body_dir/'measurements.json')
assert native['passed'] and body['component_passed']
cases=[]
for label in manifest['cases']:
    path=run/(label+'_audit.jsonl.gz');pins[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    with gzip.open(path,'rt') as f: rows=[json.loads(line) for line in f]
    assert len(rows)==manifest['intervals_per_case']
    br=read(body_dir/(label+'_robot_work.json'));assert len(br)==len(rows)
    signal=float(rows[0]['pressure_energy_before_j'])
    signed=absolute=target_work=robot_work=raw_error=adjusted_error=body_error=0.
    pose_delta=qd_delta=0.;curve=[]
    for row,robot in zip(rows,br):
        jump=(row['packet_refresh']or{}).get('native_energy_jump_j',0.)
        signed+=jump;absolute+=abs(jump)
        assert abs(signed-row['cumulative_quadrature_rebuild_energy_jump_j'])<1e-20
        target_work+=row['particle_pressure_work_j']
        robot_work+=robot['cumulative_applied_contact_work_j']-(curve[-1]['robot_work_j']if curve else 0.)
        assert abs(robot_work-robot['cumulative_applied_contact_work_j'])<1e-20
        signal=max(signal,abs(target_work),abs(robot_work))
        defect=row['whole_energy_minus_known_work_j']
        assert np.isfinite([defect,signed,absolute,signal,robot_work,target_work]).all()
        raw_error=max(raw_error,abs(defect))
        adjusted_error=max(adjusted_error,abs(defect-signed)+absolute)
        body_error=max(body_error,abs(robot['cumulative_robot_energy_work_defect_j']))
        pose_delta=max(pose_delta,float(abs(np.array(row['actual_tool_pose_after'])-rows[0]['actual_tool_pose_before']).max()))
        qd_delta=max(qd_delta,float(abs(np.array(row['qd_after'])-rows[0]['qd_before']).max()))
        curve.append(dict(time_s=row['time_s'],robot_work_j=robot_work,target_pressure_work_j=target_work,raw_whole_defect_j=defect,signed_remap_j=signed,absolute_remap_j=absolute))
    energy_budget=plan['whole_preload_energy_error_relative_budget']*signal+plan['whole_preload_energy_error_absolute_floor_j']
    robot_budget=plan['robot_energy_error_relative_to_contact_work']*abs(robot_work)+plan['robot_energy_error_absolute_floor_j']
    # No-feedback is an intentionally open one-way negative control, not a closed assembly.
    # Clear has no contact signal: retain the originally registered absolute floor.
    criteria=dict(raw_whole_work=raw_error<=energy_budget,remap_accounted_whole_work=adjusted_error<=energy_budget,robot_work=body_error<=robot_budget)
    required=label in ('feedback','replay','clear')
    cases.append(dict(case=label,required_for_closed_preload_gate=required,energy_signal_j=signal,raw_whole_work_error_j=raw_error,remap_accounted_whole_work_error_j=adjusted_error,energy_budget_j=energy_budget,cumulative_signed_remap_j=signed,cumulative_absolute_remap_j=absolute,robot_contact_work_j=robot_work,robot_energy_work_error_j=body_error,robot_energy_work_budget_j=robot_budget,target_pressure_work_j=target_work,maximum_tool_pose_component_change=pose_delta,maximum_joint_velocity_change_rad_s=qd_delta,criteria=criteria,passes_required_criteria=(all(criteria.values())if required else None)))
    (out/(label+'_work_curve.json')).write_text(json.dumps(curve,indent=2)+'\n')
report=dict(preload_fixture_work_passed=all(c['passes_required_criteria']for c in cases if c['required_for_closed_preload_gate']),cases=cases,definition_clarification='Closed preload gates apply feedback/replay/clear; no-feedback is deliberately open. Energy signal is max(initial contact potential, max absolute cumulative target pressure work, max absolute cumulative actual robot contact work); it excludes turnover and pre-existing bulk/gravity energy. Clear retains absolute floors. No limits were relaxed.',moving_blade_work_qualified=False,full_23B_qualified=False,source_sha256=pins,scope='Only the registered assigned nonfracturing preload. Actual moving tool, actuator-driven approach/indentation, coupling lag under commanded motion, cutting, global base momentum, post-cut reset and experimental validation remain separate.')
(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='source_sha256'},indent=2))
