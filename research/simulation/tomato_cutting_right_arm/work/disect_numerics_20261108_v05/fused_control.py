from numerics import *
b=Bulk();b.enable_gather();rng=np.random.default_rng(731);xx=b.z['x']+rng.normal(size=b.z['x'].shape)*1e-6;vv=rng.normal(size=xx.shape)*1e-4;b.x.copy_(tensor(xx));b.geometry();got=-b.damping(tensor(vv)).cpu().numpy().copy();ref=numpy_force(b.z,xx,vv)-numpy_force(b.z,xx,np.zeros_like(vv));err=float(np.linalg.norm(got-ref));norm=float(np.linalg.norm(ref));translation=float(b.damping(tensor(np.tile([.1,-.2,.3],(len(xx),1)))).norm().item());b.reset()
h=.001/67;graph=b.capture_implicit(h,iterations=64,fused=True);fresh=Bulk();start=time.perf_counter()
for _ in range(20):graph.replay()
torch.cuda.synchronize();graph_wall=time.perf_counter()-start
for _ in range(20):fresh.implicit(h)
first=b.arrays();reference=fresh.arrays();errors=[float(np.max(abs(a-c))) for a,c in zip(first,reference)];res=b.graph_max_residual.item()
b.material().cpu().numpy();junk=torch.full((50000,),123.,dtype=torch.float64,device='cuda');b.reset();zero=bool(b.graph_max_residual.item()==0 and (b.guess==0).all().item())
for _ in range(20):graph.replay()
second=b.arrays();repeat=[float(np.max(abs(a-c))) for a,c in zip(first,second)];b.reset();fr=Bulk();fresh_error=max(float(torch.max(abs(getattr(b,a)-getattr(fr,a))).item()) for a in ['x','v','guess','f','g','j','diag','tmp'])
# rate is scratch overwritten on every matvec, but reset should clear it too.
out={'scope':'fused PCG / gathered operator / graph execution controls','independent_damping_error_N':err,'reference_norm_N':norm,'relative_error':err/norm,'translation_nullspace_N':translation,'position_error_m':errors[0],'velocity_error_m_s':errors[1],'repeat_position_error_m':repeat[0],'repeat_velocity_error_m_s':repeat[1],'graph_true_residual':res,'reset_fresh_error':fresh_error,'reset_cleared_diagnostic_and_guess':zero,'twenty_steps_graph_wall_s':graph_wall,'passed':bool(err<=max(1e-10,.001*norm) and translation<1e-10 and errors[0]<=1e-10 and errors[1]<=1e-8 and max(repeat)<1e-12 and fresh_error==0 and zero and res<=1e-9)}
(W/'fused_control_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
