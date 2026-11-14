"""Batch identical edge quadrature work; same physical edges/law/tolerances."""
from pathlib import Path
import sys,numpy as np
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent/'disect_cut_edge_coverage_20261110_v34'))
from complete_edges import CompleteCutEdges
from adaptive_contact import intersections,GAUSS,law,query_mesh
class BatchedContact(CompleteCutEdges):
 def evaluate(self,q,v,vertices,faces,tool_velocity,com,kd=0.,ke=2000.):
  lo,hi=vertices.min(0),vertices.max(0);a,b=self.edges.T
  keep=np.flatnonzero(np.all((np.maximum(q[a],q[b])>=lo)&(np.minimum(q[a],q[b])<=hi),axis=1));meta=[];points=[]
  for e in keep:
   i,j=self.edges[e];ts=intersections(q[i],q[j],vertices,faces);ts=ts[np.r_[True,np.diff(ts)>1e-12]]
   for l,r in zip(ts[:-1],ts[1:]):meta.append((e,l,r,0));points.append(q[i]+((l+r)/2)*(q[j]-q[i]))
  middle_phi=query_mesh(vertices,faces,np.array(points).reshape(-1,3))['phi'] if points else np.zeros(0)
  pending=[entry for entry,ph in zip(meta,middle_phi) if ph<0];inside_intervals=len(pending);counts=np.zeros(len(self.edges),int);accepted=[]
  def quadrature(tasks,order):
   edges=np.array([t[0] for t in tasks],int);left=np.array([t[1] for t in tasks]);right=np.array([t[2] for t in tasks]);i,j=self.edges[edges].T;g,w=GAUSS[order]
   u=(left[:,None]+right[:,None])/2+(right-left)[:,None]*g/2;weights=self.edge_weights[edges,None]*(right-left)[:,None]*w/2
   p=q[i,None]+u[:,:,None]*(q[j,None]-q[i,None]);vel=v[i,None]+u[:,:,None]*(v[j,None]-v[i,None]);result=query_mesh(vertices,faces,p.reshape(-1,3));phi=result['phi'].reshape(-1,order);normal=result['normal'].reshape(-1,order,3);force=law(phi.ravel(),normal.reshape(-1,3),vel.reshape(-1,3),tool_velocity,ke=ke,kd=kd).reshape(-1,order,3)
   energy=.5*ke*np.minimum(phi,0)**2;fn=np.concatenate(((1-u)[:,:,None]*force,u[:,:,None]*force),axis=2);nn=np.einsum('nki,nkj->nkij',normal,normal).reshape(-1,order,9)
   hess=np.concatenate([((1-u)**2)[:,:,None]*nn,(u*(1-u))[:,:,None]*nn,(u**2)[:,:,None]*nn],axis=2)
   values=np.concatenate((energy[:,:,None],fn,hess),axis=2);metric=np.matmul(weights[:,None,:],values)[:,0,:]
   return metric,(i,j,u,weights,phi,normal,force)
  while pending:
   upcoming=[]
   for offset in range(0,len(pending),128):
    tasks=pending[offset:offset+128];edgeids=np.array([t[0] for t in tasks],int);np.add.at(counts,edgeids,1)
    if np.max(counts)>4096:raise RuntimeError('Adaptive per-edge work cap reached')
    coarse,_=quadrature(tasks,8);fine,samples=quadrature(tasks,16);err=np.abs(fine-coarse);tol=np.concatenate((1e-14+self.rtol*np.abs(fine[:,:1]),np.full((len(tasks),6),self.force_atol)+self.rtol*np.abs(fine[:,1:7]),np.full((len(tasks),27),1e-9)+self.rtol*np.abs(fine[:,7:])),axis=1)
    for n,t in enumerate(tasks):
     if np.all(err[n]<=tol[n]):accepted.append((t[0],t[1],err[n],tuple(s[n] for s in samples)))
     elif t[3]<self.max_depth:
      e,l,r,d=t;mid=(l+r)/2;upcoming.extend([(e,l,mid,d+1),(e,mid,r,d+1)])
     else:raise RuntimeError('Unresolved adaptive contact intervals')
   pending=upcoming
  # Reconstruct original edge/DFS ordering, including per-interval summation.
  accepted.sort(key=lambda a:(a[0],-a[1]));force=np.zeros_like(q);energy=0.;ids=[];coords=[];normals=[];weights=[];phis=[];errors=[]
  for _,_,err,(i,j,u,w,phi,normal,f) in accepted:
   weighted=w[:,None]*f;force[i]+=np.sum((1-u)[:,None]*weighted,axis=0);force[j]+=np.sum(u[:,None]*weighted,axis=0);energy+=float(.5*ke*np.dot(w,np.minimum(phi,0)**2));ids.append(np.tile([i,j],(len(u),1)));coords.append(u);normals.append(normal);weights.append(w);phis.append(phi);errors.append(err)
  return dict(force=force,energy_J=energy,reaction=-force.sum(0),moment=-np.cross(q-com,force).sum(0),ids=np.concatenate(ids) if ids else np.empty((0,2),int),u=np.concatenate(coords) if coords else np.empty(0),normal=np.concatenate(normals) if normals else np.empty((0,3)),weights=np.concatenate(weights) if weights else np.empty(0),phi=np.concatenate(phis) if phis else np.empty(0),inside_intervals=inside_intervals,accepted_subintervals=len(accepted),estimated_force_error_N=float(np.sum([e[1:7].max() for e in errors])))
