"""Short live-CAD mechanics entry control. No robot or cutting claim."""
from pathlib import Path
import sys,json,time,traceback
import numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_native_full_model import registry,configure_solver
from tomato_relative_full_model import RelativeObjectiveVBD,build_relative_model,configure_relative
from tomato_relative_contact import RelativeSurfaceContact
from tomato_local_frame import translated_registry,retain_canonical_material
from tomato_board_support import nodal_plane_stiffness
from tomato_live_cad_candidate import LiveCADCandidate
wp.init();wp.set_device('cuda:0');world=registry();world['x']+=[0,0,.002];origin=np.array([world['design']['cut_x_m'],0,.0295]);data,source_rest=translated_registry(world,origin);fixed=np.array(data['design']['fixture']['node_ids']);k=nodal_plane_stiffness(world);model=build_relative_model(data,fixed_nodes=fixed);h=configure_relative(configure_solver(model,data,iterations=1,solver_class=RelativeObjectiveVBD),data,board_stiffness=k,board_height=-origin[2]);retain_canonical_material(h,world,source_rest);h.surface_contact=RelativeSurfaceContact(data,h.spatial_reference,margin=.0001,capacity=256);h.surface_contact.physical_colors=model.particle_colors
s=LiveCADCandidate(h,data,fixed,maximum_outer=256,velocity_defect_budget_m_s=1e-6,declared_duration_s=.1);a,b=s.state(),s.state();prepared=np.load(r/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz');a.particle_q.assign(prepared['x_sim']);a.particle_qd.zero_();ref=np.load(r/'runs/offline/padded_cad_packet_20261102_01/cad_pressure_reference.npz');blade=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());R=ref['rotation'];t=ref['translation']-origin;packet={key:ref[key]for key in ['indices','barycentric','areas']};s.pressure.set_cad(vertices=blade['vertices'],triangles=blade['triangles'],**packet,rotation=R,translation=t,com_local=ref['com_local'],source_scope='Existing qualified padded contact packet');s.bind_domain(prepared['x_sim'],blade['vertices'],R,t)

from scipy.spatial.transform import Rotation
sys.path.insert(0,str(r/'.deps/ipctk-1.6.1-local-cp312'))
import ipctk
from tomato_cut_eligibility import CutEligibility
from tomato_swept_front import SweptFrontDetector
ipctk.set_num_threads(1)
reg=np.load(r/'runs/offline/cut_front_registration_20261102_02/cut_footprints.npz');front=json.loads((r/'runs/offline/cut_front_registration_20261102_02/registration.json').read_text())['front']['face_ids'];solid=json.loads((r/'work/exact_blade_cells.json').read_text());pose=np.r_[t+origin+[0,0,.0001],Rotation.from_matrix(R).as_quat()]
elig=CutEligibility(blade,solid,reg,front,SweptFrontDetector(ipctk),prepared['x_sim']+origin,pose)
trial=elig.trial(prepared['x_sim']+origin,np.r_[t+origin,pose[3:]])
result=dict(start_pose=pose.tolist(),end_pose=np.r_[t+origin,pose[3:]].tolist(),edge_candidates=len(trial.edge_candidates),inward=list(trial.inward_patches),overlap=list(trial.overlapping_patches),eligible=np.flatnonzero(trial.eligible).tolist(),scope='Geometry-only planned entry check; neither mechanical state nor eligibility committed')
(w/'entry_geometry.json').write_text(json.dumps(result,indent=2));print(result)
