from pathlib import Path
import json,time,numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
W=Path(__file__).resolve().parent;data=W.parent/'disect_mesh_validation_20261108_v02';z=np.load(data/'tomato_fem_mesh.npz');raw=z['x'];x=raw[:,[0,2,1]].copy();x[:,1]+=.002;x[:,2]*=-1;source_tets=z['tets'];plane=-.0225;eps=1e-12;X=list(x);crossings={};new_tets=[];sides=[];parents=[];start=time.perf_counter()
def intersection(a,b):
    if abs(X[a][0]-plane)<=eps:return a
    if abs(X[b][0]-plane)<=eps:return b
    key=tuple(sorted((a,b)))
    if key not in crossings:
        aa=np.asarray(X[a]);bb=np.asarray(X[b]);q=aa+(plane-aa[0])/(bb[0]-aa[0])*(bb-aa);q[0]=plane;crossings[key]=len(X);X.append(q)
    return crossings[key]
def clip(face,sign):
    result=[]
    for a,b in zip(face,face[1:]+face[:1]):
        ia=sign*(X[a][0]-plane)>=-eps;ib=sign*(X[b][0]-plane)>=-eps
        if ia:result.append(a)
        if ia!=ib:result.append(intersection(a,b))
    seen=set();return [a for a in result if not(a in seen or seen.add(a))]
def triangulate(poly):
    # Canonical smallest-ID fan fixes the same diagonal on shared clipped faces.
    k=poly.index(min(poly));p=poly[k:]+poly[:k];return [[p[0],p[i],p[i+1]] for i in range(1,len(p)-1)]
source_faces=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]]
for ti,t in enumerate(source_tets):
    dist=x[t,0]-plane
    if not(np.any(dist>eps) and np.any(dist<-eps)):
        new_tets.append(t.tolist());sides.append(1 if np.any(dist>eps) else -1);parents.append(ti);continue
    for sign in [-1,1]:
        faces=[clip([int(t[j]) for j in face],sign) for face in source_faces];faces=[a for a in faces if len(a)>=3]
        cap=sorted(set(a for f in faces for a in f if abs(X[a][0]-plane)<=eps));coords=np.array([X[a] for a in cap]);center=coords[:,1:].mean(0);angles=np.arctan2(coords[:,2]-center[1],coords[:,1]-center[0]);cap=[cap[i] for i in np.argsort(angles)];faces.append(cap)
        ids=sorted(set(a for f in faces for a in f));center_id=len(X);X.append(np.array([X[a] for a in ids]).mean(0))
        for face in faces:
            for tr in triangulate(face):
                tet=[center_id]+tr;pts=np.array([X[a] for a in tet]);vol=np.linalg.det(pts[1:]-pts[0])/6
                if vol==0:raise RuntimeError('Zero-volume subcell')
                if vol<0:tet[2],tet[3]=tet[3],tet[2]
                new_tets.append(tet);sides.append(sign);parents.append(ti)
X=np.array(X);new_tets=np.array(new_tets,dtype=np.int64);sides=np.array(sides);parents=np.array(parents);onplane=np.flatnonzero(abs(X[:,0]-plane)<=eps);usedminus=set(new_tets[sides<0].ravel());usedplus=set(new_tets[sides>0].ravel());paired=[int(i) for i in onplane if i in usedminus and i in usedplus];copies={i:len(X)+j for j,i in enumerate(paired)};X=np.vstack([X,X[paired]])
for i,t in enumerate(new_tets):
    if sides[i]>0:new_tets[i]=[copies.get(int(j),int(j)) for j in t]
ties=np.array([[i,copies[i]] for i in paired]);vol=np.linalg.det(X[new_tets[:,1:]]-X[new_tets[:,0]][:,None])/6;rho=z['mass'].sum()/z['volume'].sum();mass=np.zeros(len(X));np.add.at(mass,new_tets.ravel(),np.repeat(rho*vol/4,4));source_vol=np.linalg.det(x[source_tets[:,1:]]-x[source_tets[:,0]][:,None])/6
# Retain exact original supports; both copies are fixed only if an original
# support is literally on the plane. Count/disclose such cases explicitly.
fixed=list(map(int,z['fixed']));fixed += [copies[i] for i in fixed if i in copies]
oriented=new_tets[:,source_faces].reshape(-1,3);keys=np.sort(oriented,axis=1);unique,index,counts=np.unique(keys,axis=0,return_index=True,return_counts=True);boundary=oriented[index[counts==1]];cut=boundary[np.max(abs(X[boundary][:,:,0]-plane),axis=1)<=eps];outer=boundary[np.max(abs(X[boundary][:,:,0]-plane),axis=1)>eps]
ds=np.concatenate([new_tets[:,[0,1]],new_tets[:,[0,2]],new_tets[:,[0,3]]]);G=coo_matrix((np.ones(len(ds)),(ds[:,0],ds[:,1])),shape=(len(X),len(X))).tocsr();components,labels=connected_components(G,directed=False);used=np.unique(new_tets);labels_used=np.unique(labels[used]);withties=G+coo_matrix((np.ones(len(ties)),(ties[:,0],ties[:,1])),shape=G.shape).tocsr();_,l2=connected_components(withties,directed=False);cutpairs=[]
for sign in [-1,1]:
    node_set=set(new_tets[sides==sign].ravel());cutpairs.append(np.array([f for f in cut if all(i in node_set for i in f)]))
def coordkeys(faces):return sorted(tuple(sorted(tuple(np.round(p,12)) for p in tri)) for tri in X[faces])
areas=[np.linalg.norm(np.cross(X[f][:,1]-X[f][:,0],X[f][:,2]-X[f][:,0]),axis=1)/2 for f in cutpairs];normals=[np.cross(X[f][:,1]-X[f][:,0],X[f][:,2]-X[f][:,0]) for f in cutpairs]
parent_sums=np.bincount(parents,weights=vol,minlength=len(source_tets));piece_masses=[float(mass[labels==label].sum()) for label in labels_used];support_error=float(np.max(abs(X[np.array(fixed[:len(z['fixed'])])]-x[z['fixed']])));positive=bool((vol>0).all());masserr=float(abs(mass.sum()/z['mass'].sum()-1));volerr=float(abs(vol.sum()/source_vol.sum()-1));parerr=float(np.max(abs(parent_sums-source_vol))/source_vol.max())
out={'scope':'User-authorized static conforming split input only, no dynamic or separation pass','source_nodes':len(x),'source_tets':len(source_tets),'candidate_nodes':len(X),'candidate_tets':len(new_tets),'new_intersection_nodes':len(crossings),'interface_pairs':len(ties),'cut_faces_per_side':[len(a) for a in cutpairs],'cut_areas_m2':[float(a.sum()) for a in areas],'cut_faces_geometrically_paired':coordkeys(cutpairs[0])==coordkeys(cutpairs[1]),'cut_normal_x_signs':[np.unique(np.sign(n[:,0])).tolist() for n in normals],'minimum_tet_volume_m3':float(vol.min()),'positive_tets':positive,'mass_kg':float(mass.sum()),'mass_relative_error':masserr,'volume_relative_error':volerr,'maximum_parent_volume_partition_error_scaled':parerr,'nonmanifold_faces':int((counts>2).sum()),'material_components_without_ties':len(labels_used),'material_components_with_ties':len(np.unique(l2[used])),'piece_masses_kg':piece_masses,'original_support_count':len(z['fixed']),'candidate_support_count':len(fixed),'support_coordinate_error_m':support_error,'minimum_nodal_mass_kg':float(mass[used].min()),'wall_s':time.perf_counter()-start,'open_limits':['Independent surface/section coverage audit still required.','Smaller subcells require updated integration and force/reference validation.','Cohesive force constants and live paired-face contact not initialized; static input does not establish a stable assembled target.']}
np.savez_compressed(W/'conforming_split.npz',x=X,tets=new_tets,mass=mass,fixed=np.array(fixed),ties=ties,tet_side=sides,parent_tet=parents,volume=vol,cut_minus=cutpairs[0],cut_plus=cutpairs[1],outer=outer,boundary=boundary,source_x=x,source_tets=source_tets,source_outer=z['boundary'])
out['preliminary_passed']=bool(positive and masserr<1e-10 and volerr<1e-10 and parerr<1e-10 and support_error<1e-12 and out['cut_faces_geometrically_paired'] and out['nonmanifold_faces']==0 and len(labels_used)==2 and out['material_components_with_ties']==1 and min(piece_masses)/mass.sum()>.01)
(W/'conforming_split_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
