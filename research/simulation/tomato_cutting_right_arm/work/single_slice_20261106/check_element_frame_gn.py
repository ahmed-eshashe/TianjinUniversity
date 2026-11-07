exec(open(__file__.replace('check_element_frame_gn.py','check_element_frame.py')).read().split("z=np.load(w/'softening_replay03")[0])
from tomato_element_frame_coupled import failed_safe_coupled_blocks
z=np.load(w/'softening_patch_capture/stalled_solver.npz');x=z['x'];h=z['history'];mask=np.zeros(47,np.int32);n=len(x);N=47*1024;rows=wp.zeros(N,dtype=int);cols=wp.zeros(N,dtype=int);values=wp.zeros(N,dtype=wp.mat33d)
wp.launch(failed_safe_coupled_blocks,dim=(47,32,32),inputs=[0,wp.array(x,dtype=wp.vec3d),*args,wp.array(h,dtype=wp.vec2d),wp.array(mask,dtype=int),wp.ones(n,dtype=int)],outputs=[rows,cols,values]);rr=rows.numpy();cc=cols.numpy();vv=values.numpy();rng=np.random.default_rng(18);direction=rng.normal(size=x.shape)
actual=np.einsum('ni,nij,nj->',direction[rr],vv,direction[cc]);expected=0.
for i in range(47):
 pp=torch.tensor(x[pairs[i]],dtype=torch.float64);dd=torch.tensor(direction[pairs[i]],dtype=torch.float64)
 def gaps(a):
  uv=torch.tensor(coef[i].T)@a.mean(1);u,v=uv;t=u/torch.linalg.vector_norm(u);normal=sign[i]*torch.linalg.cross(u,v);normal=normal/torch.linalg.vector_norm(normal);b=torch.linalg.cross(normal,t);g=(a[:,1]-a[:,0])@torch.stack([normal,t,b],1);return torch.cat([torch.clamp(g[:,:1],min=0),g[:,1:]],1)
 _,dg=torch.autograd.functional.jvp(gaps,pp,dd);dg=dg.numpy();expected+=(1-h[i,1])*np.sum(weights[i,:,None]*dg*(dg@stiff[i]))
result=dict(actual=float(actual),expected=float(expected),relative_error=float(abs(actual-expected)/abs(expected)));result['passed']=result['relative_error']<1e-10;(w/'element_frame_gn_check.json').write_text(json.dumps(result,indent=2));print(result);assert result['passed']
