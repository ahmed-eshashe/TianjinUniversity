from pathlib import Path
import os,json,time
from tomato_isaac_startup_guard import supervise
r=Path(__file__).resolve().parents[2];out=r/'work/integration_20261102/com_r128_recheck_launcher.json';out.write_text(json.dumps(dict(pid=os.getpid(),pgid=os.getpgrp(),started_unix_s=time.time(),scope='Independent full protected repeat after original outer supervisor exit143. Original4096-step native result retained; its missing uninterrupted supervision is not promoted to a normal guard pass.'),indent=2)+'\n')
d=supervise(r/'runs/native/mounted_target_com_r128_20261102_02',mode='mounted_target_com_r128',wall_s=3600)
print(json.dumps(d,indent=2),flush=True)
