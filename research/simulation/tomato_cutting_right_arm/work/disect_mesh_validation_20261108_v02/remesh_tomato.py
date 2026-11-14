from pathlib import Path
import sys,json,time
import numpy as np
from scipy.spatial import cKDTree,ConvexHull
w=Path(__file__).resolve().parent;sys.path.insert(0,str(w/'mesh_deps'));import tetgen
z=np.load(w/'proposed_exterior_input.npz');x=z['vertices'];faces=z['triangles'];fixed=z['fixture_coordinates'];used=np.unique(faces);points=x[used];lookup={int(i):j for j,i in enumerate(used)};f=np.array([[lookup[int(i)] for i in row] for row in faces],dtype=np.int32)
for p in fixed:
 if np.linalg.norm(points-p,axis=1).min()>1e-12:points=np.vstack([points,p])
start=time.perf_counter();mesh=tetgen.TetGen(points,f);ret=mesh.tetrahedralize(order=1,minratio=1.6,mindihedral=5,nobisect=True,maxvolume=1e-8,fixedvolume=True,steinerleft=10000,quiet=False);nodes=np.asarray(ret[0]);t=np.asarray(ret[1]);vol=np.linalg.det(nodes[t[:,1:]]-nodes[t[:,0]][:,None])/6;neg=vol<0;t[neg,0],t[neg,1]=t[neg,1].copy(),t[neg,0].copy();vol=abs(vol);elapsed=time.perf_counter()-start
ff=np.sort(np.concatenate([t[:,[0,1,2]],t[:,[0,1,3]],t[:,[0,2,3]],t[:,[1,2,3]]]),axis=1);uf,n=np.unique(ff,axis=0,return_counts=True);boundary=uf[n==1];bf=nodes[boundary];hull=ConvexHull(x);outer=np.zeros(len(boundary),bool)
for a in range(0,len(hull.equations),128):
 eq=hull.equations[a:a+128];outer|=np.any(np.max(abs(bf@eq[:,:3].T+eq[:,3]),axis=1)<1e-10,axis=1)
fd,fi=cKDTree(nodes).query(fixed);sourcev=json.loads((w/'exterior_input_audit.json').read_text())['signed_enclosed_volume_m3'];mass=float(np.load(w/'source_tomato.npz')['mass'].sum());rho=mass/vol.sum();lump=np.zeros(len(nodes));np.add.at(lump,t.ravel(),np.repeat(vol*rho/4,4));ql=nodes[t];maxedge=np.linalg.norm(ql[:,:,None]-ql[:,None,:],axis=-1).max(axis=(1,2));quality=6*vol/maxedge**3
record={'method':'TetGen constrained PLC, same 4608 exterior faces, quality 1.6/5deg, no boundary bisection, maxvol 1e-8 m3, original 25 support coordinates included','tetgen_version':tetgen.__version__,'wall_s':elapsed,'nodes':len(nodes),'tetrahedra':len(t),'positive_volumes':bool((vol>0).all()),'minimum_volume_m3':float(vol.min()),'volume_m3':float(vol.sum()),'source_volume_m3':sourcev,'volume_relative_error':float(vol.sum()/sourcev-1),'unpaired_interior_faces':int((~outer).sum()),'nonmanifold_faces':int((n>2).sum()),'exterior_faces':len(boundary),'support_max_coordinate_error_m':float(fd.max()),'support_nodes':fi.tolist(),'minimum_mass_kg':float(lump.min()),'mass_kg':float(lump.sum()),'density_kg_m3':float(rho),'minimum_6V_over_maxedge_cubed':float(quality.min()),'qualified':bool((vol>0).all() and not (~outer).any() and np.all(n<=2) and fd.max()<1e-12 and abs(vol.sum()/sourcev-1)<1e-9 and (lump>0).all() and len(t)<=50000)}
np.savez(w/'tomato_fem_mesh.npz',x=nodes,tets=t,mass=lump,fixed=fi,source_support_coordinates=fixed,volume=vol,boundary=boundary)
(w/'tomato_remesh_result.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
