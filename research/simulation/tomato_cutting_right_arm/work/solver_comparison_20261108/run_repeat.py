from pathlib import Path
import time,subprocess,json
w=Path(__file__).resolve().parent
while not (w/'profile2_launch.json').exists():time.sleep(2)
with (w/'disect_repeat.log').open('w') as f:p=subprocess.run(['bash',str(w/'run_disect_repeat.sh')],stdout=f,stderr=subprocess.STDOUT)
(w/'disect_repeat_exit.json').write_text(json.dumps({'returncode':p.returncode}))
