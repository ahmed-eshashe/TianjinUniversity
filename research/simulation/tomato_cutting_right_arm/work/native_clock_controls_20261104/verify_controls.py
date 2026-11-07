from pathlib import Path
import csv,json,math
w=Path(__file__).resolve().parent
out={}
for name in ['zero','driven']:
 lines=(w/name/'trace.csv').read_text().splitlines();rows=list(csv.DictReader(lines[1:-1]));states=list(csv.DictReader((w/name/'states.csv').open()));assert lines[-1]=='END count=80 dropped=0 passes=80';assert len(rows)==80
 tests=[];previous=0.0
 for i in range(2):
  block=rows[i*40:(i+1)*40];v=float(states[i]['velocity']);imp=sum(float(x['drive_impulse']) for x in block);energy=sum(float(x['drive_impulse'])*(float(x['local_velocity_before'])+float(x['local_velocity_after']))/2 for x in block)
  expected=(1-(2/(2+4*(1/240)/32))**(32*(i+1))) if name=='driven' else 0
  check={'step':i,'momentum_error':abs(imp-2*(v-previous)),'kinetic_energy_error_j':abs(energy-(v*v-previous*previous)),'implicit_euler_velocity_error':abs(v-expected),'ordering':all(int(x['pass'])==i*40+j+1 and int(x['dof'])==0 and int(x['link'])==1 and int(x['flags'])==(5 if j<32 else 7) for j,x in enumerate(block))}
  check['passed']=check['momentum_error']<=1e-7 and check['kinetic_energy_error_j']<=1e-8 and check['implicit_euler_velocity_error']<=1e-7 and check['ordering'];tests.append(check);previous=v
 out[name]=tests
out['analytic_fixture_passed']=all(x['passed'] for name in ['zero','driven'] for x in out[name]);out['robot_motor_work_qualified']=False
(w/'analytic_results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
# Describe robot trace blocks without claiming alignment to Python step labels.
p=w.parent/'native_instrumentation_20261102/capture_on01/native_trace.csv';lines=p.read_text().splitlines();rows=list(csv.DictReader(lines[1:-1]));passes={}
for x in rows:passes.setdefault(int(x['pass']),[]).append(x)
blocks=[list(passes.values())[i:i+40] for i in range(0,len(passes),40)]
report={'passes':len(passes),'rows':len(rows),'candidate_40_pass_blocks':len(blocks),'every_pass_has_36_unique_dofs':all(len(b)==36 and {int(x['dof']) for x in b}==set(range(36)) for b in passes.values()),'each_block_32_position_8_velocity':all(len(b)==40 and all({int(x['flags']) for x in rr}=={5 if j<32 else 7} for j,rr in enumerate(b)) for b in blocks),'reported_capture_and_monitor_steps':123,'extra_candidate_blocks':len(blocks)-123,'absolute_clock_mapping_qualified':False,'reason':'Initialization calls outside Python step counter exist. Trace has no explicit boundary markers; do not assign extra blocks to named phases by subtraction alone.'}
(w/'robot_clock_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
