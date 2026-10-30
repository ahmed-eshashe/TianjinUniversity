"""Tiny bounded PPO allocator/update probe; no knife grasp objective or learned perception."""
import random
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.distributions import Normal


class ProbePolicy(nn.Module):
    def __init__(self, observation_size, action_size):
        super().__init__()
        self.body = nn.Sequential(nn.Linear(observation_size, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh())
        self.mean = nn.Linear(64, action_size)
        self.value = nn.Linear(64, 1)
        self.log_std = nn.Parameter(torch.full((action_size,), -1.5))

    def evaluate(self, observation, action=None):
        z = self.body(observation)
        distribution = Normal(torch.tanh(self.mean(z)), self.log_std.exp())
        action = distribution.sample() if action is None else action
        return action, distribution.log_prob(action).sum(-1), self.value(z).squeeze(-1), distribution.entropy().sum(-1)


class VisionProxy(nn.Module):
    """Untrained RGB-D encoder used ONLY to measure inference memory and latency."""
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(nn.Conv2d(4, 16, 5, stride=2), nn.ReLU(), nn.Conv2d(16, 32, 3, stride=2), nn.ReLU(),
                                     nn.Conv2d(32, 32, 3, stride=2), nn.ReLU(), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(32, 16))

    def forward(self, x):
        return self.encoder(x)


class RunningMoments:
    def __init__(self, size):
        self.count = 0
        self.mean = np.zeros(size, dtype=np.float64)
        self.m2 = np.zeros(size, dtype=np.float64)

    def observe(self, x):
        self.count += 1
        d = x - self.mean; self.mean += d / self.count; self.m2 += d * (x - self.mean)


def ppo_update(policy, optimizer, rollout, next_value, device):
    observations, actions, log_probs, rewards, values, dones = map(lambda x: torch.stack(x), zip(*rollout))
    advantage = torch.zeros_like(rewards); carry = torch.zeros((), device=device)
    for t in range(len(rewards) - 1, -1, -1):
        continuation = 1. - dones[t]
        next_v = next_value if t == len(rewards) - 1 else values[t + 1]
        delta = rewards[t] + .99 * continuation * next_v - values[t]
        carry = delta + .99 * .95 * continuation * carry; advantage[t] = carry
    returns = advantage + values
    advantage = (advantage - advantage.mean()) / (advantage.std() + 1e-6)
    losses = []
    for _ in range(2):
        _, logp, v, entropy = policy.evaluate(observations, actions)
        ratio = (logp - log_probs).exp()
        loss = -torch.minimum(ratio * advantage, ratio.clamp(.8, 1.2) * advantage).mean() + .5 * (v - returns).square().mean() - .001 * entropy.mean()
        if not torch.isfinite(loss):
            raise RuntimeError('Non-finite PPO probe loss')
        optimizer.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(policy.parameters(), .5); optimizer.step()
        losses.append(float(loss.detach()))
    return losses


def save_checkpoint(path, policy, optimizer, vision, moments, counters, reset_rng, config):
    payload = {'policy': policy.state_dict(), 'optimizer': optimizer.state_dict(), 'vision_proxy': vision.state_dict() if vision else None,
               'normalization': {'count': moments.count, 'mean': moments.mean, 'm2': moments.m2},
               'counters': counters, 'curriculum': {'stage': 'resource_probe_only', 'grasp_training': False},
               'rng': {'python': random.getstate(), 'numpy': np.random.get_state(), 'torch': torch.get_rng_state(),
                       'cuda': torch.cuda.get_rng_state_all(), 'reset_generator': reset_rng.bit_generator.state},
               'config': config, 'resume_boundary': 'fresh physical episode; learner/RNG state restored, not exact in-flight PhysX contact state'}
    temporary = Path(str(path) + '.tmp'); torch.save(payload, temporary); temporary.replace(path)
