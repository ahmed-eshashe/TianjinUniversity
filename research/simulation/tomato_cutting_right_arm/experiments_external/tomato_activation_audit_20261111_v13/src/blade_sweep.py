"""Motion-selected geometric topology. No contact or physical fracture law."""
from pathlib import Path
import copy,hashlib,json,time
import numpy as np
from integrated_cut import greville,RejectedEvent
from multicut import MultiCut
from rectangle_union import union_area

W=Path(__file__).resolve().parents[1]

class Blade:
    def __init__(self):
        raw=(W/'assets/blade_export.json').read_bytes();d=json.loads(raw)
        self.vertices=np.asarray(d['vertices']);self.faces=np.asarray(d['triangles']);self.sha256=hashlib.sha256(raw).hexdigest()
        a=self.vertices[[14,15]].mean(0);b=self.vertices[[16,17]].mean(0)
        self.origin=(a+b)*.5;e=(b-a)/np.linalg.norm(b-a);inward=np.array([0.,1.,0.]);inward-=e*np.dot(e,inward);inward/=np.linalg.norm(inward)
        self.frame=np.stack([e,inward,np.cross(e,inward)],axis=1)
        self.edge=(np.stack([a,b])-self.origin)@self.frame
        self.local_vertices=(self.vertices-self.origin)@self.frame
    def points(self,pose,whole=False):
        return (self.local_vertices if whole else self.edge)@pose[:3,:3].T+pose[:3,3]

def pose(translation,rotation=None):
    out=np.eye(4);out[:3,3]=translation
    out[:3,:3]=np.array([[0,0,-1],[0,1,0],[1,0,0]]) if rotation is None else rotation
    return out

def validate_pose(p):
    p=np.asarray(p,float)
    if p.shape!=(4,4) or not np.isfinite(p).all() or np.max(abs(p[3]-[0,0,0,1]))>1e-12 or np.max(abs(p[:3,:3].T@p[:3,:3]-np.eye(3)))>1e-9 or abs(np.linalg.det(p[:3,:3])-1)>1e-9:raise RejectedEvent('invalid rigid blade pose')
    return p.copy()

def material_map(p):
    X=greville(p.knots);q=p.T@p.q;design=np.c_[X,np.ones(len(X))]
    coef=np.linalg.lstsq(design,q,rcond=None)[0];res=float(np.linalg.norm(design@coef-q,axis=1).max())
    if res>1e-11:raise RejectedEvent('non-affine inverse map is outside this component scope',{'coefficient_residual_m':res})
    F=coef[:3].T;t=coef[3]
    if np.linalg.det(F)<=.1:raise RejectedEvent('invalid affine material map')
    return {'F':F,'t':t,'residual':res}

def reference(points,m):return (points-m['t'])@np.linalg.inv(m['F']).T

def shadow(s):
    out=copy.copy(s);out.pieces=s.pieces.copy();out.events=copy.deepcopy(s.events)
    out.archived_support_impulse=s.archived_support_impulse.copy();out.archived_support_moment=s.archived_support_moment.copy()
    return out


class SweepDriver:
    def __init__(self,cpu,initial_pose):
        self.cpu=cpu;self.blade=Blade();self.pose=validate_pose(initial_pose)
        self.maps={key:material_map(p) for key,p in cpu.pieces.items()}
        self.histories={};self.commands=[];self.epoch=0

    def fingerprint(self):
        h=hashlib.sha256();h.update(self.cpu.fingerprint().encode());h.update(self.pose.tobytes());h.update(json.dumps(self.histories,sort_keys=True).encode());h.update(str(self.epoch).encode())
        for key,m in self.maps.items():h.update(key.encode());h.update(m['F'].tobytes());h.update(m['t'].tobytes())
        return h.hexdigest()

    def propose(self,new_pose):
        new_pose=validate_pose(new_pose);token=self.fingerprint();trial=shadow(self.cpu);hist=copy.deepcopy(self.histories);changes=[];new_area=0.;start=time.perf_counter()
        edge0=self.blade.points(self.pose);edge1=self.blade.points(new_pose)
        maps={key:material_map(p) for key,p in self.cpu.pieces.items()}
        for key,p in self.cpu.pieces.items():
            m0,m1=self.maps[key],maps[key];a=reference(edge0,m0);b=reference(edge1,m1);points=np.concatenate([a,b]);lo=np.array([t[0] for t in p.knots]);hi=np.array([t[-1] for t in p.knots])
            # Bounding box is only an early no-intersection test, never a cut footprint.
            if np.any(points.max(0)<lo-1e-10) or np.any(points.min(0)>hi+1e-10):continue
            if np.max(abs(m1['F']-m0['F']))>1e-9:raise RejectedEvent('changing material gradient during the action is unsupported')
            if np.max(abs(new_pose[:3,:3]-self.pose[:3,:3]))>1e-10:raise RejectedEvent('rotating blade during an intersecting action is unsupported')
            e=a[1]-a[0]
            if np.max(abs((b[1]-b[0])-e))>1e-10:raise RejectedEvent('edge changes shape in material frame')
            along=int(np.argmax(abs(e)));off=e.copy();off[along]=0.
            if np.max(abs(off))>1e-10:raise RejectedEvent('oblique material-space edge unsupported')
            delta=b.mean(0)-a.mean(0);advance=delta.copy();advance[along]=0.
            if np.max(abs(advance))<=1e-10:continue  # Hold or slide along edge has zero new area.
            move=int(np.argmax(abs(advance)));other=[i for i in range(3) if i not in [along,move]][0]
            if abs(delta[along])>1e-10 or abs(delta[other])>1e-10:raise RejectedEvent('nonrectangular sweep unsupported')
            inward=np.linalg.solve(m1['F'],new_pose[:3,1]);expected_move=int(np.argmax(abs(inward)))
            transverse=inward.copy();transverse[expected_move]=0.
            if expected_move!=move or np.max(abs(transverse))>1e-9:raise RejectedEvent('sideways or oblique edge motion is not eligible cutting advance')
            if delta[move]*inward[move]>=-1e-12:continue  # Withdrawal does not create new area.
            if abs(delta[move])>.0011:raise RejectedEvent('normal sweep exceeds the declared per-action distance')
            if np.ptp(points[:,other])>1e-10:raise RejectedEvent('nonplanar sweep unsupported')
            plane=float(points[:,other].mean())
            if plane<=lo[other]+1e-10 or plane>=hi[other]-1e-10:continue
            tangents=[i for i in range(3) if i!=other]
            rect=[v for axis in tangents for v in (max(lo[axis],points[:,axis].min()),min(hi[axis],points[:,axis].max()))]
            if rect[1]-rect[0]<=1e-12 or rect[3]-rect[2]<=1e-12:continue
            record=hist.get(key)
            if record is None:
                if len(hist)>=4:raise RejectedEvent('four motion-created cut histories exhausted')
                record={'axis':other,'plane':plane,'rectangles':[]};hist[key]=record
            elif record['axis']!=other or abs(record['plane']-plane)>1e-10:raise RejectedEvent('second partial plane in connected material is unsupported')
            rectangles=record['rectangles']+[list(map(float,rect))];area=union_area(rectangles)-union_area(record['rectangles'])
            if area<=1e-18:continue
            record['rectangles']=rectangles;new_area+=area
            proposal=trial.propose(key,other,record['plane'],rectangles)
            if not proposal['noop']:
                trial.commit(proposal);changes.append({'piece':key,'complete':proposal['children'] is not None,'transfer':proposal['insertion'],'partition':proposal['partition']})
        command={'from_pose':self.pose.tolist(),'to_pose':new_pose.tolist(),'new_reference_area_m2':new_area,'changes':changes,'fixture_only':True,'paid_fracture_area_m2':0.,'kind':'CAD-edge-motion geometry, not physical failure'}
        return {'fingerprint':token,'cpu':trial,'histories':hist,'pose':new_pose,'command':command,'topology_changed':bool(changes),'construction_s':time.perf_counter()-start,'maps':{key:material_map(p) for key,p in trial.pieces.items()}}

    def commit(self,p):
        if p['fingerprint']!=self.fingerprint():raise RejectedEvent('stale blade-motion proposal')
        self.cpu=p['cpu'];self.histories=p['histories'];self.pose=p['pose'];self.maps=p['maps'];self.commands.append(p['command']);self.epoch+=1
        return p['topology_changed']

    def save(self,stem):
        stem=Path(stem);self.cpu.save(stem.with_suffix('.npz'));raw=stem.with_suffix('.npz').read_bytes()
        meta={'schema':1,'blade_sha256':self.blade.sha256,'state_sha256':hashlib.sha256(raw).hexdigest(),'pose':self.pose.tolist(),'histories':self.histories,'commands':self.commands,'epoch':self.epoch,'maps':{key:{'F':m['F'].tolist(),'t':m['t'].tolist(),'residual':m['residual']} for key,m in self.maps.items()}}
        stem.with_suffix('.json').write_text(json.dumps(meta,indent=2,allow_nan=False))

    @classmethod
    def restore(cls,stem):
        stem=Path(stem);meta=json.loads(stem.with_suffix('.json').read_text());raw=stem.with_suffix('.npz').read_bytes()
        if meta['schema']!=1 or hashlib.sha256(raw).hexdigest()!=meta['state_sha256']:raise ValueError('sweep checkpoint mismatch')
        out=cls.__new__(cls);out.cpu=MultiCut.restore(stem.with_suffix('.npz'));out.blade=Blade()
        if out.blade.sha256!=meta['blade_sha256']:raise ValueError('blade asset mismatch')
        out.pose=validate_pose(meta['pose']);out.histories=meta['histories'];out.commands=meta['commands'];out.epoch=meta['epoch'];out.maps={key:{'F':np.asarray(m['F']),'t':np.asarray(m['t']),'residual':m['residual']} for key,m in meta['maps'].items()}
        if list(out.maps)!=list(out.cpu.pieces) or len(out.histories)>4 or len(out.commands)!=out.epoch:raise ValueError('sweep checkpoint history mismatch')
        return out

    def whole_blade_clear(self):
        vertices=self.blade.points(self.pose,whole=True)
        boxes=[]
        for p in self.cpu.pieces.values():
            coefs=p.T@p.q
            clearance=np.maximum(vertices.min(0)-coefs.max(0),coefs.min(0)-vertices.max(0))
            boxes.append(float(clearance.max()))
        return {'clear':all(x>1e-10 for x in boxes),'AABB_separation_margin_m':boxes,'scope':'Sufficient full-CAD-vs-material-convex-hull clearance, not a contact/penetration test'}
