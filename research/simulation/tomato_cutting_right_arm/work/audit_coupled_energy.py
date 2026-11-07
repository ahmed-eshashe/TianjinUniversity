"""Saved-state work ledger; no native imports or stepping."""
from pathlib import Path
import json,math,sys
ROOT=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');sys.path.insert(0,str(ROOT/'rl'))
from tomato_bent_rebased_reference import dynamics
from tomato_wrench_contract import dot
DT=1/2400

def kinetic(q,v):
 m=dynamics(q,v,[0.,0.])[0]
 return .5*sum(v[i]*m[i][j]*v[j] for i in range(2) for j in range(2))
def audit_case(c):
 records=[];total_r=total_p=total_wr=total_wp=0.
 for s in c['steps']:
  b=s['before'];a=s['after'];mp=c['particle_mass_kg'];f=s['force_n'];w=s['wrench']
  dp=[x-y for x,y in zip(a['p'],b['p'])];dv=[x-y for x,y in zip(a['vp'],b['vp'])]
  dkp=.5*mp*(dot(a['vp'],a['vp'])-dot(b['vp'],b['vp']));wp=dot(f,dp);loss=.5*mp*dot(dv,dv)
  particle_residual=dkp-wp+loss
  dkr=kinetic(a['q'],a['qd'])-kinetic(b['q'],b['qd'])
  # Analytic world end-COM Jacobian at input physical angles.
  from tomato_two_joint_sequence_reference import geometry
  from tomato_bent_rebased_reference import physical_angles
  _,j=geometry(c['yaw'],physical_angles(b['q']));effort=[sum(j[k][n]*w[k] for k in range(6)) for n in range(2)]
  dq=[x-y for x,y in zip(a['q'],b['q'])];wr=dot(effort,dq)
  matrix,bias,acc=dynamics(b['q'],b['qd'],effort)
  tgs=DT*DT/32*dot(effort,acc)
  rigid_residual=dkr-wr+tgs
  # Both work terms are physical path work; the split contact lag is retained.
  total_r+=dkr;total_p+=dkp;total_wr+=wr;total_wp+=wp
  records.append(dict(interval=s['interval'],particle_kinetic_change_j=dkp,particle_force_work_j=wp,implicit_particle_loss_j=loss,
   particle_work_residual_j=particle_residual,chain_kinetic_change_j=dkr,chain_generalized_work_j=wr,tgs_schedule_work_correction_j=tgs,chain_work_residual_j=rigid_residual,
   transfer_work_sum_j=wp+wr))
 scale=max(abs(total_wr),abs(total_wp),1e-12);gate=.01*scale+1e-12
 residual=max(abs(sum(x['particle_work_residual_j'] for x in records)),abs(sum(x['chain_work_residual_j'] for x in records)))
 if residual>gate:raise ValueError(f'Energy ledger mismatch {residual} > {gate}')
 return dict(id=c['id'],records=records,particle_work_j=total_wp,chain_work_j=total_wr,chain_kinetic_change_j=total_r,particle_kinetic_change_j=total_p,
  cumulative_particle_residual_j=sum(x['particle_work_residual_j'] for x in records),cumulative_chain_residual_j=sum(x['chain_work_residual_j'] for x in records),gate_j=gate,
  passed=True,closed_contact_potential_ledger_validated=False)
if __name__=='__main__':
 m=json.loads((ROOT/'runs/native/bent_replay_20261101_01/bent_replay_measurements.json').read_text())
 a=[audit_case(c) for c in m['episodes'][0]]
 (ROOT/'work/coupled_energy_audit.json').write_text(json.dumps(a,indent=2)+'\n')
 for c in a:print({k:v for k,v in c.items() if k!='records'})
