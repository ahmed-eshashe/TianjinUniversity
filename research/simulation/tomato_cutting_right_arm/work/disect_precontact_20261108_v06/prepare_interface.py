"""Offline native topology preparation/audit only, never a dynamic pass."""
from pathlib import Path
import sys,os,json,time,numpy as np
W=Path(__file__).resolve().parent;ROOT=W.parents[1];data=W.parent/'disect_mesh_validation_20261108_v02';sys.path.insert(0,str(data/'DiSECt/meshing'));os.chdir(W)
from meshcutter import MeshCutter
z=np.load(data/'tomato_fem_mesh.npz');raw=z['x'];x=raw[:,[0,2,1]].copy();x[:,1]+=.002;x[:,2]*=-1;t=z['tets'];boundary=z['boundary'];start=time.perf_counter()
corners=np.array([[-.0225,-.01,-.05],[-.0225,.08,-.05],[-.0225,.08,.05],[-.0225,-.01,.05]]);surface=corners[[[0,1,2],[0,2,3]]]
mc=MeshCutter(boundary.tolist(),t.tolist(),x.tolist());mc.verbose=False;mc.triangle_test_tolerance=0.;success=bool(mc.cut(surface));(W/'meshing_log.txt').write_text(mc.log())
arrays={'particle_x':np.array(mc.particle_x),'tets':np.array(mc.tet_indices),'triangles':np.array(mc.tri_indices),'cut_triangles':np.array(mc.cut_tri_indices),'virtual_triangles':np.array(mc.cut_virtual_tri_indices),'above':np.array(mc.cut_virtual_tri_indices_above_cut),'below':np.array(mc.cut_virtual_tri_indices_below_cut),'edge_indices':np.array(mc.cut_edge_indices),'edge_coords':np.array(mc.cut_edge_coords),'springs':np.array(mc.cut_spring_indices),'spring_normals':np.array(mc.cut_spring_normal)}
copies={int(new):int(old) for new,old in mc.vertex_copy_from.items()};tcopies={int(new):int(old) for new,old in mc.tet_copy_from.items()};m=list(z['mass'])
for i in range(len(x),len(arrays['particle_x'])):m.append(m[copies[i]])
np.savez_compressed(W/'interface_preparation.npz',**arrays,mass_as_upstream=np.array(m));(W/'interface_native_metadata.json').write_text(json.dumps({'native_success':success,'vertex_copy_from':copies,'tet_copy_from':tcopies,'wall_s':time.perf_counter()-start},indent=2));print(json.dumps({'native_success':success,'old_nodes':len(x),'new_nodes':len(m),'old_tets':len(t),'new_tets':len(arrays['tets']),'springs':len(arrays['springs']),'original_mass_kg':float(z['mass'].sum()),'copied_upstream_mass_kg':float(np.sum(m)),'mass_relative_difference':float(np.sum(m)/z['mass'].sum()-1)},indent=2))
