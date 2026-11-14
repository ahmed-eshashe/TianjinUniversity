from pathlib import Path
r=Path(__file__).resolve().parents[2]; w=Path(__file__).parent
s=(r/'rl/tomato_robot_slice_extension_v16.py').read_text()
s=s.replace("ROOT=Path(__file__).resolve().parents[1]",f"ROOT=Path({str(r)!r})")
s=s.replace("R=Path(__file__).resolve().parents[1]",f"R=Path({str(r)!r})")
s=s.replace(' for k in range(start_k,maximum_steps):', ''' import cProfile
 profile=cProfile.Profile();profile.enable()
 for k in range(start_k,min(maximum_steps,start_k+4)):''')
s=s.replace(' if k%25==0:', ' if k%25==0 or k==start_k+3:')
s=s.replace(' display();result=dict(', " profile.disable();profile.dump_stats(str(out/'steady_profile.pstats'))\n display();result=dict(")
(w/'profile_extension.py').write_text(s)
s=(r/'rl/tomato_research_cut_robot_worker_v16.py').read_text()
s=s.replace('R=Path(__file__).resolve().parents[1]',f'R=Path({str(r)!r})')
s=s.replace('from tomato_robot_slice_extension_v16 import run as run_cut','from profile_extension import run as run_cut')
(w/'profile_worker.py').write_text(s)
