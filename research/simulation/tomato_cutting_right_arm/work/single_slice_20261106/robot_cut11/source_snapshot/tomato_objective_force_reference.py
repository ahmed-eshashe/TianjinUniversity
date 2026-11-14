"""Independent explicit frame-gradient formula, checked against CPU autograd."""
import numpy as np
from tomato_objective_cohesion_reference import response

def explicit_force(positions,patch,*,history=(0.,0.),eligible=False):
 x=np.asarray(positions,dtype=float);check=response(x,patch,history=history,eligible=eligible);factor=1-check['trial_history'][1]
 mid=x.mean(1);a,b,c=patch['anchors'];u=mid[b]-mid[a];v=mid[c]-mid[a];t=u/np.linalg.norm(u);cross=np.cross(u,v);n=patch['sign']*cross/np.linalg.norm(cross);other=np.cross(n,t);gap=x[:,1]-x[:,0];local=np.column_stack([gap@n,gap@t,gap@other]);eff=local.copy();eff[:,0]=np.maximum(eff[:,0],0);traction=patch['weights'][:,None]*(eff@patch['local_k']);traction[local[:,0]<0,0]=0
 world=traction[:,0,None]*n+traction[:,1,None]*t+traction[:,2,None]*other;f=np.stack([world,-world],axis=1)*factor
 gn=(traction[:,0,None]*gap).sum(0);gt=(traction[:,1,None]*gap).sum(0);gb=(traction[:,2,None]*gap).sum(0);gn+=np.cross(t,gb);gt+=np.cross(gb,n)
 gc=patch['sign']*(gn-n*(n@gn))/np.linalg.norm(cross);gu=(gt-t*(t@gt))/np.linalg.norm(u)+np.cross(v,gc);gv=np.cross(gc,u)
 for index,g in [(a,-gu-gv),(b,gu),(c,gv)]:f[index]-=.5*factor*g
 return f
