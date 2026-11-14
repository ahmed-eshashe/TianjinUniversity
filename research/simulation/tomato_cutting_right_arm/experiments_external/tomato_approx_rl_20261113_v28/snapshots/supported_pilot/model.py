from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull

def lattice(shape='cube',h=.0035,size=.021,scale=1.):
 if shape=='cube':
  n=round(size/h);coords=(np.arange(n)+.5)*h-n*h/2;xyz=np.array(np.meshgrid(coords,coords,coords,indexing='ij')).reshape(3,-1).T;mask=np.ones(len(xyz),bool);mass=1000*(n*h)**3
 else:
  z=np.load('/home/omen/Documents/Codex/experiments/tomato_cut_surface_20261113_v25/states/tomato_baseline.npz');points=z['poly_vertices']*scale;lo=points.min(0);hi=points.max(0);center=(lo+hi)/2;points-=center;hull=ConvexHull(points);axes=[np.arange(-np.ceil((hi-lo)[k]/2/h),np.ceil((hi-lo)[k]/2/h)+1)*h for k in range(3)];xyz=np.array(np.meshgrid(*axes,indexing='ij')).reshape(3,-1).T;mask=np.ones(len(xyz),bool)
  # Chunk the half-space test to bound host memory.
  for i in range(0,len(xyz),256):mask[i:i+256]=np.max(xyz[i:i+256]@hull.equations[:,:3].T+hull.equations[:,3],axis=1)<=1e-12
  mass=.121253418*scale**3
 xyz=xyz[mask];xyz[:,1]-=xyz[:,1].min();xyz[:,1]+=h*.5;keys=np.rint((xyz-xyz.min(0))/h).astype(int);lookup={tuple(k):i for i,k in enumerate(keys)};edges=[];ratios=[]
 for i,k in enumerate(keys):
  for dx in [-1,0,1]:
   for dy in [-1,0,1]:
    for dz in [-1,0,1]:
     delta=(dx,dy,dz)
     if delta<=(0,0,0):continue
     j=lookup.get(tuple(k+delta))
     if j is not None:edges.append((i,j));s=dx*dx+dy*dy+dz*dz;ratios.append([0,1.,.5,.1875][s])
 edges=np.array(edges,np.int32);length=np.linalg.norm(xyz[edges[:,1]]-xyz[edges[:,0]],axis=1);k=100000*h/1.875*np.array(ratios);m=np.full(len(xyz),mass/len(xyz));area=np.full(len(edges),h*h/9);return dict(x=xyz.astype(np.float32),edges=edges,length=length.astype(np.float32),stiffness=k.astype(np.float32),mass=m.astype(np.float32),fracture_area=area.astype(np.float32),h=h,radius=.45*h,shape=shape,scale=scale,mass_total=mass)
