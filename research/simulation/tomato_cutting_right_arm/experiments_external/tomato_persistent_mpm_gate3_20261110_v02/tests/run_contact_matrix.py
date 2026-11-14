from pathlib import Path
import subprocess,json,sys,time
W=Path(__file__).resolve().parents[1];cases=[['--half'],['--name','broad'],['--name','broad','--half'],['--name','miss']];out=[]
for args in cases:
 name='_'.join(args).replace('--','');t=time.monotonic()
 with (W/'runs'/f'contact_matrix_{name}.log').open('w') as f:p=subprocess.run([sys.executable,str(W/'tests/contact_coupon.py'),*args],stdout=f,stderr=subprocess.STDOUT,timeout=600,env=None)
 out.append({'args':args,'exit':p.returncode,'wall_s':time.monotonic()-t});(W/'runs/contact_matrix_progress.json').write_text(json.dumps(out,indent=2));print(out[-1],flush=True)
 if p.returncode:break
