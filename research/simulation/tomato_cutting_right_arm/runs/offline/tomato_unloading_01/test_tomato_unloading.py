import fcntl,resource,signal,sys,unittest,json
from pathlib import Path
r=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path[:0]=[str(r/'rl'),str(r/'rl/tests')]
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
with (r/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 suite=unittest.TestLoader().loadTestsFromNames(['test_tomato_unloading','test_tomato_blade_damage','test_tomato_surface_cohesion','test_tomato_coupled_contact','test_tomato_volume_protection','test_tomato_contact_reference','test_tomato_offline'])
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
 s={'passed':result.wasSuccessful(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'forbidden_imports':forbidden}
 (r/'runs/offline/tomato_unloading_01/tests.json').write_text(json.dumps(s,indent=2)+'\n');sys.exit(not result.wasSuccessful())
