from pathlib import Path
import sys,json,numpy as np
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;sys.path.insert(0,str(r/'rl'))
import warp as wp
from tomato_grouped_pressure_assembly import grouped_blocks
wp.init();wp.set_device('cuda:0');rng=np.random.default_rng(142);n=12000;groups=23;g=rng.integers(0,groups,n,dtype=np.int32);b=rng.dirichlet([1,1,1],n);a=rng.normal(size=(n,3,3));h=a@a.transpose(0,2,1);out=wp.zeros(9*groups,dtype=wp.mat33d)
wp.launch(grouped_blocks,dim=(n,3,3),inputs=[wp.array(g,dtype=int),wp.array(b,dtype=wp.vec3d),wp.array(h,dtype=wp.mat33d)],outputs=[out]);expected=np.zeros((groups,3,3,3,3))
for j in range(3):
 for k in range(3):np.add.at(expected[:,j,k],g,(b[:,j]*b[:,k])[:,None,None]*h)
actual=out.numpy().reshape(expected.shape);error=float(np.max(abs(actual-expected)));assert np.allclose(actual,expected,rtol=1e-12,atol=1e-12)
result=dict(passed=True,samples=n,groups=groups,max_absolute_error=error);(w/'grouped_pressure_check.json').write_text(json.dumps(result,indent=2));print(result)
