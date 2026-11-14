from pathlib import Path
import numpy as np,json,hashlib,difflib,shutil,datetime
w=Path(__file__).resolve().parent;old=w.parent/'solver_comparison_20261108/vendor/DiSECt';r=w.parents[1]
# Keep independent geometry checks separate from solver's own Boolean flag.
d=np.load(w/'mesh_audit_input.npz');x=d['particle_x'];e=d['edge_indices'];c=d['edge_coords'];v=(1-c[:,None])*x[e[:,0]]+c[:,None]*x[e[:,1]]
mesh=json.loads((w/'mesh_audit.json').read_text());mesh['cut_surface_geometry']={}
for key in ['above','below']:
 f=d[key];p=v[f];area=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)/2
 _,ids=np.unique(np.round(v,10),axis=0,return_inverse=True);tri=ids[f[area>1e-15]];edges=np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1);u,n=np.unique(edges,axis=0,return_counts=True)
 mesh['cut_surface_geometry'][key]={'area_m2':float(area.sum()),'expected_prism_section_area_m2':.005,'edge_incidence_after_coordinate_merge_and_zero_area_exclusion':{str(k):int((n==k).sum()) for k in np.unique(n)},'interpretation':'Geometric audit only; merging/excluding were not applied to simulation. Correct summed area alone does not establish full valid topology.'}
mesh['solver_scope']='cut triangle arrays are referenced by visualization/model construction; dflex/sim.py does not reference them. Thus surface degeneracy does not prove material dynamics invalid; full mesh-validation contract remains unresolved.'
mesh['qualified']=False
(w/'mesh_audit.json').write_text(json.dumps(mesh,indent=2))
a=np.load(w/'forward01_final.npz');b=np.load(w/'forward02_final.npz');runs=[]
for n in ['01','02']:
 q=json.loads((w/f'forward{n}_result.json').read_text());z=np.load(w/f'forward{n}_final.npz');t=z['tet_indices'];ix=z['initial_x'];fx=z['x'];iv=np.linalg.det(ix[t[:,1:]]-ix[t[:,0]][:,None,:]);fv=np.linalg.det(fx[t[:,1:]]-fx[t[:,0]][:,None,:])
 runs.append({'id':n,'exit_code':0,'simulated_s':q['simulated_s'],'setup_wall_s':q['setup_wall_s'],'stepping_wall_s':q['wall_s'],'wall_s_per_sim_s':q['wall_s_per_sim_s'],'peak_rss_kib':q['peak_rss_kib'],'peak_torch_gpu_allocated_bytes':q['peak_gpu_allocated_bytes'],'peak_torch_gpu_reserved_bytes':q['peak_gpu_reserved_bytes'],'all_sampled_finite':all(i['finite'] for i in q['rows']),'final_minimum_signed_tet_ratio':float((fv/iv).min()),'final_inverted_tets':int((fv/iv<=0).sum()),'remaining_nonzero_cut_springs':int((z['stiffness']>0).sum()),'peak_force_resultant_model_N':float(max(np.linalg.norm(i['force_resultant']) for i in q['rows'])),'peak_sum_contact_force_magnitudes_model_N':max(i['force_sum_norm'] for i in q['rows'])})
result={'date':'2026-11-08','scope':'Bounded DiSECt feasibility study stopped at full mesh-validation gate. No tomato dynamics, robot integration or training.','decision':'Retain DiSECt for restricted isolated feasibility work; do not integrate yet.','compatibility':{'native_memory_lifetime_repair':'Copy edge endpoints by value before vertex vector growth; native mesher now returns true.','shutdown':'gdb stack in Torch autograd graph destruction; explicitly disable Torch gradient recording for forward-only motion. Two full runs exit 0. This is not gradient/backward compatibility qualification.','preliminary_import_attempts':'attempt01 and attempt02 failed before physics because copied generated-kernel cache lacked kernels.so; copied unchanged binary from prior benchmark, hash recorded.','full_mesh_validation':'OPEN: cut-surface degenerate and duplicate faces retained and independently counted; no silent filtering/threshold change.'},'runs':runs,'repeat_max_position_difference_m':float(np.linalg.norm(a['x']-b['x'],axis=1).max()),'repeat_max_spring_stiffness_difference':float(abs(a['stiffness']-b['stiffness']).max()),'tomato_source_exported':True,'tomato_cut_passed':False,'robot_integrated_cut_passed':False,'experimental_validation':'pending','original_run':'paused at checkpoint 6925, not resumed','next_action':'One focused mesh-preparation validation/fix using analytic prism and tomato exterior. Keep material springs/connectivity unchanged; validate complete cut-face coverage and nondegenerate unique triangles. Inspect original tomato cells for FEM conformity before dynamics. If this needs broad remesher development, report replacement mesh options before work.'}
(w/'result.json').write_text(json.dumps(result,indent=2))
patch=[]
for name in ['meshing/meshing.cpp','dflex/model.py']:
 patch.extend(difflib.unified_diff((old/name).read_text().splitlines(True),(w/'DiSECt'/name).read_text().splitlines(True),fromfile='before/'+name,tofile='after/'+name))
(w/'focused_repairs.patch').write_text(''.join(patch))
checkpoint=r/'work/single_slice_20261106/robot_cut18/checkpoints/step_006925.npz'
files=[w/'USER_CONTRACT.txt',w/'contract.json',w/'focused_repairs.patch',w/'example_forward.py',w/'DiSECt/dflex/kernels/kernels.so',old/'dflex/kernels/kernels.so',checkpoint]
(w/'preserved_inputs.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()},indent=2))
print(json.dumps(result,indent=2))
