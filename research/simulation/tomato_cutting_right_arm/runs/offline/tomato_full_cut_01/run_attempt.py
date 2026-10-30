"""Serial bounded full-cut attempt; never continue a rejected state."""
import json,os,subprocess,time
from pathlib import Path
R=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');F=R/'runs/offline/tomato_full_cut_01'
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
previous=F/'probe_4p125';records=[];start=time.monotonic()
# Original finite-triangle certification does not cover capped wedge triangles.
# Stop there rather than letting nodal-only contact silently certify a full cut.
for step in range(34,385):
    depth=step*.125
    if depth>=8.:
        stop={'reason':'finite_triangle_bevel_cap_contact_unvalidated','requested_depth_mm':depth,'accepted_depth_mm':(step-1)*.125};break
    out=F/'insertion'/f'{step:03d}';out.parent.mkdir(exist_ok=True)
    cmd=[str(R/'.venv-native/bin/python'),'rl/offline_tomato_full_cut.py','--depth-mm',str(depth),'--previous',str(previous),'--output',str(out)]
    try:
        result=subprocess.run(cmd,cwd=R,env=env,capture_output=True,text=True,timeout=60)
        (out.parent/(out.name+'.log')).write_text(result.stdout+result.stderr)
        entry={'depth_mm':depth,'returncode':result.returncode,'output':str(out.relative_to(R)),'elapsed_s':time.monotonic()-start}
        if result.returncode:
            records.append(entry);stop={'reason':'worker_failed_or_capped','record':entry};break
        s=json.loads((out/'summary.json').read_text());entry.update({k:s[k] for k in ['passed','flags','damaged_patches','max_damage','completely_failed_patches','runtime_s','peak_rss_bytes']});records.append(entry)
        print(entry,flush=True)
        if not s['passed']:
            stop={'reason':'endpoint_validation_failed','record':entry};break
        previous=out
    except subprocess.TimeoutExpired:
        stop={'reason':'parent_60s_timeout','depth_mm':depth};break
else:stop={'reason':'insertion_complete_release_not_yet_validated'}
report={'records':records,'stop':stop,'last_accepted':str(previous.relative_to(R)),'full_cut_passed':False,'slice_release_validated':False,'simulator':False,'training':False}
(F/'attempt.json').write_text(json.dumps(report,indent=2)+'\n');print(stop,flush=True)
