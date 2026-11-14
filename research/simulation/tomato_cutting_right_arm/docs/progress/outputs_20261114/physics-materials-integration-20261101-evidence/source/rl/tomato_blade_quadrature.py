"""Force-converged reference-area quadrature on clipped actual soft triangles."""
import numpy as np
from tomato_exact_blade_coverage import coverage
from tomato_exact_blade_queries import sample

def force_vector(count,candidates,query):
 force=np.zeros((count,3));phi=np.minimum(query['phi'],0.);local=-1.75e9*np.asarray([s['area_m2'] for s in candidates])[:,None]*phi[:,None]*query['normal']
 for point,value in zip(candidates,local):
  for node,weight in zip(point['corners'],point['barycentric']):force[node]+=weight*value
 return force

def converged(vertices,cells,positions,triangles,reference,local_vertices,faces,rotation,translation,capacity=131072):
 previous=None;records=[]
 for level in range(6):
  c=coverage(vertices,cells,positions,triangles,capacity=capacity,reference_positions=reference,quadrature_level=level);samples=c['samples']
  if not samples:return c,dict(phi=[],normal=[],closest=[]),dict(level=level,checks=[],clear=True)
  query=sample(local_vertices,faces,(np.asarray([s['point_m'] for s in samples])-translation)@rotation);query['normal']=query['normal']@rotation.T
  force=force_vector(len(positions),samples,query)
  if previous is not None:
   error=float(np.linalg.norm(force-previous));scale=max(float(np.linalg.norm(force)),float(np.linalg.norm(previous)),1e-12);record=dict(level=level,points=len(samples),force_difference_n=error,relative_difference=error/scale);records.append(record)
   if error<=.01*scale+1e-5:return c,query,dict(level=level,checks=records,clear=False)
  previous=force
 raise ValueError('Authored blade quadrature did not converge within fixed 1-percent/1e-5 N gate: '+str(records))
