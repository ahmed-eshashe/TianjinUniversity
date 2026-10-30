import os,sys,fcntl,resource,signal,json,time,unittest
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3]
assert datetime.now(timezone.utc)<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:assert os.environ[n]=='1'
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
start=time.monotonic();sys.path[:0]=[str(R/'rl'),str(R/'rl/tests')]
names=['test_tomato_contact_global_search','test_tomato_contact_spectral_search','test_tomato_contact_search','test_tomato_contact_continuation','test_tomato_triangle_contact','test_tomato_full_cut_checks','test_tomato_unloading','test_tomato_blade_damage','test_tomato_contact_reference','test_tomato_coupled_contact','test_tomato_offline','test_tomato_surface_cohesion','test_tomato_volume_protection']
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in names)
result=unittest.TextTestRunner(verbosity=2).run(suite)
assert not any(n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'} for n in sys.modules)
report={'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'runtime_s':time.monotonic()-start,'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'simulation':False,'training':False}
(Path(__file__).parent/'tests.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
sys.exit(not result.wasSuccessful())
