from pipeline_loop import *
rows=[];checks={};errors=[]
try:
 assert json.loads((W/'invariants.json').read_text())['status']=='pass'
 t=time.perf_counter();template=Body(n=10);template.prepare_geometry_cache();Aggregate(template);template_s=time.perf_counter()-t
 t=time.perf_counter();episode(template,groups=1,batch=1,frames=2);warm_s=time.perf_counter()-t
 for variant in [0,1]:
  # Matched synchronous episode, including reset and graph initialization.
  serial,m=episode(template,groups=2,batch=8,overlap=False,variant=variant);rows.append(m);print(m,flush=True)
  for run in range(3):
   states,m=episode(template,groups=2,batch=8,overlap=True,variant=variant);m['repeat']=run;rows.append(m);print(m,flush=True)
   if run==0:
    for i in range(2):
     for f in [0,1,3,5,7,9]:
      for j in range(8):
       err,ok=compare(serial[i][f][j],states[i][f][j]);checks[f'v{variant}_g{i}_f{f}_b{j}']=ok;errors.append(err)
 rates=[r['diagnostic_transitions_s'] for r in rows if r['overlap']]
 result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'errors':errors,'minimum_rate':min(rates),'median_rate':float(np.median(rates)),'geometric_diagnostic_speed_gate_all_repeats':min(rates)>=100,'target_actual_RL_steps_s':100,'template_preparation_s':template_s,'warmup_s':warm_s,'physical_cut':False,'RL_qualified':False}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'rows':rows,'errors':errors,'physical_cut':False,'RL_qualified':False}
(W/'final_performance.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k not in ['rows','checks','errors']},flush=True)
