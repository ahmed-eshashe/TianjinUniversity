from pathlib import Path
import json,numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).resolve().parent
p=W/'datasets/hybrid_v03_test/test_000'
r=json.loads((p/'result.json').read_text());assert r['success']
pred=json.loads((p/'visual_prediction.json').read_text());points=np.array(pred['pixels'])
fig,axes=plt.subplots(1,2,figsize=(12,5),gridspec_kw={'width_ratios':[1,1.3]})
fig.patch.set_facecolor('#101821')
axes[0].imshow(Image.open(p/'vision_input_rgb.png'));axes[0].plot(points[:,0],points[:,1],'-o',color='#38efb5',lw=2,ms=6)
axes[0].set_title("Robot’s head view: learned handle position",color='white',fontsize=12,pad=12)
axes[1].imshow(Image.open(p/'final_review.png'));axes[1].set_title('Actual simulated pickup: finger contact only',color='white',fontsize=12,pad=12)
for ax in axes:ax.axis('off')
fig.suptitle('Vision chooses the grasp. The motion controller performs the pickup.',color='white',fontsize=15,y=.98)
fig.text(.5,.035,f"Reserved test 000 passed • {r['last']['hold_s']:.1f} s unsupported • {r['last']['slip_m']*1000:.2f} mm relative slip • no attachment",ha='center',color='#b7d3e8',fontsize=11)
fig.subplots_adjust(left=.025,right=.975,bottom=.10,top=.86,wspace=.06)
fig.savefig(W/'reports/vision_pickup_verified.png',dpi=140,facecolor=fig.get_facecolor());plt.close(fig)
