import copy,hashlib,json
from pathlib import Path
import numpy as np
from blade_sweep import Blade,validate_pose,shadow
from front_system import FrontSystem
from planar_chart import certified_rectangle
from integrated_cut import RejectedEvent
from rectangle_union import union_area

def field_snapshot(cpu):
    out={}
    for key,p in cpu.pieces.items():
        old=copy.copy(p);old.q=p.q.copy();old.vg=p.vg.copy();out[key]=old
    return out

class DeformedSweep:
    def __init__(self,cpu,initial_pose):
        self.cpu=cpu;self.pose=validate_pose(initial_pose);self.blade=Blade();self.previous=field_snapshot(cpu)
        self.histories={};self.commands=[];self.epoch=0
    def fingerprint(self):
        h=hashlib.sha256(self.cpu.fingerprint().encode());h.update(self.pose.tobytes());h.update(json.dumps(self.histories,sort_keys=True).encode());h.update(str(self.epoch).encode())
        for key,p in self.previous.items():h.update(key.encode());h.update(p.q.tobytes())
        return h.hexdigest()
    def propose(self,new_pose):
        new_pose=validate_pose(new_pose);trial=shadow(self.cpu);hist=copy.deepcopy(self.histories);changes=[];area=0.;charts=[]
        for key,p in self.cpu.pieces.items():
            if key not in self.previous:raise RejectedEvent('uncommitted topology replacement')
            c=certified_rectangle(self.previous[key],p,self.blade,self.pose,new_pose)
            if c is None:continue
            rec=hist.get(key)
            if rec is None:
                if len(hist)>=4:raise RejectedEvent('four cut histories exhausted')
                rec={'axis':c['axis'],'plane':c['plane'],'rectangles':[]};hist[key]=rec
            elif rec['axis']!=c['axis'] or abs(rec['plane']-c['plane'])>1e-10:raise RejectedEvent('second partial plane in connected material')
            rectangles=rec['rectangles']+[c['rectangle']];delta=union_area(rectangles)-union_area(rec['rectangles'])
            if delta<=1e-18:continue
            rec['rectangles']=rectangles;area+=delta;charts.append(c)
            proposal=trial.propose(key,rec['axis'],rec['plane'],rectangles);trial.commit(proposal)
            changes.append({'piece':key,'complete':proposal['children'] is not None,'transfer':proposal['insertion'],'partition':proposal['partition'],'basis_sizes':{k:len(v.q) for k,v in trial.pieces.items()}})
        command={'from_pose':self.pose.tolist(),'to_pose':new_pose.tolist(),'new_reference_area_m2':area,'changes':changes,'charts':charts,'fixture_only':True,'paid_fracture_area_m2':0.,'kind':'non-affine certified planar geometric sweep; not physical fracture'}
        return {'fingerprint':self.fingerprint(),'cpu':trial,'histories':hist,'pose':new_pose,'command':command,'topology_changed':bool(changes)}
    def commit(self,p):
        if p['fingerprint']!=self.fingerprint():raise RejectedEvent('stale deformed sweep proposal')
        self.cpu=p['cpu'];self.histories=p['histories'];self.pose=p['pose'];self.previous=field_snapshot(self.cpu);self.commands.append(p['command']);self.epoch+=1
        return p['topology_changed']
    def save(self,stem):
        stem=Path(stem)
        if any(np.max(abs(p.q-self.previous[k].q))>0 for k,p in self.cpu.pieces.items()):raise RejectedEvent('save after an accepted action, not midtrial')
        self.cpu.save(stem.with_suffix('.npz'))
        meta={'schema':11,'blade_sha256':self.blade.sha256,'state_sha256':hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),'pose':self.pose.tolist(),'histories':self.histories,'commands':self.commands,'epoch':self.epoch}
        stem.with_suffix('.json').write_text(json.dumps(meta,indent=2,allow_nan=False))
    @classmethod
    def restore(cls,stem):
        stem=Path(stem);m=json.loads(stem.with_suffix('.json').read_text())
        if m['schema']!=11 or hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest()!=m['state_sha256']:raise ValueError('checkpoint hash/schema mismatch')
        out=cls(FrontSystem.restore(stem.with_suffix('.npz')),m['pose'])
        if out.blade.sha256!=m['blade_sha256']:raise ValueError('blade hash mismatch')
        out.histories=m['histories'];out.commands=m['commands'];out.epoch=m['epoch'];return out
