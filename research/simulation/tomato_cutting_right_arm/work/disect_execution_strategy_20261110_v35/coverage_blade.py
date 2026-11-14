from pathlib import Path
import sys,json
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_contact_linesearch_20261109_v32'))
sys.path.insert(0,str(W.parent/'disect_cut_edge_coverage_20261110_v34'))
from stable_blade import StableBlade,s,m,closure,torch,tensor
from complete_edges import CompleteCutEdges
class CoverageBlade(StableBlade):
 def __init__(self):
  assert json.loads((W.parent/'disect_cut_edge_coverage_20261110_v34/controls_result.json').read_text())['passed']
  super().__init__();self.adaptive=CompleteCutEdges(m)
