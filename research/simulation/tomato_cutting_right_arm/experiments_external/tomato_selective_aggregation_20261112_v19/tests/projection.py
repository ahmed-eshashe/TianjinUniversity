"""Fixed declared fields: assess aggregation projection, not physical fracture."""
from pathlib import Path
import sys,json,time,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
from reference_v17 import Body
from aggregation import Aggregate as BaseAggregate
threshold=float(sys.argv[1]) if len(sys.argv)>1 else 1e-8
def Aggregate(body):return BaseAggregate(body,threshold)
rows=[];start=time.perf_counter()
for n,h in [(4,.006),(10,.006),(20,.003)]:
 for shape in ['affine','smooth','localized']:
  if n==20 and shape=='affine':continue
  b=Body(n=n,h=h);L=n*h;x,y,z=b.grid.T
  b.u[:,1]=-.01*y;b.u[:,0]=.005*z
  if shape=='smooth':b.u[:,1]+=.002*L*np.sin(2*np.pi*x/L)*np.cos(np.pi*z/L)
  if shape=='localized':b.u[:,1]+=.002*L*np.exp(-(x*x+y*y+z*z)/(2*(L/6)**2))
  b.v=np.cross([.2,.1,.3],b.grid)+np.array([.01,.02,-.01])
  if shape!='affine':b.v[:,0]+=.005*np.sin(2*np.pi*y/L)
  b.split([1,1,1],1e-6);before=b.metrics();t=time.perf_counter();a=Aggregate(b);elapsed=time.perf_counter()-t;after=a.metrics()
  energy_error=abs(after['U']-before['U'])/max(before['U'],1e-10)
  row={'n':n,'h_m':h,'field':shape,'construction_s':elapsed,'regions':len(b.X),'nodes':len(b.u),'reduced_nodes':len(a.q),'max_block':a.report['max_mass_block'],'block_sizes':a.report['mass_block_sizes'],'unresolved_nodes':len(a.report['unresolved_nodes']),'transfer':a.transfer,'elastic_energy_relative':energy_error,'accepted_transfer':a.transfer['position_m']<=1e-4 and a.transfer['velocity_m_s']<=.005 and a.transfer['energy_relative']<=.05 and a.transfer['angular_relative']<=.01}
  rows.append(row);print({k:v for k,v in row.items() if k!='block_sizes'},flush=True)
  (W/f'projection_{threshold}.json').write_text(json.dumps({'rows':rows,'wall_s':time.perf_counter()-start,'physical_cut':False},indent=2))
