import resource,signal,sys,fcntl,json,unittest
from pathlib import Path
r=Path(__file__).resolve().parents[3];f=Path(__file__).resolve().parent
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
with (r/'logs/right_arm_control.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    sys.path[:0]=[str(r/'rl'),str(r/'rl/tests')]
    names=['test_tomato_contact_search','test_tomato_contact_continuation','test_tomato_triangle_contact','test_tomato_full_cut_checks','test_tomato_unloading','test_tomato_blade_damage','test_tomato_contact_reference','test_tomato_coupled_contact','test_tomato_offline','test_tomato_surface_cohesion','test_tomato_volume_protection']
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in names)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]
    report={'passed':result.wasSuccessful() and not forbidden,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'forbidden_imports':forbidden}
    (f/'tests.json').write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(not report['passed'])
