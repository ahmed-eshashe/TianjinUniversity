"""Dedicated native coupon worker source. Execution is disabled for preparation."""
import argparse
import json
from pathlib import Path
from tomato_native_launch_contract import digest,owned_file

PREPARATION_EXECUTION_DISABLED=True


def validate_inputs(root,config):
    if config.get('purpose')!='single_blade_coupon' or config.get('native_execution_enabled') is not False:
        raise ValueError('Disabled isolated single-blade configuration required')
    from tomato_coupon_segment import validate_segment
    validate_segment(config)
    for name in ('blade','trajectory'):
        ref=config[name];p=owned_file(root,ref['path'])
        if digest(p)!=ref['sha256']:raise ValueError(name+' hash mismatch')
    sources=config.get('source_sha256',{})
    required={'rl/tomato_native_worker.py','rl/tomato_native_coupon.py','rl/tomato_native_step.py',
              'rl/tomato_soft_contact_observer.py','rl/tomato_coupon_segment.py','rl/tomato_coupon_trajectory.py',
              'rl/tomato_reaction_metadata.py','rl/tomato_kinematic_interval.py'}
    if not required<=set(sources):raise ValueError('Complete direct worker source binding required')
    for path,h in sources.items():
        if digest(owned_file(root,path))!=h:raise ValueError('Worker source mismatch')
    helper=Path(config['observer_helper_path'])
    if helper!=Path('/home/omen/miniconda3/envs/isaaclab_6/lib/python3.12/site-packages/newton/_src/solvers/vbd/rigid_vbd_kernels.py') or digest(helper)!=config['observer_helper_sha256']:
        raise ValueError('Private observer helper version mismatch')
    return {'blade':json.loads(owned_file(root,config['blade']['path']).read_text()),
            'trajectory':json.loads(owned_file(root,config['trajectory']['path']).read_text())}


def run(root,config,output,*,native_execution_authorized=False):
    # A later reviewed change and external authorization must both occur. No CLI
    # option, config bit or self-issued request can bypass preparation's guard.
    if PREPARATION_EXECUTION_DISABLED or native_execution_authorized is not True:
        raise PermissionError('Native worker execution disabled during preparation')
    inputs=validate_inputs(root,config)
    from tomato_native_coupon import build_native_candidate
    from tomato_soft_contact_observer import make_native_observer
    from tomato_coupon_segment import SegmentJournal,run_native_segment
    journal=SegmentJournal(output,run_id=config['run_id'],episode_id=config['episode_id'],source_sha256=config['source_sha256'])
    bundle=build_native_candidate(inputs['blade'],native_execution_authorized=True)
    kernel=make_native_observer(expected_helper_sha256=config['observer_helper_sha256'],native_execution_authorized=True)
    return run_native_segment(bundle,inputs['trajectory'],config,journal,kernel,native_execution_authorized=True)


def preview(root,config,output):
    validate_inputs(root,config)
    out=Path(output).resolve()
    if out.exists():raise ValueError('Future output directory already used')
    return {'command':['/home/omen/miniconda3/envs/isaaclab_6/bin/python',str(Path(root).resolve()/'rl/tomato_native_worker.py'),
                       '--root',str(Path(root).resolve()),'--config',str(config['_config_path']), '--output',str(out)],
            'execution_enabled':False,'worker_budget_s':60,'native_runtime_validated':False,
            'pending':['reviewed supervision and runtime authorization','native constructors/kernel compilation','real contact/work audits']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();cfg=json.loads(a.config.read_text());cfg['_config_path']=str(a.config.resolve())
    print(json.dumps(preview(a.root,cfg,a.output),indent=2))

if __name__=='__main__':main()
