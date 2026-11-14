"""One native worker at a time, explicit teacher/actor separation, preserved runs."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
W=Path(__file__).resolve().parent;B=W.parent/'vision_knife_pickup_20261113_v32'
a=argparse.ArgumentParser();a.add_argument('--script',default='hybrid_pickup_v10.py');a.add_argument('--tag',required=True);a.add_argument('--ids',nargs='+',required=True);a.add_argument('--checkpoint',type=Path);a.add_argument('--teacher-targets',type=Path);a.add_argument('--override',type=Path);args=a.parse_args()
manifest=json.loads((W/'generalization_curriculum_v01.json').read_text());cases={x['id']:x for x in manifest['episodes']}
base=json.loads((B/'datasets/hybrid_v07_validation/recovery_validation_000/configuration.json').read_text())['args']
offsets=json.loads(args.teacher_targets.read_text()) if args.teacher_targets else None
override=json.loads(args.override.read_text()) if args.override else {}
dest=W/'datasets'/args.tag;dest.mkdir(parents=True,exist_ok=True);rows=[]
for case_id in args.ids:
    ep=cases[case_id];out=dest/case_id;assert not out.exists(),'Preserve prior evidence'
    if ep['split']=='test':
        assert offsets is None and args.checkpoint is not None
        frozen=json.loads((W/'FROZEN_CANDIDATE.json').read_text())
        for path,sha in frozen['hashes'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
        assert frozen['script']==str((W/args.script).resolve()) and frozen['checkpoint']==str(args.checkpoint.resolve())
    settings={**base,'output':str(out),'scene':ep['scene'],'dx':ep['dx'],'dy':ep['dy'],'yaw_deg':ep['yaw_deg'],
              'rest_roll_deg':ep['rest_roll_deg'],'teacher_target':offsets is not None,
              'teacher_along_shift':offsets[ep['family']][str(ep['rest_roll_deg'])]['along_m'] if offsets else 0.,
              'teacher_wrist_yaw_deg':offsets[ep['family']][str(ep['rest_roll_deg'])]['yaw_deg'] if offsets else 0.,
              'close_seconds':12.,'balance_timeout':8.,'lift_seconds':6.,
              'grasp':str(W/'reports/pinch_geometry02.json'),'neutral_start':str(W/'reports/neutral_start.json'),
              'visual_checkpoint':str(args.checkpoint.resolve()) if args.checkpoint else str(W/'policies/handle_vision_v01/best.pt')}
    settings.update(override)
    if ep['split']=='test':
        assert not settings['teacher_target'] and settings['teacher_along_shift']==0.
        assert (str(args.override.resolve()) if args.override else None)==frozen.get('execution_override')
        for key,value in frozen['execution_contract'].items():assert settings.get(key)==value,(key,settings.get(key),value)
    command=[sys.executable,'-u',str(W/args.script)]
    for k,v in settings.items():
        if isinstance(v,bool):
            if v:command.append('--'+k.replace('_','-'))
        elif v is not None:command+=['--'+k.replace('_','-'),str(v)]
    (dest/'progress.json').write_text(json.dumps(dict(current=case_id,completed=rows,total=len(args.ids))))
    start=time.monotonic()
    with (dest/(case_id+'.log')).open('w') as log:
        result=subprocess.run(command,cwd=W,stdout=log,stderr=subprocess.STDOUT,
                              env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
    r=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else {}
    fail=(out/'failure.txt').read_text().splitlines()[-1] if (out/'failure.txt').exists() else None
    row=dict(id=case_id,family=ep['family'],face=ep['rest_roll_deg'],split=ep['split'],success=bool(r.get('success')) and result.returncode==0,teacher=offsets is not None,wall_s=time.monotonic()-start,failure=fail)
    rows.append(row);print(json.dumps(row),flush=True)
    (dest/'progress.json').write_text(json.dumps(dict(current=None,completed=rows,total=len(args.ids)),indent=2))
    if ep['split']=='test' and (sum(not x['success'] for x in rows)>2 or any(t in (fail or '') for t in ['Contact stop','Blade/'])):
        print('Independent gate cannot pass; retained outcomes and stopped this campaign.',flush=True);break
(dest/'results.json').write_text(json.dumps(rows,indent=2))
