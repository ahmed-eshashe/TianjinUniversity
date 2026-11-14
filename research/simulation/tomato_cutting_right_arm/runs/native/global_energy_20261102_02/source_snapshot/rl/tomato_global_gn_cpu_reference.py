"""Independent NumPy/CPU-autograd GN action; no simulator imports."""
import argparse,json,time
from pathlib import Path
import numpy as np
import torch

def closest_point_triangle(p,a,b,c):
 e0=b-a;e1=c-a;gram=np.array([[e0@e0,e0@e1],[e0@e1,e1@e1]]);uv=np.linalg.solve(gram,np.array([e0@(p-a),e1@(p-a)]));bary=np.r_[1-uv.sum(),uv];candidates=[]
 if bary.min()>=0:candidates.append(bary)
 for i,j in [(0,1),(1,2),(2,0)]:
  tri=np.array([a,b,c]);v=tri[j]-tri[i];t=np.clip((p-tri[i])@v/(v@v),0,1);w=np.zeros(3);w[i]=1-t;w[j]=t;candidates.append(w)
 return min(candidates,key=lambda w:np.linalg.norm(w@np.array([a,b,c])-p))

def closest_edges(a,b,c,d):
 u=b-a;v=d-c;w=a-c;aa=u@u;bb=u@v;cc=v@v;dd=u@w;ee=v@w;candidates=[(0.,np.clip(ee/cc,0,1)),(1.,np.clip((b-c)@v/cc,0,1)),(np.clip(-dd/aa,0,1),0.),(np.clip((d-a)@u/aa,0,1),1.)];den=aa*cc-bb*bb
 if den>1e-14*aa*cc:
  s=(bb*ee-cc*dd)/den;t=(aa*ee-bb*dd)/den
  if 0<=s<=1 and 0<=t<=1:candidates.append((s,t))
 return min(candidates,key=lambda st:np.linalg.norm(a+st[0]*u-c-st[1]*v))

def reference_action(data):
 x=data['x'];vectors=data['vectors'];free=data['free'].astype(bool);v=vectors.copy();v[:,~free]=0;mass=data['mass'];dt=float(data['dt'][0]);out=(mass/dt**2)[None,:,None]*v;k=data['spring_k'];pairs=data['spring_pairs'];difference=x[pairs[:,0]]-x[pairs[:,1]];normal=difference/np.linalg.norm(difference,axis=1)[:,None];direction=v[:,pairs[:,0]]-v[:,pairs[:,1]];factor=k[None,:]*np.einsum('pi,kpi->kp',normal,direction);f=factor[:,:,None]*normal[None]
 for index in range(len(v)):np.add.at(out[index],pairs[:,0],f[index]);np.add.at(out[index],pairs[:,1],-f[index])
 cells=data['cells'];q=x[cells];a=q[:,1]-q[:,0];b=q[:,2]-q[:,0];c=q[:,3]-q[:,0];V=data['volumes'];J=np.linalg.det(q[:,1:]-q[:,:1])/(6*V)
 if J.min()<=.1:raise ValueError('CPU reference volume floor')
 g=np.stack([np.cross(b,c),np.cross(c,a),np.cross(a,b)],1)/(6*V[:,None,None]);g=np.concatenate([-g.sum(1)[:,None],g],1);active=J<.5;scale=np.zeros(len(J));scale[active]=10000*V[active]/(.16*((J[active]-.1)/.4)**2);dJ=np.einsum('cni,kcni->kc',g,v[:,cells]);f=(scale[None,:]*dJ)[:,:,None,None]*g[None]
 for index in range(len(v)):np.add.at(out[index],cells.ravel(),f[index].reshape(-1,3))
 torch.set_num_threads(1);all_pairs=data['cohesive_pairs'];counts=data['cohesive_counts'];anchors=data['anchors'];sign=data['sign'];weights=data['weights'];stiff=data['local_k']
 if np.any(data['history'])or np.any(data['eligible']):raise ValueError('This independent action fixture is explicitly undamaged/nonfracturing')
 for patch,count in enumerate(counts):
  ids=all_pairs[patch,:count];current=torch.tensor(x[ids],dtype=torch.float64,requires_grad=True);aa,bb,cc=anchors[patch]
  def effective(z):
   mid=z.mean(1);u=mid[bb]-mid[aa];vv=mid[cc]-mid[aa];t=u/torch.linalg.vector_norm(u);nn=sign[patch]*torch.linalg.cross(u,vv);nn=nn/torch.linalg.vector_norm(nn);frame=torch.stack([nn,t,torch.linalg.cross(nn,t)],dim=1);gap=(z[:,1]-z[:,0])@frame;return torch.cat([torch.clamp(gap[:,:1],min=0),gap[:,1:]],dim=1)
  jac=torch.autograd.functional.jacobian(effective,current).detach().numpy().reshape(count,3,2*count,3);local=v[:,ids.ravel()];de=np.einsum('qani,kni->kqa',jac,local);traction=np.einsum('ab,kqb->kqa',stiff[patch],de)*weights[patch,:count][None,:,None];f=np.einsum('qani,kqa->kni',jac,traction)
  for index in range(len(v)):np.add.at(out[index],ids.ravel(),f[index])
 proxy=data['proxy'];endpoint=data['endpoint'];kinds=data['kind'];threshold=data['threshold'];physical=data['physical_ids'];W=data['endpoint_weight'];radius=float(data['radius'][0]);stiffness=float(data['contact_k'][0]);active_contacts=0
 for record,ids in enumerate(endpoint):
  p0,p1,p2,p3=proxy[ids];u=np.zeros(3);vv=np.zeros(3);m=1.;dm=0.
  if kinds[record]==0:
   bc=closest_point_triangle(p0,p1,p2,p3);coeff=np.r_[1.,-bc]
  else:
   s,t=closest_edges(p0,p1,p2,p3);coeff=np.array([1-s,s,-1+t,-t]);u=p1-p0;vv=p3-p2;squared=np.linalg.norm(np.cross(u,vv))**2;eps=threshold[record]
   if squared<eps:ratio=squared/eps;m=ratio*(2-ratio);dm=2*(1-ratio)/eps
  delta=coeff@proxy[ids];d=np.linalg.norm(delta)
  if d>=radius:continue
  if d<=1e-8:raise ValueError('CPU reference singular contact')
  active_contacts+=1;n=delta/d;tau=radius/2;minimum=1e-5;k2=tau*tau*stiffness
  if d<tau and d>minimum:second=k2/d**2;energy=.5*k2-k2*np.log(d/tau)
  elif d<=minimum:second=k2/minimum**2;gap=d-minimum;energy=.5*k2-k2*np.log(minimum/tau)-k2/minimum*gap+.5*second*gap*gap
  else:second=stiffness;energy=.5*stiffness*(radius-d)**2
  nodes=physical[record];valid=nodes>=0;nodes=nodes[valid];w=W[record,valid];c0=w@coeff;uc=w[:,1]-w[:,0];vc=w[:,3]-w[:,2];local=v[:,nodes];nd=np.einsum('n,kni,i->k',c0,local,n);du=np.einsum('n,kni->ki',uc,local);dv=np.einsum('n,kni->ki',vc,local);dcross=np.cross(du,vv)+np.cross(u,dv);f=m*second*c0[None,:,None]*nd[:,None,None]*n[None,None,:]+2*energy*dm*(uc[None,:,None]*np.cross(vv,dcross)[:,None,:]-vc[None,:,None]*np.cross(u,dcross)[:,None,:])
  for index in range(len(v)):np.add.at(out[index],nodes,f[index])
 board=(x[:,2]<float(data['board_height'][0]))*data['board_k'];out[:,:,2]+=board[None,:]*v[:,:,2];out[:,~free]=vectors[:,~free];return out,active_contacts

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();start=time.monotonic();data=np.load(a.input);expected,count=reference_action(data);actual=data['matrix_products'];errors=[]
 for i,(x,y)in enumerate(zip(expected,actual)):
  absolute=float(abs(x-y).max());relative=float(np.linalg.norm(x-y)/max(np.linalg.norm(x),1e-12));errors.append(dict(vector=i,absolute_error_n_m=absolute,relative_error=relative))
 passed=all(row['absolute_error_n_m']<=1e-6 or row['relative_error']<=1e-7 for row in errors);report=dict(passed=passed,errors=errors,independent_active_contacts=count,elapsed_wall_s=time.monotonic()-start,scope='Independent NumPy bulk/contact Gram actions and CPU-autograd moving-frame cohesive Jacobians versus native assembled full coupled matrix. Undamaged operator only, no mechanical stepping.')
 a.output.write_text(json.dumps(report,indent=2)+'\n');return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
