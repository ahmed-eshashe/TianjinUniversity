from pathlib import Path
W=Path(__file__).resolve().parents[1];s=(W/'src/partition_gpu.py').read_text();start=s.index('@wp.kernel\ndef integrate(');end=s.index('\n@wp.kernel\ndef collect',start);block=s[start:end]
signature_end=block.index('\n pair=');header=block[:signature_end].replace('maxdepth:int):','maxdepth:int,polycounts:wp.array(dtype=int),polysources:wp.array(dtype=int),active_count:wp.array(dtype=int)):')
calcstart=block.index('\n pair=');clipstart=block.index('\n if intersects and bad[0]==0:');clipend=block.index('\n  if n>=3 and bad[0]==0:',clipstart)
calc=block[calcstart:clipstart];clip=block[clipstart:clipend]
prepare=header.replace('def integrate(', 'def prepare_domains(')+calc+'\n polycounts[pair]=0;polysources[pair]=0'+clip+'''
  if n>=3:
   area=wp.float64(0.)
   for k in range(1,n-1):
    B=wp.matrix_from_rows(polygon[pair,src,0],polygon[pair,src,k],polygon[pair,src,k+1]);area+=wp.abs(wp.determinant(B))
   if area>wp.float64(1e-30):polycounts[pair]=n;polysources[pair]=src;wp.atomic_add(active_count,0,1)
'''
integrate=header+calc+'\n if polycounts[pair]>=3 and bad[0]==0:\n  n=polycounts[pair];src=polysources[pair]'+block[clipend:]
integrate=integrate.replace('atol=absolute_tol*areas[face]/(area_total*wp.float64(ncells))','atol=absolute_tol/wp.float64(active_count[0])')
s=s[:start]+prepare+'\n'+integrate+s[end:]
s=s.replace('capacity=256','capacity=64')
s=s.replace("self.failure=wp.zeros(6,dtype=wp.float64,device='cuda:0');self.adaptive=True", "self.failure=wp.zeros(6,dtype=wp.float64,device='cuda:0');self.polycounts=wp.zeros(self.npairs,dtype=int,device='cuda:0');self.polysources=wp.zeros(self.npairs,dtype=int,device='cuda:0');self.active_count=wp.zeros(1,dtype=int,device='cuda:0');self.adaptive=True")
a=s.index('  wp.launch(integrate,self.npairs,');b=s.index('\n  wp.launch(collect',a)
launch=s[a:b].replace('self.maxdepth],block_dim=32)','self.maxdepth,self.polycounts,self.polysources,self.active_count],block_dim=32)')
s=s[:a]+'  self.active_count.zero_()\n'+launch.replace('wp.launch(integrate,','wp.launch(prepare_domains,')+'\n'+launch+s[b:]
(W/'src/allocated_gpu.py').write_text(s)
p=W/'tests/partition_contact_cycle.py';s=p.read_text().replace('from partition_gpu import','from allocated_gpu import').replace("name='partition_r4_'","name='allocated_'").replace('relative_tol=o.tol)','relative_tol=o.tol,absolute_tol=o.tol*.0005)')
s=s.replace("(out/'exception.txt').write_text(repr(e))", "(out/'exception.txt').write_text(repr(e));ii=int(g.failure.numpy()[0]);np.savez(out/'failure_details.npz',failure=g.failure.numpy(),B=g.Bs.numpy()[ii],values=g.vals.numpy()[ii],depths=g.depths.numpy()[ii])")
(W/'tests/allocated_contact_cycle.py').write_text(s)
p=W/'tests/partition_static_gpu.py';s=p.read_text().replace('from partition_gpu import','from allocated_gpu import').replace('partition_static_gpu_cap256.json','allocated_static_gpu.json').replace("relative_tol=ref['relative_tol'])", "relative_tol=ref['relative_tol'],absolute_tol=ref['relative_tol']*.0005)")
(W/'tests/allocated_static_gpu.py').write_text(s)
