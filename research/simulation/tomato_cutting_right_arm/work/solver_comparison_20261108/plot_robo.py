from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
w=Path(__file__).resolve().parent
fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for ax,label in zip(axs,['robo_straight_1','robo_curved_1','robo_straight_0.8']):
 z=np.load(w/f'{label}_final.npz')
 for name,color in [('initial','#94a3b8'),('x','#d04b32')]:
  x=z[name];keep=np.abs(x[:,2]-.5)<.004;ax.scatter(x[keep,0],x[keep,1],s=1,c=color,alpha=.5,label='Initial'if name=='initial'else'Final')
 ax.set_title(label.replace('robo_','').replace('_',' '));ax.set_aspect('equal');ax.set_xlabel('x (model coordinates)');ax.set_ylabel('y');ax.legend(markerscale=4)
fig.suptitle('RoboNinja forward benchmarks: central particle cross-section\nDifferent material and scale from the tomato; detached slices not established',fontsize=12)
fig.savefig(w/'robo_cross_sections.png',dpi=160)
