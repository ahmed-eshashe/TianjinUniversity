from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
w=Path(__file__).resolve().parent;diag=w.parent/'disect_stability_20261108_v03';old=json.loads((diag/'settle_result.json').read_text());new=json.loads((w/'settle_result.json').read_text());tr=json.loads((diag/'damping_translation_check.json').read_text());cr=json.loads((w/'controls_result.json').read_text());fig,ax=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
for d,label,color in [(old,'Original damping; dt 0.20 µs','#a33a35'),(new,'Relative damping; dt 0.15 µs','#197e73')]:
 a=d['rows'];ax[0].plot([r['sim_s']*1000 for r in a],[r['min_volume_ratio'] for r in a],label=label,color=color,lw=2)
ax[0].axhline(.1,color='0.4',ls='--',label='Declared stop');ax[0].set(xlabel='Simulated time (ms)',ylabel='Minimum sampled volume ratio',title='Short gravity checks (timesteps differ)');ax[0].legend(fontsize=8);ax[0].grid(alpha=.2)
values=[tr['predicted_damping_force_norm_N'],cr['translation']['actual_norm_N']];ax[1].bar(['Original operator\nindependent prediction','Corrected operator\nGPU measurement'],values,color=['#a33a35','#197e73']);ax[1].set_yscale('log');ax[1].set(ylabel='Global damping-force norm (model N)',title='Uniform translation at 0.1 m/s');ax[1].grid(axis='y',alpha=.2);fig.savefig(w/'stability_diagnosis.png',dpi=170);fig.savefig(w/'stability_diagnosis.pdf')
