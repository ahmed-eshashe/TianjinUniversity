import gymnasium as gym

gym.register(
    id="Isaac-Reach-Knife-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.reach_knife_env_cfg:ReachKnifeEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:ReachKnifePPORunnerCfg",
    },
)
