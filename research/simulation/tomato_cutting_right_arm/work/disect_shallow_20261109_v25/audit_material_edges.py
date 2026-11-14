"""Read-only test for material-edge/knife crossings missed by point sampling.
Uses actual saved state; no simulation or altered forces. First-hit geometry follows
DiSECt's edge-triangle collision idea, without executing its force implementation.
"""
from pathlib import Path
import sys,json,numpy as np
from numba import njit
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));from blade_contact import CADBlade
@njit(cache=True)
def first_hits(q,edges,vertices,faces):
 out=np.full((len(edges),5),np.nan)
 for k in range(len(edges)):
  origin=q[edges[k,0]];direction=q[edges[k,1]]-origin;best=2.;normal=np.zeros(3)
  for f in faces:
   a=vertices[f[0]];e1=vertices[f[1]]-a;e2=vertices[f[2]]-a;h=np.cross(direction,e2);det=np.dot(e1,h)
   if abs(det)<1e-14:continue
   inv=1/det;s=origin-a;u=inv*np.dot(s,h)
   if u< -1e-10 or u>1+1e-10:continue
   cross=np.cross(s,e1);v=inv*np.dot(direction,cross)
   if v< -1e-10 or u+v>1+1e-10:continue
   t=inv*np.dot(e2,cross)
   if t>1e-7 and t<1-1e-7 and t<best:
    best=t;n=np.cross(e1,e2);n/=np.sqrt(np.dot(n,n))
    if np.dot(n,direction)>0:n=-n
    normal=n
  if best<2.:
   out[k,0]=best;out[k,1:4]=normal;out[k,4]=1.
 return out
m=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz');state=np.load(W/'coarse0040_final.npz');q=state['x'];p=json.loads((W/'correction_plan.json').read_text());t=float(state['step']*state['dt']);u=t/p['durations_s'][0];ramp=10*u**3-15*u**4+6*u**5;depth=p['downward_stroke_m']*ramp;path=np.array(p['front_lateral_path_m']);curve=PchipInterpolator(path[:,0],path[:,1]);T=np.array(p['selected']['translation_m'])+[float(curve(depth)),-depth,0];cad=CADBlade();vertices=cad.vertices@cad.rotation.T+T;query=cad.query(q,T);cut=np.unique(m['ties']);cutmask=np.zeros(len(q),bool);cutmask[cut]=True;cells=m['tets'];raw=np.concatenate([cells[:,[i,j]] for i in range(4) for j in range(i)],axis=0);raw=np.unique(np.sort(raw,axis=1),axis=0);raw=raw[cutmask[raw[:,0]]!=cutmask[raw[:,1]]];edges=raw.copy();swap=cutmask[edges[:,0]];edges[swap]=edges[swap,::-1];# interior -> cut endpoint
lo=vertices.min(0);hi=vertices.max(0);mins=np.minimum(q[edges[:,0]],q[edges[:,1]]);maxs=np.maximum(q[edges[:,0]],q[edges[:,1]]);keep=np.all((maxs>=lo)&(mins<=hi),axis=1)&(query['phi'][edges[:,0]]>1e-6);edges=edges[keep];hits=first_hits(q,edges,vertices,cad.triangles);has=np.isfinite(hits[:,0]);node_inside=query['phi'][edges[:,1]]< -1e-8;dots=np.einsum('ij,ij->i',np.nan_to_num(hits[:,1:4]),query['normal'][edges[:,1]]);opposed=has&node_inside&(dots<-.5);missed=has&(query['phi'][edges[:,1]]>1e-6);side=np.zeros(len(q),int)
for sign in [-1,1]:side[np.unique(cells[m['tet_side']==sign])]=sign
examples=[]
for i in np.flatnonzero(opposed|missed)[:12]:examples.append(dict(interior_node=int(edges[i,0]),cut_node=int(edges[i,1]),material_bank=int(side[edges[i,1]]),cut_node_SDF_m=float(query['phi'][edges[i,1]]),first_entry_fraction=float(hits[i,0]),entry_normal=hits[i,1:4].tolist(),point_SDF_normal=query['normal'][edges[i,1]].tolist(),normal_dot=float(dots[i]),point_detector_misses_crossing=bool(missed[i])))
out=dict(scope='Read-only actual-state CAD/material-edge coverage audit; not a new contact law or cutting pass',sim_s=t,screened_material_edges=len(edges),intersecting_edges=int(has.sum()),edges_with_both_endpoints_outside_knife=int(missed.sum()),inside_cut_endpoints_with_opposed_entry_vs_point_normal=int(opposed.sum()),examples=examples,reference_implementation='vendor/DiSECt/dflex/sim.py:cut_edge_tri_collision and eval_spring_tri_collision',interpretation='Point SDF and oriented material-edge entry can select different knife faces. Any counted crossings require contact-model review before deeper cutting. No force law change adopted.');(W/'material_edge_audit_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
