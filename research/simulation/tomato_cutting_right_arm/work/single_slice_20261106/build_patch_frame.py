from pathlib import Path
r=Path(__file__).resolve().parents[2]/'rl'
s=(r/'tomato_failed_safe_objective.py').read_text();s=s[s.index('import warp as wp'):]
s=s.replace('anchors:wp.array[wp.vec3i]','anchors:wp.array3d[wp.float64]')
block='a=anchors[p];p0=pairs[p,a[0]];p1=pairs[p,a[1]];p2=pairs[p,a[2]]'
long=block+';origin=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-origin;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-origin'
s=s.replace(long,'u,v=patch_vectors(x,pairs,anchors,p)')
s=s.replace(block+'\n origin=wp.float64(.5)*(x[p0[0]]+x[p0[1]]);u=wp.float64(.5)*(x[p1[0]]+x[p1[1]])-origin;v=wp.float64(.5)*(x[p2[0]]+x[p2[1]])-origin','u,v=patch_vectors(x,pairs,anchors,p)')
a=s.index(' ga=-grad_u-grad_v;');b=s.index('\n\n\n@wp.kernel(enable_backward=False)',a)
s=s[:a]+''' for j in range(8):
  if j<counts[p]:
   pair=pairs[p,j];grad=anchors[p,j,0]*grad_u+anchors[p,j,1]*grad_v
   wp.atomic_add(force,pair[0],-wp.float64(.5)*factor*grad);wp.atomic_add(force,pair[1],-wp.float64(.5)*factor*grad)
'''+s[b:]
s=s.replace('wp.length(u)<=wp.float64(1.e-8) or wp.length(wp.cross(u,v))<=wp.float64(1.e-12)','wp.length(u)<=wp.float64(1.e-8) or wp.length(wp.cross(u,v))<=wp.float64(1.e-8)')
helper='''\n@wp.func
def patch_vectors(x:wp.array[wp.vec3d],pairs:wp.array2d[wp.vec2i],coeff:wp.array3d[wp.float64],p:int):
 u=wp.vec3d(0.);v=wp.vec3d(0.)
 for j in range(8):
  pair=pairs[p,j];mid=wp.float64(.5)*(x[pair[0]]+x[pair[1]])
  u+=coeff[p,j,0]*mid;v+=coeff[p,j,1]*mid
 return u,v
'''
s=s.replace('import warp as wp','import warp as wp\n'+helper,1)
assert 'p0[' not in s
(r/'tomato_patch_frame_objective.py').write_text('"""Weighted affine patch frame; original bilinear cohesive law. Versioned model extension."""\n'+s)
s=(r/'tomato_failed_safe_coupled.py').read_text();s=s[s.index('import warp as wp'):].replace('frame_differentials,gap_jac,put_block','gap_jac,put_block,skew3');s=s.replace('anchors:wp.array[wp.vec3i]','anchors:wp.array3d[wp.float64]')
a=s.index(';a=anchors[p];');b=s.index(';t=wp.normalize(u)',a)
s=s[:a]+';half=wp.float64(.5);zero=wp.float64(0.);one=wp.float64(1.);u,v=patch_vectors(x,pairs,anchors,p)'+s[b:]
s=s.replace('frame_differentials(na,p0,p1,p2,u,v,t,n,sign[p])','patch_differentials(na,p,pairs,anchors,u,v,t,n,sign[p])').replace('frame_differentials(nb,p0,p1,p2,u,v,t,n,sign[p])','patch_differentials(nb,p,pairs,anchors,u,v,t,n,sign[p])')
helper='''from tomato_patch_frame_objective import patch_vectors

@wp.func
def patch_differentials(node:int,p:int,pairs:wp.array2d[wp.vec2i],coeff:wp.array3d[wp.float64],u:wp.vec3d,v:wp.vec3d,t:wp.vec3d,n:wp.vec3d,sign:wp.float64):
 au=wp.float64(0.);av=wp.float64(0.)
 for j in range(8):
  for side in range(2):
   if pairs[p,j][side]==node:au+=wp.float64(.5)*coeff[p,j,0];av+=wp.float64(.5)*coeff[p,j,1]
 identity=wp.identity(n=3,dtype=wp.float64);T=(au/wp.length(u))*(identity-wp.outer(t,t));C=av*skew3(u)-au*skew3(v);N=(sign/wp.length(wp.cross(u,v)))*(identity-wp.outer(n,n))*C;B=-skew3(t)*N+skew3(n)*T;return N,T,B

'''
pos=s.index('@wp.kernel');s=s[:pos]+helper+s[pos:];(r/'tomato_patch_frame_coupled.py').write_text('"""Complete weighted-patch frame GN blocks; unchanged traction law."""\n'+s)
s=(r/'tomato_failed_safe_global.py').read_text().replace('from tomato_failed_safe_coupled import','from tomato_patch_frame_coupled import').replace('from tomato_failed_safe_objective import','from tomato_patch_frame_objective import')
(r/'tomato_patch_frame_global.py').write_text(s)
s=(r/'tomato_live_history_transaction.py').read_text().replace('from tomato_failed_safe_objective import','from tomato_patch_frame_objective import')
(r/'tomato_patch_frame_transaction.py').write_text(s)
s=(r/'tomato_live_fracture_candidate.py').read_text().replace('from tomato_failed_safe_global import','from tomato_patch_frame_global import').replace('from tomato_live_history_transaction import','from tomato_patch_frame_transaction import')
(r/'tomato_patch_frame_fracture.py').write_text(s)
