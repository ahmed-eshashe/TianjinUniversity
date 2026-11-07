import sys,numpy as np
sys.path.insert(0,'.deps/ipctk-1.6.1-cp312');import ipctk
c=ipctk.TightInclusionCCD(tolerance=1e-9,max_iterations=10000000,conservative_rescaling=.8)
a=np.array([[0.,-.01,-.01],[0,.01,-.01],[0,0,.01]]);b=np.array([-.01,-.004,0.]);print(c.point_triangle_ccd(b,*a,b+[.02,0,0],*a))
