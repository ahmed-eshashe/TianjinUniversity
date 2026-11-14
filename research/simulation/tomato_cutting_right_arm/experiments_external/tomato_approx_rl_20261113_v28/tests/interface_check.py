from pathlib import Path
import sys,json,numpy as np
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'src'))
import warp as wp
wp.config.kernel_cache_dir=str(W/'cache/warp');wp.config.enable_backward=False
from environment import CuttingEnv
E=CuttingEnv(2,dt=.0002,shape='cube');obs,info=E.reset();obs,r,t,tr,info=E.step(np.zeros((2,6)));result={'actor_observation_shape':list(obs.shape),'critic_observation_shape':list(info['critic_observation'].shape),'action_space_contains_zero':E.action_space.contains(np.zeros((2,6),np.float32)),'observation_space_contains_result':E.observation_space.contains(obs),'damage_in_actor':False,'pass':bool(obs.shape==(2,25) and info['critic_observation'].shape==(2,3) and E.observation_space.contains(obs))};(W/'reports/interface_check.json').write_text(json.dumps(result,indent=2));print(result)
