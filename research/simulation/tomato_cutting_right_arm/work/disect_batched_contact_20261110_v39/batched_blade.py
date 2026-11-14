from pathlib import Path
import sys
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_execution_strategy_20261110_v35'))
sys.path.insert(0,str(W.parent/'disect_precision_sign_20261110_v38'))
from coverage_blade import CoverageBlade,s,m,closure,torch,tensor
from batched_contact import BatchedContact
class BatchedBlade(CoverageBlade):
 def __init__(self):
  super().__init__();self.adaptive=BatchedContact(m)
