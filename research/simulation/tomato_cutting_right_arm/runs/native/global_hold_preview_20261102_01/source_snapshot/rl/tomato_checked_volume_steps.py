"""Volume bounds verified at the actual binary32 candidate coordinates.

The constitutive J=0.1 floor is unchanged. Rejected numerical proposals are
halved until both float64 geometry and the production float32 barrier agree
that every incident cell remains strictly admissible.
"""
import warp as wp

@wp.func
def double_ratio(a:wp.vec3,b:wp.vec3,c:wp.vec3,d:wp.vec3,v:wp.float64):
 aa=wp.vec3d(wp.float64(a[0]),wp.float64(a[1]),wp.float64(a[2]));bb=wp.vec3d(wp.float64(b[0]),wp.float64(b[1]),wp.float64(b[2]));cc=wp.vec3d(wp.float64(c[0]),wp.float64(c[1]),wp.float64(c[2]));dd=wp.vec3d(wp.float64(d[0]),wp.float64(d[1]),wp.float64(d[2]))
 return wp.dot(bb-aa,wp.cross(cc-aa,dd-aa))/(wp.float64(6.)*v)

@wp.func
def valid_cell(a:wp.vec3,b:wp.vec3,c:wp.vec3,d:wp.vec3,v:float,v64:wp.float64):
 e=b-a;f=c-a;g=d-a;scale=1./(6.*v);j=wp.dot(e,wp.cross(f,g))*scale
 # A conservative roundoff bound for differences, six triple products,
 # determinant accumulation and division. Original binary32 coordinates are
 # exact inputs; 64*eps exceeds the operation-count gamma bound here.
 absolute=wp.abs(e[0]*f[1]*g[2])+wp.abs(e[0]*f[2]*g[1])+wp.abs(e[1]*f[0]*g[2])+wp.abs(e[1]*f[2]*g[0])+wp.abs(e[2]*f[0]*g[1])+wp.abs(e[2]*f[1]*g[0])
 relative_volume_error=float(wp.abs(wp.float64(v)-v64)/v64)
 bound=64.*1.1920928955078125e-7*absolute*wp.abs(scale)+wp.abs(j)*relative_volume_error
 valid=bool(False)
 if wp.isfinite(j) and j>.1:
  if j>.1+bound:valid=True
  else:valid=double_ratio(a,b,c,d,v64)>wp.float64(.1)
 return valid

@wp.kernel
def check_predictor(baseline:wp.array[wp.vec3],displacement:wp.array[wp.vec3],cells:wp.array[wp.vec4i],volumes:wp.array[float],volumes64:wp.array[wp.float64],fraction:wp.array[float],active:wp.array[int],bad:wp.array[int]):
 i=wp.tid()
 if active[0]!=0:
  t=cells[i];f=fraction[0];a=baseline[t[0]]+f*displacement[t[0]];b=baseline[t[1]]+f*displacement[t[1]];c=baseline[t[2]]+f*displacement[t[2]];d=baseline[t[3]]+f*displacement[t[3]]
  if not valid_cell(a,b,c,d,volumes[i],volumes64[i]):wp.atomic_add(bad,0,1)

@wp.kernel
def finish_predictor(fraction:wp.array[float],active:wp.array[int],bad:wp.array[int]):
 if active[0]!=0:
  if bad[0]>0:fraction[0]*=.5
  else:active[0]=0

@wp.kernel
def checked_colored_step(color:int,colors:wp.array[int],x:wp.array[wp.vec3],baseline:wp.array[wp.vec3],displacement:wp.array[wp.vec3],offsets:wp.array[int],rows:wp.array[int],cells:wp.array[wp.vec4i],volumes:wp.array[float],volumes64:wp.array[wp.float64],invalid:wp.array[int],clips:wp.array[int]):
 node=wp.tid()
 if colors[node]==color:
  delta=baseline[node]+displacement[node]-x[node];fraction=float(1.);accepted=bool(False);candidate=x[node]
  # Start from the analytic affine bound; verify actual rounded candidates below.
  for index in range(offsets[node],offsets[node+1]):
   i=rows[index];t=cells[i];a=x[t[0]];b=x[t[1]];c=x[t[2]];d=x[t[3]]
   old=wp.dot(b-a,wp.cross(c-a,d-a))/(6.*volumes[i]);proposed=x[node]+delta
   if node==t[0]:a=proposed
   elif node==t[1]:b=proposed
   elif node==t[2]:c=proposed
   elif node==t[3]:d=proposed
   new=wp.dot(b-a,wp.cross(c-a,d-a))/(6.*volumes[i]);slope=new-old
   if new<=.1 and slope<0.:fraction=wp.min(fraction,.9*(old-.1)/(-slope))
  for attempt in range(40):
   if not accepted:
    candidate=x[node]+fraction*delta;okay=bool(True)
    for index in range(offsets[node],offsets[node+1]):
     i=rows[index];t=cells[i];a=x[t[0]];b=x[t[1]];c=x[t[2]];d=x[t[3]]
     if node==t[0]:a=candidate
     elif node==t[1]:b=candidate
     elif node==t[2]:c=candidate
     elif node==t[3]:d=candidate
     if not valid_cell(a,b,c,d,volumes[i],volumes64[i]):okay=False
    if okay:accepted=True
    else:fraction*=.5
  if not accepted:wp.atomic_add(invalid,0,1)
  else:
   if fraction<1.:wp.atomic_add(clips,0,1)
   x[node]=candidate;displacement[node]=candidate-baseline[node]

@wp.kernel
def reject_unverified_predictor(fraction:wp.array[float],active:wp.array[int],invalid:wp.array[int]):
 if active[0]!=0:
  fraction[0]=0.;wp.atomic_add(invalid,0,1)
