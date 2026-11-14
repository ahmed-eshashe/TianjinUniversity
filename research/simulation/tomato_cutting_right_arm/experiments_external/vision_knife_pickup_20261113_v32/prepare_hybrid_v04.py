from pathlib import Path
import json
W=Path(__file__).resolve().parent
s=(W/'hybrid_pickup_v03.py').read_text()
s=s.replace("close_start_s=0.;start=time.monotonic()", "close_start_s=0.;thumb_close_start=None;finger_touch_s=0.;start=time.monotonic()")
s=s.replace('global step,last,hold,reference,initial_height,max_force_seen,max_mimic_error,grip_ready_s,last_command,policy_hidden,policy_initial,policy_previous_action','global step,last,hold,reference,initial_height,max_force_seen,max_mimic_error,grip_ready_s,last_command,policy_hidden,policy_initial,policy_previous_action,thumb_close_start,finger_touch_s')
s=s.replace("  if update_command and pressure and args.compliant:\n   actual=", """  if pressure and args.compliant and phase=='close':
   finger_touch_s=finger_touch_s+dt if last is not None and last['loads']['index']>.2 else 0.
   if thumb_close_start is None and finger_touch_s>=.05:thumb_close_start=step*dt
  if update_command and pressure and args.compliant:
   actual=""")
needle="    target[0,hids[index]]=min(float(actual[hids[index]])+eff/stiffness,float(.315 if part=='thumb' else min(1.45,grasp_hand[index]+args.finger_extra_flex)))"
replace="""    if part=='thumb':
     if thumb_close_start is None:
      target[0,hids[index]]=float(pre_hand[index]);continue
     eff*=min(1.,max(0.,(step*dt-thumb_close_start)/1.))
    target[0,hids[index]]=min(float(actual[hids[index]])+eff/stiffness,float(.315 if part=='thumb' else min(1.45,grasp_hand[index]+args.finger_extra_flex)))"""
assert needle in s;s=s.replace(needle,replace)
s=s.replace("(out/'before_lift.json').write_text(json.dumps(last,indent=2));capture('grasp')", "(out/'before_lift.json').write_text(json.dumps(last,indent=2));(out/'closure_sequence.json').write_text(json.dumps(dict(finger_contact_before_thumb=True,thumb_close_start_s=thumb_close_start,index_contact_threshold_N=.2,index_contact_dwell_s=.05,thumb_ramp_s=1.),indent=2));capture('grasp')")
(W/'hybrid_pickup_v04.py').write_text(s)
cmd=json.loads((W/'reports/hybrid_fine_diagnostic_command.json').read_text());cmd[2]=str(W/'hybrid_pickup_v04.py');cmd[4]=str(W/'datasets/hybrid_v04_development/train_012')
ep=next(x for x in json.loads((W/'curriculum_split_v01.json').read_text())['episodes'] if x['id']=='train_012')
for key in ['dx','dy','yaw_deg']:cmd[cmd.index('--'+key.replace('_','-'))+1]=str(ep[key])
cmd+=['--close-seconds','4.'];(W/'reports/hybrid_sequenced_candidate_command.json').write_text(json.dumps(cmd))
(W/'reports/hybrid_v03_test_gate_failure.txt').write_text('v03 failed independent qualification: 2 of 4 attempted held-out placements passed; test_002 and test_003 stopped on excessive closure contact loads. Batch stopped after the second failure. test_004..007 were not run. All outcomes preserved. Inspected failures are now development evidence; any later qualified candidate needs fresh reserved placements, not relabelled old tests. No safety/success threshold is relaxed.\n')
(W/'reports/hybrid_sequenced_candidate.txt').write_text('v04 controller candidate: saved geometry shows fingertips remain above the board, but the thumb loads the knife before index contact develops. Test index-first closure: hold the thumb at its pregrasp angle until index normal contact exceeds .2 N for .05 s, then ramp existing .65 Nm thumb effort over 1 s. Closing allowed 4 s; unchanged opposed-contact gate before lift and balanced v03 hold. This uses simulated finger contact feedback in the engineered gripper controller, not knife pose. No physical asset/law/limit changes. Validate on development placements, then three validation placements, then new held-out placements frozen before use.\n')
