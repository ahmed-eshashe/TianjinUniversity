from pathlib import Path
import sys
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_normal_contact_20261109_v30'))
from implicit_blade import ImplicitBlade,s,m,closure,torch,tensor
from stable_solver import StableLineSearchBulk

class StableBlade(ImplicitBlade):
    def implicit(self,h,**kw):
        self.contact_step=h
        try:return StableLineSearchBulk.implicit(self,h,**kw)
        finally:self.contact_step=None
