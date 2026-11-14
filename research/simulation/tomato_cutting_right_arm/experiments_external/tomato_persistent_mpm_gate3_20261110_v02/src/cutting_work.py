"""Transactional ideal cutting work. New model; no old cohesive-law qualification."""
from dataclasses import dataclass
import copy,json,hashlib
import numpy as np
from shapely.geometry import Polygon,box
from shapely import from_wkb,to_wkb
@dataclass(frozen=True)
class Trial:
 epoch:int
 step_id:int
 novel_wkb:bytes
 area:float
 required_work:float
 advancing:bool

class CutLedger:
 def __init__(self,patch_bounds,Gc=80.):
  self.domain=box(*patch_bounds);self.covered=Polygon();self.Gc=float(Gc);self.fracture_work=0.;self.epoch=0;self.last_step=-1
 def trial(self,step_id,edge_old,edge_new,contact_kind,contact_active):
  old=np.asarray(edge_old,float);new=np.asarray(edge_new,float)
  if old.shape!=(2,2) or new.shape!=(2,2):raise ValueError('finite two-endpoint reference edge required')
  advance=float(np.mean(new[:,1]-old[:,1]));eligible=contact_kind=='edge' and contact_active and advance>1e-15
  region=Polygon([old[0],old[1],new[1],new[0]]) if eligible else Polygon()
  if eligible and not region.is_valid:raise ValueError('crossed or rotating sweep outside initial envelope')
  novel=region.intersection(self.domain).difference(self.covered) if eligible else Polygon();area=float(novel.area)
  return Trial(self.epoch,int(step_id),to_wkb(novel),area,self.Gc*area,eligible)
 def force(self,trial,relative_displacement,material_map=np.eye(3)):
  # Work-conjugate force for a finite reference advance. Zero new area = no charge.
  ds=float(relative_displacement)
  if trial.area==0:return np.zeros(3)
  if ds<=0:raise ValueError('positive relative advance required')
  # The canonical reference advance direction is +y. Map traction by F^-T.
  return trial.required_work/ds*np.linalg.solve(np.asarray(material_map).T,[0.,1.,0.])
 def commit(self,trial,measured_work,accepted):
  if not accepted:return False
  if trial.epoch!=self.epoch or trial.step_id<=self.last_step:raise ValueError('stale or duplicate commit')
  if not np.isfinite(measured_work) or measured_work<-1e-12:raise ValueError('invalid work')
  if measured_work+1e-12<trial.required_work:raise ValueError('unpaid new fracture area')
  self.covered=self.covered.union(from_wkb(trial.novel_wkb));self.fracture_work+=trial.required_work;self.last_step=trial.step_id;self.epoch+=1
  return True
 def state(self):return {'covered_wkb':to_wkb(self.covered).hex(),'Gc':self.Gc,'work_J':self.fracture_work,'area_m2':float(self.covered.area),'epoch':self.epoch,'last_step':self.last_step,'domain_wkb':to_wkb(self.domain).hex()}
 @classmethod
 def restore(cls,s):
  a=cls(from_wkb(bytes.fromhex(s['domain_wkb'])).bounds,s['Gc']);a.covered=from_wkb(bytes.fromhex(s['covered_wkb']));a.fracture_work=s['work_J'];a.epoch=s['epoch'];a.last_step=s['last_step'];return a
 def fingerprint(self):return hashlib.sha256(json.dumps(self.state(),sort_keys=True).encode()).hexdigest()
