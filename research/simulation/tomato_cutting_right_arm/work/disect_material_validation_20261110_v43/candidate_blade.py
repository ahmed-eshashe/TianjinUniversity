from pathlib import Path
import sys,numpy as np,importlib.util
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_batched_contact_20261110_v39'))
previous_assembly=sys.modules.pop('assembly',None)
spec=importlib.util.spec_from_file_location('assembly',W.parent/'disect_physical_20261109_v22/assembly.py')
baseline_assembly=importlib.util.module_from_spec(spec);sys.modules['assembly']=baseline_assembly;spec.loader.exec_module(baseline_assembly)
from batched_blade import BatchedBlade,torch,tensor
baseline_packet=baseline_assembly.z
if previous_assembly is not None:sys.modules['assembly']=previous_assembly
else:sys.modules.pop('assembly',None)
class CandidateBlade(BatchedBlade):
 def __init__(self):
  super().__init__()
  # Constructor has not stepped. Copy packet before replacing only elastic arrays.
  self.z={k:(v.copy() if isinstance(v,np.ndarray) else v) for k,v in self.z.items()}
  self.z['tet_mu']=np.full(len(self.z['tet_mu']),205128.20512820513,dtype=np.float64)
  self.z['tet_lambda']=np.full(len(self.z['tet_lambda']),358974.35897435894,dtype=np.float64)
  self.mu=tensor(self.z['tet_mu']);self.la=tensor(self.z['tet_lambda'])
  assert torch.equal(self.x,self.x0) and not torch.any(self.v)
