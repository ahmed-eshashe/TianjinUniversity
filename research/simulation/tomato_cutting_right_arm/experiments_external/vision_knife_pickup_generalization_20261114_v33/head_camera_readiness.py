"""Check raw sensor readiness before a single grasp inference; no object truth."""
from pathlib import Path
import json,time
import numpy as np

def ready_head_images(read_images,output,max_attempts=120,max_wall_s=30.):
    start=time.monotonic();rows=[]
    for attempt in range(max_attempts):
        rgb,depth=read_images();crop=rgb[96:416,96:544,:3].astype(np.float32);z=depth[96:416,96:544]
        fraction=float(np.mean(np.isfinite(z)&(z>.05)&(z<3.)))
        contrast=float(np.std(crop.mean(-1)));ready=fraction>=.85 and contrast>=5.
        rows.append(dict(attempt=attempt,valid_depth_fraction=fraction,spatial_contrast=contrast,ready=ready,wall_s=time.monotonic()-start))
        if ready:break
        if time.monotonic()-start>=max_wall_s:break
    Path(output).write_text(json.dumps(dict(rule='Raw crop depth validity >=85% and spatial grayscale contrast >=5, before any inference',no_object_truth_or_network_confidence_used=True,physics_advanced_during_wait=False,ready=ready,attempts=rows),indent=2))
    if not ready:raise ValueError('Head RGB-D sensor did not provide a valid startup frame')
    return rgb,depth
