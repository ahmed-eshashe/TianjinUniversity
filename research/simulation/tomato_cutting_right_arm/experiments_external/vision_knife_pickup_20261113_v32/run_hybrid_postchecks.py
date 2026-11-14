"""Run only after the current independent pickup gate passes."""
from pathlib import Path
import json,os,subprocess,sys
W=Path(__file__).resolve().parent;P='/home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python'
version=json.loads((W/'CURRENT_CANDIDATE.json').read_text())['version']
subprocess.run([P,str(W/'audit_current_pickup.py')],cwd=W,check=True)
r=json.loads((W/('reports/hybrid_'+version+'_campaign.json')).read_text());assert r['limited_curriculum_physical_gate_passed'], 'Finish physical gate before postchecks'
base=[P,'-u',str(W/('run_hybrid_'+version+'_curriculum.py')),'--ids','recovery_validation_000','--manifest',str(W/'curriculum_recovery_v02.json'),'--render']
subprocess.run(base+['--tag','hybrid_'+version+'_blank','--vision-ablation','blank'],cwd=W,check=True)
ep=W/'datasets'/('hybrid_'+version+'_blank')/'recovery_validation_000';prediction=json.loads((ep/'visual_prediction.json').read_text());trajectory=json.loads((ep/'trajectory.json').read_text());failure=(ep/'failure.txt').read_text();check=dict(expected_rejection=True,prediction_rejected=not prediction['accepted'],no_approach=all(x['phase']=='settle' for x in trajectory),max_sim_s=max(x['sim_s'] for x in trajectory),failure=failure.splitlines()[-1]);assert check['prediction_rejected'] and check['no_approach'];(W/('reports/hybrid_'+version+'_blank_guard.json')).write_text(json.dumps(check,indent=2))
# Prepared assets were held out from visual model training and all controller selection.
for name,scene in [('compact','compact_wide_handle_v01.usda'),('medium','medium_original_handle_v01.usda')]:
 subprocess.run(base+['--tag','hybrid_'+version+'_geometry_'+name,'--scene',str(W/scene)],cwd=W,check=True)
print('Blank-input guard and two held-out geometry probes completed. Geometry probes do not establish broad geometry coverage.',flush=True)
