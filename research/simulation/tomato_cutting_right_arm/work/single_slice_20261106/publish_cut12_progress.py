from pathlib import Path
import time,subprocess,sys
w=Path(__file__).parent;r=w.parents[1];p=w/'robot_cut12';last=None
while True:
 status=p/'cutting_status.json'
 if status.exists() and status.stat().st_mtime_ns!=last:
  last=status.stat().st_mtime_ns
  subprocess.run([sys.executable,str(r/'work/integration_20261102/publish_integration_gates.py')],stdout=subprocess.DEVNULL,check=True)
 if (p/'worker_result.json').exists():break
 time.sleep(30)
