from pipeline_loop import *
rows=[]
try:
 assert json.loads((W/'invariants.json').read_text())['status']=='pass'
 t=time.perf_counter();template=Body(n=10);template.prepare_geometry_cache();Aggregate(template);template_s=time.perf_counter()-t
 episode(template,groups=1,batch=1,frames=2)
 for groups,workers in [(3,8),(4,4),(4,8),(2,4),(2,4),(4,8),(4,4),(3,8)]:
  _,row=episode(template,groups=groups,batch=8,overlap=True,workers=workers);rows.append(row);print(row,flush=True)
 result={'status':'complete','rows':rows,'template_preparation_s':template_s,'scope':'Execution layouts only; identical model/resolution/timestep/event schedule per environment. Includes reset, event, GPU, observation and conservation costs. No physical blade/fracture/robot/policy.'}
except Exception as e:traceback.print_exc();result={'status':'exception','exception':repr(e),'rows':rows}
(W/'layout_compare.json').write_text(json.dumps(result,indent=2))
