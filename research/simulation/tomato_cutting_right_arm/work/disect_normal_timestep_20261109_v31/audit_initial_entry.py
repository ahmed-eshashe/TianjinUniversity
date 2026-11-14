from pathlib import Path
import json,numpy as np
from scipy.optimize import brentq
from scipy.interpolate import PchipInterpolator
W=Path(__file__).resolve().parent;R=W.parents[1]
z=np.load(W.parent/'disect_physical_20261109_v22/settle_contact_final.npz');mesh=np.load(W.parent/'disect_completion_20261108_v18/conforming_split.npz')
pair=mesh['ties'];mid=z['x'][pair].mean(1);front=mid[mid[:,1].argmax()]
cad=json.loads((R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());ref=np.load(R/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz')
A=np.array([[1,0,0],[0,0,-1],[0,1,0]],float);rotation=A.T@ref['rotation'];plan=json.loads((W/'correction_plan.json').read_text());T=np.array(plan['selected']['translation_m']);v=np.array(cad['vertices'])@rotation.T+T;faces=np.array(cad['triangles']);points=[]
for face in faces:
 for a,b in [(face[0],face[1]),(face[1],face[2]),(face[2],face[0])]:
  da=v[a,2]-front[2];db=v[b,2]-front[2]
  if abs(da)<1e-14:points.append(v[a])
  if da*db<0:points.append(v[a]+(-da/(db-da))*(v[b]-v[a]))
points=np.array(points);assert len(points);low=points[:,1].min();edge=points[points[:,1]<=low+1e-8];apex=np.array([(edge[:,0].min()+edge[:,0].max())/2,low,front[2]])
clearance=apex[1]-front[1];curve=PchipInterpolator(*np.array(plan['front_lateral_path_m']).T)
result={'scope':'Read-only initial settled interface versus exact CAD apex cross-section; not a contact/trajectory correction or a claim about loaded target motion','front_point_m':front.tolist(),'initial_apex_at_same_z_m':apex.tolist(),'initial_vertical_apex_clearance_m':float(clearance),'source_triangles':len(faces)}
if 0<=clearance<=plan['downward_stroke_m']:
 def depth(t):
  u=t/plan['durations_s'][0];return plan['downward_stroke_m']*(10*u**3-15*u**4+6*u**5)
 t=brentq(lambda t:depth(t)-clearance,0,plan['durations_s'][0]);position=apex+np.array([float(curve(clearance)),-clearance,0])
 result.update(predicted_initial_apex_crossing_time_s=t,predicted_initial_lateral_apex_offset_m=float(position[0]-front[0]),apex_x_width_at_tolerance_m=float(edge[:,0].max()-edge[:,0].min()))
(W/'initial_entry_geometry_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
