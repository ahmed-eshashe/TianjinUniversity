"""Independent CPU value of the undamaged full incremental potential."""
import argparse,json
from pathlib import Path
import numpy as np
from tomato_bulk_reference import bulk_reference
from tomato_global_gn_cpu_reference import closest_point_triangle,closest_edges

def energy(d):
 x=d['x'];free=d['free'].astype(bool);dt=float(d['dt'][0]);bulk=bulk_reference(x,dict(x=d['source_x'],springs=d['spring_pairs'],k=d['spring_k'],cells=d['cells'],volumes=d['volumes']));inertial=float(np.sum(.5*d['mass'][free]/dt**2*np.sum((x[free]-d['target'][free])**2,axis=1)));board=float(np.sum(.5*d['board_k']*np.maximum(float(d['board_height'][0])-x[:,2],0)**2));cohesive=0.
 if np.any(d['history'])or np.any(d['eligible']):raise ValueError('Undamaged independent energy fixture only')
 for p,count in enumerate(d['cohesive_counts']):
  q=x[d['cohesive_pairs'][p,:count]];mid=q.mean(1);aa,bb,cc=d['anchors'][p];u=mid[bb]-mid[aa];v=mid[cc]-mid[aa];t=u/np.linalg.norm(u);n=d['sign'][p]*np.cross(u,v);n/=np.linalg.norm(n);frame=np.column_stack([n,t,np.cross(n,t)]);gap=(q[:,1]-q[:,0])@frame;gap[:,0]=np.maximum(gap[:,0],0);cohesive+=.5*np.sum(d['weights'][p,:count,None]*gap*(gap@d['local_k'][p]))
 radius=float(d['radius'][0]);k=float(d['contact_k'][0]);proxy=d['proxy'];contact=0.;active=0
 for record,ids in enumerate(d['endpoint']):
  p0,p1,p2,p3=proxy[ids];m=1.
  if d['kind'][record]==0:coeff=np.r_[1.,-closest_point_triangle(p0,p1,p2,p3)]
  else:
   s,t=closest_edges(p0,p1,p2,p3);coeff=np.array([1-s,s,-1+t,-t]);u=p1-p0;v=p3-p2;squared=np.linalg.norm(np.cross(u,v))**2;eps=d['threshold'][record]
   if squared<eps:ratio=squared/eps;m=ratio*(2-ratio)
  distance=float(np.linalg.norm(coeff@proxy[ids]))
  if distance>=radius:continue
  active+=1;tau=radius/2;minimum=1e-5;k2=tau*tau*k
  if distance<tau and distance>minimum:value=.5*k2-k2*np.log(distance/tau)
  elif distance<=minimum:
   gap=distance-minimum;value=.5*k2-k2*np.log(minimum/tau)-k2/minimum*gap+.5*k2/minimum**2*gap*gap
  else:value=.5*k*(radius-distance)**2
  contact+=m*value
 return dict(inertial_j=inertial,spring_j=bulk['spring_energy_j'],volume_j=bulk['volume_energy_j'],board_j=board,cohesive_j=float(cohesive),contact_j=float(contact),active_contacts=active,total_j=float(inertial+bulk['energy_j']+board+cohesive+contact))
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=np.load(a.input);values=energy(d);error=abs(values['total_j']-float(d['native_energy'][0]));relative=error/max(abs(values['total_j']),1e-12);passed=error<=1e-10 or relative<=1e-9;a.output.write_text(json.dumps(dict(passed=passed,values=values,absolute_error_j=error,relative_error=relative,scope='Independent CPU undamaged incremental potential value, no integration.'),indent=2)+'\n');return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
