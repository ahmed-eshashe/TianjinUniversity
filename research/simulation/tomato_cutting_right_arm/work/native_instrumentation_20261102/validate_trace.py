"""Validate experimental native-row trace structure, never certify motor work."""
import csv,json,math,re,sys
from pathlib import Path
p=Path(sys.argv[1]);count=0;passes=set();max_response_error=0.
with p.open() as f:
 if f.readline().strip()!='TOMATO_INTERNAL_DRIVE_TRACE_V1':raise ValueError('Wrong trace format')
 names=f.readline().strip().split(',')
 if len(names)!=12:raise ValueError('Wrong trace schema')
 footer=None
 for line in f:
  if line.startswith('END '):
   footer=re.fullmatch(r'END count=(\d+) dropped=(\d+) passes=(\d+)\n?',line)
   if f.read():raise ValueError('Trailing data')
   break
  row=next(csv.reader([line]));
  if len(row)!=12:raise ValueError('Truncated row')
  vals=list(map(float,row[5:]));pid=int(row[0]);flags=int(row[4])
  if not all(map(math.isfinite,vals))or pid<=0 or not 0<=flags<=7:raise ValueError('Invalid row')
  dt,step,elapsed,imp,before,after,response=vals
  if dt<=0 or step<=0 or elapsed<0 or response<0:raise ValueError('Invalid time/response')
  error=abs(after-(before+imp*response));max_response_error=max(max_response_error,error)
  # Float32 solver arithmetic: structural sanity only, not a physical precision gate.
  if error>8*2**-23*max(abs(before),abs(after),abs(imp*response),1e-30):raise ValueError('Response arithmetic inconsistent')
  count+=1;passes.add(pid)
 if footer is None:raise ValueError('Missing completion footer')
 n,dropped,np=map(int,footer.groups())
 if n!=count or dropped or (passes and max(passes)>np):raise ValueError('Incomplete/overflowed trace')
print(json.dumps({'rows':count,'seen_passes':len(passes),'max_local_response_error':max_response_error,'scope':'row-trace sanity only; no motor-work or simulation-equivalence qualification'}))
