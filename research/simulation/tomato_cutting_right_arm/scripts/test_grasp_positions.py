"""Run finite position trials sequentially through the unchanged memory watchdog."""
import argparse,datetime,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES={'control':[0.,0.],'x_plus_5cm':[.05,0.],'x_minus_5cm':[-.05,0.],'y_plus_5cm':[0.,.05],'y_minus_5cm':[0.,-.05]}
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,help='Reuse an existing directory to resume completed cases')
p.add_argument('--case',choices=list(CASES),action='append')
args=p.parse_args()
out=(args.output or ROOT/'logs'/('position_tests_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))).resolve()
out.mkdir(parents=True,exist_ok=True)
summary_path=out/'summary.json'
summary=json.loads(summary_path.read_text()) if summary_path.exists() else {'controller':'Scripted IK with contact-force feedback; no RL','robot_base_fixed':True,'support_board_translated_with_knife':True,'knife_yaw_changed':False,'all_trials_require_wrapped_contact':True,'cases':[]}
def save():
 temp=summary_path.with_suffix('.tmp');temp.write_text(json.dumps(summary,indent=2));temp.replace(summary_path)
for name,offset in CASES.items():
 if args.case and name not in args.case:continue
 if any(c['name']==name for c in summary['cases']):continue
 case_dir=out/name;case_dir.mkdir(exist_ok=True)
 # Shared outputs must not be mistaken for the result of a refused/failed launch.
 before={n:(ROOT/'logs'/n).stat().st_mtime_ns if (ROOT/'logs'/n).exists() else None for n in ['kitchen_grasp_report.json','kitchen_grasp_status.json','kitchen_grasp_memory_report.json']}
 summary['running_case']=name;save();print('START',name,offset,flush=True)
 start=time.monotonic()
 with (case_dir/'simulation.log').open('w') as log:
  run=subprocess.run([str(ROOT/'run_kitchen_grasp.sh'),'--test-offset-xy',*[str(v) for v in offset]],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 result={'name':name,'offset_world_xy_m':offset,'exit_code':run.returncode,'elapsed_seconds':round(time.monotonic()-start,1),'passed':False}
 for n in before:
  source=ROOT/'logs'/n
  if source.exists() and source.stat().st_mtime_ns!=before[n]:
   shutil.copy2(source,case_dir/n)
   data=json.loads(source.read_text())
   if n=='kitchen_grasp_report.json':
    if data.get('configuration',{}).get('test_offset_xy')!=offset:raise RuntimeError('Trial configuration did not match requested position')
    result.update({k:data[k] for k in ['lift_passed','lift_m','relative_slip_m','initial_handle_world_m','max_contact_n']})
    result['passed']=bool(run.returncode==0 and data['passed']);result['wrap_checks']=data['wrap_grasp']['checks']
   elif n=='kitchen_grasp_memory_report.json':result['memory']=data
   else:result['status']=data.get('state');result['error']=data.get('error')
 summary['cases'].append(result);summary.pop('running_case',None);save()
 print('RESULT',json.dumps(result),flush=True)
 log_text=(case_dir/'simulation.log').read_text()
 if 'Close the full scene or other large apps first' in log_text or 'already running' in log_text or result.get('memory',{}).get('reason')!='normal exit':
  summary['stopped_early']='Launch refused or memory/process guard stopped this trial; remaining cases were not launched';save();break
summary['completed_cases']=len(summary['cases']);summary['passed_cases']=sum(c['passed'] for c in summary['cases']);save()
print('SUMMARY',str(summary_path),summary['passed_cases'],'/',summary['completed_cases'],flush=True)
sys.exit(0 if summary['cases'] and all(c['passed'] for c in summary['cases']) and 'stopped_early' not in summary else 1)
