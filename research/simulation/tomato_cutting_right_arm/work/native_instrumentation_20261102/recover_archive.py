from pathlib import Path
import json,urllib.request,concurrent.futures,shutil,zipfile,hashlib,time
m=json.loads(Path('repair_range.json').read_text());source=Path('/tmp/tmpocsdgupb/physxsdk@5.9.1.21bc7b56-release-omni-110.3-linux-x86_64.zip');total=source.stat().st_size
start=m['start'];n=4;width=(total-start+n-1)//n
chunks=[(k,start+k*width,min(total-1,start+(k+1)*width-1))for k in range(n)if start+k*width<total]
def fetch(item):
 k,a,b=item;p=Path(f'official_tail_{k}.bin');req=urllib.request.Request(m['source_url'],headers={'Range':f'bytes={a}-{b}'})
 with urllib.request.urlopen(req,timeout=90)as r:
  assert r.status==206 and r.headers['Content-Range']==f'bytes {a}-{b}/{total}'
  data=r.read();assert len(data)==b-a+1;p.write_bytes(data)
 return item
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(fetch,chunks))
p=Path('verified-downloads');p.mkdir(exist_ok=True);dest=p/source.name;assert not dest.exists();shutil.copy2(source,dest)
with dest.open('r+b')as f:
 for k,a,b in chunks:f.seek(a);f.write(Path(f'official_tail_{k}.bin').read_bytes())
with zipfile.ZipFile(dest)as z:assert z.testzip()is None;count=len(z.infolist())
Path('archive_verification.json').write_text(json.dumps({'official_source':m['source_url'],'replaced_range_start':start,'archive_bytes':total,'zip_entries_crc_passed':count,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2)+'\n')
print('All',count,'archive entries pass CRC; recovered only from official HTTP ranges.')
