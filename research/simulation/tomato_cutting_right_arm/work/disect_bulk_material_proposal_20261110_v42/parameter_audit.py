"""Independent small-strain interpretation of the existing stabilized NH law.
No production coefficients or simulation state are changed by this script.
"""
from pathlib import Path
import json,numpy as np
W=Path(__file__).resolve().parent

def P(F,mu,la):
 I=float(np.sum(F*F));J=float(np.linalg.det(F));cof=J*np.linalg.inv(F).T;alpha=1+.75*mu/la
 return mu*(1-1/(I+1))*F+la*(J-alpha)*cof

def audit(mu,la):
 eps=1e-6;I=np.eye(3);H=np.zeros((3,3));H[0,1]=1;shear=(P(I+eps*H,mu,la)-P(I-eps*H,mu,la))/(2*eps);H=np.zeros((3,3));H[0,0]=1;axial=(P(I+eps*H,mu,la)-P(I-eps*H,mu,la))/(2*eps);me=.75*mu;le=la-.625*mu;numeric_mu=float(shear[0,1]);numeric_la=float(axial[1,1]);assert abs(numeric_mu-me)<1e-4 and abs(numeric_la-le)<1e-4
 E=me*(3*le+2*me)/(le+me);nu=le/(2*(le+me));return dict(kernel_mu_Pa=mu,kernel_lambda_Pa=la,effective_lame_mu_Pa=me,effective_lame_lambda_Pa=le,Young_modulus_Pa=E,Poisson_ratio=nu,numerical_shear_tangent_Pa=numeric_mu,numerical_axial_cross_tangent_Pa=numeric_la,stress_at_identity_max_Pa=float(abs(P(I,mu,la)).max()))
old=audit(12000.,12000.);E=400000.;nu=.3;mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));new=audit(4*mu/3,la+5*mu/6);assert abs(new['Young_modulus_Pa']-E)<1e-8 and abs(new['Poisson_ratio']-nu)<1e-12
out={'status':'read-only mathematical interpretation/proposal, no adopted material change','existing':old,'proposed_literature_inspired_candidate':new,'mapping':'mu_kernel=(4/3)*mu_linear; lambda_kernel=lambda_linear+(5/6)*mu_linear. The effective linear tangent of the implemented law is mu_linear=0.75*mu_kernel, lambda_linear=lambda_kernel-0.625*mu_kernel.','numerical_derivative_controls_passed':True,'earlier_30kPa_0_25_interpretation_corrected':True,'not_a_new_physical_or_experimental_validation':True,'source_stress_law':'work/disect_precontact_20261108_v06/backend/kernels.cu lines18-22; damping/activation zero for small-strain audit','publication':'Jamdagni & Jia, IEEE T-RO40(2024), TableII, tomato chopping: E0.4MPa and nu0.3','paper_url':'https://faculty.sites.iastate.edu/jia/files/inline-files/TRO24.pdf','local_primary_paper':str(W.parent/'review_20261102/TRO24.pdf'),'limits':'Different specimen, geometry, support, constitutive implementation and parameter-fitting context. Published values are a prior for a separately validated sensitivity candidate, not identified parameters or experimental validation of our tomato.'};(W/'parameter_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
