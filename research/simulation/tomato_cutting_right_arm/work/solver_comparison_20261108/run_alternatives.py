from pathlib import Path
import time,subprocess,json
w=Path(__file__).resolve().parent
while not (w/'profile_launch.json').exists():time.sleep(5)
with (w/'disect_benchmark.log').open('w') as f:
 p=subprocess.run(['bash',str(w/'run_disect.sh')],stdout=f,stderr=subprocess.STDOUT)
(w/'disect_exit.json').write_text(json.dumps({'returncode':p.returncode}))
