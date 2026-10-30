import importlib.metadata as m,json,subprocess,tomllib
from pathlib import Path
import torch,torchaudio,torchvision,numba,llvmlite,psutil,click
from isaaclab.envs import DirectRLEnv
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
@numba.njit
def square(x): return x*x
assert square(3)==9
x=torch.ones((32,32),device='cuda'); assert float((x@x).mean())==32
# Audio ABI actually exercised, rather than merely satisfying package metadata.
audio=torchaudio.functional.resample(torch.zeros(1,160),16000,8000)
assert audio.shape==(1,80)
from huggingface_hub import HfApi
import IPython,rerun
check=subprocess.run([__import__('sys').executable,'-m','pip','check'],capture_output=True,text=True)
expected={
 'mujoco-usd-converter 0.5.0 has requirement mujoco<3.12,>=3.11.0, but you have mujoco 3.12.0.',
 'isaacsim-core 6.1.0.0 has requirement mujoco==3.11.0, but you have mujoco 3.12.0.',
 'isaacsim-core 6.1.0.0 has requirement mujoco-warp==3.11.0, but you have mujoco-warp 3.12.0.',
 'isaacsim-core 6.1.0.0 has requirement newton[sim]==1.5.0, but you have newton 1.6.0.',
 'isaacsim-core 6.1.0.0 has requirement torch==2.11.0, but you have torch 2.12.0+cu130.',
 'isaacsim-core 6.1.0.0 has requirement torchvision==0.26.0, but you have torchvision 0.27.0+cu130.'}
actual=set(check.stdout.strip().splitlines())
assert actual==expected,(actual-expected,expected-actual)
lab=tomllib.loads(Path('/home/omen/IsaacLab/pyproject.toml').read_text())
overrides=lab['tool']['uv']['override-dependencies']
for requirement in ['mujoco~=3.12.0','mujoco-warp~=3.12.0','newton[sim]==1.6.0','torch==2.12.0','torchvision==0.27.0']:
 assert requirement in overrides,requirement
out={'passed':True,'jit_compilation':True,'cuda_operation':True,'audio_operation':True,'native_import':True,
 'pip_check_clean':False,'only_remaining_mismatches_are_explicit_lab_overrides':True,
 'expected_metadata_mismatches':sorted(actual),'unexpected_metadata_mismatches':[],
 'versions':{n:m.version(n) for n in ['torch','torchvision','torchaudio','numba','llvmlite','click','psutil','huggingface-hub','ipython','rerun-sdk']}}
print(json.dumps(out,indent=2))
