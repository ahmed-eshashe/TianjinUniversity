"""Provisional extraction of the published vector figure; not raw experiment data."""
from pathlib import Path
import xml.etree.ElementTree as ET
import re,json,hashlib,math
import numpy as np
ROOT=Path('/home/omen/teamwork_projects/tomato_cutting_right_arm');p=ROOT/'work/reference_papers/IROS19-page5.svg';root=ET.parse(p).getroot()
candidates=[x for x in root.iter() if x.tag.endswith('path') and x.get('stroke')=='rgb(0%, 0%, 0%)' and x.get('stroke-dasharray') and '126.404, 260.073943' in x.get('transform','') and len(x.get('d',''))>900]
assert len(candidates)==1
trace=candidates[0];assert set(re.findall('[A-Za-z]',trace.get('d')))=={'M','L'}
xy=np.array([float(v) for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',trace.get('d'))]).reshape(-1,2)
# Affine transform from the PDF vector figure; axes verified against labelled 0.01 m and 10 N ticks.
X=.036*xy[:,0]+126.404;Y=-.036*xy[:,1]+260.073943
depth=(X-126.404)/(151.66268-126.404)*.01;force=(260.826991-Y)/(260.826991-245.391847)*10
assert np.min(np.diff(depth))>=-1e-10
peak=int(np.argmax(force));fracture_depth=float(depth[peak]);peak_force=float(force[peak])
# A descriptive force-depth surrogate, fitted on alternating samples and assessed on the withheld interleaved samples.
idx=np.arange(len(depth));train=idx%2==0;test=~train
pre=(depth>.001)&(depth<fracture_depth-.0005)&(force>0)
a=np.polyfit(np.log(depth[pre&train]),np.log(force[pre&train]),1)
pre_prediction=np.exp(a[1])*depth[pre&test]**a[0];pre_error=pre_prediction-force[pre&test]
post=(depth>fracture_depth+.001)&(depth<.043)
b=np.polyfit(depth[post&train],force[post&train],1);post_prediction=np.polyval(b,depth[post&test]);post_error=post_prediction-force[post&test]
np.savez(ROOT/'work/reference_papers/tomato_figure_trace_internal.npz',depth_m=depth,force_n=force)
report=dict(source_url='https://faculty.sites.iastate.edu/jia/files/inline-files/IROS19.pdf',source_pdf_sha256=hashlib.sha256((ROOT/'work/reference_papers/IROS19.pdf').read_bytes()).hexdigest(),source_page=5,source_figure='6, tomato row, dashed measured force',trace_points=len(depth),raw_experimental_data=False,
 observed_peak_force_n=peak_force,observed_peak_depth_m=fracture_depth,
 axis_digitization_resolution_assumption=dict(horizontal_page_points=.2,vertical_page_points=.2,depth_uncertainty_m=.2/(151.66268-126.404)*.01,force_uncertainty_n=.2/(260.826991-245.391847)*10),
 descriptive_fit=dict(before_peak_power_exponent=float(a[0]),before_peak_coefficient=float(np.exp(a[1])),post_peak_linear_slope_n_per_m=float(b[0]),post_peak_intercept_n=float(b[1]),interleaved_pre_rmse_n=float(np.sqrt(np.mean(pre_error**2))),interleaved_post_rmse_n=float(np.sqrt(np.mean(post_error**2)))),
 limitations=['Trace extracted from the vector path in a plotted figure, not instrument samples.','Axis uncertainty is a declared extraction assumption, not biological variability.','Alternating points from one curve are correlated; this is interpolation assessment, not independent experimental validation.','Descriptive fit is not the native cohesive or bulk material model.','Specimen scan, boundary conditions and independent repeat trials are not supplied by this extraction.'],native_material_validated=False)
(ROOT/'work/tomato_digitized_reference_assessment.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
