"""Read-only local progress display; never starts numerical work."""
import fcntl, html, json, os, signal, time, tomllib
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
R=Path(__file__).resolve().parents[1]
S=R/os.environ.get('TOMATO_SESSION_DIR','runs/offline/tomato_overnight_20261026')
A=Path('/home/omen/.codex/automations/bounded-overnight-tomato-checks/automation.toml')
def read(p):
    try:return json.loads(p.read_text())
    except (OSError,ValueError):return {}
def esc(v):return html.escape(str(v))
def local(stamp):
    try:return datetime.fromisoformat(stamp.replace('Z','+00:00')).astimezone().strftime('%d %b %H:%M:%S %Z')
    except (ValueError,TypeError):return 'Not recorded'
def held(name):
    with (R/'logs'/name).open('a') as f:
        try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return True
        fcntl.flock(f,fcntl.LOCK_UN);return False
def worker_names():
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            args=(p/'cmdline').read_bytes().split(b'\0')
            if not args or 'python' not in Path(os.fsdecode(args[0])).name:continue
            for raw in args[1:]:
                n=Path(os.fsdecode(raw)).name
                if n.startswith(('offline_tomato_','audit_tomato_','run_cycle_guarded_branch','run_frozen_guess','qualify_seed_provenance')) and n.endswith('.py'):
                    found.append(n);break
        except (OSError,ValueError):pass
    return found
class Page(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/favicon.ico':self.send_response(204);self.end_headers();return
        s=read(S/'session.json');now=datetime.now(timezone.utc)
        try:auto=tomllib.loads(A.read_text())
        except (OSError,ValueError):auto={}
        deadline=datetime.fromisoformat(s['deadline_utc']);left=max(0,int((deadline-now).total_seconds()))
        workers=worker_names();worker_lock=held('right_arm_control.lock');parent_lock=held('offline_overnight.lock')
        if left==0:state='Time window ended';tone='idle';detail='No further numerical work is authorized in this window.'
        elif worker_lock and workers:state='Numerical worker running';tone='running';detail='An offline test or independent check is using the shared worker lock.'
        elif workers or parent_lock:state='Batch active';tone='running';detail='A bounded batch is preparing, checking or saving its result.'
        elif worker_lock:state='Shared worker lock occupied';tone='warn';detail='The shared worker is occupied; this display cannot identify it as a tomato test.'
        elif (s.get('status','').startswith('stopped_quota') or s.get('status')=='waiting_quota'):
            state='Stopped — quota check unavailable';tone='warn';detail='Numerical work has stopped. Current quota could not be verified. No further tests should start while this stop instruction remains.'
        elif auto.get('status')=='ACTIVE':state='Waiting for scheduled session';tone='idle';detail='No numerical worker is running right now. Continuation is scheduled every 5 minutes.'
        else:state='Continuation paused';tone='warn';detail='No numerical worker is running and scheduled continuation is not active.'
        rows=[];folder=R/'runs/offline/tomato_curvature_search_01'
        for p in folder.glob('insertion*/status.json'):
            try:rows.append((p.stat().st_mtime,p,read(p)))
            except OSError:pass
        rows.sort(reverse=True)
        accepted=[]
        for _,p,b in rows:
            if b.get('accepted'):
                q=R/b['accepted']/'summary.json';v=read(q)
                if v.get('passed'):accepted.append((v.get('depth_mm',0),p,b,v))
        accepted.sort(key=lambda x:x[0],reverse=True)
        depth=accepted[0][0] if accepted else read(R/s.get('last_accepted','')/'summary.json').get('depth_mm','Unknown')
        result_time=datetime.fromtimestamp(rows[0][0],timezone.utc).astimezone().strftime('%H:%M:%S %Z') if rows else 'Unknown'
        lease=read(S/'quota_lease.json');used=lease.get('maximum_reported_used_percent')
        quota=(f'{100-used:g}% last confirmed' if (s.get('status','').startswith('stopped_quota') or s.get('status')=='waiting_quota') else f'{100-used:g}% remaining') if isinstance(used,(int,float)) else 'Unknown'
        table=''
        for stamp,p,b in rows[:6]:
            outcome='Independently passed' if b.get('accepted') else {'in_progress':'Solving — not yet accepted','physical_gate_failed':'Rejected by a physical check','bounded_worker_budget':'Batch limit — candidate saved','repeated_uncommitted_optimizer_state':'Solver stalled — candidate saved'}.get(b.get('stop_reason'),b.get('stop_reason','Unknown'))
            table+=f'<tr><td>{datetime.fromtimestamp(stamp).astimezone().strftime("%H:%M:%S")}</td><td>{esc(b.get("depth_mm","—"))}</td><td>{esc(outcome)}</td></tr>'
        if not table:table='<tr><td colspan="3">No batch results found.</td></tr>'
        body=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="5"><title>Tomato work — live status</title><style>
        :root{{color-scheme:light dark;font-family:system-ui,sans-serif;background:light-dark(#f5f6f8,#151719);color:light-dark(#17212b,#eef2f5)}}body{{max-width:900px;margin:auto;padding:32px 22px}}h1{{font-size:24px;margin-bottom:6px}}h2{{font-size:17px}}.sub{{opacity:.72}}.status{{padding:22px;border-radius:14px;background:light-dark(#fff,#23272b);margin:24px 0}}.pill{{display:inline-block;padding:7px 12px;border-radius:24px;background:light-dark(#e9edf1,#343b43);font-weight:600}}.running .pill{{background:light-dark(#d8f2e2,#174b30)}}.warn .pill{{background:light-dark(#fff0c6,#614b13)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:20px;margin-top:25px}}.value{{font-size:23px;font-weight:600;margin:6px 0}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{text-align:left;padding:12px 8px;border-bottom:1px solid light-dark(#dce1e6,#394149)}}small{{font-size:13px}}code{{overflow-wrap:anywhere}}.footer{{margin-top:24px;opacity:.75}}@media(max-width:500px){{body{{padding:18px 12px}}td,th{{padding:10px 4px;font-size:13px}}}}</style></head><body>
        <h1>Tomato project · live activity</h1><div class="sub">Read-only display · refreshes every 5 seconds</div>
        <section class="status {tone}" aria-live="polite"><span class="pill">{state}</span><p>{detail}</p><small>Display checked: {now.astimezone().strftime('%H:%M:%S %Z')} · Last batch update: {result_time}</small>
        <div class="grid"><div>Accepted insertion<div class="value">{esc(round(depth,7) if isinstance(depth,(int,float)) else depth)} mm</div><small>Independent checks passed</small></div><div>Last reported quota<div class="value">{quota}</div><small>Checked {esc(local(lease.get('checked_utc')))}<br>Unreported windows remain unknown</small></div><div>Time left in window<div class="value">{left//3600}h {(left%3600)//60}m</div><small>Ends {esc(local(s.get('deadline_utc')))}</small></div></div></section>
        <h2>Recent test activity</h2><table><thead><tr><th>Last update</th><th>Target (mm)</th><th>Result</th></tr></thead><tbody>{table}</tbody></table>
        <p class="footer">Full slice separation remains unvalidated. Offline numerical work only.<br>This page shows recorded results and actual process/lock checks. Refreshing the display does not mean a numerical worker is running.</p>
        </body></html>'''
        data=body.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':
    HTTPServer.allow_reuse_address=True
    server=HTTPServer(('127.0.0.1',int(os.environ.get('TOMATO_STATUS_PORT','0'))),Page);server.timeout=2
    record={'pid':os.getpid(),'url':f'http://127.0.0.1:{server.server_port}','read_only':True,'refresh_seconds':5}
    (S/'live_status_display.json').write_text(json.dumps(record,indent=2)+'\n');print(record,flush=True)
    while datetime.now(timezone.utc)<datetime.fromisoformat(read(S/'session.json')['deadline_utc']):server.handle_request()
    server.server_close()
