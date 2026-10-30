"""Independent surface/overlap checks on saved proposals; never activates them."""
import json
import numpy as np
from pxr import Usd
from scipy.spatial import ConvexHull
from offline_grasp_audit import ROOT,collider_inventory,overlap_radius
from plan_contact_seating import HandGeometry


def main():
    folder=ROOT/'runs/offline/grasp_refinement_01'
    result=json.loads((folder/'polished_candidates.json').read_text())
    stage=Usd.Stage.Open(str(ROOT/'rl/scene/phase3_grasp.usda'));model=HandGeometry(stage)
    _,geometry=collider_inventory(stage,model)
    meta=json.loads((ROOT/'rl/scene/manifest.json').read_text())
    from pxr import UsdGeom
    handle=np.array(UsdGeom.Mesh(stage.GetPrimAtPath(meta['knife_path']+'/CollisionHandle')).GetPointsAttr().Get())
    cases=[]
    for i,c in enumerate(result['candidates']):
        links=model.transforms(c['joint_rad']);r=np.array(c['hand_rotation_in_knife']);t=np.array(c['hand_root_in_knife_m'])
        inner=[];overlaps=[]
        for item in c['exact_contact_geometry']:
            name=item['body'];v=geometry[name][0][0];l=links[name];br=r@l[:3,:3];bp=t+r@l[:3,3]
            radius=overlap_radius(v@br.T+bp,handle)
            if radius>1e-6:overlaps.append({'body':name,'intersection_inscribed_radius_m':radius,'approximation':geometry[name][0][1]})
            witness=item['inner_witness']
            if witness:
                local=br.T@(np.array(witness['a_m'])-bp);eq=ConvexHull(v).equations
                plane=float(np.max(eq[:,:3]@local+eq[:,3]))
                inner.append({'body':name,'distance_m':item['inner_region_distance_m'],
                              'original_surface_plane_residual_m':plane,
                              'on_original_convex_exterior_within_1um':abs(plane)<=1e-6})
        blockers=['positive required contact gaps remain','conditional point-contact load model infeasible',
                  'cooked decomposed shapes and continuous route unverified']
        if overlaps:blockers.append('handle intersections require resolution')
        cases.append({'candidate_index':i,'inner_witnesses':inner,'handle_intersections':overlaps,
                      'active':False,'ready_for_pickup_test':False,
                      'blocking_reasons':blockers})
    (folder/'surface_validation.json').write_text(json.dumps({'scope':'Offline geometry only; numerical surface tolerance is not a physical success tolerance','cases':cases},indent=2))
    print(json.dumps(cases,indent=2))


if __name__=='__main__':main()
