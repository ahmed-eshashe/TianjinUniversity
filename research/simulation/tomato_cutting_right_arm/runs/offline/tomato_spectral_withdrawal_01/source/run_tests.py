"""Serial capped provenance tests, no mechanical simulator."""
import sys,json,resource,signal,fcntl,os,unittest
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
lease=json.loads((R/'runs/offline/tomato_triangle_withdrawal_01/quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480 and lease['maximum_reported_used_percent']<45
handles=[]
for n in ['logs/offline_overnight.lock','logs/right_arm_control.lock']:
 h=(R/n).open('a');fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);handles.append(h)
sys.path.insert(0,str(R/'rl'))
suite=unittest.defaultTestLoader.discover(str(R/'rl/tests'),pattern='test_tomato_withdrawal_provenance.py')
r=unittest.TextTestRunner(verbosity=2).run(suite)
(F/'tests.json').write_text(json.dumps({'passed':r.wasSuccessful(),'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'simulator':False,'training':False},indent=2)+'\n')
assert not any(n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'} for n in sys.modules)
sys.exit(0 if r.wasSuccessful() else 1)
