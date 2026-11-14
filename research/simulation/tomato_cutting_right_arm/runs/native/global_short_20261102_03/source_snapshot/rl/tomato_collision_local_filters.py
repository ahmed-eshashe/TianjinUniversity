"""Same-piece rest-neighbor exclusions; all cross-piece contact remains enabled."""
import numpy as np

def point_segment_distance(p,a,b):
 v=b-a;t=np.clip(np.sum((p-a)*v,axis=-1)/np.sum(v*v,axis=-1),0,1)
 return np.linalg.norm(p-(a+t[...,None]*v),axis=-1)

def point_triangle_distance(p,tri):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];u=b-a;v=c-a;w=p-a;uu=np.sum(u*u,1);uv=np.sum(u*v,1);vv=np.sum(v*v,1);wu=np.sum(w*u,1);wv=np.sum(w*v,1);den=uu*vv-uv*uv;s=(vv*wu-uv*wv)/den;t=(uu*wv-uv*wu)/den;n=np.cross(u,v);distance=np.abs(np.sum(w*n,1))/np.linalg.norm(n,axis=1);inside=(s>=0)&(t>=0)&(s+t<=1);edge=np.minimum(np.minimum(point_segment_distance(p,a,b),point_segment_distance(p,b,c)),point_segment_distance(p,c,a));return np.where(inside,distance,edge)

def segment_distance(a,b,c,d):
 u=b-a;v=d-c;w=a-c;aa=np.dot(u,u);bb=np.sum(u*v,axis=-1);cc=np.sum(v*v,axis=-1);dd=np.sum(w*u,axis=-1);ee=np.sum(w*v,axis=-1);den=aa*cc-bb*bb;safe=np.abs(den)>1e-24;s=np.where(safe,(bb*ee-cc*dd)/np.where(safe,den,1),0);t=np.where(safe,(aa*ee-bb*dd)/np.where(safe,den,1),0);interior=safe&(s>=0)&(s<=1)&(t>=0)&(t<=1);line=np.linalg.norm((a+s[:,None]*u)-(c+t[:,None]*v),axis=1);edge=np.minimum.reduce([point_segment_distance(a,c,d),point_segment_distance(b,c,d),point_segment_distance(c,a,b),point_segment_distance(d,a,b)]);return np.where(interior,line,edge)

def local_filter_maps(embedding,design,*,radius):
 x=embedding['reference_positions'];triangles=embedding['triangles'];surface=embedding['surface_node_ids'];node_piece={n:i for i,p in enumerate(design['pieces']) for n in p['surface_node_ids']};piece=np.array([node_piece[int(n)] for n in surface]);tri_piece=piece[triangles[:,0]];points=x[triangles];lo=points.min(1);hi=points.max(1);vertex_map={}
 for v,p in enumerate(x):
  candidates=np.flatnonzero((tri_piece==piece[v])&np.all(p>=lo-radius,axis=1)&np.all(p<=hi+radius,axis=1))
  hit=candidates[point_triangle_distance(p,points[candidates])<radius]
  if len(hit):vertex_map[v]=set(hit.tolist())
 edges=sorted(set(tuple(sorted((int(t[i]),int(t[j])))) for t in triangles for i,j in [(0,1),(1,2),(2,0)]));edges=np.asarray(edges,int);ep=x[edges];el=ep.min(1);eh=ep.max(1);edge_piece=piece[edges[:,0]];edge_map={}
 for i,(a,b) in enumerate(ep):
  candidates=np.flatnonzero((edge_piece==edge_piece[i])&np.all(eh>=el[i]-radius,axis=1)&np.all(el<=eh[i]+radius,axis=1));hit=candidates[segment_distance(a,b,ep[candidates,0],ep[candidates,1])<radius]
  if len(hit):edge_map[i]=set(hit.tolist())
 if any(tri_piece[t]!=piece[v] for v,ts in vertex_map.items() for t in ts) or any(edge_piece[j]!=edge_piece[i] for i,js in edge_map.items() for j in js):raise ValueError('Local filter must never exclude cross-piece contact')
 return vertex_map,edge_map,edges
