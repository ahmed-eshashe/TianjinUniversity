from pathlib import Path
import urllib.request,concurrent.futures,sys,hashlib,json,zipfile
url=sys.argv[1];out=Path('verified-downloads')/urllib.parse.unquote(url.rsplit('/',1)[1])
receipt=out.with_name(out.name+'.receipt.json')
if out.exists() and receipt.exists():
 saved=json.loads(receipt.read_text())
 if saved['url']==url and hashlib.sha256(out.read_bytes()).hexdigest()==saved['sha256']:
  print('Already verified',out);sys.exit(0)
for head_attempt in range(3):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=20)as r:total=int(r.headers['Content-Length'])
  break
 except OSError:
  if head_attempt==2:raise
size=(total+7)//8
parts=[(i,i*size,min(total-1,(i+1)*size-1))for i in range(8)if i*size<total]
def get(part):
 i,a,b=part
 p=out.with_name(out.name+f'.part{i}')
 for attempt in range(5):
  have=p.stat().st_size if p.exists() else 0
  assert have<=b-a+1
  if have==b-a+1:return p
  offset=a+have
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={offset}-{b}'}),timeout=90)as r:
    assert r.status==206 and r.headers['Content-Range']==f'bytes {offset}-{b}/{total}'
    with p.open('ab',buffering=0)as f:
     while True:
      block=r.read(1048576)
      if not block:break
      f.write(block)
  except (OSError,TimeoutError) as error:
   if attempt==4:raise
 assert p.stat().st_size==b-a+1
 return p
with concurrent.futures.ThreadPoolExecutor(max_workers=8)as pool:paths=list(pool.map(get,parts))
with out.open('wb')as f:
 for p in paths:f.write(p.read_bytes())
if out.suffix=='.zip':
 with zipfile.ZipFile(out)as z:assert z.testzip()is None
out.with_name(out.name+'.receipt.json').write_text(json.dumps({'url':url,'bytes':total,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zip_crc_passed':out.suffix=='.zip'},indent=2)+'\n')
print('Downloaded and checked',out)
