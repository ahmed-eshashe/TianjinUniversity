---
name: reinforcement-learning
description: "Formulation of continuous control MDPs, residual RL, reward shaping, PPO/SAC, and SkRL integration for contact-rich robotics."
---

# Reinforcement Learning & Continuous Control Skill

## When to Use
Use when:
- Designing observation spaces, action parameterizations, and reward functions for manipulation tasks.
- Implementing residual RL over kinematic or impedance motion primitives.
- Setting up PPO or SAC hyperparameters in Isaac Lab / SkRL.
- Debugging RL training instability (exploding policy entropy, reward hacking, catastrophic forgetting).

## Mathematical Framework
1. **Markov Decision Process (MDP)**:
   - State space $\mathcal{S} \subseteq \mathbb{R}^{33}$, Action space $\mathcal{A} \subseteq \mathbb{R}^6$, Transition dynamics $\mathcal{P}(\mathbf{s}' \mid \mathbf{s}, \mathbf{a})$, Reward function $R(\mathbf{s}, \mathbf{a}, \mathbf{s}')$, Discount factor $\gamma = 0.99$.
2. **Residual Formulation**:
   - Nominal trajectory: $\mathbf{a}_{nom}(t) = [v_{saw} \sin(\omega t), -v_{feed}, 0]^T$
   - Executed action: $\mathbf{a}_t = \mathbf{a}_{nom}(t) + \pi_\theta(\mathbf{s}_t)$
   - Action clipping: enforce $\|\pi_\theta(\mathbf{s}_t)\|_\infty \le \mathbf{a}_{max}$ to guarantee stability.
3. **Reward Engineering**:
   - Avoid sparse rewards. Use smooth potential-based reward shaping.
   - Guard against reward cheating: if the agent gets reward for high sawing frequency without penetrating, add a penalty for idle strokes without normal contact.
