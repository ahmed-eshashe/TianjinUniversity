exec(open(__file__.replace('check_master_regression.py','check_master_frame.py')).read().split("z=np.load(w/'softening_replay03")[0])
import copy
translated=copy.deepcopy(d);translated['x']+=np.array([.13,-.2,.002]);other_support=frame_support(translated)
assert np.array_equal(pairs,other_support[0]);assert np.array_equal(coef,other_support[2])
z=np.load(w/'failure_probe02/nonlinear_iterate.npz');x=z['x'];h=z['history'];mask=np.zeros(47,np.int32)
f,e,hh=native(x,h,mask);fr,er=reference(x,h,mask)
mid=x[pairs][:,:,1];uv=np.einsum('pji,pjk->pik',coef,mid);areas=np.linalg.norm(np.cross(uv[:,0],uv[:,1]),axis=1)
result=dict(translation_invariant_support=True,force_reference_error=float(abs(f-fr).max()),energy_reference_error=abs(e-er),max_force_N=float(np.linalg.norm(f,axis=1).max()),min_frame_area=float(areas.min()),net_force=float(np.linalg.norm(f.sum(0))),net_moment=float(np.linalg.norm(np.cross(x,f).sum(0))),scope='Diagnostic at prior formulation failed iterate; no continuation qualification')
result['passed']=result['force_reference_error']<1e-8 and result['energy_reference_error']<1e-10 and result['min_frame_area']>1e-5 and result['net_moment']<1e-9
(w/'master_frame_regression.json').write_text(json.dumps(result,indent=2));print(result);assert result['passed']
