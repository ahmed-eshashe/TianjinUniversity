from pipeline_loop import *
rows=[];checks={};errors=[]
try:
 t=time.perf_counter();template=Body(n=10);template.prepare_geometry_cache();Aggregate(template);template_s=time.perf_counter()-t
 episode(template,groups=1,batch=1,frames=2)
 baselines={}
 for variant in [0,1]:
  state,m=episode(template,groups=2,batch=8,overlap=True,variant=variant);m['purpose']='fresh reference';baselines[variant]=state;rows.append(m);print(m,flush=True)
 reuse=[]
 for run in range(9):
  variant=run%2;states,m=episode(template,groups=2,batch=8,overlap=True,variant=variant,reuse=reuse);m.update(purpose='repeated episode',repeat=run,reused_GPU=run>0);rows.append(m);print(m,flush=True)
  if run in [1,2,8]:
   for i in range(2):
    for frame in [0,1,7,9]:
     for j in range(8):
      err,ok=compare(baselines[variant][i][frame][j],states[i][frame][j]);checks[f'r{run}_g{i}_f{frame}_b{j}']=ok;errors.append(err)
 rates=[r['diagnostic_transitions_s'] for r in rows if r.get('reused_GPU')]
 result={'status':'pass' if all(checks.values()) else 'failed','checks':checks,'rows':rows,'errors':errors,'minimum_rate':min(rates),'median_rate':float(np.median(rates)),'all_repeated_episodes_above_100':min(rates)>=100,'template_preparation_s':template_s,'physical_cut':False,'RL_qualified':False,'scope':'Same sixteen independent 60 mm/6 mm synthetic blocks, 12.5 us substeps, ten controls and four current geometric events per episode. Resets/events/uploads/full state observation/conservation included; one-time executable initialization reused after episode zero. No blade/contact/fracture/robot/policy.'}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'checks':checks,'rows':rows,'errors':errors}
(W/'steady_performance.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k not in ['rows','checks','errors']},flush=True)
