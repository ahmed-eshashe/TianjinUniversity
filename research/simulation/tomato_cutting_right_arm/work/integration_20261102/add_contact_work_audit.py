from pathlib import Path
p=Path('rl/tomato_embedding_contact_worker.py');s=p.read_text();needle="    records.append(row);write(out,'embedding_contact_partial.json',dict(cases=records))"
insert="""    if args.mollified and label=='compression1':
     # Central finite work uses the ACTUAL float32 endpoints, not nominal h*v.
     # Candidate identities remain fixed; closest features and mollifier update.
     derivatives=[]
     for direction in ['normal','tangent','random']:
      velocity=np.zeros_like(pos)
      if direction=='normal':velocity[left,0]=1.
      elif direction=='tangent':velocity[left,1]=1.
      else:velocity=random_velocity/np.max(np.abs(random_velocity))
      for step in [2e-7,1e-7,5e-8]:
       plus=(pos+step*velocity).astype(np.float32);minus=(pos-step*velocity).astype(np.float32)
       energies=[]
       for endpoint in [plus,minus]:
        physical.assign(endpoint);engine.evaluate(physical,1/2400);wp.synchronize();energies.append(float(engine.contact_energy.numpy()[0]))
       predicted=-float(np.sum(engine_force*(plus.astype(float)-minus.astype(float))))
       observed=energies[0]-energies[1];relative=abs(observed-predicted)/max(abs(predicted),abs(observed),1e-12)
       derivatives.append(dict(direction=direction,step_m=step,energy_difference_j=observed,negative_force_work_j=predicted,relative_error=relative))
     row['current_geometry_work_audit']=derivatives
     # Nonsmooth feature transitions can reduce centered convergence order.
     for direction in ['normal','tangent','random']:
      tests=[d for d in derivatives if d['direction']==direction]
      if min(abs(d['energy_difference_j']-d['negative_force_work_j']) for d in tests)>1e-10 and min(d['relative_error'] for d in tests)>.02:raise ValueError('Current contact force is not potential gradient '+str(tests))
     physical.assign(pos);engine.evaluate(physical,1/2400)
    records.append(row);write(out,'embedding_contact_partial.json',dict(cases=records))"""
# Preserve high precision force before output casting for derivative comparison.
s=s.replace("force=f.numpy().astype(float);proxy_force=", "force=f.numpy().astype(float);engine_force=engine.physical_force.numpy().copy();proxy_force=")
assert needle in s;s=s.replace(needle,insert);p.write_text(s)
