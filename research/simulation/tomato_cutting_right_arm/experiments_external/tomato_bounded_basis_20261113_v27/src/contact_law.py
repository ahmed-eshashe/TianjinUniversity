"""Time-step independent normal potential and dissipative regularized friction."""
import numpy as np

def evaluate(phi,normal,relative,area,K=1e9,mu=.2,vs=.001):
 depth=np.maximum(-np.asarray(phi),0.);normal=np.asarray(normal);relative=np.asarray(relative);area=np.asarray(area)
 Fn=K*area*depth;vn=(relative*normal).sum(1);t=relative-vn[:,None]*normal;speed=np.linalg.norm(t,axis=1)
 Ft=-mu*Fn[:,None]*np.tanh(speed/vs)[:,None]*t/np.maximum(speed[:,None],1e-30)
 f=Fn[:,None]*normal+Ft
 return {'force':f,'normal_force':Fn,'friction_force':Ft,'energy':float(.5*K*np.sum(area*depth**2)),'friction_power_W':float(-np.sum(Ft*relative)),'sum_magnitudes_N':float(np.linalg.norm(f,axis=1).sum())}
