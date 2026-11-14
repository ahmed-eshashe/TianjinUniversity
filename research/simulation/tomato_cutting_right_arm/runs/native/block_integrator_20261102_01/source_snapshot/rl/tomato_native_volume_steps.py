"""Feasible numerical trial steps for the original J > 0.1 volume barrier."""
import warp as wp

@wp.kernel
def predictor_fraction(x:wp.array[wp.vec3],displacement:wp.array[wp.vec3],cells:wp.array[wp.vec4i],volumes:wp.array[float],fraction:wp.array[float],invalid:wp.array[int]):
 i=wp.tid();ids=cells[i];d1=x[ids[1]]-x[ids[0]];d2=x[ids[2]]-x[ids[0]];d3=x[ids[3]]-x[ids[0]];e1=displacement[ids[1]]-displacement[ids[0]];e2=displacement[ids[2]]-displacement[ids[0]];e3=displacement[ids[3]]-displacement[ids[0]];scale=1./(6.*volumes[i]);j=wp.dot(d1,wp.cross(d2,d3))*scale
 c1=(wp.dot(e1,wp.cross(d2,d3))+wp.dot(d1,wp.cross(e2,d3))+wp.dot(d1,wp.cross(d2,e3)))*scale
 c2=(wp.dot(e1,wp.cross(e2,d3))+wp.dot(e1,wp.cross(d2,e3))+wp.dot(d1,wp.cross(e2,e3)))*scale;c3=wp.dot(e1,wp.cross(e2,e3))*scale;bound=wp.abs(c1)+wp.abs(c2)+wp.abs(c3)
 if j<=.1:wp.atomic_add(invalid,0,1)
 elif j-bound<=.1:wp.atomic_min(fraction,0,.9*(j-.1)/bound)

@wp.kernel
def apply_predictor(x:wp.array[wp.vec3],baseline:wp.array[wp.vec3],displacement:wp.array[wp.vec3],fraction:wp.array[float]):
 i=wp.tid();x[i]=baseline[i]+fraction[0]*displacement[i];displacement[i]=x[i]-baseline[i]

@wp.kernel
def colored_step(color:int,colors:wp.array[int],x:wp.array[wp.vec3],baseline:wp.array[wp.vec3],displacement:wp.array[wp.vec3],offsets:wp.array[int],rows:wp.array[int],cells:wp.array[wp.vec4i],volumes:wp.array[float],invalid:wp.array[int],clips:wp.array[int]):
 node=wp.tid()
 if colors[node]==color:
  delta=baseline[node]+displacement[node]-x[node];fraction=float(1.)
  if wp.length(delta)>0.:
   for index in range(offsets[node],offsets[node+1]):
    i=rows[index];ids=cells[i];d1=x[ids[1]]-x[ids[0]];d2=x[ids[2]]-x[ids[0]];d3=x[ids[3]]-x[ids[0]];scale=1./(6.*volumes[i]);j=wp.dot(d1,wp.cross(d2,d3))*scale;g1=wp.cross(d2,d3)*scale;g2=wp.cross(d3,d1)*scale;g3=wp.cross(d1,d2)*scale;g=-g1-g2-g3
    if node==ids[1]:g=g1
    elif node==ids[2]:g=g2
    elif node==ids[3]:g=g3
    slope=wp.dot(g,delta)
    if j<=.1:wp.atomic_add(invalid,0,1)
    elif j+slope<=.1:fraction=wp.min(fraction,.9*(j-.1)/(-slope))
   if fraction<1.:wp.atomic_add(clips,0,1)
   x[node]=x[node]+fraction*delta;displacement[node]=x[node]-baseline[node]

@wp.kernel
def validate_final_material(x:wp.array[wp.vec3],pairs:wp.array2d[wp.vec2i],rest:wp.array2d[wp.vec3],counts:wp.array[int],history:wp.array[wp.vec2],eligible:wp.array[int],invalid:wp.array[int]):
 patch=wp.tid()
 if eligible[patch]!=0 and history[patch][1]<1.:
  for j in range(counts[patch]):
   pair=pairs[patch,j];g=x[pair[1]]-x[pair[0]]-rest[patch,j]
   if g[0]<-1.e-12 and wp.length(wp.vec2(g[1],g[2]))>1.e-12:wp.atomic_add(invalid,0,1)
