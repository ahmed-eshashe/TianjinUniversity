from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[2]
E=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/isaacsim/extscache')
paths=[E/'omni.physics.tensors-110.3.2+110.3.0.lx64.r.cp312.u7f4/omni/physics/tensors/api.py',E/'omni.physx-110.3.2+110.3.0.lx64.r.cp312.u7f4/omni/physx/bindings/_physx.pyi',Path('/home/omen/IsaacLab/source/isaaclab/isaaclab/actuators/actuator_pd.py'),R/'work/astra_effort_resolution_20261102/physx_5_9_1_DyFeatherstoneArticulation.cpp',R/'work/astra_effort_resolution_20261102/physx_5_9_1_DyFeatherstoneForwardDynamic.cpp']
records=[]
for p in paths:
 s=p.read_text(); row={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix in ('.py','.pyi'):
  tree=ast.parse(s)
  row['relevant_methods']=[{'name':n.name,'line':n.lineno,'doc':ast.get_docstring(n)} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and any(w in n.name.lower() for w in ('effort','force','impulse','energy','work','step_event','on_step','drive','acceleration'))]
 else:
  row['relevant_lines']=[{'line':i,'text':line.strip()} for i,line in enumerate(s.splitlines(),1) if any(w in line for w in ('driveDeltaF','driveImpulse','jointV +=','externalForcesEveryTgsIterationEnabled ?'))]
 records.append(row)
out=Path(__file__).parent/'interface_inventory.json'
assert not out.exists()
out.write_text(json.dumps({'scope':'static inspection of installed Python tensor/PhysX bindings, IsaacLab actuator and matching-family public CPU source; not proof of every private binary interface','sources':records,'native_runs':0,'qualified_work_method_available':False},indent=2)+'\n')
print('Recorded and hashed',len(records),'source files; no simulation invoked.')
