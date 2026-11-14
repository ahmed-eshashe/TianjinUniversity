from pathlib import Path
import numpy as np,json
w=Path(__file__).resolve().parent;r=w.parents[1];d=json.loads((r/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5/surface_design.json').read_text());x=np.array([n['position_m'] for n in d['nodes']]);ux,inv=np.unique(x,axis=0,return_inverse=True);f=inv[np.array([f for p in d['pieces'] for f,tag in zip(p['triangles'],p['face_tags']) if tag=='exterior'])];e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,n=np.unique(e,axis=0,return_counts=True);q=ux[f];area=np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)/2;volume=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6
boundary={'vertices_used':len(np.unique(f)),'triangles':len(f),'boundary_edge_incidence':{str(k):int((n==k).sum()) for k in np.unique(n)},'zero_area_faces':int((area<1e-15).sum()),'duplicate_triangles':int(len(f)-len(np.unique(np.sort(f,axis=1),axis=0))),'signed_enclosed_volume_m3':float(volume),'closed_manifold_by_edge_count':bool((n==2).all()),'fixture_original_node_ids':d['fixture']['node_ids'],'fixture_coordinates_m':x[d['fixture']['node_ids']].tolist(),'proposed_mass_kg':float(np.load(w/'source_tomato.npz')['mass'].sum()),'proposed_uniform_density_kg_m3':float(np.load(w/'source_tomato.npz')['mass'].sum()/volume)}
np.savez(w/'proposed_exterior_input.npz',vertices=ux,triangles=f,fixture_coordinates=x[d['fixture']['node_ids']]);(w/'exterior_input_audit.json').write_text(json.dumps(boundary,indent=2))
(w/'MESH_OPTIONS.txt').write_text('''Decision needed before creating a new FEM tessellation

Recommended: independently remesh the SAME original tomato exterior into a conforming volume mesh in this isolated study. Preserve the 65 x 65 x 55 mm shape, the 121.671 g total mass, nominal cut x=-22.5 mm and the original 25 support coordinates. Validate boundary closure, positive volumes, paired interior faces, mass and support mapping before dynamics. Preserve the source spring/cohesion research branch and evidence.

What changes: internal tetrahedral connectivity and possibly interior node locations/count, mass lumping and constitutive representation. DiSECt FEM and cutting springs are not identical to the original spring/skin/cohesion law. Even a successful cut would be a synthetic DiSECt tomato result, not experimental validation or an equal-accuracy replacement.

Mesh preparation scope: one constrained tetrahedralization route from the audited original exterior, target roughly the original order of 16000 cells, exact support-coordinate retention or an explicitly reported mapping failure. No automatic nearest-node support substitution. No geometry smoothing, changed fruit size or deleted material ties. A route requiring major mesher development stops with a feasibility report. Record any resolution change rather than claiming a matched resolution.

Material starting evidence: original tomato_surface_mechanics.py constructs synthetic small-strain central-force bulk with nominal E=30000 Pa and nu=0.25 under prescribed-surface probes. These are a defensible nominal bulk reference only; no direct equality of relaxed response, skin or fracture law follows. Report calibration/mapping limits separately before contact. No parameters chosen after seeing separation.

Alternative: keep the original exact internal point set and attempt a conforming retriangulation. This better preserves node identity but may retain poor-quality/sliver elements and require robust coplanar handling; explicit-solver stability can suffer. It still changes connectivity and does not preserve the spring material law.

Alternative: retain DiSECt as an example-only speed reference and do not create a tomato FEM representation. This avoids a model conversion but cannot answer whether DiSECt can efficiently slice our tomato.

No new tetrahedralization or tomato dynamics has been performed in this follow-up. Proposed exterior input and audits are saved for review.
''')
print(json.dumps({k:v for k,v in boundary.items() if not k.startswith('fixture')},indent=2))
