from pathlib import Path
import json,hashlib
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
from tomato_host_blade_geometry import query_mesh
R=Path(__file__).resolve().parents[2];out=R/'runs/offline/host_blade_query_20261102_01';out.mkdir(exist_ok=False);(out/'input_manifest.json').write_text(json.dumps(dict(scope='Independent host distance/sign/normal arithmetic on analytically known rigid boxes only; no native CAD query, robot or cutting gate.',distance_budget_m=1e-12,normal_budget=1e-10,closest_budget_m=1e-12),indent=2)+'\n');v=np.array([[x,y,z]for x in [-.1,.1]for y in [-.2,.2]for z in [-.3,.3]]);faces=ConvexHull(v).simplices.copy()
for face in faces:
 tri=v[face]
 if np.cross(tri[1]-tri[0],tri[2]-tri[0])@tri.mean(0)<0:face[1],face[2]=face[2],face[1]
points=np.array([[.01,.02,.03],[.12,.02,.03],[.12,.25,.03],[.12,.25,.4],[-.13,-.02,-.03]]);closest=np.clip(points,[-.1,-.2,-.3],[.1,.2,.3]);closest[0,0]=.1;delta=points-closest;distance=np.linalg.norm(delta,axis=1);sign=np.array([-1,1,1,1,1]);phi=sign*distance;normal=sign[:,None]*delta/distance[:,None];cases=[]
for label,rot,trans in [('reference',np.eye(3),np.zeros(3)),('rigid_pose',Rotation.from_rotvec([.4,-.2,.7]).as_matrix(),np.array([.4,-.2,.3]))]:
 q=query_mesh(v@rot.T+trans,faces,points@rot.T+trans);de=float(abs(q['phi']-phi).max());ne=float(abs(q['normal']-normal@rot.T).max());ce=float(abs(q['closest']-(closest@rot.T+trans)).max());cases.append(dict(case=label,points=5,distance_error_m=de,normal_error=ne,closest_error_m=ce))
 if de>1e-12 or ne>1e-10 or ce>1e-12:raise ValueError(cases[-1])
report=dict(passed=True,cases=cases,scope='Ten analytic box queries covering inside, face, edge, corner and rigid transforms. Host arithmetic controls only, not general CAD, generated pressure, actual robot or physical contact qualification.',source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'rl/tomato_host_blade_geometry.py']});(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
