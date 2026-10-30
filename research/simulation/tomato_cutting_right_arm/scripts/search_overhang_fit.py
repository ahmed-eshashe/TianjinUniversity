"""3-D handle fit with the original board shifted to permit handle overhang."""
from pathlib import Path
exec(Path(__file__).with_name('search_handle_fit.py').read_text().split('centers=np.array')[0])
centers=np.array(list(itertools.product(np.linspace(.04,.12,81),[-.04],np.linspace(.06,.145,86))))
rot=old@Rotation.from_euler('y',75,degrees=True).as_matrix();kv=world_vectors@rot;kv=kv[ConvexHull(kv).vertices]
board=s.GetPrimAtPath('/Indoor/RZ/SM_kitchen_Board');bm=np.array(xc.GetLocalToWorldTransform(board)).T;bv=np.array(UsdGeom.Mesh(board).GetPointsAttr().Get());blo=bv.min(0);bhi=bv.max(0)
h=km[:3,:3]@np.array(meta['knife_handle_local'])+km[:3,3];direction=old[:,1];bi=np.linalg.inv(bm);hl=bi[:3,:3]@h+bi[:3,3];dl=bi[:3,:3]@direction
edge=min((bhi[i]-hl[i])/dl[i] if dl[i]>0 else (blo[i]-hl[i])/dl[i] for i in [0,1] if abs(dl[i])>1e-6);bm[:3,3]-=direction*(edge-.02);bi=np.linalg.inv(bm);hl=bi[:3,:3]@h+bi[:3,3]
centers_b=centers@rot.T@bi[:3,:3].T;cache={};results=[]
for finger,pitch,yaw in itertools.product([50,60,70,80,90],[5,10,15,20,25],[20,40,60,77]):
 vs=geometry({'index':finger,'middle':finger,'ring':finger,'pinky':90},yaw,pitch);dists=[];normals=[];board_mins=[];table_mins=[]
 for name,v in vs:
  key=(name,pitch,yaw) if 'thumb' in name else (name,finger)
  if key not in cache:
   v=v[ConvexHull(v).vertices];obstacle=(v[:,None,:]-kv[None,:,:]).reshape(-1,3);eq=ConvexHull(obstacle).equations
   ds=centers@eq[:,:3].T+eq[:,3];ii=ds.argmax(1);dd=ds[np.arange(len(centers)),ii];nn=eq[ii,:3]
   zz=(v@rot[2])[:,None]-(centers@rot[2])[None,:];vb=v@rot.T@bi[:3,:3].T
   xx=hl[0]+vb[:,0,None]-centers_b[None,:,0];yy=hl[1]+vb[:,1,None]-centers_b[None,:,1]
   inside=(xx>=blo[0])&(xx<=bhi[0])&(yy>=blo[1])&(yy<=bhi[1])
   board_min=np.where(inside,zz,1e3).min(0);table_min=zz.min(0)
   cache[key]=(dd,nn,board_min,table_min)
  dd,nn,bb,tt=cache[key];dists.append(dd);normals.append(nn);board_mins.append(bb);table_mins.append(tt)
 di=next(i for i,(n,v) in enumerate(vs) if 'index_distal' in n);dt=next(i for i,(n,v) in enumerate(vs) if 'thumb_distal' in n)
 dists=np.array(dists);opp=np.sum(normals[di]*normals[dt],axis=1);nz_i=np.abs(normals[di]@rot[2]);nz_t=np.abs(normals[dt]@rot[2]);ny=np.maximum(np.abs(normals[di][:,1]),np.abs(normals[dt][:,1]))
 bmmin=np.min(board_mins,axis=0);tmmin=np.min(table_mins,axis=0)
 cost=((dists[di]-.0005)**2+(dists[dt]-.0005)**2)*1e4+np.maximum(-.0003-dists,0).sum(0)*100+np.maximum(opp+.85,0)*5+np.maximum(nz_i-.2,0)*5+np.maximum(nz_t-.2,0)*5+np.maximum(ny-.3,0)*5+np.maximum(-.027-tmmin,0)*100+np.maximum(-.0075-bmmin,0)*100
 j=cost.argmin();results.append({'cost':float(cost[j]),'finger':finger,'pitch':pitch,'yaw':yaw,'tilt':75,'center_xyz':centers[j].tolist(),'min_board_relative':float(bmmin[j]),'min_table_relative':float(tmmin[j]),'index_gap':float(dists[di,j]),'thumb_gap':float(dists[dt,j]),'opposition':float(opp[j]),'index_normal_vertical':float(nz_i[j]),'thumb_normal_vertical':float(nz_t[j])})
 if len(results)%10==0:
  print('progress',len(results),'best',min(results,key=lambda x:x['cost']),flush=True);json.dump(sorted(results,key=lambda x:x['cost'])[:40],open('work/overhang_fit_candidates.json','w'),indent=2)
results.sort(key=lambda x:x['cost']);json.dump(results[:40],open('work/overhang_fit_candidates.json','w'),indent=2)
