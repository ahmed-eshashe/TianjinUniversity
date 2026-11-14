from pathlib import Path
import json,numpy as np
W=Path(__file__).resolve().parent;V=W.parent/'disect_normal_contact_20261109_v30'
def bundle(directory,names):
    frames={};rows={};runs=[]
    for name in names:
        result=json.loads((directory/f'{name}_result.json').read_text());runs.append(result)
        z=np.load(directory/f'{name}_trajectory.npz')
        arrays={key:z[key] for key in ['x','v','reaction','moment','history']}
        for i,t in enumerate(z['t']):frames[round(float(t),12)]={key:array[i] for key,array in arrays.items()}
        for row in result['rows']:rows[round(row['sim_s'],12)]=row
    return frames,rows,runs
a,ar,ac=bundle(W,['prefix0038']);b,br,bc=bundle(V,['strong0032','strong0080'])
assert ac[0]['dt_s']==2*bc[0]['dt_s']
times=sorted(set(a)&set(b));assert times[0]==0 and times[-1]==.038 and len(times)==77
maxima=dict(position_m=0.,velocity_m_s=0.,force_relative=0.,sum_force_relative=0.,moment_relative=0.,damage_absolute=0.,dissipation_relative=0.)
for t in times:
    x,y=a[t],b[t]
    maxima['position_m']=max(maxima['position_m'],float(np.linalg.norm(x['x']-y['x'],axis=1).max()))
    maxima['velocity_m_s']=max(maxima['velocity_m_s'],float(np.linalg.norm(x['v']-y['v'],axis=1).max()))
    for key,floor,out in [('reaction',1e-6,'force_relative'),('moment',1e-8,'moment_relative')]:
        maxima[out]=max(maxima[out],float(np.linalg.norm(x[key]-y[key])/max(np.linalg.norm(y[key]),floor)))
    maxima['damage_absolute']=max(maxima['damage_absolute'],float(np.abs(x['history'][:,1]-y['history'][:,1]).max()))
    maxima['sum_force_relative']=max(maxima['sum_force_relative'],abs(ar[t]['sum_force_N']-br[t]['sum_force_N'])/max(br[t]['sum_force_N'],1e-6))
    maxima['dissipation_relative']=max(maxima['dissipation_relative'],abs(ar[t]['fracture_dissipation_J']-br[t]['fracture_dissipation_J'])/max(br[t]['fracture_dissipation_J'],1e-8))
physical=bool(ac[0]['completed_window'] and all(r['admissible'] for result in ac+bc for r in result['rows']))
no_damage=all(row['damage_max']==0 for row in list(ar.values())+list(br.values()))
limits=dict(position_m=1e-4,velocity_m_s=.005,force_relative=.05,sum_force_relative=.05,moment_relative=.05,damage_absolute=.01,dissipation_relative=.05)
passed=bool(physical and no_damage and all(maxima[k]<=limits[k] for k in maxima))
out=dict(scope='Independent fresh 38 ms nonfracturing loaded prefix, 6.25/3.125 us; reference cap segments stitched at shared physical time without changing raw results',shared_samples=len(times),maxima=maxima,limits=limits,physical_checks_passed=physical,no_damage_in_either_case=no_damage,passed=passed,gate_b_passed=False,actual_damage_refinement_required=True,wall_s_coarse=ac[0]['wall_s'],wall_s_reference_segments=sum(r['wall_s'] for r in bc),peak_RSS_KiB_coarse=ac[0]['peak_RSS_KiB'])
(W/'loaded_prefix_review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert passed
