from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent
for name in ['cut01','cut02_fine']:
 run=W/'runs'/name;manifest=json.loads((run/'source_manifest.json').read_text());copied={};dest=run/'checked_sources';dest.mkdir(exist_ok=True)
 for path,digest in manifest.items():
  p=Path(path);data=p.read_bytes()
  if name=='cut01' and p.name=='robot_cut.py':
   s=data.decode().replace('contact_hold_steps=0;settle_quiet=0.','contact_hold_steps=0')
   s=s.replace("     if name=='settle':\n      settle_quiet=settle_quiet+25*stepdt if last_info['supported'][0] else 0.\n      if settle_quiet>=.5:break\n",'')
   s=s.replace("    if abs(clock.time-38.86)<stepdt*.1:np.savez_compressed(out/'state_at_38_86.npz',x=g.x.numpy(),v=g.v.numpy(),alive=g.alive.numpy())\n",'')
   s=s.replace("dict(time=20.,q=target[0,right].tolist())","dict(time=1.,q=target[0,right].tolist())")
   s=s.replace("'settling_quiet_requirement_s':.5,'settling_max_s':20.,",'');data=s.encode()
  actual=hashlib.sha256(data).hexdigest();copied[path]=actual==digest
  if actual==digest:
   output=dest/p.relative_to(W);output.parent.mkdir(exist_ok=True,parents=True);output.write_bytes(data)
 (run/'source_archive_check.json').write_text(json.dumps(copied,indent=2));print(name,all(copied.values()),[p for p,v in copied.items()if not v])
