"""Collect training/validation head images only; never consume test scenes."""
from pathlib import Path
import json,os,subprocess,sys,time
W=Path(__file__).resolve().parent
B=W.parent/'vision_knife_pickup_20261113_v32'
manifest=json.loads((W/'extra_training_curriculum_v02.json').read_text())
base=json.loads((B/'datasets/hybrid_v07_validation/recovery_validation_000/configuration.json').read_text())['args']
for family in ['short','wide','medium']:
    out=W/'head_images_v02'/family
    assert not out.exists(),'Preserve collected images'
    out.parent.mkdir(exist_ok=True)
    scene=next(x['scene'] for x in manifest['episodes'] if x['family']==family)
    settings={**base,'output':str(out),'scene':scene,'capture_family':family,
              'capture_manifest':str(W/'extra_training_curriculum_v02.json'),
              'dx':0.,'dy':0.,'yaw_deg':0.,'rest_roll_deg':0.,'render':False,
              'grasp':str(W/'reports/pinch_geometry02.json'),'neutral_start':str(W/'reports/neutral_start.json')}
    cmd=[sys.executable,'-u',str(W/'collect_head_images_v02.py')]
    for k,v in settings.items():
        if isinstance(v,bool):
            if v:cmd.append('--'+k.replace('_','-'))
        elif v is not None:cmd+=['--'+k.replace('_','-'),str(v)]
    start=time.monotonic()
    with (out.parent/(family+'.log')).open('w') as log:
        p=subprocess.run(cmd,cwd=W,stdout=log,stderr=subprocess.STDOUT,
                         env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
    print(family,'exit',p.returncode,'seconds',time.monotonic()-start,flush=True)
    assert p.returncode==0,'Inspect image collection failure before proceeding'
