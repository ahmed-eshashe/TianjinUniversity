"""Sequential physical qualification; stops at any failed prerequisite.
Speed is deferred by explicit user choice. This does not launch section4.
"""
from pathlib import Path
import json,subprocess,time,datetime,sys
W=Path(__file__).resolve().parent;launcher=W.parent/'disect_numerics_20261108_v05/run.sh'
def status(phase,**extra):
 d=dict(phase=phase,updated=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),**extra)
 p=W/'qualification_progress.tmp';p.write_text(json.dumps(d,indent=2));p.replace(W/'qualification_progress.json');print(d,flush=True)
def load(name):return json.loads((W/name).read_text())
def run(script,name,*args):
 status(name)
 with (W/(name+'.log')).open('w') as log:
  code=subprocess.run(['bash',str(launcher),str(W/script),*args],stdout=log,stderr=subprocess.STDOUT).returncode
 if code:raise RuntimeError(f'{name}: process exit {code}; inspect saved log')
try:
 status('waiting_for_coarse_hold')
 while not (W/'settle_contact_result.json').exists():time.sleep(2)
 time.sleep(1)
 if not load('settle_contact_result.json')['settling_passed']:raise RuntimeError('Coarse hold did not pass; no refined hold or blade test launched')
 run('settle.py','settle_contact_refined','--refined')
 if not load('settle_contact_refined_result.json')['settling_passed']:raise RuntimeError('Refined hold did not pass')
 run('qualify_settling.py','settling_qualification')
 if not load('settling_qualification.json')['passed']:raise RuntimeError('Settling comparison did not pass')
 run('plan_indent.py','plan_indent')
 if not load('indent_plan.json')['passed']:raise RuntimeError('Blade plan invalid')
 run('indent.py','indent')
 if not load('indent_result.json')['component_passed']:raise RuntimeError('Blade coarse control failed')
 run('indent.py','indent_refined','--refined')
 if not load('indent_refined_result.json')['component_passed']:raise RuntimeError('Blade refined control failed')
 run('compare_contact.py','compare_contact')
 if not load('contact_comparison_result.json')['contact_comparison_passed']:raise RuntimeError('Blade comparison failed')
 status('physical_checks_complete_pending_review',section4_started=False,speed_deferred=True)
except Exception as exc:
 status('stopped_at_gate',reason=str(exc),section4_started=False);sys.exit(1)
