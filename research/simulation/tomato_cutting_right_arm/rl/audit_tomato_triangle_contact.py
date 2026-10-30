"""Independent polygon clipping audit of accepted fixed-damage contact states."""
import argparse,fcntl,hashlib,json,resource,signal,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def clipped(poly,axis,value,greater):
    """Sutherland-Hodgman clipping of actual Cartesian triangle polygons."""
    result=[]
    if not poly:return result
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da=(a[axis]-value)*(1 if greater else -1);db=(b[axis]-value)*(1 if greater else -1)
        if da>=0:result.append(a)
        if (da<0<db) or (db<0<da):result.append(a+da/(da-db)*(b-a))
    return result


def minimum_polygon_gap(design,x,tip,blade):
    """Gap is affine on each independently clipped bevel or cap polygon."""
    import numpy as np
    gap=float('inf');vertices=0
    for piece,sign in zip(design['pieces'],[-1.,1.]):
        for tri,tag in zip(piece['triangles'],piece['face_tags']):
            if tag!='cut':continue
            for low,high in [(tip,tip+blade['single_bevel_length_m']),(tip+blade['single_bevel_length_m'],tip+blade['height_m'])]:
                polygon=[v.copy() for v in x[tri]]
                polygon=clipped(polygon,2,low,True);polygon=clipped(polygon,2,high,False)
                polygon=clipped(polygon,1,-blade['length_m']/2,True);polygon=clipped(polygon,1,blade['length_m']/2,False)
                for v in polygon:
                    width=np.clip((v[2]-tip)*blade['max_thickness_m']/blade['single_bevel_length_m'],0.,blade['max_thickness_m'])
                    gap=min(gap,float(sign*(v[0]-design['cut_x_m'])-width/2));vertices+=1
    return gap,vertices


def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));resource.setrlimit(resource.RLIMIT_CPU,(45,45));signal.alarm(55)
    with (ROOT/'logs/right_arm_control.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        import numpy as np
        from tomato_coupled_contact import assemble_model,cut_pairs,supports
        from tomato_blade_damage import EvolvingCohesion,BLADE
        from tomato_bonds import DamageState
        from tomato_triangle_contact import triangle_geometry,blade_resistance
        s=json.loads((a.checkpoint/'summary.json').read_text());assert s['passed'] and not s['damage_evolution_enabled']
        for name,h in s['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
        for name,h in s['state_hashes'].items():assert hashlib.sha256((a.checkpoint/name).read_bytes()).hexdigest()==h,name
        source=ROOT/'runs/offline/tomato_slice_refinement_01/meshes_half_spacing/bulk5'
        design=json.loads((source/'surface_design.json').read_text());assign=json.loads((source/'mass_stiffness_assignments.json').read_text())
        points,model=assemble_model(design,assign,0.);pairs=cut_pairs(design);model.cohesion=EvolvingCohesion(design,pairs)
        model.cohesion.states=[DamageState(**d) for d in s['damage_states']]
        seed=json.loads((ROOT/s['seed_checkpoint']/'summary.json').read_text());assert seed['damage_states']==s['damage_states']
        x=np.load(a.checkpoint/'positions.npy');lam=np.load(a.checkpoint/'multipliers.npy');state=model.evaluate(x);fixed,_=supports(design,points,'indentation',0.)
        ids=np.array(sorted(fixed));free=np.setdiff1d(np.arange(x.size),ids);tip=float(points[pairs[:,0],2].max())-s['depth_mm']/1000;g=triangle_geometry(design,points,pairs,tip)
        residual=state['gradient_n'].ravel()-g['matrix'].T@lam;scale=max(np.linalg.norm(state['gradient_n'].ravel()[ids]),np.linalg.norm(g['matrix'].T@lam),1e-4)
        force=float(np.linalg.norm(residual[free])/scale);independent_gap,count=minimum_polygon_gap(design,x,tip,BLADE)
        cp=float(np.max(np.abs(lam*(g['matrix']@x.ravel()-g['bounds']))));fixederr=float(np.max(np.abs(x.ravel()[ids]-np.array([fixed[i] for i in ids]))))
        projection=float(np.max(np.abs(x[pairs.ravel(),1:]-points[pairs.ravel(),1:])));cutgap=float(np.min(x[pairs[:,1],0]-x[pairs[:,0],0]))
        flags=[]
        if force>1e-6:flags.append('force_residual')
        if independent_gap<-1e-9 or cutgap<-1e-9 or lam.min()<-1e-9 or cp>1e-10:flags.append('contact')
        if fixederr>1e-12 or projection>1e-12:flags.append('supports_or_projection')
        if state['min_cell_ratio']<.1 or state['min_length_ratio']<.1:flags.append('collapse')
        if abs(state['energy_j']-s['energy_j'])>1e-10:flags.append('energy_recomputation')
        if np.max(np.abs(lam[~g['active']]),initial=0.)>0:flags.append('inactive_facet_force')
        n=g['base_rows'];loaded={kind:int(sum(m['kind']==kind and lam[n+j]>1e-9 for j,m in enumerate(g['cap_rows']))) for kind in ['entry_edge','cap_edge']}
        forbidden=[n for n in sys.modules if n.split('.')[0] in {'newton','warp','torch','isaaclab','isaacsim','omni','pxr'}];assert not forbidden
        result={'passed':not flags,'flags':flags,'checkpoint':str(a.checkpoint),'depth_mm':s['depth_mm'],'independent_polygon_minimum_gap_m':independent_gap,'clipped_polygon_vertices_checked':count,'minimum_cut_gap_m':cutgap,'force_residual':force,'complementarity_n_m':cp,'fixed_support_error_m':fixederr,'projection_error_m':projection,'min_J':state['min_cell_ratio'],'min_length_ratio':state['min_length_ratio'],'energy_j':state['energy_j'],'blade_resistance_n':blade_resistance(g,x,lam),'loaded_edge_constraints':loaded,'damage_states_unchanged':True,'trajectory_validated':False,'full_cut':False,'simulator':False,'training':False,'forbidden_imports':forbidden}
        a.output.write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
