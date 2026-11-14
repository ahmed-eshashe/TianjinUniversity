from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W.parent/'disect_precontact_20261108_v06'));from blade_contact import CADBlade
cad=CADBlade();a=json.loads((W/'edge_alignment_diagnostic.json').read_text());z=a['CAD_cross_section_z_m'];y0=a['CAD_lowest_edge_points_m'][0][1];v=cad.vertices@cad.rotation.T;segments=[]
for t in cad.triangles:
 points=[]
 for i,j in [(0,1),(1,2),(2,0)]:
  p=v[t[i]];q=v[t[j]]
  if (p[2]-z)*(q[2]-z)<0:points.append(p+(z-p[2])/(q[2]-p[2])*(q-p))
 if len(points)==2:segments.append(points)
rows=[]
for depth in [.0001,.0005,.001,.002,.004,.008,.012,.016,.020,.025,.030,.035,.04]:
 y=y0+depth;xs=[]
 for p,q in segments:
  if (p[1]-y)*(q[1]-y)<0:xs.append(p[0]+(y-p[1])/(q[1]-p[1])*(q[0]-p[0]))
 if xs:rows.append(dict(depth_m=depth,knife_width_x_m=max(xs)-min(xs),medial_x_m=.5*(max(xs)+min(xs)),medial_drift_from_edge_m=.5*(max(xs)+min(xs))-a['CAD_lowest_edge_points_m'][0][0]))
out=dict(scope='Exact triangle cross-section; geometric planning only, not an imposed opening or fracture predictor',rows=rows,original_onset_m=.001,original_failure_m=.004);(W/'wedge_profile_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
