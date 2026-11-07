from pathlib import Path
import subprocess,json,hashlib,urllib.parse
pm=Path('PhysX/omni/ovexts/tools/packman/packman').resolve()
for receipt in sorted(Path('verified-downloads').glob('*.receipt.json')):
 d=json.loads(receipt.read_text());archive=receipt.with_name(receipt.name.removesuffix('.receipt.json'))
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==d['sha256']
 stem=archive.name.removesuffix('.7z').removesuffix('.zip');name,ver=stem.split('@',1)
 r=subprocess.run([str(pm),'install',name,ver,'-pf','local-download.packman.xml','-r','resumed-local'],capture_output=True,text=True,timeout=300)
 Path(name+'.install.log').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(name+' install failed')
 print('Installed:',name,flush=True)
