"""Offline local contact references. Not a full deformable collision solver."""
import math
import numpy as np
from scipy.spatial import ConvexHull
from tomato_bonds import DamageState,bundle_response,update_bundle_damage
from offline_tomato_patch_sweep import patch_data


def cut_outline(design,piece):
    ids=sorted({i for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut' for i in tri})
    points=np.asarray([design['nodes'][i]['position_m'][1:] for i in ids])
    return points[ConvexHull(points).vertices]


def outlines_overlap(a,b,tolerance=1e-12):
    """Complete finite 2D convex SAT, including perimeter touching."""
    for polygon in (a,b):
        edges=np.roll(polygon,-1,axis=0)-polygon
        axes=np.stack([-edges[:,1],edges[:,0]],axis=1)
        axes/=np.linalg.norm(axes,axis=1)[:,None]
        pa=a@axes.T;pb=b@axes.T
        if np.any(pa.max(axis=0)<pb.min(axis=0)-tolerance) or np.any(pb.max(axis=0)<pa.min(axis=0)-tolerance):
            return False
    return True


def edge_hits_site(site_yz,old_tip_z,new_tip_z,blade,*,y_offset=0.,x_offset=0.):
    """Continuous edge sweep at the predefined cut plane; finite blade length."""
    y,z=site_yz
    return (abs(x_offset)<=1e-12 and abs(y-y_offset)<=blade['length_m']/2 and
            min(old_tip_z,new_tip_z)-1e-12<=z<=max(old_tip_z,new_tip_z)+1e-12)


def containing_cut_triangles(design,piece,site_yz):
    """Finite barycentric inclusion on actual cut triangles, including rim/edges."""
    triangles=[tri for tri,tag in zip(piece['triangles'],piece['face_tags']) if tag=='cut']
    p=np.asarray([[design['nodes'][i]['position_m'][1:] for i in tri] for tri in triangles])
    u=p[:,1]-p[:,0];v=p[:,2]-p[:,0];w=np.asarray(site_yz)-p[:,0]
    det=u[:,0]*v[:,1]-u[:,1]*v[:,0]
    a=(w[:,0]*v[:,1]-w[:,1]*v[:,0])/det
    b=(u[:,0]*w[:,1]-u[:,1]*w[:,0])/det
    return np.flatnonzero((a>=-1e-10)&(b>=-1e-10)&(a+b<=1+1e-10)).tolist()


def wedge_patch_coupon(design,patch,blade,steps,*,mode='cut'):
    """One actual bond bundle with constrained 1D opening driven by a bevel.

    A massless supported coupon, not a full tomato. Unilateral equilibrium is
    q>=w, lambda>=0, lambda*(q-w)=0: while cohesion loads the bevel, q=w.
    Lateral reactions are supplied by the disclosed coupon supports. No inertia,
    nodal spring/volume deformation or free-slice dynamics are integrated here.
    """
    rest,k,law=patch_data(design,patch);state=DamageState();previous_force=0.;previous_q=0.
    work=0.;blade_work=0.;loss=0.;peak=0.;first_failure=None;hit=False
    y,z=patch['anchor_yz_m'];bevel=blade['single_bevel_length_m'];thickness=blade['max_thickness_m']
    for i in range(steps+1):
        depth=bevel*i/steps
        if mode=='partial':depth*=.25
        old_tip=z-bevel*(i-1)/steps if i else z+1e-6
        tip=z-depth
        if mode=='off_plane':x_offset=.01
        else:x_offset=0.
        y_offset=1. if mode=='miss' else 0.
        swept=edge_hits_site((y,z),old_tip,tip,blade,y_offset=y_offset,x_offset=x_offset)
        if mode!='face_rub':hit=hit or swept
        geometric_contact=abs(x_offset)<1e-12 and abs(y-y_offset)<blade['length_m']/2 and 0<=depth<=bevel
        width=thickness*depth/bevel if geometric_contact else 0.
        q=max(previous_q,width)  # minimal-motion solution; no tensile contact on withdrawal
        current=[(v[0]+q,v[1],v[2]) for v in rest]
        before=bundle_response(rest,current,k,[0.]*len(k),state)
        eligible=hit and geometric_contact and before['force_n'][0]>0
        new=update_bundle_damage(law,state,rest,current,k,opening_m=q,shear_m=0.,eligible=eligible)
        response=bundle_response(rest,current,k,[0.]*len(k),new)
        force=response['force_n'][0]
        work+=.5*(previous_force+force)*(q-previous_q)
        blade_work+=.5*(previous_force+force)*thickness/bevel*(depth-(bevel*(i-1)/steps if mode!='partial' else .25*bevel*(i-1)/steps)) if i else 0.
        # Exact fixed-geometry loss caused by the constitutive state update.
        loss+=before['stored_energy_j']-response['stored_energy_j']
        peak=max(peak,force*thickness/bevel)
        if new.damage==1 and first_failure is None:first_failure=depth
        state=new;previous_q=q;previous_force=force
    target=law.area_m2*law.fracture_energy_j_m2
    final=bundle_response(rest,current,k,[.2]*len(k),state,velocities=[(1.,2.,3.)]*len(k))
    stopped=update_bundle_damage(law,state,rest,current,k,opening_m=q,shear_m=0.,eligible=hit and geometric_contact and force>0)
    return {'patch_id':patch['id'],'mode':mode,'steps':steps,'damage':state.damage,'edge_swept_hit':hit,
            'work_j':work,'damage_dissipation_j':loss,'target_fracture_energy_j':target,
            'blade_virtual_work_j':blade_work,
            'work_relative_error':work/target-1,'damage_energy_relative_error':loss/target-1,
            'max_opening_m':q,'peak_prescribed_blade_reaction_n':peak,'first_failure_bevel_depth_m':first_failure,
            'zero_broken_force_and_damping':state.damage==1 and all(x==0 for x in final['force_n']),
            'stopped_state_unchanged':stopped==state,'full_deformable_cut':False}


def normal_contact_coupon(outline_a,outline_b,mass,dt,*,gap=.001,offset_yz=(0.,0.),damage=1.,initial_velocity=-.02,force_scale=1.):
    """Rigid-shape normal approach with exact impact time, not post-crossing repair.

    Damage is prescribed for this contact-only diagnostic and never gates contact.
    The outline/shape stays rigid, lateral translation is fixed, rotation absent.
    """
    overlap=outlines_overlap(outline_a,outline_b+np.asarray(offset_yz))
    if gap<0 or mass<=0 or dt<=0:raise ValueError('Invalid initial contact state')
    q=gap;v=initial_velocity;minimum=q;impulses=0.;fixture_impulses=0.;impact_loss=0.;work=0.;kinetic0=.5*mass*v*v
    max_reaction=0.;crossings=0;contact_steps=0;first_impact=None
    n=round(.05/dt)
    for step in range(n):
        # Press, then withdraw. Force is external; no timed damage or bond removal.
        force=force_scale*(-.1 if step*dt<.025 else .02);acceleration=force/mass
        remaining=dt;q0=q
        if overlap and q<=1e-14 and v<=0 and force<0:
            v=0.;q=0.;max_reaction=max(max_reaction,-force);contact_steps+=1
        else:
            predicted=q+v*dt+.5*acceleration*dt*dt
            if overlap and predicted<0:
                discriminant=v*v-2*acceleration*q
                roots=[(-v+s*math.sqrt(max(0.,discriminant)))/acceleration for s in (-1.,1.)] if abs(acceleration)>1e-20 else [-q/v]
                times=[t for t in roots if -1e-12<=t<=dt+1e-12]
                if not times:raise ValueError('Unresolved swept contact')
                toi=max(0.,min(times));velocity=v+acceleration*toi
                impact_loss+=.5*mass*velocity**2;impulses+=-mass*velocity
                fixture_impulses+=mass*velocity
                q=0.;v=0.;contact_steps+=1
                if first_impact is None:first_impact=step*dt+toi
                remaining=dt-toi
                if force<0:max_reaction=max(max_reaction,-force)
                else:q=.5*acceleration*remaining**2;v=acceleration*remaining
            else:q=predicted;v+=acceleration*dt
        work+=force*(q-q0);minimum=min(minimum,q)
        if overlap and q< -1e-12:crossings+=1
    final_energy=.5*mass*v*v
    residual=final_energy-kinetic0-work+impact_loss
    return {'dt_s':dt,'prescribed_damage':damage,'finite_outlines_overlap':overlap,
            'minimum_gap_m':minimum,'final_gap_m':q,'final_velocity_m_s':v,
            'crossings':crossings,'contact_steps':contact_steps,'impact_time_s':first_impact,
            'impact_impulse_ns':impulses,'max_sustained_reaction_n':max_reaction,
            'external_work_j':work,'impact_dissipation_j':impact_loss,'energy_residual_j':residual,
            'momentum_pair_residual_ns':abs(impulses+fixture_impulses),
            'scope':'parallel rigid-shape normal motion, no deformable/general self-contact'}
