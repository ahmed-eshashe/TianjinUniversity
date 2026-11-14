"""Independent NumPy/float64 reference for the exact-domain quadrature."""
from pathlib import Path
import numpy as np
from adaptive_reference import facets,RULE
from independent_cad_query import query_mesh
from contact_law import evaluate

def masters(n):
 out=[]
 for i in range(n):
  for j in range(n-i):
   for tri in ([[i,j],[i+1,j],[i,j+1]],)+(([[i+1,j],[i+1,j+1],[i,j+1]],) if i+j<n-1 else ()):
    yz=np.array(tri)/n;out.append(np.c_[1-yz.sum(1),yz])
 return np.array(out)

def integral(a,cad,T,R,tool_velocity,resolution=4,surface=None):
 z=np.load(Path(__file__).resolve().parents[1]/'assets/blade_partition.npz');cells=z['x'][z['tets']];planes=z['planes'];cmin=cells.min(1);cmax=cells.max(1);
 if surface is None:
  from poly_surface import Surface
  surface=Surface(a)
 ids=np.arange(len(surface.X)).reshape(-1,3);X=surface.triangles;areas=surface.tri_area;positions=surface.positions(a.q);velocity=surface.velocities(a.v);
 Bs=masters(resolution);points=[];vel=[];weights=[];node_ids=[];barycentrics=[]
 for face,nodes in enumerate(ids):
  p=positions[nodes];local=(p-T)@R
  for ci in np.flatnonzero(np.all(local.max(0)>=cmin,axis=1)&np.all(local.min(0)<=cmax,axis=1)):
   polygon=list(np.eye(3))
   for plane in planes[ci]:
    ds=local@plane[:3]+plane[3];new=[]
    for i,p0 in enumerate(polygon):
     p1=polygon[(i+1)%len(polygon)];d0=p0@ds;d1=p1@ds
     if d0<=0:new.append(p0)
     if (d0<0<d1) or (d1<0<d0):new.append(p0+d0/(d0-d1)*(p1-p0))
    polygon=new
    if not polygon:break
   for i in range(1,len(polygon)-1):
    root=np.array([polygon[0],polygon[i],polygon[i+1]]);area=areas[face]*abs(np.linalg.det(root));B=(RULE[None]@(Bs@root)).reshape(-1,3);points.extend(B@p);vel.extend(B@velocity[nodes]);weights.extend(np.full(len(B),area/len(B)));node_ids.extend(np.tile(nodes,(len(B),1)));barycentrics.extend(B)
 F=np.zeros_like(positions)
 if not points:return dict(force=surface.Q.T@F,energy=0.,friction_power=0.,tool_power=0.,moment=np.zeros(3))
 points=np.array(points);vel=np.array(vel);weights=np.array(weights);barycentrics=np.array(barycentrics);node_ids=np.array(node_ids);query=query_mesh(cad.vertices,cad.faces,(points-T)@R);normal=query['normal']@R.T;law=evaluate(query['phi'],normal,vel-tool_velocity,weights);force=law['force'];np.add.at(F,node_ids.ravel(),(barycentrics[:,:,None]*force[:,None,:]).reshape(-1,3));return dict(force=surface.Q.T@F,energy=.5*1e9*np.sum(weights*np.maximum(-query['phi'],0)**2),friction_power=-np.sum(law['friction_force']*(vel-tool_velocity)),tool_power=np.sum(force*tool_velocity),moment=np.cross(points-T,force).sum(0))
