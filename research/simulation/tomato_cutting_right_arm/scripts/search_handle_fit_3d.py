"""Three-dimensional convex contact fit for the existing knife handle and hand."""
from pathlib import Path
prefix=Path(__file__).with_name('search_handle_fit.py').read_text().split('centers=np.array')[0]
exec(prefix)
centers=np.array(list(itertools.product(np.linspace(.04,.085,46),[-.05,-.025,0,.025,.05],np.linspace(.075,.13,56))))
rot=old@Rotation.from_euler('y',75,degrees=True).as_matrix();kv=world_vectors@rot;kv=kv[ConvexHull(kv).vertices]
results=[]
for finger,pitch,yaw in itertools.product([80,90],[0,5,10,15,20,25,30],[0,20,40,60,77]):
 vs=geometry(finger,yaw,pitch);dists=[];normals=[]
 for name,v in vs:
  v=v[ConvexHull(v).vertices];obstacle=(v[:,None,:]-kv[None,:,:]).reshape(-1,3);eq=ConvexHull(obstacle).equations
  ds=centers@eq[:,:3].T+eq[:,3];ii=ds.argmax(1);dists.append(ds[np.arange(len(centers)),ii]);normals.append(eq[ii,:3])
 di=next(i for i,(n,v) in enumerate(vs) if 'index_distal' in n);dt=next(i for i,(n,v) in enumerate(vs) if 'thumb_distal' in n)
 dists=np.array(dists);opp=np.sum(normals[di]*normals[dt],axis=1)
 minheight=np.concatenate([v for _,v in vs])@rot[2];minheight=minheight.min()-centers@rot[2]
 nz_i=np.abs(normals[di]@rot[2]);nz_t=np.abs(normals[dt]@rot[2])
 cost=(dists[di]**2+dists[dt]**2)*1e4+np.maximum(-.0003-dists,0).sum(0)*100+np.maximum(opp+.85,0)*5+np.maximum(nz_i-.2,0)*5+np.maximum(nz_t-.2,0)*5+np.maximum(-.0095-minheight,0)*100
 j=cost.argmin();results.append({'cost':float(cost[j]),'finger':finger,'pitch':pitch,'yaw':yaw,'tilt':75,'center_xyz':centers[j].tolist(),'minimum_height_relative_handle':float(minheight[j]),'index_gap':float(dists[di,j]),'thumb_gap':float(dists[dt,j]),'opposition':float(opp[j]),'index_normal_vertical':float(nz_i[j]),'thumb_normal_vertical':float(nz_t[j])})
 if len(results)%10==0:print('progress',len(results),flush=True)
results.sort(key=lambda x:x['cost']);json.dump(results[:40],open('work/handle_fit_3d_candidates.json','w'),indent=2)
for row in results[:10]:print(row)
