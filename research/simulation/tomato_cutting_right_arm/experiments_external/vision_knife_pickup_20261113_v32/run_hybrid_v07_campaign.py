from pathlib import Path
import json,subprocess,sys
W=Path(__file__).resolve().parent;P='/home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python'
validation=[f'recovery_validation_{i:03}' for i in range(3)]
for label,ids in [('validation',validation),('test',[f'recovery_test_{i:03}' for i in range(8)])]:
 command=[P,'-u',str(W/'run_hybrid_v07_curriculum.py'),'--ids',*ids,'--tag','hybrid_v07_'+label,'--manifest',str(W/'curriculum_recovery_v02.json'),'--render']
 subprocess.run(command,cwd=W,check=True)
 outcomes=[]
 for case in ids:
  p=W/'datasets'/('hybrid_v07_'+label)/case/'result.json';outcomes.append(p.exists() and json.loads(p.read_text()).get('success') is True)
 subprocess.run([P,str(W/'audit_current_pickup.py')],cwd=W,check=True)
 if label=='validation' and not all(outcomes):
  print('Validation gate not passed:',outcomes,flush=True);sys.exit(1)
print('Campaign complete. Inspect the saved independent-test gate before qualification.',flush=True)
