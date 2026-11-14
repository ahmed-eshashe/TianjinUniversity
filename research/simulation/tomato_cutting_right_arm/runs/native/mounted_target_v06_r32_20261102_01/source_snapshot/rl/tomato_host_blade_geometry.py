"""Pure NumPy CAD distance and reference-area pressure geometry diagnostics.

Independent host calculations only. No native query, time integration, robot
feedback, CCD or experimental force qualification is implied by this module.
"""
import numpy as np
from tomato_exact_blade_coverage import coverage

def query_mesh(vertices,faces,points):
 v=np.asarray(vertices,dtype=float);tri=v[np.asarray(faces,dtype=int)];points=np.asarray(points,dtype=float).reshape(-1,3);a,b,c=tri[:,0],tri[:,1],tri[:,2];e0=b-a;e1=c-a;aa=np.sum(e0*e0,1);ab=np.sum(e0*e1,1);bb=np.sum(e1*e1,1);det=aa*bb-ab*ab
 if not np.isfinite(points).all()or np.any(det<=1e-30):raise ValueError('Finite points and nondegenerate closed mesh required')
 rows={k:[]for k in ['phi','normal','closest','face','winding']}
 for start in range(0,len(points),512):
  p=points[start:start+512];rel=p[:,None]-a;u=(np.einsum('pfi,fi->pf',rel,e0)*bb-np.einsum('pfi,fi->pf',rel,e1)*ab)/det;w=(np.einsum('pfi,fi->pf',rel,e1)*aa-np.einsum('pfi,fi->pf',rel,e0)*ab)/det;closest=a+u[:,:,None]*e0+w[:,:,None]*e1;best=np.sum((p[:,None]-closest)**2,2);best[(u<0)|(w<0)|(u+w>1)]=np.inf
  for first,second in [(a,b),(b,c),(c,a)]:
   edge=second-first;t=np.clip(np.einsum('pfi,fi->pf',p[:,None]-first,edge)/np.sum(edge*edge,1),0,1);candidate=first+t[:,:,None]*edge;distance=np.sum((p[:,None]-candidate)**2,2);take=distance<best;closest[take]=candidate[take];best[take]=distance[take]
  face=np.argmin(best,1);q=closest[np.arange(len(p)),face];distance=np.sqrt(best[np.arange(len(p)),face]);ra=a-p[:,None];rb=b-p[:,None];rc=c-p[:,None];la=np.linalg.norm(ra,axis=2);lb=np.linalg.norm(rb,axis=2);lc=np.linalg.norm(rc,axis=2);numerator=np.einsum('pfi,pfi->pf',ra,np.cross(rb,rc));denominator=la*lb*lc+np.sum(ra*rb,2)*lc+np.sum(rb*rc,2)*la+np.sum(rc*ra,2)*lb;winding=np.sum(2*np.arctan2(numerator,denominator),1)/(4*np.pi);sign=np.where(abs(winding)>.5,-1.,1.);normal=np.zeros_like(p);valid=distance>1e-15;normal[valid]=sign[valid,None]*(p[valid]-q[valid])/distance[valid,None]
  if np.max(np.minimum(abs(winding),abs(abs(winding)-1)),initial=0)>1e-6:raise ValueError('Uncertain independent solid-angle sign')
  for key,value in [('phi',sign*distance),('normal',normal),('closest',q),('face',face),('winding',winding)]:rows[key].append(value)
 return {k:np.concatenate(values)if values else np.empty((0,3)if k in ['normal','closest']else(0,))for k,values in rows.items()}

def evaluate_pose(blade,cell_data,x,triangles,reference,R,t,com,*,level=1,capacity=131072):
 v=np.asarray(blade['vertices']);faces=np.asarray(blade['triangles']);vertices=np.asarray(cell_data['vertices']);world_vertices=vertices@R.T+t;clipped=coverage(world_vertices,np.asarray(cell_data['cells']),x,triangles,reference_positions=reference,quadrature_level=level,capacity=capacity);samples=clipped['samples'];force=np.zeros_like(x)
 if not samples:return dict(energy_j=0.,force_n=force,body_wrench=np.zeros(6),sum_absolute_sample_forces_n=0.,maximum_penetration_m=0.,contact_samples=0,face_ids=[],clipped=clipped,query=None)
 points=np.array([s['point_m']for s in samples]);query=query_mesh(v,faces,(points-t)@R);normal=query['normal']@R.T;phi=np.minimum(query['phi'],0);area=np.array([s['area_m2']for s in samples]);sample_force=-(1.75e9*area*phi)[:,None]*normal
 if np.any(query['phi']>1e-10):raise ValueError('Clipped solid-cell sample lies outside original CAD exterior')
 ids=np.array([s['corners']for s in samples]);bary=np.array([s['barycentric']for s in samples])
 for corner in range(3):np.add.at(force,ids[:,corner],bary[:,corner,None]*sample_force)
 center=t+R@com;wrench=np.r_[-sample_force.sum(0),np.cross(points-center,-sample_force).sum(0)]
 return dict(energy_j=float(.5*np.sum(1.75e9*area*phi*phi)),force_n=force,body_wrench=wrench,sum_absolute_sample_forces_n=float(np.linalg.norm(sample_force,axis=1).sum()),maximum_penetration_m=float(-phi.min()),contact_samples=len(samples),face_ids=np.unique(query['face']).astype(int).tolist(),clipped=clipped,query=query)
