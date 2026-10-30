"""Refine only the small damage-onset interval, without changing model parameters."""
from pathlib import Path
import os,subprocess,json
r=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');f=r/'runs/offline/tomato_blade_damage_01'
files=sorted((f/'insertion_final').glob('*/summary.json'));entries=[(p,json.loads(p.read_text())) for p in files]
accepted=[(p,d) for p,d in entries if d['passed']]
if not accepted:raise SystemExit('No accepted coarse baseline')
zero=[(p,d) for p,d in accepted if d['damaged_patches']==0]
base,base_s=zero[-1]
if base_s['depth_mm']>=4:raise SystemExit('No damage within insertion bound; do not extend automatically')
start=base_s['depth_mm'];previous=base.parent
folder=f/'insertion_refined';folder.mkdir(exist_ok=False)
(folder/'baseline.json').write_text(json.dumps({'checkpoint':str(base.parent.relative_to(r)),'depth_mm':start,'energy_j':base_s['energy_j'],'cumulative_blade_work_j':base_s['cumulative_blade_work_j'],'fracture_dissipation_j':base_s['fracture_dissipation_j']},indent=2)+'\n')
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
for i in range(1,round((4-start)/.0625)+1):
 depth=round(start+i*.0625,6);out=folder/f'{i:02}'
 args=[str(r/'.venv-native/bin/python'),'rl/offline_tomato_blade_damage.py','--depth-mm',str(depth),'--previous',str(previous),'--output',str(out)]
 result=subprocess.run(args,cwd=r,env=env,capture_output=True,text=True,timeout=60)
 (folder/f'{i:02}.log').write_text(result.stdout+result.stderr);print(depth,result.returncode,result.stdout,result.stderr,flush=True)
 if result.returncode:raise SystemExit(1)
 summary=json.loads((out/'summary.json').read_text())
 if not summary['passed']:raise SystemExit(1)
 previous=out
last=json.loads((previous/'summary.json').read_text())
fracture=last['fracture_dissipation_j']-base_s['fracture_dissipation_j']
work=last['cumulative_blade_work_j']-base_s['cumulative_blade_work_j']
stored=last['energy_j']-base_s['energy_j'];error=work-stored-fracture
summary={'baseline_depth_mm':start,'final_depth_mm':last['depth_mm'],'step_mm':.0625,'increment_blade_work_j':work,'increment_stored_energy_j':stored,'increment_fracture_dissipation_j':fracture,'energy_residual_j':error,'fracture_normalized_residual':abs(error)/max(fracture,1e-12),'damaged_patches':last['damaged_patches'],'passed':fracture>0 and abs(error)<.01*fracture+1e-12}
(folder/'interval_energy.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary,flush=True)
