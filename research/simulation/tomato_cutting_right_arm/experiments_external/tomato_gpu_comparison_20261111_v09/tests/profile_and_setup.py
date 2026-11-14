from pathlib import Path
from datetime import datetime, timezone
import sys, json, time, subprocess, os, platform
import numpy as np, scipy, warp as wp

W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from multicut import MultiCut,full_rectangle
from reference import block
from gpu_backend import GPUReference
BASE=Path('/home/omen/Documents/Codex/experiments/tomato_multicut_20261110_v07')

s=MultiCut.restore(BASE/'runs/dynamics/partial.npz');g=GPUReference(s);g.step(1,graph=False)
with wp.ScopedTimer('32 uncaptured checked substeps',print=False,synchronize=True,cuda_filter=wp.TIMING_KERNEL) as timer:
    g.step(32,graph=False)
aggregate={}
for r in timer.timing_results:aggregate[r.name]=aggregate.get(r.name,0.)+r.elapsed
out={'scope':'Device-kernel diagnostic only, not throughput; captured checked timing is in comparison.json','host_wall_ms':timer.elapsed,'kernel_elapsed_ms':aggregate,'summed_kernel_ms':sum(aggregate.values()),'samples':len(timer.timing_results)}
(W/'profile.json').write_text(json.dumps(out,indent=2));print(out,flush=True)

rows=[]
for cuts in [0,1,2,4]:
    start=time.perf_counter();s=MultiCut(block(8,.0015));intact_s=time.perf_counter()-start;events=[]
    for pid,axis,plane in [('root',0,-.0021),('rootR',0,.0021),('rootRL',1,.0003),('rootL',2,.0004)][:cuts]:
        start=time.perf_counter();s.commit(s.propose(pid,axis,plane,full_rectangle(s.pieces[pid],axis)));events.append(time.perf_counter()-start)
    g=GPUReference(s);start=time.perf_counter();g.graph(32);warm_s=time.perf_counter()-start
    rows.append({'cuts':cuts,'CPU_intact_assembly_s':intact_s,'CPU_each_topology_event_s':events,'CPU_mass_inverse_and_operator_preparation_s':g.preparation_s,'CPU_sparse_packing_and_GPU_upload_s':g.upload_s,'cached_module_and_graph_s':warm_s,'device_owned_array_MiB':g.memory()/2**20})
result={'setup_samples':rows,'timing_label_correction':'comparison.json CPU_topology_and_gpu_operator_preparation_s measures only mass inverse and operator preparation from ALREADY BUILT CPU topology. This supplement separately measures actual CPU assembly and cut-event construction.','scope':'Small prescribed-block setup; not online physical crack processing, tomato reset, or a distribution of latencies.'}
(W/'setup_costs.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
meta={'recorded':datetime.now(timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'numpy':np.__version__,'scipy':scipy.__version__,'warp':wp.__version__,'platform':platform.platform(),'openblas_threads':os.environ.get('OPENBLAS_NUM_THREADS'),'GPU':subprocess.run(['nvidia-smi','--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu,power.draw','--format=csv'],capture_output=True,text=True).stdout,'compute_processes':subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv'],capture_output=True,text=True).stdout,'power_supplies':{p.name:{n:(p/n).read_text().strip() for n in ['type','online','status','capacity'] if (p/n).exists()} for p in Path('/sys/class/power_supply').glob('*')},'context_note':'Normal desktop/browser GPU activity remained present. No Isaac window, dependency installation or driver/clock/environment modification.'}
(W/'environment.json').write_text(json.dumps(meta,indent=2))
