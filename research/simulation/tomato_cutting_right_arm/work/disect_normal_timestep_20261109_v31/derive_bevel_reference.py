from pathlib import Path
import json,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[1]
b=json.loads((W/'initial_entry_geometry_audit.json').read_text());p=json.loads((W/'correction_plan.json').read_text());T=np.array(p['selected']['translation_m']);plane=np.array(b['front_point_m'])[2];raw=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rot=A.T@ref['rotation'];v=np.array(raw['vertices'])@rot.T+T;faces=np.array(raw['triangles']);coords=[];lookup={};adj={}
def index(point):
 key=tuple(np.round(point,12))
 if key not in lookup:lookup[key]=len(coords);coords.append(point);adj[lookup[key]]=set()
 return lookup[key]
for face in faces:
 ps=[]
 for i,j in [(face[0],face[1]),(face[1],face[2]),(face[2],face[0])]:
  a=v[i,2]-plane;b0=v[j,2]-plane
  if a*b0<0:ps.append(v[i]+(-a/(b0-a))*(v[j]-v[i]))
 if len(ps)==2:
  i,j=map(index,ps);adj[i].add(j);adj[j].add(i)
coords=np.array(coords);start=int(coords[:,1].argmin());assert len(adj[start])==2
other=min(adj[start],key=lambda j:abs(coords[j,1]-coords[start,1])/max(abs(coords[j,0]-coords[start,0]),1e-20));direction=coords[other]-coords[start];direction/=np.linalg.norm(direction);prev=start;current=other
for _ in range(len(coords)):
 nexts=adj[current]-{prev};assert len(nexts)==1
 nxt=next(iter(nexts));dd=coords[nxt]-coords[current];dd/=np.linalg.norm(dd)
 if np.dot(dd,direction)<1-1e-7:break
 prev,current=current,nxt
else:raise RuntimeError('No bevel end found')
left=coords[start];right=coords[current];center=(left+right)/2
out={'scope':'Exact CAD finite leading-bevel cross-section reference; this is a motion reference convention, not a change to the CAD/mount/contact/material law.','lowest_corner_world_m':left.tolist(),'other_bevel_corner_world_m':right.tolist(),'leading_bevel_midpoint_world_m':center.tolist(),'leading_bevel_midpoint_rotated_local_m':(center-T).tolist(),'edge_width_m':float(np.linalg.norm(right-left)),'world_x_span_m':float(right[0]-left[0]),'world_y_span_m':float(right[1]-left[1]),'fixed_world_z_m':float(plane)}
(W/'leading_bevel_reference.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
