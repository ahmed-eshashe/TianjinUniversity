from pathlib import Path
p=Path('rl/tomato_contact_dynamics_worker.py');s=p.read_text();s=s.replace("p.add_argument('--objective',action='store_true');", "p.add_argument('--objective',action='store_true');p.add_argument('--graph',action='store_true');")
s=s.replace("  for episode in range(2):\n   reset();trace=[]", """  graph=None;warm_steps=0
  if args.graph:
   reset();solver.step(states[0],states[1],None,None,dt);solver.step(states[1],states[0],None,None,dt);wp.synchronize();steps+=2;warm_steps=2;reset()
   with wp.ScopedCapture() as capture:
    solver.step(states[0],states[1],None,None,dt);solver.step(states[1],states[0],None,None,dt)
   graph=capture.graph
   if args.steps%2:raise ValueError('Even measured steps required for two-step graph')
  for episode in range(2):
   reset();trace=[]""")
s=s.replace('   for i in range(args.steps):', '   for batch in range(args.steps//2 if args.graph else args.steps):\n    i=batch*2 if args.graph else batch')
s=s.replace("solver.step(sin,sout,None,None,dt);wp.synchronize();steps+=1;solver.commit_cohesion(sout);", "\n    if args.graph:wp.capture_launch(graph);sout=states[0]\n    else:solver.step(sin,sout,None,None,dt)\n    wp.synchronize();steps+=2 if args.graph else 1;solver.commit_cohesion(sout);")
s=s.replace('dict(step=i+1,wall_s=', 'dict(step=i+(2 if args.graph else 1),wall_s=')
p.write_text(s)
p=Path('rl/tomato_isaac_startup_guard.py');s=p.read_text();s=s.replace("('startup', 'contact_dynamics',", "('startup', 'contact_preflight', 'contact_dynamics',")
needle="    if mode == 'contact_dynamics':\n        return";s=s.replace(needle,"    if mode == 'contact_preflight':\n        return (worker.get('diagnostic_passed') is True and worker.get('contact_dynamics_passed') is True\n                and worker.get('controlled_steps') == 0 and worker.get('newton_steps') == 482\n                and worker.get('episodes_completed') == 2 and worker.get('steps_per_episode') == 240\n                and worker.get('objective_material') is True)\n"+needle,1)
s=s.replace("    if mode == 'contact_dynamics':\n        worker_path", "    if mode in ('contact_dynamics','contact_preflight'):\n        worker_path")
p.write_text(s)
