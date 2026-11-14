"""Rest-relative storage with float64 physical geometry; unchanged spring/barrier laws."""
import warp as wp

@wp.func
def physical_point(reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],node:int):
 a=u[node];return reference[node]+wp.vec3d(wp.float64(a[0]),wp.float64(a[1]),wp.float64(a[2]))

@wp.kernel(enable_backward=False)
def reconstruct(reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],x:wp.array[wp.vec3d]):
 i=wp.tid();x[i]=physical_point(reference,u,i)

@wp.kernel(enable_backward=False)
def relative_bulk(color:int,colors:wp.array[int],x:wp.array[wp.vec3d],spring_offsets:wp.array[int],spring_ids:wp.array[int],spring_pairs:wp.array[int],spring_rest:wp.array[wp.float64],spring_k:wp.array[wp.float64],cell_offsets:wp.array[int],cell_ids:wp.array[int],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],invalid:wp.array[int],forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 node=wp.tid()
 if color<0 or colors[node]==color:
  f=wp.vec3d(0.);h=wp.mat33d(0.);identity=wp.identity(n=3,dtype=wp.float64)
  for index in range(spring_offsets[node],spring_offsets[node+1]):
   spring=spring_ids[index];a=spring_pairs[2*spring];b=spring_pairs[2*spring+1];diff=x[a]-x[b];length=wp.max(wp.length(diff),wp.float64(1e-8));l0=spring_rest[spring];k=spring_k[spring];sgn=wp.float64(1.)
   if node!=a:sgn=wp.float64(-1.)
   f+=sgn*k*(l0-length)/length*diff;h+=k*(identity-(l0/length)*(identity-wp.outer(diff,diff)/(length*length)))
  for index in range(cell_offsets[node],cell_offsets[node+1]):
   i=cell_ids[index];ids=cells[i];a=x[ids[1]]-x[ids[0]];b=x[ids[2]]-x[ids[0]];c=x[ids[3]]-x[ids[0]];V=volumes[i];j=wp.dot(a,wp.cross(b,c))/(wp.float64(6.)*V)
   if j<=wp.float64(.1):wp.atomic_add(invalid,0,1)
   elif j<wp.float64(.5):
    r=(j-wp.float64(.1))/wp.float64(.4);first=(wp.float64(1.)-wp.float64(1.)/r)/wp.float64(.4);second=wp.float64(1.)/(r*r*wp.float64(.16));g1=wp.cross(b,c)/(wp.float64(6.)*V);g2=wp.cross(c,a)/(wp.float64(6.)*V);g3=wp.cross(a,b)/(wp.float64(6.)*V);g=-g1-g2-g3
    if node==ids[1]:g=g1
    elif node==ids[2]:g=g2
    elif node==ids[3]:g=g3
    f-=wp.float64(10000.)*V*first*g;h+=wp.float64(10000.)*V*second*wp.outer(g,g)
  forces[node]=wp.vec3(float(f[0]),float(f[1]),float(f[2]));hessians[node]=wp.mat33(float(h[0,0]),float(h[0,1]),float(h[0,2]),float(h[1,0]),float(h[1,1]),float(h[1,2]),float(h[2,0]),float(h[2,1]),float(h[2,2]))

@wp.kernel(enable_backward=False)
def relative_plane(color:int,colors:wp.array[int],x:wp.array[wp.vec3d],stiffness:wp.array[float],height:wp.float64,forces:wp.array[wp.vec3],hessians:wp.array[wp.mat33]):
 i=wp.tid()
 if (color<0 or colors[i]==color) and x[i][2]<height:
  f=forces[i];f[2]+=float(wp.float64(stiffness[i])*(height-x[i][2]));forces[i]=f;h=hessians[i];h[2,2]+=stiffness[i];hessians[i]=h

@wp.kernel(enable_backward=False)
def relative_predictor_check(reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],delta:wp.array[wp.vec3],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],fraction:wp.array[float],active:wp.array[int],bad:wp.array[int],invalid:wp.array[int]):
 i=wp.tid()
 if active[0]!=0:
  ids=cells[i];p0=physical_point(reference,u,ids[0]);p1=physical_point(reference,u,ids[1]);p2=physical_point(reference,u,ids[2]);p3=physical_point(reference,u,ids[3]);q0=u[ids[0]]+fraction[0]*delta[ids[0]];q1=u[ids[1]]+fraction[0]*delta[ids[1]];q2=u[ids[2]]+fraction[0]*delta[ids[2]];q3=u[ids[3]]+fraction[0]*delta[ids[3]];z0=reference[ids[0]]+wp.vec3d(wp.float64(q0[0]),wp.float64(q0[1]),wp.float64(q0[2]));z1=reference[ids[1]]+wp.vec3d(wp.float64(q1[0]),wp.float64(q1[1]),wp.float64(q1[2]));z2=reference[ids[2]]+wp.vec3d(wp.float64(q2[0]),wp.float64(q2[1]),wp.float64(q2[2]));z3=reference[ids[3]]+wp.vec3d(wp.float64(q3[0]),wp.float64(q3[1]),wp.float64(q3[2]));d1=p1-p0;d2=p2-p0;d3=p3-p0;e1=z1-z0-d1;e2=z2-z0-d2;e3=z3-z0-d3;scale=wp.float64(1.)/(wp.float64(6.)*volumes[i]);j=wp.dot(d1,wp.cross(d2,d3))*scale
  c1=(wp.dot(e1,wp.cross(d2,d3))+wp.dot(d1,wp.cross(e2,d3))+wp.dot(d1,wp.cross(d2,e3)))*scale;c2=(wp.dot(e1,wp.cross(e2,d3))+wp.dot(e1,wp.cross(d2,e3))+wp.dot(d1,wp.cross(e2,e3)))*scale;c3=wp.dot(e1,wp.cross(e2,e3))*scale
  if j<=wp.float64(.1):wp.atomic_add(invalid,0,1)
  if j-wp.abs(c1)-wp.abs(c2)-wp.abs(c3)<=wp.float64(.1):wp.atomic_max(bad,0,1)

@wp.func
def ratio_with_candidate(reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],ids:wp.vec4i,node:int,candidate:wp.vec3,volume:wp.float64):
 a=physical_point(reference,u,ids[0]);b=physical_point(reference,u,ids[1]);c=physical_point(reference,u,ids[2]);d=physical_point(reference,u,ids[3]);q=reference[node]+wp.vec3d(wp.float64(candidate[0]),wp.float64(candidate[1]),wp.float64(candidate[2]))
 if ids[0]==node:a=q
 elif ids[1]==node:b=q
 elif ids[2]==node:c=q
 else:d=q
 return wp.dot(b-a,wp.cross(c-a,d-a))/(wp.float64(6.)*volume)

@wp.kernel(enable_backward=False)
def relative_colored_step(color:int,colors:wp.array[int],reference:wp.array[wp.vec3d],u:wp.array[wp.vec3],baseline:wp.array[wp.vec3],displacement:wp.array[wp.vec3],offsets:wp.array[int],rows:wp.array[int],cells:wp.array[wp.vec4i],volumes:wp.array[wp.float64],invalid:wp.array[int],clips:wp.array[int]):
 node=wp.tid()
 if colors[node]==color:
  old=u[node];target=baseline[node]+displacement[node];delta=target-old;fraction=float(1.);baseline_bad=bool(False)
  for index in range(offsets[node],offsets[node+1]):
   cell=rows[index];j=ratio_with_candidate(reference,u,cells[cell],node,old,volumes[cell]);end=ratio_with_candidate(reference,u,cells[cell],node,target,volumes[cell])
   if j<=wp.float64(.1):baseline_bad=True
   elif end<=wp.float64(.1):fraction=wp.min(fraction,float(wp.float64(.9)*(j-wp.float64(.1))/(j-end)))
  accepted=bool(False);candidate=old
  if not baseline_bad:
   for attempt in range(40):
    candidate=old+fraction*delta;safe=bool(True)
    for index in range(offsets[node],offsets[node+1]):
     cell=rows[index]
     if ratio_with_candidate(reference,u,cells[cell],node,candidate,volumes[cell])<=wp.float64(.1):safe=False
    if safe:accepted=True;break
    fraction*=.5
  if accepted:
   u[node]=candidate;displacement[node]=candidate-baseline[node]
   if fraction<1.:wp.atomic_add(clips,0,1)
  else:wp.atomic_add(invalid,0,1)
