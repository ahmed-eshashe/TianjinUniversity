"""Supplement the in-flight pilot with exact original kB-based host reserves."""
import argparse
import json
import os
from pathlib import Path
import signal
import time

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
matches=[]
for entry in Path('/proc').iterdir():
    if not entry.name.isdigit():continue
    try:cmd=(entry/'cmdline').read_bytes().replace(b'\0',b' ').decode()
    except (FileNotFoundError,PermissionError,ProcessLookupError):continue
    if '/rl/benchmark.py ' in cmd and '--output '+str(a.output.resolve())+' ' in cmd:matches.append(int(entry.name))
if len(matches)!=1:raise SystemExit(f'Expected exactly one benchmark child, found {matches}')
pid=matches[0];start=time.monotonic();minimum=10**20;reason='normal exit';warning=None;samples=0
while Path(f'/proc/{pid}').exists():
    available=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))
    minimum=min(minimum,available);samples+=1
    if available<2_000_000 or (warning is not None and time.monotonic()-warning>12):
        reason='strict reserve stop'
        try:os.killpg(pid,signal.SIGTERM)
        except ProcessLookupError:pass
        break
    if available<3_000_000 and warning is None:
        warning=time.monotonic();(a.output/'checkpoint_and_stop.request').write_text('Exact original RAM reserve warning.\n')
    time.sleep(.5)
report={'pid':pid,'reason':reason,'samples':samples,'elapsed_s':time.monotonic()-start,'minimum_available_ram_kb':minimum,
        'warning_requested':warning is not None,'warning_kb':3_000_000,'stop_kb':2_000_000}
(a.output/'strict_host_monitor.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
