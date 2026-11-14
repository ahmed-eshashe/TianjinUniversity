from pathlib import Path
import json,pstats,numpy as np
w=Path(__file__).resolve().parent
s=pstats.Stats(str(w/'current_profile/steady_profile.pstats'))
def stat(file,name):
 return sum(v[3] for k,v in s.stats.items()if k[0].endswith(file)and k[2]==name)
current={'profile_wall_s':s.total_tt,'simulated_s':4/600,'wall_s_per_sim_s':s.total_tt/(4/600),'nonlinear_solve_s':stat('tomato_fraction_boundary.py','step'),'contact_packet_refresh_s':stat('tomato_compiled_local_packet_refresh.py','refresh_packet'),'cut_eligibility_overlap_s':stat('tomato_cut_eligibility.py','_overlap'),'numpy_write_s':stat('_npyio_impl.py','savez'),'text_write_s':stat('pathlib.py','write_text'),'copy_file_s':stat('shutil.py','copyfile'),'gpu_to_numpy_calls':sum(v[0]for k,v in s.stats.items()if k[0].endswith('warp/_src/types.py')and k[2]=='numpy'),'gpu_to_numpy_cumulative_s':stat('warp/_src/types.py','numpy'),'note':'GPU-to-NumPy time includes synchronization and overlaps nonlinear/contact categories; do not add it to them. cProfile overhead included. Startup excluded.'}
if (w/'current_profile3/timings.json').exists():current['explicit_timers_repeat']=json.loads((w/'current_profile3/timings.json').read_text())
report={'scope':'Laptop feasibility benchmarks, NOT accuracy-equivalent engine comparison or adoption. All headless, forward only. Production checkpointed at step 6925; scene/grip/interface unchanged.','current':current,'disect':[],'roboninja':[],'sources':{'DiSECt':'https://github.com/NVlabs/DiSECt','RoboNinja':'https://github.com/real-stanford/roboninja'}}
for file in ['disect_result.json','disect_repeat_result.json']:
 d=json.loads((w/file).read_text());rows=d.pop('rows');d.update(force_resultant_peak=float(max(np.linalg.norm(r['force_resultant'])for r in rows)),sum_contact_force_magnitudes_peak=max(r['force_sum_norm']for r in rows),all_sampled_states_finite=all(r['finite']for r in rows),final_zero_stiffness_springs=rows[-1]['zero_stiffness_springs'],exit_returncode=-11);report['disect'].append(d)
report['disect_stability']=json.loads((w/'disect_stability_assessment.json').read_text())
for p in sorted(w.glob('robo_*_result.json')):
 d=json.loads(p.read_text());rows=d.pop('rows');d['all_sampled_states_finite']=all(r['finite']for r in rows);d['simulated_s']=rows[-1]['sim_s'];d['largest_sampled_speed']=max(r['max_speed']for r in rows);report['roboninja'].append(d)
report['roboninja_separation']=json.loads((w/'robo_separation_assessment.json').read_text())
report['decision']={'current':'Not suitable as the main learning backend at measured throughput; preserve for comparison, not physical ground truth.','disect':'First candidate for a bounded hardening and same-tomato comparison; not adoption-ready: meshing failure flag, GC segfault and repeat variation.','roboninja':'Promising path/size flexibility but substantially different material/contact law; dense-grid memory, force adapter and tomato skin/separation need work.','no_new_engine_adopted':True}
(w/'comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps(current,indent=2))
