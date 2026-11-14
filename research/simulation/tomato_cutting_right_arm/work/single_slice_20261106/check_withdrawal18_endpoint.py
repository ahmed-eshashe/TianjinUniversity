"""Bounded endpoint geometry check; does not launch further motion."""
from pathlib import Path
import time,json,subprocess,sys
w=Path(__file__).resolve().parent;r=w.parents[1];endpoint=w/'robot_cut18/endpoint_review.json';deadline=time.monotonic()+86530
while not endpoint.exists():
 if time.monotonic()>deadline:raise SystemExit('Endpoint review unavailable before deadline')
 time.sleep(10)
info=json.loads(endpoint.read_text());cp=Path(info['checkpoint']);cp=cp if cp.is_absolute() else r/cp
subprocess.run([sys.executable,str(w/'assess_withdrawal_gate.py'),str(cp)],cwd=r,check=True)
