"""Read-only assessment of accepted master-frame material checkpoints."""
from pathlib import Path
import json, sys
import numpy as np

w = Path(__file__).parent
r = w.parents[1]
sys.path.insert(0, str(r / 'rl'))
from tomato_native_full_model import registry
from tomato_master_frame_live import frame_support

f = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted((w / 'robot_cut12/checkpoints').glob('*.npz'))[-1]
z = np.load(f)
d = registry()
pairs, counts, coeff, weights, models, _ = frame_support(d)
rows = []
for i, patch in enumerate(d['cohesion'].patches):
    xx = z['x'][pairs[i]]
    uv = coeff[i].T @ xx[:, 1]
    t = uv[0] / np.linalg.norm(uv[0])
    cross = np.cross(*uv)
    n = models[i]['sign'] * cross / np.linalg.norm(cross)
    basis = np.column_stack([n, t, np.cross(n, t)])
    gap = (xx[:, 1] - xx[:, 0]) @ basis
    gap[:, 0] = np.maximum(gap[:, 0], 0)
    energy = .5 * np.sum(weights[i, :, None] * gap * (gap @ models[i]['local_k']))
    centroid = np.sum(weights[i, :, None] * xx.mean(1), axis=0) / weights[i].sum()
    rows.append(dict(patch=i, centroid_canonical_m=(centroid + [-.0225, 0, .0295]).tolist(),
        current_opening_mm=float(np.sqrt(2 * energy / patch['law'].stiffness_n_m) * 1000),
        historical_opening_mm=float(z['history'][i, 0] * 1000),
        damage=float(z['history'][i, 1]), seen=bool(z['seen'][i]),
        eligible=bool(z['eligible'][i]), frame_area_ratio=float(np.linalg.norm(cross))))
result = dict(checkpoint=str(f), read_only=True, unchanged_material_law=True,
              seen=sum(p['seen'] for p in rows), eligible=sum(p['eligible'] for p in rows),
              fully_failed=sum(p['damage'] >= 1 for p in rows), patches=rows)
output = f.parent.parent / ('interface_assessment_' + f.stem + '.json')
output.write_text(json.dumps(result, indent=2))
print(json.dumps({k: v for k, v in result.items() if k != 'patches'}))
print('Largest current openings:', [(p['patch'], round(p['current_opening_mm'], 3)) for p in sorted(rows, key=lambda x: x['current_opening_mm'], reverse=True)[:8]])
