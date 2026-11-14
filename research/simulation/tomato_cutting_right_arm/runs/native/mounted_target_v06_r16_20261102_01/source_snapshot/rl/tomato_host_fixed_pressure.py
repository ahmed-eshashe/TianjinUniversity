"""Host exact-CAD pressure on FIXED positive material quadrature points.

The closest feature is reevaluated, but material barycentric coordinates and
reference weights stay fixed. Thus the force and physical-point body moment
are derivatives of one discrete potential across supported smooth features.
Packet coverage/regeneration and time stepping require separate gates.
"""
import numpy as np
from tomato_host_blade_geometry import query_mesh

def packet_from_samples(samples):
 return dict(indices=np.asarray([s['corners']for s in samples],dtype=np.int32).reshape(-1,3),barycentric=np.asarray([s['barycentric']for s in samples],dtype=float).reshape(-1,3),areas=np.asarray([s['area_m2']for s in samples],dtype=float))

def evaluate_fixed(blade,x,packet,R,t,com):
 x=np.asarray(x);ids=packet['indices'];bary=packet['barycentric'];area=packet['areas'];points=np.einsum('ni,nij->nj',bary,x[ids]);query=query_mesh(blade['vertices'],blade['triangles'],(points-t)@R);normal=query['normal']@R.T;phi=np.minimum(query['phi'],0);sample=-(1.75e9*area*phi)[:,None]*normal;force=np.zeros_like(x)
 for corner in range(3):np.add.at(force,ids[:,corner],bary[:,corner,None]*sample)
 center=t+R@com;wrench=np.r_[-sample.sum(0),np.cross(points-center,-sample).sum(0)]
 return dict(energy_j=float(.5*np.sum(1.75e9*area*phi*phi)),force_n=force,body_wrench=wrench,points_world=points,query=query)
