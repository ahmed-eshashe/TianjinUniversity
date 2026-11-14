"""Dedicated disabled preparation preview; deliberately has no execute option."""
import argparse,json
from pathlib import Path
from tomato_native_launch_contract import validate_request


def preview(root,request,now_utc):
    result=validate_request(root,request,now_utc=now_utc)
    return {**result,'purpose':request['purpose'],'config_path':request['config_path'],
            'worker_wall_budget_s':request['wall_budget_s'],
            'launcher_status':'DISABLED_PENDING_REVIEWED_NATIVE_SUPERVISOR',
            'imports_or_processes_started':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--request',type=Path,required=True)
    p.add_argument('--now-utc',required=True)
    a=p.parse_args();print(json.dumps(preview(a.root,json.loads(a.request.read_text()),a.now_utc),indent=2))

if __name__=='__main__':main()
