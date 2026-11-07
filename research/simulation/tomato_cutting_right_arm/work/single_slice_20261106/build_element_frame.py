from pathlib import Path
r=Path(__file__).resolve().parents[2]/'rl'
for old,new in [('objective','objective'),('coupled','coupled'),('global','global'),('transaction','transaction'),('fracture','fracture')]:
 s=(r/f'tomato_patch_frame_{old}.py').read_text().replace('tomato_patch_frame_','tomato_element_frame_')
 if old=='objective':s=s.replace('range(8)','range(16)')
 if old=='coupled':s=s.replace('range(8)','range(16)').replace('offset+256*p+16*sa+sb','offset+1024*p+32*sa+sb')
 if old=='global':s=s.replace('cohesive_offset+256*np','cohesive_offset+1024*np').replace('dim=(np,16,16)','dim=(np,32,32)')
 (r/f'tomato_element_frame_{new}.py').write_text(s)
s=(r/'tomato_patch_frame_live.py').read_text().replace('tomato_patch_frame_','tomato_element_frame_');a=s.index('def frame_coefficients');b=s.index('class PatchFrameLiveCAD',a)
s=s[:a]+'''def frame_support(data):
 from tomato_objective_cohesion_reference import make_patch
 import itertools
 pairs=data['pairs'];lookup={int(a):i for i,(a,b) in enumerate(pairs)}
 tetra_faces={tuple(sorted(t[list(c)])) for t in data['cells'] for c in itertools.combinations(range(4),3)}
 piece=data['design']['pieces'][0];faces=[]
 for face,tag in zip(piece['triangles'],piece['face_tags']):
  if tag!='cut' or tuple(sorted(face)) not in tetra_faces:continue
  partner=[int(pairs[lookup[int(a)],1]) for a in face]
  if tuple(sorted(partner)) in tetra_faces:faces.append(face)
 faces=np.asarray(faces,int)
 if not len(faces):raise ValueError('No jointly volume-backed interface face')
 centers=data['x'][faces].mean(1);all_pairs=np.zeros((47,16,2),np.int32);coefficients=np.zeros((47,16,2));all_weights=np.zeros((47,16));counts=[];models=[];supports=[]
 for i,p in enumerate(data['cohesion'].patches):
  original=data['pairs'][p['indices']];law=p['law'];m=make_patch(data['x'][original],p['weights'],p['stiffness'],(law.onset_m,law.failure_m,law.stiffness_n_m));mid=data['x'][original].mean(1);a,b,c=m['anchors'];u=mid[b]-mid[a];u/=np.linalg.norm(u);v=mid[c]-mid[a];v-=u*(v@u);v/=np.linalg.norm(v);basis=np.column_stack([u,v])
  anchor=np.array(data['design']['interface_patches'][i]['anchor_yz_m']);face=faces[np.argmin(np.linalg.norm(centers[:,1:]-anchor,axis=1))];nodes=list(p['indices']);support_ids=[]
  for node in face:
   index=lookup[int(node)]
   if index not in nodes:nodes.append(index)
   support_ids.append(nodes.index(index))
  all_pairs[i,:len(nodes)]=pairs[nodes];counts.append(len(nodes));all_weights[i,:len(original)]=p['weights'];points=data['x'][face];coordinates=(points-points.mean(0))@basis;fit=np.linalg.solve(coordinates.T@coordinates,coordinates.T);fit-=fit.sum(1)[:,None]/3
  if np.max(abs(fit@coordinates-np.eye(2)))>1e-10:raise ValueError('Invalid face deformation map')
  coefficients[i,support_ids]=fit.T;models.append(m);supports.append(face.tolist())
 return all_pairs,np.array(counts,np.int32),coefficients,all_weights,models,supports

def configure_patch_frame(holder,data):
 pairs,counts,coefficients,weights,_,_=frame_support(data)
 holder.pairs=wp.array(pairs,dtype=wp.vec2i);holder.counts=wp.array(counts,dtype=int);holder.objective_weights=wp.array(weights,dtype=wp.float64);holder.objective_anchors=wp.array(coefficients,dtype=wp.float64)
 return holder

'''+s[b:]
s=s.replace('Versioned weighted affine interface frames','Versioned volume-backed element interface frames')
(r/'tomato_element_frame_live.py').write_text(s)
s=(r/'tomato_adaptive_patch_slice_engine.py').read_text().replace('tomato_patch_frame_live','tomato_element_frame_live')
(r/'tomato_element_frame_slice_engine.py').write_text(s)
