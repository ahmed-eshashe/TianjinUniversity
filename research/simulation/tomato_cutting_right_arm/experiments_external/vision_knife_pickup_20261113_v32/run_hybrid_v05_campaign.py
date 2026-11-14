from pathlib import Path
import json,os,subprocess,sys
W=Path(__file__).resolve().parent;P='/home/omen/teamwork_projects/tomato_cutting_right_arm/.venv-native/bin/python'
stages=[('regression',['test_002','test_003'],'curriculum_split_v01.json'),('validation',[f'recovery_validation_{i:03}' for i in range(3)],'curriculum_recovery_v02.json'),('test',[f'recovery_test_{i:03}' for i in range(8)],'curriculum_recovery_v02.json')]
for label,ids,manifest in stages:
 command=[P,'-u',str(W/'run_hybrid_v05_curriculum.py'),'--ids',*ids,'--tag','hybrid_v05_'+label,'--manifest',str(W/manifest),'--render']
 subprocess.run(command,cwd=W,check=True)
 results=[]
 for case in ids:
  p=W/'datasets'/('hybrid_v05_'+label)/case/'result.json';results.append(p.exists() and json.loads(p.read_text()).get('success') is True)
 if label!='test' and not all(results):
  print('Gate not passed:',label,results,flush=True);sys.exit(1)
print('Campaign evaluation finished; audit all saved outcomes before qualification.',flush=True)
