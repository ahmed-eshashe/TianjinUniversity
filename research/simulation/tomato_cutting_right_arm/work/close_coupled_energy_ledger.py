from pathlib import Path
import sys,json,math
ROOT=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(ROOT/'rl'))
from tomato_reaction_metadata import quaternion_rotation
from tomato_wrench_contract import dot
from audit_coupled_energy import audit_case

def potential(p,pose,width,k):
 normal=[row[1] for row in quaternion_rotation(pose[3:])]
 d=width-dot(normal,[x-y for x,y in zip(p,pose[:3])])
 return .5*k*max(d,0.)**2,d
m=json.loads((ROOT/'runs/native/bent_replay_20261101_01/bent_replay_measurements.json').read_text());results=[]
for c in m['episodes'][0]:
 audit=audit_case(c);pose=c['initial_link_packet']['link_pose'];k=1750.;u0,_=potential(c['initial']['p'],pose,c['half_width_m'],k);previous=u0
 total_spring_loss=total_split=total_numerical=total_kinetic=0.;records=[]
 for s,a in zip(c['steps'],audit['records']):
  up,dp=potential(s['before']['p'],pose,c['half_width_m'],k)
  us,ds=potential(s['after']['p'],pose,c['half_width_m'],k)
  newpose=s['after_link_packet']['link_pose'];uf,_=potential(s['after']['p'],newpose,c['half_width_m'],k)
  spring_loss=.5*k*(max(dp,0.)-max(ds,0.))**2
  spring_identity=(us-up)+a['particle_force_work_j']+spring_loss
  split=(uf-us)+a['chain_generalized_work_j']
  numerical=a['implicit_particle_loss_j']+spring_loss+a['tgs_schedule_work_correction_j']
  delta_k=a['particle_kinetic_change_j']+a['chain_kinetic_change_j'];res=delta_k+uf-up+numerical-split
  total_spring_loss+=spring_loss;total_split+=split;total_numerical+=numerical;total_kinetic+=delta_k
  records.append(dict(interval=s['interval'],spring_work_identity_error_j=spring_identity,splitting_energy_defect_j=split,numerical_loss_j=numerical,closed_ledger_residual_j=res))
  pose=newpose;previous=uf
 residual=total_kinetic+previous-u0+total_numerical-total_split;gate=.01*u0+1e-12
 if abs(residual)>gate or abs(total_split)>gate or min(r['numerical_loss_j'] for r in records)<-1e-12:raise ValueError('Coupled contact energy qualification failed')
 results.append(dict(id=c['id'],initial_contact_potential_j=u0,final_contact_potential_j=previous,final_total_kinetic_j=total_kinetic,
   total_recorded_numerical_loss_j=total_numerical,total_splitting_defect_j=total_split,closed_ledger_residual_j=residual,gate_j=gate,relative_closed_residual=abs(residual)/u0,relative_splitting_defect=abs(total_split)/u0,passed=True,records=records))
(ROOT/'work/closed_coupled_energy_ledger.json').write_text(json.dumps(results,indent=2)+'\n')
for r in results:print({k:v for k,v in r.items() if k!='records'})
