"""Offline single/surface and parameter sensitivity of the rolled proposals."""
import json
import numpy as np
from scipy.spatial.transform import Rotation
from multipoint_load_audit import ROOT,CAPS
from contact_load_model import solve_contact_load


def main():
    folder=ROOT/'runs/offline/load_support_01'
    source=json.loads((folder/'oriented_support_candidates.json').read_text())
    physics=json.loads((ROOT/'docs/rl/phase3_physics.json').read_text());out=[]
    for candidate in source['candidates']:
        points=candidate['surface_points'];r=Rotation.from_quat(candidate['knife_pose_xyzw'][3:]).as_matrix()
        gravity=r.T@np.array([0,0,-physics['knife_mass_kg']*9.81]);single=[]
        for part in ['palm','thumb',*candidate['target_fingers']]:
            choices=[p for p in points if p['part']==part]
            if part in ['index','pinky']:
                inner=[p for p in choices if p['inner']]
                if inner:choices=inner
            if choices:single.append(min(choices,key=lambda p:p['gap_m']))
        variants={}
        for name,ps,mu,offset in [('one_representative_per_part',single,.6,0.),('surface_mu04',points,.4,0.),
                                   ('surface_mu08',points,.8,0.),('surface_com_toward_blade20mm',points,.6,-.02),
                                   ('surface_com_toward_butt20mm',points,.6,.02)]:
            com=np.array(physics['knife_com_local_m']);com[0]+=offset
            variants[name]=solve_contact_load(ps,com,gravity,mu=mu,scale=1.25,required_parts=['palm','thumb',*candidate['target_fingers']],
                required_inner=['index','pinky'],torque_caps=CAPS)
        out.append({'axial_roll_change_deg':candidate['knife_axial_roll_change_deg'],'probes':variants})
        print(json.dumps({'roll':candidate['knife_axial_roll_change_deg'],'feasible':{name:p['feasible'] for name,p in variants.items()}}),flush=True)
    (folder/'oriented_support_sensitivity.json').write_text(json.dumps({'scope':'Diagnostic parameter probes, no mass/friction/geometry changes in assets or active plan','cases':out},indent=2,allow_nan=False))


if __name__=='__main__':main()
