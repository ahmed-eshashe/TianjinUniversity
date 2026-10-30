"""Verify actual settled placements and unchanged controller settings across saved trials."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);args=p.parse_args()
folder=args.folder.resolve();summary=json.loads((folder/'summary.json').read_text())
rows=[];reference=None;reference_cfg=None
for case in summary['cases']:
 d=folder/case['name'];log=(d/'simulation.log').read_text().splitlines()
 settled=next((json.loads(line.removeprefix('SETTLED_SCENE ')) for line in log if line.startswith('SETTLED_SCENE ')),None)
 status_path=d/'kitchen_grasp_status.json';status=json.loads(status_path.read_text()) if status_path.exists() else {}
 cfg=status.get('configuration',{});cfg={k:v for k,v in cfg.items() if k!='test_offset_xy'}
 if case['name']=='control' and settled:
  reference=settled['handle'];reference_cfg=cfg
 actual=[settled['handle'][i]-reference[i] for i in range(3)] if settled and reference else None
 expected=[*case['offset_world_xy_m'],0.]
 err=sum((a-b)**2 for a,b in zip(actual,expected))**.5 if actual is not None else None
 row={'name':case['name'],'requested_offset_world_m':expected,'actual_settled_offset_world_m':actual,'placement_error_m':err,'placement_verified_within_2mm':err is not None and err<.002,'same_controller_except_placement':bool(cfg and cfg==reference_cfg),'strict_wrap_required':cfg.get('require_wrap') is True}
 report_path=d/'kitchen_grasp_report.json'
 if report_path.exists():
  r=json.loads(report_path.read_text());row['original_free_knife_verified']=r['knife_path']=='/Indoor/RZ/SM_kitchen_knife_02' and not r['duplicate_knife_created'] and not r['grasp_attachment_created']
 rows.append(row)
audit={'case_count':len(rows),'cases':rows,'all_settled_placements_verified':bool(rows) and all(r['placement_verified_within_2mm'] for r in rows),'controller_unchanged_and_strict_wrap_required':bool(rows) and all(r['same_controller_except_placement'] and r['strict_wrap_required'] for r in rows),'scope':'Translation only; existing supporting board moves with knife; fixed base and wrist orientation; no claim about rotated/flat-counter/arbitrary kitchen placements'}
(folder/'placement_audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
raise SystemExit(0 if audit['all_settled_placements_verified'] and audit['controller_unchanged_and_strict_wrap_required'] else 1)
