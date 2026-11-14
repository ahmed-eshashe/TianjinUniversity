from pathlib import Path
import subprocess,sys,json,time
W=Path(__file__).resolve().parents[1];out=[]
for args in [[],['--half'],['--name','broad'],['--name','broad','--half']]:
 name='_'.join(args).replace('--','') or 'edge';start=time.monotonic()
 with (W/'runs'/f'clock_{name}.log').open('w') as f:p=subprocess.run([sys.executable,str(W/'tests/contact_coupon.py'),*args],stdout=f,stderr=subprocess.STDOUT,timeout=600)
 out.append({'args':args,'exit':p.returncode,'wall_s':time.monotonic()-start});(W/'runs/contact_clock_progress.json').write_text(json.dumps(out,indent=2));print(out[-1],flush=True)
 if p.returncode:break
