from numerics import *
h=.001/67;b=Bulk();graph=b.capture_implicit(h);fresh=Bulk()
for _ in range(20):graph.replay();fresh.implicit(h)
torch.cuda.synchronize();first=b.arrays();ref=fresh.arrays();errors=[float(np.max(abs(a-c))) for a,c in zip(first,ref)];res=b.graph_max_residual.item()
# Deliberately allocate and sample between replays: graph external inputs must survive allocator reuse.
b.material().cpu().numpy();junk=torch.full((50000,),123.,dtype=torch.float64,device='cuda');b.reset();zero=bool(b.graph_max_residual.item()==0 and (b.guess==0).all().item())
for _ in range(20):graph.replay()
second=b.arrays();repeat=[float(np.max(abs(a-c))) for a,c in zip(first,second)];b.reset();reset_fresh=max(float(torch.max(abs(getattr(b,a)-getattr(Bulk(),a))).item()) for a in ['x','v','guess','f','g','j','diag','tmp'])
out={'scope':'20-step full-mesh CUDA-graph/adaptive equivalence, sampling/allocation and reset regression','position_error_m':errors[0],'velocity_error_m_s':errors[1],'repeat_position_error_m':repeat[0],'repeat_velocity_error_m_s':repeat[1],'graph_true_residual':res,'reset_fresh_error':reset_fresh,'reset_cleared_diagnostic_and_guess':zero,'passed':bool(errors[0]<=1e-10 and errors[1]<=1e-8 and max(repeat)<1e-12 and reset_fresh==0 and zero and res<=1e-9)}
(W/'graph_control_result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert out['passed']
