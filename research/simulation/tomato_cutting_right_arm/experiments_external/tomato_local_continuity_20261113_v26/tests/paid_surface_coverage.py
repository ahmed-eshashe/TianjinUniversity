"""Independent solid-cell coverage of the retained shallow crack surfaces."""
from pathlib import Path
import sys,os,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
from compiled_body import Body
from local_continuity import Aggregate
from poly_surface import Surface
from blade_geometry import CAD
from sharp_front import blade_edge
cad=CAD();z=np.load(W/'assets/blade_partition.npz');cells=z['x'][z['tets']];planes=z['planes'];cmin=cells.min(1);cmax=cells.max(1);ang=np.pi/6;R=np.array([[1.,0,0],[0,np.cos(ang),-np.sin(ang)],[0,np.sin(ang),np.cos(ang)]])@cad.R;edge0=blade_edge(cad,np.zeros(3),R);T0=np.array([.00013,.00304+.003*abs((edge0[1,1]-edge0[0,1])/(edge0[1,2]-edge0[0,2])),0.])-edge0.mean(0);rows=[]
for p in sorted((W/'runs/continue_paid_r6').glob('accepted_event_*.npz')):
 a=Aggregate(Body.restore(p));s=Surface(a);t=a.body.history[-1]['authorization']['time'];T=T0+np.array([0,-.0012,0])*.5*(1-np.cos(np.pi*t/.03));world=s.positions(a.q).reshape(-1,3,3);exterior=np.any(np.all(np.isclose(abs(s.triangles),.003,atol=1e-13,rtol=0),axis=1),axis=1);total=uncovered=overlap=0.
 for face in np.flatnonzero(~exterior):
  local=(world[face]-T)@R;fraction=0.
  for ci in np.flatnonzero(np.all(local.max(0)>=cmin,axis=1)&np.all(local.min(0)<=cmax,axis=1)):
   polygon=list(np.eye(3))
   for plane in planes[ci]:
    ds=local@plane[:3]+plane[3];new=[]
    for i,p0 in enumerate(polygon):
     p1=polygon[(i+1)%len(polygon)];d0=p0@ds;d1=p1@ds
     if d0<=0:new.append(p0)
     if (d0<0<d1) or (d1<0<d0):new.append(p0+d0/(d0-d1)*(p1-p0))
    polygon=new
    if not polygon:break
   for k in range(1,len(polygon)-1):fraction+=abs(np.linalg.det(np.array([polygon[0],polygon[k],polygon[k+1]])))
  total+=s.tri_area[face];uncovered+=s.tri_area[face]*max(1-fraction,0);overlap+=s.tri_area[face]*max(fraction-1,0)
 row=dict(file=p.name,time=t,total_crack_face_area_m2=total,uncovered_area_m2=uncovered,overlap_area_m2=overlap,uncovered_relative=uncovered/max(total,1e-30),passed=uncovered<=1e-6*total+128*np.finfo(float).eps*.000216 and overlap<=1e-6*total+128*np.finfo(float).eps*.000216);row['passed']=bool(row['passed']);rows.append(row);print(json.dumps(row),flush=True)
out=dict(passed=all(r['passed'] for r in rows),events=rows,scope='Exact CAD solid partition coverage, current shallow crack faces including connectors; no knife-hull replacement. Tolerance quantifies float face-difference artifacts, does not delete material. Not arbitrary-path/full-slice validation.');(W/'reports/paid_surface_coverage.json').write_text(json.dumps(out,indent=2));assert out['passed']
