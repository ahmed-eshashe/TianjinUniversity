from pathlib import Path
import json,numpy as np,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;z=np.load(Path(sys.argv[1]));d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());b=json.loads((r/'runs/offline/tomato_preupgrade_20261027T171031Z/blade_export.json').read_text());origin=np.array([d['cut_x_m'],0,.0295]);x=(z['x']+origin)*1000;v=(np.array(b['vertices'])@z['blade_rotation'].T+z['blade_translation']+origin)*1000
fig=plt.figure(figsize=(12,6))
for i,(az,elev) in enumerate([(-65,20),(-145,25)]):
 ax=fig.add_subplot(1,2,i+1,projection='3d')
 for p in d['pieces']:
  tris=x[np.array(p['triangles'])];ax.add_collection3d(Poly3DCollection(tris,facecolor='#e8453c' if p['side']=='remainder' else '#f8a397',edgecolor='none',alpha=.8))
 ax.add_collection3d(Poly3DCollection(v[np.array(b['triangles'])],facecolor='#7895ac',edgecolor='none',alpha=.5))
 ax.set(xlim=(-45,40),ylim=(-45,45),zlim=(0,65),xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)');ax.set_box_aspect((85,90,65));ax.view_init(elev=elev,azim=az)
fig.suptitle(f"Research model · accepted step {int(z['step'])} · {int((z['history'][:,1]>=1).sum())}/47 failed connections\nPrescribed blade component; no robot-cut qualification")
fig.tight_layout();fig.savefig(w/'current_material_state.png',dpi=140)
