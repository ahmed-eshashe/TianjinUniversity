from pathlib import Path
import json,shutil,hashlib
r=Path(__file__).resolve().parents[2];run=r/'runs/native/embedding_contact_20261102_03';d=json.loads((run/'embedding_contact_measurements.json').read_text());s=run/'source_snapshot';s.mkdir(exist_ok=True)
for name,h in d['source_sha256'].items():
 p=Path(name);assert hashlib.sha256(p.read_bytes()).hexdigest()==h;shutil.copy2(p,s/p.name)
(s/'manifest.json').write_text(json.dumps(d['source_sha256'],indent=2)+'\n')
