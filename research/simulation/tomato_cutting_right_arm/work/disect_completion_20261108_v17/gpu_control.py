import os,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'deps13'));os.environ['CUDA_PATH']=os.environ['CUDA_HOME']
import numpy as np,cupy as cp
from scipy.sparse import diags
from scipy.sparse.linalg import splu
from cupyx.scipy.sparse.linalg._solve import SuperLU
A=diags([-np.ones(999),np.ones(1000)*3,-np.ones(999)],[-1,0,1]).tocsc();f=splu(A);g=SuperLU(f);rhs=np.sin(np.arange(1000));actual=cp.asnumpy(g.solve(cp.asarray(rhs)));error=np.linalg.norm(actual-f.solve(rhs))/np.linalg.norm(f.solve(rhs));assert error<1e-10
Path(__file__).with_name('gpu_control.json').write_text(json.dumps(dict(relative_error=error,passed=True,cupy=cp.__version__)));print(error)
