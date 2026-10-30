"""Render the recorded resource trace after a bounded benchmark completes."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
rows=[json.loads(x) for x in (a.run/'resources.jsonl').read_text().splitlines()]
rows=[x for x in rows if x['rss_bytes']>0]
t=[x['wall_s']/60 for x in rows]
fig,axes=plt.subplots(2,1,figsize=(10,6.5),sharex=True,layout='constrained')
axes[0].plot(t,[x['rss_bytes']/1e9 for x in rows],label='Simulator process RAM',color='#2563eb')
axes[0].plot(t,[x['available_ram_bytes']/1e9 for x in rows],label='Available host RAM',color='#159a76')
axes[0].axhline(3_000_000*1024/1e9,color='#cc8800',linestyle='--',label='Checkpoint reserve')
axes[0].axhline(2_000_000*1024/1e9,color='#bf3345',linestyle=':',label='Hard stop reserve')
axes[0].set_ylabel('Host memory (decimal GB)')
axes[1].plot(t,[x['gpu_used_bytes']/1024**3 for x in rows],label='Total GPU memory used',color='#7c3aed')
axes[1].plot(t,[x['gpu_free_bytes']/1024**3 for x in rows],label='Free GPU memory',color='#159a76')
axes[1].axhline(1.5,color='#cc8800',linestyle='--',label='Checkpoint reserve')
axes[1].axhline(1.,color='#bf3345',linestyle=':',label='Hard stop reserve')
axes[1].set_ylabel('GPU memory (GiB)');axes[1].set_xlabel('Wall time since simulator launch (minutes)')
for ax in axes:
 ax.set_ylim(bottom=0);ax.grid(alpha=.18);ax.legend(loc='center left',bbox_to_anchor=(1.,.5),frameon=False,fontsize=8)
fig.suptitle('One environment with RGB-D and bounded PPO resource updates\nResource probe only; no knife grasp training',fontsize=12)
a.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.output,dpi=150);plt.close(fig);print(a.output)
