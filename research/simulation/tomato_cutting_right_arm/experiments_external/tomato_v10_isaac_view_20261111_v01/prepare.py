"""Read-only tessellation of frozen v10 checkpoints; never advance mechanics."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from scipy.interpolate import BSpline
W=Path(__file__).parent
B=W.parent/'tomato_blade_sweep_20261111_v10'
sys.path.insert(0,str(B/'src'))
from blade_sweep import SweepDriver
frozen=json.loads((B/'artifact_hashes.json').read_text())['sha256']
def verify():
    bad=[n for n,h in frozen.items() if hashlib.sha256((B/n).read_bytes()).hexdigest()!=h]
    assert not bad,bad
verify()
plane=.0003
def geometry(side):
    bounds=[[-.006,plane] if side=='left' else [plane,.006],[-.006,.006],[-.006,.006]]
    points=[];faces=[];interior=[];n=17
    for axis in range(3):
        for end in [0,1]:
            other=[i for i in range(3) if i!=axis]
            aa,bb=np.meshgrid(*[np.linspace(*bounds[j],n) for j in other],indexing='ij')
            p=np.empty((n*n,3));p[:,axis]=bounds[axis][end];p[:,other[0]]=aa.ravel();p[:,other[1]]=bb.ravel();off=len(points);points.extend(p)
            inside=axis==0 and ((side=='left' and end==1) or (side=='right' and end==0))
            for i in range(n-1):
                for j in range(n-1):
                    k=off+i*n+j; target=interior if inside else faces
                    target.extend([[k,k+n,k+1],[k+1,k+n,k+n+1]])
    return np.array(points),np.array(faces,np.int32),np.array(interior,np.int32)
def tensor_eval(knots,q,X):
    X=X.copy()
    for i,t in enumerate(knots):X[:,i]=np.clip(X[:,i],t[0],t[-1])
    vals=[BSpline(t,np.eye(len(t)-3),2)(X[:,i]) for i,t in enumerate(knots)]
    N=np.einsum('pi,pj,pk->pijk',*vals).reshape(len(X),-1)
    return N@q
def field(d,side):
    if len(d.cpu.pieces)==2:
        p=d.cpu.pieces['rootL' if side=='left' else 'rootR'];return p.knots,p.q
    p=d.cpu.pieces['root']
    if p.plane is None:return p.knots,p.q
    assert p.axis==0 and abs(p.plane-plane)<1e-10
    knots=list(p.knots);t=knots[0];actual=p.plane;left=np.r_[t[t<actual],np.repeat(actual,3)];right=np.r_[np.repeat(actual,3),t[t>actual]]
    Q=(p.T@p.q).reshape(*p.plane_data['dims'],3);n=len(left)-3
    knots[0]=left if side=='left' else right
    return knots,(Q[:n] if side=='left' else Q[n:]).reshape(-1,3)
names=[f'primary_frame{i}' for i in range(1,15)]+['primary_withdrawn','primary_opened']
geom={s:geometry(s) for s in ['left','right']}; saved={};meta=[];points={s:[] for s in geom};blades=[];edges=[]
for name in names:
    d=SweepDriver.restore(B/'runs/gpu_motion'/name)
    for side,(X,_,__) in geom.items():
        knots,q=field(d,side);points[side].append(tensor_eval(knots,q,X))
    blades.append(d.blade.points(d.pose,whole=True));edges.append(d.blade.points(d.pose))
    meta.append({'checkpoint':name,'material_time_s':d.cpu.time,'pieces':len(d.cpu.pieces),'cut_count':d.cpu.cut_count,'topology_events':len(d.cpu.events)})
    print(name,meta[-1],flush=True)
for side in geom:
    saved[side+'_points']=np.array(points[side]);saved[side+'_faces']=geom[side][1];saved[side+'_inside']=geom[side][2]
saved['blade_points']=np.array(blades);saved['blade_faces']=d.blade.faces;saved['edge_points']=np.array(edges)
np.savez_compressed(W/'surfaces.npz',**saved)
gap=float(saved['right_points'][-1,:,0].min()-saved['left_points'][-1,:,0].max())
assert gap>.0002
verify()
result={'source':str(B),'verified_source_hashes':len(frozen),'frames':meta,'surface_gap_m':gap,'source_preserved':True,'mechanics_advanced':False,'display':'Continuous basis evaluated at tessellated outer/cut faces. Actual spatial scale. Saved endpoints only; playback interpolation is display-only.','limits':'Geometry-only block cutting. Knife wireframe is original CAD. Horizontal withdrawal is an unsimulated pose query. Opening is auxiliary material loads, not knife fracture.'}
(W/'capture_result.json').write_text(json.dumps(result,indent=2)+'\n')
print('READY',gap)
