from pathlib import Path
import sys,json,numpy as np
from scipy.spatial import ConvexHull
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from model import lattice
m=lattice('tomato');z=np.load('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz');p=z['poly_vertices'];p-=.5*(p.min(0)+p.max(0));hull=ConvexHull(p);V=hull.volume;rest=m['x'][m['edges'][:,1]]-m['x'][m['edges'][:,0]];mu=100000/(2*1.4);lam=100000*.4/(1.4*.2);rows=[]
for kind,amount in [('extension',.01),('extension',.05),('extension',.1),('shear',.01),('shear',.1),('compression',-.02)]:
 F=np.eye(3)
 if kind=='extension':F[0,0]+=amount;F[1,1]-=.4*amount;F[2,2]-=.4*amount
 elif kind=='shear':F[0,1]=amount
 else:F*=1+amount
 current=rest@F.T;length=np.linalg.norm(current,axis=1);f=m['stiffness'][:,None]*(length-m['length'])[:,None]*current/length[:,None];P=f.T@rest/V;J=np.linalg.det(F);reference=mu*(F-np.linalg.inv(F).T)+lam*np.log(J)*np.linalg.inv(F).T
 rows.append({'case':kind,'amount':amount,'approx_P_Pa':P.tolist(),'reference_P_Pa':reference.tolist(),'relative_tensor_difference':float(np.linalg.norm(P-reference)/np.linalg.norm(reference))})
angles=[];edges=np.unique(np.sort(np.r_[hull.simplices[:,[0,1]],hull.simplices[:,[1,2]],hull.simplices[:,[2,0]]],axis=1),axis=0)
for deg in [0,15,30,45,60,75,90]:
 theta=np.deg2rad(deg);normal=np.array([np.cos(theta),0,-np.sin(theta)]);offset=.00175;d=p@normal-offset;cross=d[edges[:,0]]*d[edges[:,1]]<0;es=edges[cross];t=d[es[:,0]]/(d[es[:,0]]-d[es[:,1]]);points=p[es[:,0]]+t[:,None]*(p[es[:,1]]-p[es[:,0]]);basis=np.c_[[0,1,0],[np.sin(theta),0,np.cos(theta)]];area=ConvexHull(points@basis).volume
 d=m['x']@normal-offset;cross=d[m['edges'][:,0]]*d[m['edges'][:,1]]<0;approx=float(m['fracture_area'][cross].sum());angles.append({'angle_deg':deg,'surface_area_m2':float(area),'bond_budget_equivalent_area_m2':approx,'relative_difference':approx/area-1})
out={'description':'Measured model-form differences, NOT validation against physical tomatoes. Same imposed homogeneous deformations compared to v27 compressible neo-Hookean E=100kPa nu=0.4; new network nominal nu=0.25, boundary/discrete effects included. No relaxed tolerance is silently used as calibration.','particles':len(m['x']),'bonds':len(rest),'sphere_union_volume_fraction_relative_reference':float(len(m['x'])*4/3*np.pi*m['radius']**3/V),'reference_bbox_m':np.ptp(p,axis=0).tolist(),'particle_envelope_bbox_m':(np.ptp(m['x'],axis=0)+2*m['radius']).tolist(),'mass_kg':float(m['mass'].sum()),'elastic_response':rows,'fracture_directionality':angles};(W/'reports/reference_differences.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
