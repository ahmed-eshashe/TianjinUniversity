"""Actual CAD padded-material packet against independently generated quadrature."""
from pathlib import Path
import json,hashlib,time,traceback
import numpy as np
from scipy.spatial.transform import Rotation
from tomato_padded_material_coverage import padded_coverage,signed_uv_area
from tomato_host_fixed_pressure import packet_from_samples,evaluate_fixed
from tomato_exact_blade_coverage import coverage
R=Path(__file__).resolve().parents[2];out=R/'runs/offline/padded_cad_packet_20261102_02';out.mkdir(exist_ok=False);reference_path=R/'runs/offline/prepared_contact_candidate_20261102_03/fixed_cad_pressure_reference.npz';prepared=R/'runs/native/static_preparation_cached_20261102_01/prepared_equilibrium.npz';blade_path=R/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json';cells_path=R/'work/exact_blade_cells.json';design=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json';inputs=[reference_path,prepared,blade_path,cells_path,design,Path(__file__),R/'rl/tomato_padded_material_coverage.py',R/'rl/tomato_host_fixed_pressure.py',R/'rl/tomato_host_blade_geometry.py'];pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs};(out/'input_manifest.json').write_text(json.dumps(dict(source_sha256=pins,padding_m=4e-5,quadrature_relative_force_budget=.01,quadrature_absolute_force_budget_n=1e-5,quadrature_relative_energy_budget=.01,quadrature_absolute_energy_budget_j=1e-11,fixed_packet_fd_budget_n_or_nm=1e-7,translation_fd_eps_m=[1e-10,1e-11],rotation_fd_eps_rad=[1e-9,1e-10],scope='Host padded-domain ownership/coverage and exact fixed-material CAD force/energy controls. No native query, actual relative-motion bound, mechanics, robot feedback/work, CCD or cut qualification.'),indent=2)+'\n');start=time.monotonic()
try:
 z=np.load(reference_path);x=z['x'];rotation=z['rotation'];translation=z['translation'];com=z['com_local'];blade=json.loads(blade_path.read_text());cell_data=json.loads(cells_path.read_text());cells=np.array(cell_data['cells']);v=np.array(cell_data['vertices']);d=json.loads(design.read_text());triangles=np.array([tri for piece in d['pieces']for tri in piece['triangles']]);material=np.load(prepared)['reference_world'];g=[];previous=None;passed=False
 for level in [1,2,3,4,5]:
  domain=padded_coverage(v@rotation.T+translation,cells,x,triangles,material,padding_m=4e-5,level=level);packet=packet_from_samples(domain['samples']);np.savez(out/'latest_material_packet.npz',x=x,rotation=rotation,translation=translation,com_local=com,**packet);value=evaluate_fixed(blade,x,packet,rotation,translation,com);scale=max(float(np.linalg.norm(z['force'])),float(np.linalg.norm(value['force_n'])),1e-12);reference_error=float(np.linalg.norm(value['force_n']-z['force']));step_error=None if previous is None else float(np.linalg.norm(value['force_n']-previous['force_n']));energy_error=float(abs(value['energy_j']-z['energy'][0]));row=dict(level=level,samples=len(packet['areas']),reference_area_m2=domain['reference_area_m2'],removed_duplicate_reference_area_m2=domain['raw_duplicated_reference_area_m2']-domain['reference_area_m2'],force_reference_error_n=reference_error,successive_force_error_n=step_error,force_scale_n=scale,energy_reference_error_j=energy_error);g.append(row);(out/'quadrature_partial.json').write_text(json.dumps(g,indent=2)+'\n');print(row,flush=True)
  if previous is not None and reference_error<=.01*scale+1e-5 and step_error<=.01*scale+1e-5 and energy_error<=.01*abs(z['energy'][0])+1e-11:passed=True;break
  previous=value
 if not passed:raise ValueError('Padded CAD packet did not reach fixed reference/force/energy convergence bounds')
 fd=[];center=translation+rotation@com
 for axis in range(6):
  errors=[]
  for eps in ([1e-10,1e-11]if axis<3 else[1e-9,1e-10]):
   if axis<3:
    delta=np.eye(3)[axis]*eps;plus=evaluate_fixed(blade,x,packet,rotation,translation+delta,com)['energy_j'];minus=evaluate_fixed(blade,x,packet,rotation,translation-delta,com)['energy_j']
   else:
    delta=np.eye(3)[axis-3]*eps;rp=Rotation.from_rotvec(delta).as_matrix()@rotation;rm=Rotation.from_rotvec(-delta).as_matrix()@rotation;plus=evaluate_fixed(blade,x,packet,rp,center-rp@com,com)['energy_j'];minus=evaluate_fixed(blade,x,packet,rm,center-rm@com,com)['energy_j']
   errors.append(float(abs(-(plus-minus)/(2*eps)-value['body_wrench'][axis])))
  fd.append(dict(case='rigid_axis_'+str(axis),errors_n_or_nm=errors));(out/'fd_partial.json').write_text(json.dumps(fd,indent=2)+'\n')
  if not np.isfinite(errors).all()or max(errors)>1e-7:raise ValueError(('Padded packet rigid derivative failed',fd[-1]))
 rng=np.random.default_rng(771);active=np.unique(packet['indices'])
 for case in range(3):
  direction=np.zeros_like(x);direction[active]=rng.normal(size=(len(active),3));direction/=np.linalg.norm(direction);errors=[]
  for eps in [1e-10,1e-11]:
   plus=evaluate_fixed(blade,x+eps*direction,packet,rotation,translation,com)['energy_j'];minus=evaluate_fixed(blade,x-eps*direction,packet,rotation,translation,com)['energy_j'];errors.append(float(abs(-(plus-minus)/(2*eps)-np.sum(value['force_n']*direction))))
  fd.append(dict(case='nodal_direction_'+str(case),errors_n_or_nm=errors));(out/'fd_partial.json').write_text(json.dumps(fd,indent=2)+'\n')
  if not np.isfinite(errors).all()or max(errors)>1e-7:raise ValueError(('Padded packet nodal derivative failed',fd[-1]))
 motion=[];up=rotation[:,1]
 for shift in [up*18e-6,-up*18e-6,rotation[:,2]*18e-6]:
  actual=coverage(v@rotation.T+translation+shift,cells,x,triangles,reference_positions=material,quadrature_level=1);miss=0
  for sample in actual['samples']:
   b=np.array(sample['barycentric']);found=False
   for polygon in domain['polygons_by_triangle'].get(sample['triangle_id'],[]):
    poly=np.array(polygon)
    if signed_uv_area(poly)<0:poly=poly[::-1]
    inside=True
    for index,first in enumerate(poly):
     edge=poly[(index+1)%len(poly),1:]-first[1:];normal=np.array([edge[1],-edge[0]])
     if normal@(b[1:]-first[1:])>1e-10:inside=False;break
    if inside:found=True;break
   if not found:miss+=1
  motion.append(dict(rigid_translation_m=shift.tolist(),actual_generated_samples=len(actual['samples']),samples_outside_original_padded_material_domain=miss))
  if miss:raise ValueError(('Relative motion coverage sample failed',motion[-1]))
 if not all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in pins.items()):raise ValueError('Padded packet inputs/source changed')
 np.savez(out/'cad_pressure_reference.npz',x=x,x_sim=z['x_sim'],world_from_sim_translation_m=z['world_from_sim_translation_m'],rotation=rotation,translation=translation,com_local=com,force=value['force_n'],body_wrench=value['body_wrench'],energy=np.array([value['energy_j']]),phi=value['query']['phi'],normal_local=value['query']['normal'],closest_local=value['query']['closest'],face=value['query']['face'],**packet);(out/'material_domains.json').write_text(json.dumps(domain['polygons_by_triangle'],separators=(',',':'))+'\n');report=dict(passed=True,quadrature=g,derivatives=fd,relative_motion_coverage_samples=motion,scope='Actual-CAD HOST positive fixed material quadrature packet, padded ownership/convergence/force-potential controls and three 18-micrometre translated-geometry sample screens. No native force, actual per-step motion bound, CCD, physics, mounted work or cut qualification.',elapsed_wall_s=time.monotonic()-start,source_sha256=pins);(out/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');print('PADDED_HOST_PASS',report['elapsed_wall_s'],flush=True)
except BaseException:
 (out/'failure.json').write_text(json.dumps(dict(traceback=traceback.format_exc(),source_sha256=pins,scope='Incomplete host padded packet only; no native/physical qualification attempted.'),indent=2)+'\n');raise
