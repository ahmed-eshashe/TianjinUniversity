"""Locate swept minima in saved states; no mechanics solve or state acceptance."""
import os,sys,json,hashlib,resource,signal,fcntl,time
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];F=Path(__file__).parent;V=R/'runs/offline/tomato_curvature_search_01'
resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
now=datetime.now(timezone.utc);assert now<datetime(2026,10,26,4,53,35,tzinfo=timezone.utc)
lease=json.loads((R/'runs/offline/tomato_triangle_withdrawal_01/quota_lease.json').read_text());assert 0<=(now-datetime.fromisoformat(lease['checked_utc'])).total_seconds()<=480 and lease['maximum_reported_used_percent']<45
for n in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:assert os.environ[n]=='1'
parent=(R/'logs/offline_overnight.lock').open('a');fcntl.flock(parent,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock=(R/'logs/right_arm_control.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
start=time.monotonic();sys.path.insert(0,str(R/'rl'))
import numpy as np
from tomato_coupled_contact import assemble_model,cut_pairs
from tomato_triangle_contact import triangle_geometry,swept_triangle_gap
from tomato_blade_damage import BLADE
from audit_tomato_triangle_contact import minimum_polygon_gap
source=R/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5';design=json.loads((source/'surface_design.json').read_text());assign=json.loads((source/'mass_stiffness_assignments.json').read_text());points,_=assemble_model(design,assign,0.);pairs=cut_pairs(design)
def read(folder,allow_rejected=False):
 s=json.loads((folder/'summary.json').read_text());assert s['passed'] or (allow_rejected and s['flags']==['contact'])
 for n,h in s['source_hashes'].items():assert digest(R/n)==h
 for n,h in s['state_hashes'].items():assert digest(folder/n)==h
 return s,np.load(folder/'positions.npy')
records=[]
cases=['insertion06_global_seed/attempt005','insertion09_refined_global/attempt004','insertion11_quarter_global/attempt004','insertion14_small_global/attempt004','insertion16_sixteenth_global/attempt003','insertion18_small_global/attempt004','insertion20_small_global/attempt004']
for name in cases:
 folder=V/name;s,new=read(folder,True);prev=R/s['previous_checkpoint'];old_s,old=read(prev);assert digest(prev/'summary.json')==s['previous_summary_sha256']
 old_tip,new_tip=old_s['tip_z_m'],s['tip_z_m'];dt=new_tip-old_tip;knots={0.,1.}
 for z in points[pairs[:,0],2]:
  for event in [z,z-BLADE['single_bevel_length_m']]:
   t=(event-old_tip)/dt
   if 0<t<1:knots.add(float(t))
 knots=sorted(knots);best=None
 for a,b in zip(knots[:-1],knots[1:]):
  geometries=[triangle_geometry(design,points,pairs,old_tip+(a+(b-a)*u)*dt) for u in [0.,.5,1.]]
  gaps=[g['matrix']@(old+(a+(b-a)*u)*(new-old)).ravel()-g['physical'] for g,u in zip(geometries,[0.,.5,1.])]
  rows=np.flatnonzero(geometries[1]['active']);f0,fm,f1=[v[rows] for v in gaps];c=2*(f1+f0-2*fm);d=f1-f0-c
  u=np.zeros(len(rows));good=np.abs(c)>1e-18;u[good]=-d[good]/(2*c[good]);inside=good&(u>0)&(u<1)
  choices=[(f0,np.zeros(len(rows))),(f1,np.ones(len(rows)))]
  values=np.full(len(rows),np.inf);values[inside]=f0[inside]+d[inside]*u[inside]+c[inside]*u[inside]**2;choices.append((values,u))
  for vals,us in choices:
   j=int(np.argmin(vals));value=float(vals[j]);row=int(rows[j]);t=a+(b-a)*float(us[j])
   if best is None or value<best['minimum_gap_m']:
    cross=float(((geometries[2]['matrix'].getrow(row)-geometries[0]['matrix'].getrow(row))@((b-a)*(new-old)).ravel())[0])
    best={'minimum_gap_m':value,'row':row,'time_fraction':t,'activation_interval':[a,b],'interval_fraction':float(us[j]),'quadratic_coefficient_m':float(c[j]),'moving_weights_cross_term_m':cross,'fit_cross_error_m':abs(cross-float(c[j])),'row_gap_at_interval_start_m':float(f0[j]),'row_gap_at_interval_end_m':float(f1[j])}
 t=best['time_fraction'];x=old+t*(new-old);g=triangle_geometry(design,points,pairs,old_tip+t*dt);row=best['row'];exact=float((g['matrix'].getrow(row)@x.ravel())[0]-g['physical'][row]);poly,count=minimum_polygon_gap(design,x,old_tip+t*dt,BLADE);reference=swept_triangle_gap(design,points,pairs,old,new,old_tip,new_tip)
 assert abs(best['minimum_gap_m']-reference)<1e-12 and abs(best['minimum_gap_m']-s['swept_blade_minimum_gap_m'])<1e-12
 assert abs(exact-best['minimum_gap_m'])<1e-12 and abs(poly-best['minimum_gap_m'])<1e-12 and best['fit_cross_error_m']<1e-12
 if row>=g['base_rows']:kind=g['cap_rows'][row-g['base_rows']]['kind'];nodes=g['cap_rows'][row-g['base_rows']]['nodes']
 else:kind='cut_contact' if row<len(pairs) else 'blade_vertex';nodes=[]
 best.update(checkpoint=str(folder.relative_to(R)),summary_sha256=digest(folder/'summary.json'),previous_summary_sha256=digest(prev/'summary.json'),previous_depth_mm=old_s['depth_mm'],depth_mm=s['depth_mm'],step_mm=s['depth_mm']-old_s['depth_mm'],physical_endpoint_previously_accepted=s['passed'],constraint_kind=kind,nodes=nodes,direct_row_gap_m=exact,independent_polygon_gap_m=poly,polygon_vertices=count,original_swept_function_gap_m=reference,maximum_nodal_step_m=float(np.linalg.norm(new-old,axis=1).max()),physical_source_hashes=s['source_hashes']);records.append(best)
assert not any(n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'} for n in sys.modules)
report={'diagnostic_only':True,'new_physical_endpoints_accepted':False,'states_or_damage_or_work_changed':False,'source_hashes':{str(Path(__file__).relative_to(R)):digest(Path(__file__))},'records':records,'runtime_s':time.monotonic()-start,'max_rss_bytes':int(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))*1024,'simulator':False,'training':False}
(F/'swept_path_diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print({k:report[k] for k in ['runtime_s','max_rss_bytes','new_physical_endpoints_accepted']});print([{k:v[k] for k in ['depth_mm','constraint_kind','time_fraction','minimum_gap_m','quadratic_coefficient_m']} for v in records])
