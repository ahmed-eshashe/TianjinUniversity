from pathlib import Path
import xml.etree.ElementTree as E
import subprocess,json,concurrent.futures,os
root=Path('.').resolve();pm=root/'PhysX/omni/ovexts/tools/packman/packman';source=Path('/home/omen/.cache/packman/chk/kit-kernel/110.3.0+feature.manylinux_2_35_x86_64.release/dev/all-deps.packman.xml')
names={'pybind11','glm','python','cxxopts','doctest','carb_sdk_plugins','usd-release','cuda','imgui','omni_client_library','gsl','boost_preprocessor','premake'}
pkgs=[]
for d in E.parse(source).getroot().findall('dependency'):
 if d.get('name') in names:
  p=d.find('package');pkgs.append((p.get('name'),'2.4.5+nv1-3'if d.get('name')=='doctest'else p.get('version')))
pkgs += [('usd_ext_physics','25.11+feature.78482.ea68db0a.gl.manylinux_2_35_x86_64.release'),('ovruntime_deps.release','110.1.1+production.305458.6312fa25.gl.manylinux_2_35_x86_64')]
if os.environ.get('TOMATO_SKIP_CUDA')=='1':pkgs=[p for p in pkgs if p[0]!='cuda']
records=[]
def fetch(pkg):
 name,ver=pkg
 r=subprocess.run([str(pm),'resolve',name,ver],capture_output=True,text=True,timeout=60)
 if r.returncode:raise RuntimeError(r.stderr+r.stdout)
 lines=r.stdout.strip().splitlines();urls=[s for s in lines if s.startswith('https://')]
 # A locally installed package is already ready; otherwise obtain the official resolved archive.
 if not urls:return {'package':name,'version':ver,'resolution':r.stdout,'local':True}
 url=urls[-1]
 log=root/(name.replace('/','_')+'.fetch.log')
 with log.open('w')as f:
  q=subprocess.run(['python3','fetch_package.py',url],stdout=f,stderr=subprocess.STDOUT,timeout=3600)
 if q.returncode:raise RuntimeError('Download failed: '+str(log))
 return {'package':name,'version':ver,'url':url,'local':False}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 for result in pool.map(fetch,pkgs):
  records.append(result);print('Ready:',result['package'],flush=True)
  Path('dependency_seed_partial.json').write_text(json.dumps(records,indent=2)+'\n')
for r in records:
 if not r['local']:
  p=subprocess.run([str(pm),'install',r['package'],r['version'],'-pf','local-download.packman.xml','-r','resumed-local'],capture_output=True,text=True,timeout=180)
  Path(r['package']+'.install.log').write_text(p.stdout+p.stderr)
  if p.returncode:raise RuntimeError('Install failed: '+r['package'])
  print('Installed:',r['package'],flush=True)
Path('dependency_seed_non_cuda_complete.json' if os.environ.get('TOMATO_SKIP_CUDA')=='1' else 'dependency_seed_complete.json').write_text(json.dumps(records,indent=2)+'\n')
