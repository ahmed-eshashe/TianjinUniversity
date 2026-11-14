"""Conservative material-edge integration over exact solid intersection intervals.

Entry/exit motion contributes no boundary work because phi=0 there. Nearest
feature transitions have continuous phi squared. Adaptive integration resolves
the remaining force changes; no endpoint-only or entry-plane penalty is used.
"""
from pathlib import Path
import sys,numpy as np
from numba import njit
W=Path(__file__).resolve().parent;R=W.parents[1]
sys.path.insert(0,str(R/'rl'))
sys.path.insert(0,str(W.parent/'disect_edge_contact_20261109_v26'))
from tomato_compiled_blade_query import query_mesh
from edge_contact import material_edges

@njit(cache=True)
def intersections(a,b,vertices,faces):
    times=np.empty(len(faces)+2);times[0]=0.;times[1]=1.;count=2
    direction=b-a
    for face in faces:
        p=vertices[face[0]];e1=vertices[face[1]]-p;e2=vertices[face[2]]-p
        h=np.cross(direction,e2);det=np.dot(e1,h)
        if abs(det)<1e-18:continue
        s=a-p;u=np.dot(s,h)/det;cross=np.cross(s,e1)
        v=np.dot(direction,cross)/det;t=np.dot(e2,cross)/det
        if u>=-1e-12 and v>=-1e-12 and u+v<=1+1e-12 and t>0 and t<1:
            times[count]=t;count+=1
    return np.sort(times[:count])

GAUSS={n:np.polynomial.legendre.leggauss(n) for n in [8,16]}

def law(phi,normal,velocity,tool_velocity,ke=2000.,kd=0.,kf=2500.,mu=.5):
    relative=velocity-tool_velocity;vn=np.sum(relative*normal,axis=1)
    tangent=relative-vn[:,None]*normal;speed=np.linalg.norm(tangent,axis=1)
    elastic=ke*np.maximum(-phi,0);ratio=speed/kf
    friction=elastic*(mu*np.tanh(4*ratio)+(.5-mu)*ratio/(.25*ratio**2+.75)**2)
    return (elastic+kd*np.maximum(-vn,0)*(phi<0))[:,None]*normal-friction[:,None]*tangent/np.maximum(speed[:,None],1e-300)

class AdaptiveContact:
    def __init__(self,mesh,force_atol=1e-10,rtol=1e-6,max_depth=40):
        self.edges=material_edges(mesh);self.cut=np.unique(mesh['ties'])
        self.outer=np.setdiff1d(np.unique(mesh['outer']),self.cut)
        degree=np.bincount(self.edges[:,1],minlength=len(mesh['x']))
        self.edge_weights=1/degree[self.edges[:,1]]
        self.force_atol=force_atol;self.rtol=rtol;self.max_depth=max_depth

    def evaluate(self,q,v,vertices,faces,tool_velocity,com,kd=0.,ke=2000.):
        lo,hi=vertices.min(0),vertices.max(0);a,b=self.edges.T
        keep=np.all((np.maximum(q[a],q[b])>=lo)&(np.minimum(q[a],q[b])<=hi),axis=1)
        accepted=[];errors=[];unresolved=[];inside_intervals=0
        for edge_index in np.flatnonzero(keep):
            i,j=self.edges[edge_index];weight=self.edge_weights[edge_index]
            times=intersections(q[i],q[j],vertices,faces)
            times=times[np.r_[True,np.diff(times)>1e-12]]
            middle=(times[1:]+times[:-1])/2
            phi=query_mesh(vertices,faces,q[i]+middle[:,None]*(q[j]-q[i]))['phi']
            intervals=[(x,y) for x,y,p in zip(times[:-1],times[1:],phi) if p<0]
            inside_intervals+=len(intervals)
            def quadrature(left,right,order):
                g,w=GAUSS[order];u=(left+right)/2+(right-left)*g/2
                weights=weight*(right-left)*w/2
                points=q[i]+u[:,None]*(q[j]-q[i]);vel=v[i]+u[:,None]*(v[j]-v[i])
                result=query_mesh(vertices,faces,points)
                force=law(result['phi'],result['normal'],vel,tool_velocity,ke=ke,kd=kd)
                # Compare energy, both material force pullbacks, and embedded
                # normal damping matrices. Samples remain positive-weighted.
                energy=.5*ke*np.minimum(result['phi'],0)**2
                fn=np.concatenate(((1-u)[:,None]*force,u[:,None]*force),axis=1)
                nn=np.einsum('ni,nj->nij',result['normal'],result['normal'])
                hess=np.concatenate([((1-u)**2)[:,None]*nn.reshape(-1,9),
                                     (u*(1-u))[:,None]*nn.reshape(-1,9),
                                     (u**2)[:,None]*nn.reshape(-1,9)],axis=1)
                metric=np.r_[weights@energy,weights@fn,weights@hess]
                return metric,(i,j,u,weights,result['phi'],result['normal'],force)
            stack=[(x,y,0) for x,y in intervals];evaluations=0
            while stack:
                evaluations+=1
                if evaluations>4096:raise RuntimeError('Adaptive per-edge work cap reached')
                left,right,depth=stack.pop()
                coarse,_=quadrature(left,right,8);fine,samples=quadrature(left,right,16)
                err=np.abs(fine-coarse)
                tolerance=np.r_[1e-14+self.rtol*abs(fine[0]),
                                 np.full(6,self.force_atol)+self.rtol*np.abs(fine[1:7]),
                                 np.full(27,1e-9)+self.rtol*np.abs(fine[7:])]
                if np.all(err<=tolerance):
                    accepted.append(samples);errors.append(err)
                elif depth<self.max_depth:
                    mid=(left+right)/2;stack.extend([(left,mid,depth+1),(mid,right,depth+1)])
                else:unresolved.append(dict(edge=int(edge_index),interval=[left,right],error=err.tolist()))
        if unresolved:raise RuntimeError(f'Unresolved adaptive contact intervals: {len(unresolved)}')
        force=np.zeros_like(q);energy=0.;ids=[];coords=[];normals=[];weights=[];phis=[]
        for i,j,u,w,phi,normal,f in accepted:
            weighted=w[:,None]*f
            force[i]+=np.sum((1-u)[:,None]*weighted,axis=0)
            force[j]+=np.sum(u[:,None]*weighted,axis=0)
            energy+=float(.5*ke*np.dot(w,np.minimum(phi,0)**2))
            ids.append(np.tile([i,j],(len(u),1)));coords.append(u);normals.append(normal);weights.append(w);phis.append(phi)
        return dict(force=force,energy_J=energy,reaction=-force.sum(0),
                    moment=-np.cross(q-com,force).sum(0),
                    ids=np.concatenate(ids) if ids else np.empty((0,2),int),
                    u=np.concatenate(coords) if coords else np.empty(0),
                    normal=np.concatenate(normals) if normals else np.empty((0,3)),
                    weights=np.concatenate(weights) if weights else np.empty(0),
                    phi=np.concatenate(phis) if phis else np.empty(0),
                    inside_intervals=inside_intervals,accepted_subintervals=len(accepted),
                    estimated_force_error_N=float(np.sum([e[1:7].max() for e in errors])))
