"""Continue this isolated job after image capture; never launch two Isaac workers."""
from pathlib import Path
import json,subprocess,sys,time,psutil
W=Path(__file__).resolve().parent
for p in psutil.process_iter(['cmdline']):
 if any(Path(x).name=='queued_capture_v02.py' for x in (p.info['cmdline'] or [])):
  try:p.wait()
  except psutil.NoSuchProcess:pass
assert len(list((W/'head_images_v02').glob('*/*/metadata.json')))==192,'Capture incomplete'
steps=[
 ('labels',['prepare_grasp_labels_v04.py','--targets','grasp_targets_v02_candidate.json','--output','grasp_data_v05']),
 ('training',['train_grasp_vision_v02.py','--data','grasp_data_v05','--output','policies/grasp_vision_v02_expanded','--steps','6000']),
 ('image_validation',['evaluate_grasp_vision_v02.py','--data','grasp_data_v05','--checkpoint','policies/grasp_vision_v02_expanded/best.pt','--output','reports/vision_v02_expanded_validation.json']),
 ('index_closing_check',['run_curriculum_v33.py','--script','hybrid_pickup_v15.py','--tag','v15_index_search','--ids','train_medium_face180_00','--teacher-targets','grasp_targets_v02_candidate.json'])]
for phase,command in steps:
 (W/'reports/post_capture_progress.json').write_text(json.dumps(dict(phase=phase,time=time.time())))
 print('START',phase,flush=True)
 with (W/'reports'/('post_capture_'+phase+'.log')).open('w') as log:
  subprocess.run([sys.executable,'-u',*command],cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('FINISHED',phase,flush=True)
(W/'reports/post_capture_progress.json').write_text(json.dumps(dict(phase='finished',time=time.time())))
