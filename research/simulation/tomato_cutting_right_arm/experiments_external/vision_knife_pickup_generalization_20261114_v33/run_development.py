"""Serial physical development. Inspected old failures are not independent tests."""
from pathlib import Path
import argparse, json, os, subprocess, sys, time

W = Path(__file__).resolve().parent
B = W.parent / 'vision_knife_pickup_20261113_v32'
a = argparse.ArgumentParser()
a.add_argument('--version', default='v08')
a.add_argument('--tag', required=True)
a.add_argument('--cases', nargs='+', required=True)
a.add_argument('--override', type=Path)
a.add_argument('--case-overrides', type=Path)
args = a.parse_args()
cases = {
    'dropped': ('hybrid_v07_test/recovery_test_005', 0., 0.),
    'compact': ('hybrid_v07_geometry_compact/recovery_validation_000', .018, 0.),
    'medium': ('hybrid_v07_geometry_medium/recovery_validation_000', -.008, 0.),
    'opposite': ('rest_pose_probe_v01/opposite_face_000', .010, 180.),
    'reference': ('hybrid_v07_test/recovery_test_000', 0., 0.),
}
dest = W / 'datasets' / args.tag
dest.mkdir(parents=True, exist_ok=True)
overrides = json.loads(args.override.read_text()) if args.override else {}
case_overrides = json.loads(args.case_overrides.read_text()) if args.case_overrides else {}
results = []
for name in args.cases:
    folder, shift, roll = cases[name]
    settings = json.loads((B / 'datasets' / folder / 'configuration.json').read_text())['args']
    out = dest / name
    assert not out.exists(), 'Preserve prior evidence'
    settings.update(output=str(out), teacher_along_shift=shift, rest_roll_deg=roll,
                    grasp=str(W/'reports/pinch_geometry02.json'), neutral_start=str(W/'reports/neutral_start.json'),
                    visual_checkpoint=str(W/'policies/handle_vision_v01/best.pt'), lift_seconds=6.)
    settings.update(overrides)
    settings.update(case_overrides.get(name, {}))
    cmd = [sys.executable, '-u', str(W / ('hybrid_pickup_'+args.version+'.py'))]
    for k,v in settings.items():
        if isinstance(v,bool):
            if v:cmd.append('--'+k.replace('_','-'))
        elif v is not None:cmd += ['--'+k.replace('_','-'),str(v)]
    (dest/'progress.json').write_text(json.dumps(dict(current=name,completed=results)))
    start=time.monotonic()
    with (dest/(name+'.log')).open('w') as log:
        p=subprocess.run(cmd,cwd=W,stdout=log,stderr=subprocess.STDOUT,
                         env={**os.environ,'OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
    r=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else {}
    f=(out/'failure.txt').read_text().splitlines()[-1] if (out/'failure.txt').exists() else None
    row=dict(case=name,success=bool(r.get('success')) and p.returncode==0,wall_s=time.monotonic()-start,
             failure=f,teacher_shift_m=settings['teacher_along_shift'])
    results.append(row);print(json.dumps(row),flush=True)
    (dest/'progress.json').write_text(json.dumps(dict(current=None,completed=results),indent=2))
(dest/'results.json').write_text(json.dumps(results,indent=2))
