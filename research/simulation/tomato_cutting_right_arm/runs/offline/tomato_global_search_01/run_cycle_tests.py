import resource,signal,sys,fcntl,json,unittest,time
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
assert datetime.now(timezone.utc)<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
sys.path[:0]=[str(R/'rl'),str(R/'rl/tests')];start=time.monotonic()
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_tomato_optimizer_cycle'))
from tomato_optimizer_cycle import restart_fingerprint
replays={}
for name in ['insertion08_refined','insertion04_predicted','insertion07_refined']:
 fingerprints=[restart_fingerprint(json.loads(p.read_text())) for p in sorted((R/'runs/offline/tomato_curvature_search_01'/name).glob('attempt*/candidate.json'))]
 replays[name]={'candidates':len(fingerprints),'consecutive_identical_restart_states':sum(a==b for a,b in zip(fingerprints,fingerprints[1:]))}
assert replays['insertion08_refined']['consecutive_identical_restart_states']==9
assert all(replays[n]['consecutive_identical_restart_states']==0 for n in ['insertion04_predicted','insertion07_refined'])
report={'passed':result.wasSuccessful(),'tests':result.testsRun,'replays':replays,'runtime_s':time.monotonic()-start,'simulator':False,'training':False}
(F/'cycle_tests.json').write_text(json.dumps(report,indent=2)+'\n');print(report);sys.exit(not result.wasSuccessful())
