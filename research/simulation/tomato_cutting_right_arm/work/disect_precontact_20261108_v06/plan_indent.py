from pathlib import Path
import sys,json,math,numpy as np
from blade_contact import CADBlade
W=Path(__file__).resolve().parent;assert json.loads((W/'settling_qualification.json').read_text())['passed'];assert json.loads((W/'blade_law_control_result.json').read_text())['passed'];assert json.loads((W/'blade_dashpot_control_result.json').read_text())['passed']
state=np.load(W/'settle_contact_final.npz');q=state['x'];mesh=np.load(W.parent/'disect_mesh_validation_20261108_v02/tomato_fem_mesh.npz');ids=np.unique(mesh['boundary']);cad=CADBlade();mapped=cad.vertices@cad.rotation.T;T=np.array([-.0225-np.median(mapped[:,0]),q[:,1].max()-mapped[:,1].min()+.001,-mapped[:,2].mean()]);queries=0
def distance(t):
    global queries
    queries+=1;return float(cad.query(q[ids],t)['phi'].min())
upper=T[1];assert distance(T)>0
for k in range(100):
    lower=upper-.001;trial=T.copy();trial[1]=lower
    if distance(trial)<0:break
    upper=lower
else:raise RuntimeError('No static contact bracket; do not force a pose')
for _ in range(35):
    mid=(upper+lower)/2;trial=T.copy();trial[1]=mid
    if distance(trial)>5e-6:upper=mid
    else:lower=mid
T[1]=(upper+lower)/2;initial_clearance=distance(T);bottom=T.copy();bottom[1]-=60e-6
mapping=np.load(W/'board_mapping.npz');route=json.loads((W.parents[1]/'work/single_slice_20261106/bodyward_withdrawal_plan_v1.json').read_text());direction=mapping['rotation'].T@np.array(route['direction_world']);assert abs(direction[1])<1e-10;direction[1]=0;direction/=np.linalg.norm(direction)
for n in range(1,101):
    displacement=n*1e-5;finish=bottom+direction*displacement
    if distance(finish)>=60e-6:break
else:raise RuntimeError('Bodyward withdrawal cannot clear within1mm; do not substitute upward motion')
local=(q[ids]-T)@cad.rotation;broad=np.all((local>=cad.minimum-.002)&(local<=cad.maximum+.002),axis=1);possible=ids[broad];free=np.setdiff1d(possible,mesh['fixed']);minimum_mass=float(mesh['mass'][free].min());elastic_bound=.5*np.sqrt(minimum_mass/2000);dt=min(7.462686567164179e-6,elastic_bound);sub=math.ceil(.0005/dt);dt=.0005/sub
out={'scope':'Frozen normal indentation/horizontal unloading plan for intact candidate only','initial_translation_m':T.tolist(),'blade_rotation':cad.rotation.tolist(),'initial_nodal_clearance_m':initial_clearance,'downward_stroke_m':60e-6,'bodyward_direction_sim':direction.tolist(),'horizontal_withdrawal_m':displacement,'horizontal_height_change_m':float(direction[1]*displacement),'final_static_clearance_m':distance(finish),'durations_s':[.015,.020,.010],'total_s':.045,'sample_interval_s':.0005,'selected_dt_s':dt,'substeps_per_sample':sub,'minimum_potential_contact_node_mass_kg':minimum_mass,'elastic_contact_dt_scale_s':elastic_bound,'source_orientation':'padded_cad_packet_20261102_01/cad_pressure_reference.npz','queries':queries,'passed':True};(W/'indent_plan.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
