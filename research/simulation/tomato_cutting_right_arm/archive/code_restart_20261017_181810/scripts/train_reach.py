import sys
import tasks.reach_knife
from isaaclab_rl.entrypoints.dispatch import run_train_cli

if __name__ == "__main__":
    # Prepend default task arguments if not provided
    args = sys.argv[1:]
    if "--task" not in args:
        args = ["--task", "Isaac-Reach-Knife-v0"] + args
    if "--rl_library" not in args:
        args = ["--rl_library", "rsl_rl"] + args
    
    run_train_cli(args)
