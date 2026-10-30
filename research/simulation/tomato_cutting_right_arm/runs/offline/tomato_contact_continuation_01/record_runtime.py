"""Read installed package metadata only; no simulator or numerical imports."""
import sys,platform,json,os,resource,signal,fcntl
from pathlib import Path
from importlib.metadata import version
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
r=Path(__file__).resolve().parents[3];f=Path(__file__).resolve().parent
with (r/'logs/right_arm_control.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 report={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'packages':{n:version(n) for n in ['numpy','scipy','osqp']},'thread_environment':{n:os.environ.get(n) for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},'simulator_or_training_modules':[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}]}
 assert not report['simulator_or_training_modules']
 (f/'runtime_versions.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
