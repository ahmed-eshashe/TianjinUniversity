import fcntl,resource,signal,sys,json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=Path(__file__).resolve().parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
with (R/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);sys.path[:0]=[str(R/'rl'),str(R/'rl/tests')]
 suite=unittest.defaultTestLoader.loadTestsFromName('test_tomato_contact_search');result=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)};(F/'search_tests.json').write_text(json.dumps(report,indent=2)+'\n');sys.exit(not report['passed'])
