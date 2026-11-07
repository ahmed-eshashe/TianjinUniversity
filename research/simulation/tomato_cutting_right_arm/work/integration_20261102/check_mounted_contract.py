from pathlib import Path
import json
r=Path(__file__).resolve().parents[2];c=json.loads((r/'runs/offline/integration_contract_20261102_01/contract.json').read_text());d=json.loads((r/'runs/native/mounted_contact_20261102_03/mounted_contact_measurements.json').read_text());p=max(x['actual_max_initial_penetration_m'] for case in d['cases'] for x in case['records']);limit=c['mounted_coupon']['gates']['maximum_penetration_m'];assert p<=limit
result=dict(run='mounted_contact_20261102_03',maximum_reported_penetration_m=p,predeclared_limit_m=limit,passed=True,note='Checks a gate present before execution against saved measurements; does not add new robot/contact evidence.')
(r/'work/integration_20261102/mounted_penetration_check.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
