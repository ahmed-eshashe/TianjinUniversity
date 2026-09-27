import os
import weasyprint
import shutil

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Continuous Q-Learning & Soft Actor-Critic: Beginner's Guide to CS285 Lecture 8</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {
      content: "CS285 Lecture 8: Continuous Q-Learning & Soft Actor-Critic";
      font-size: 8pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #64748b;
    }
    @bottom-center {
      content: "Page " counter(page) " of " counter(pages);
      font-size: 8.5pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #64748b;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.58;
    font-size: 10pt;
  }

  .header-block {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 16px;
    margin-bottom: 20px;
  }
  .course-tag {
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    font-weight: 700;
    font-size: 8pt;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }
  h1 {
    color: #0f172a;
    font-size: 20pt;
    font-weight: 800;
    margin: 0 0 6px 0;
    line-height: 1.25;
  }
  .subtitle {
    color: #475569;
    font-size: 10.5pt;
    margin: 0 0 10px 0;
    font-weight: 500;
  }
  .meta-bar {
    font-size: 8.5pt;
    color: #64748b;
    display: flex;
    justify-content: space-between;
  }

  h2 {
    color: #1e3a8a;
    font-size: 13pt;
    font-weight: 700;
    margin-top: 22px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    page-break-after: avoid;
  }

  h3 {
    color: #0f172a;
    font-size: 10.8pt;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 5px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 8px 0;
    text-align: justify;
  }

  .callout {
    padding: 10px 14px;
    margin: 11px 0;
    border-radius: 6px;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }
  .callout p { margin: 0; }
  .callout-title {
    font-weight: 700;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }

  .intuition {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e3a8a;
  }
  .intuition .callout-title { color: #1d4ed8; }

  .robotics {
    background: #ecfdf5;
    border-left: 4px solid #10b981;
    color: #064e3b;
  }
  .robotics .callout-title { color: #047857; }

  .math-box {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #78350f;
  }
  .math-box .callout-title { color: #b45309; }

  .warning-box {
    background: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #7f1d1d;
  }
  .warning-box .callout-title { color: #b91c1c; }

  .silent-bug {
    background: #fdf2f8;
    border-left: 4px solid #db2777;
    color: #831843;
  }
  .silent-bug .callout-title { color: #be185d; }

  .formula {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 10px 0;
    text-align: center;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 10.8pt;
    color: #0f172a;
    page-break-inside: avoid;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9.2pt;
    page-break-inside: avoid;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 7px 10px;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 6px 10px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #f8fafc; }

  .diagram-container {
    text-align: center;
    margin: 12px 0;
    page-break-inside: avoid;
  }

  .code-block {
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    font-family: Consolas, Monaco, "Courier New", monospace;
    font-size: 8.6pt;
    line-height: 1.45;
    margin: 12px 0;
    page-break-inside: avoid;
  }

  .quiz-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 12px 14px;
    margin: 14px 0;
    page-break-inside: avoid;
  }
  .quiz-q { font-weight: 700; color: #0f172a; margin-bottom: 6px; }
  .quiz-a { color: #334155; font-size: 9.3pt; margin-top: 4px; border-top: 1px dashed #cbd5e1; padding-top: 4px; }

  .page-break { page-break-before: always; }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 8 Enhanced Study Guide</span>
  <h1>Mastering Continuous Q-Learning &amp; SAC</h1>
  <div class="subtitle">Complete Beginner-Friendly Breakdown: The Continuous Max Problem, Polyak Averaging, Clipped Twin-Q, Maximum Entropy Derivation &amp; Soft Actor-Critic</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Companion:</b> DEX-ROB Lab, Tianjin University</span>
    <span><b>Frameworks:</b> Achiam (Spinning Up ch19) + Haarnoja &amp; Levine</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The "Mental Map": Why Does Lecture 8 Exist?</h2>
<p>
  In Lecture 6, we learned how Actor-Critic combines policy optimization with value estimation. But there exists an alternative branch of Reinforcement Learning: <b>Value-Based Methods (Q-Learning)</b>.
</p>
<p>
  Classic Q-learning (such as Deep Q-Networks / DQN used by DeepMind for Atari games) learns a state-action function $Q(s, a)$ and picks the optimal action by taking $\arg\max_a Q(s, a)$.
</p>
<p>
  <b>The Fatal Flaw for Robotics:</b> In continuous robotic manipulation, the action is not a discrete choice among 4 buttons; it is a continuous vector of joint velocities, feed rates, and impedance stiffness values. Finding the maximum of a non-linear neural network over an infinite continuous space is computationally impossible in real-time.
</p>
<p>
  <b>Lecture 8 bridges this gap:</b> Sergey Levine explains how to stabilize deep Q-learning using Target Networks and Double Q-learning, how to handle continuous action spaces, and how <b>Soft Actor-Critic (SAC)</b> merges Q-learning with Maximum Entropy to create one of the most powerful off-policy continuous control algorithms in modern robotics.
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 8 -->
<div class="diagram-container">
<svg width="680" height="90" viewBox="0 0 680 90">
  <rect x="5" y="10" width="125" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="67" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. Target Networks</text>
  <text x="67" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Polyak Averaging:</text>
  <text x="67" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Freezing Moving Targets</text>

  <rect x="140" y="10" width="125" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="202" y="36" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">2. Overestimation</text>
  <text x="202" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Clipped Twin-Q:</text>
  <text x="202" y="66" font-size="8.5" fill="#475569" text-anchor="middle">min(Q1, Q2) Solution</text>

  <rect x="275" y="10" width="125" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="337" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">3. Continuous Max</text>
  <text x="337" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Intractable max_a:</text>
  <text x="337" y="66" font-size="8.5" fill="#475569" text-anchor="middle">CEM vs Actor Maximizer</text>

  <rect x="410" y="10" width="125" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="472" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">4. Max Entropy RL</text>
  <text x="472" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Reward + α H(π):</text>
  <text x="472" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Anti-Freezing Exploration</text>

  <rect x="545" y="10" width="125" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="607" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">5. The Deadly Triad</text>
  <text x="607" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Bootstrapping +</text>
  <text x="607" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Function Approx + Buffer</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: Stabilizing Q-Learning: Target Networks &amp; Polyak Averaging</h2>
<p>
  <b>(Slides 1–25, Spoken Transcript 02:20–19:40)</b> In exact tabular Q-learning, the Bellman optimality update is guaranteed to converge. But when we replace the table with a Deep Neural Network $Q_\theta(s, a)$, training frequently explodes. Why?
</p>

<h3>1.1 The "Chasing Your Own Tail" Problem</h3>
<div class="formula">
  \mathcal{L}(\theta) = \mathbb{E}_{(s, a, r, s') \sim \mathcal{D}} \left[ \left( Q_\theta(s, a) - \left[ r + \gamma \max_{a'} Q_\theta(s', a') \right] \right)^2 \right]
</div>
<p>
  The network weights $\theta$ appear in <i>both</i> prediction and target. Every gradient step shifts the target itself!
  To break this vicious feedback loop, we maintain a secondary set of weights $\bar{\theta}$ called the <b>Target Network</b>:
  $y_t = r_t + \gamma \max_{a'} Q_{\bar{\theta}}(s_{t+1}, a')$.
</p>

<!-- SVG Diagram: Polyak Averaging -->
<div class="diagram-container">
<svg width="680" height="130" viewBox="0 0 680 130">
  <rect x="50" y="20" width="220" height="70" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="160" y="45" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">Online Critic Q_θ(s, a)</text>
  <text x="160" y="62" font-size="8.5" fill="#3b82f6" text-anchor="middle">Updated via SGD at every step</text>
  <text x="160" y="76" font-size="8.5" fill="#475569" text-anchor="middle">Fast-moving parameter set</text>

  <path d="M 280 55 L 400 55" stroke="#10b981" stroke-width="2.5" marker-end="url(#arr-poly)"/>
  <text x="340" y="45" font-size="9" font-weight="700" fill="#047857" text-anchor="middle">Polyak Averaging (τ = 0.005)</text>
  <text x="340" y="75" font-size="8" fill="#64748b" text-anchor="middle">θ̄ ‹- τ θ + (1 - τ) θ̄</text>

  <rect x="410" y="20" width="220" height="70" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="520" y="45" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">Target Critic Q_θ̄(s, a)</text>
  <text x="520" y="62" font-size="8.5" fill="#047857" text-anchor="middle">Slowly tracks online network</text>
  <text x="520" y="76" font-size="8.5" fill="#475569" text-anchor="middle">Generates stable Bellman targets</text>

  <defs>
    <marker id="arr-poly" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981"/>
    </marker>
  </defs>
</svg>
</div>

<h3>1.2 Polyak Averaging Half-Life</h3>
<p>
  Instead of hard-copying weights every 10,000 steps, continuous control algorithms smoothly blend target weights after every training step:
  $\bar{\theta} \leftarrow \tau \theta + (1 - \tau) \bar{\theta}$ (with $\tau = 0.005$).
  This corresponds to an exponential decay half-life of:
</p>
<div class="formula">
  t_{\text{half}} = \frac{\ln(2)}{\tau} = \frac{0.693}{0.005} \approx 138 \text{ gradient steps}
</div>
<p>
  This prevents abrupt target discontinuities, ensuring smooth impedance gain transitions on physical robotic hardware.
</p>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: Overestimation Bias &amp; Clipped Double Q-Learning</h2>
<p>
  <b>(Slides 26–42, Spoken Transcript 19:50–35:15)</b> A profound mathematical flaw exists in standard Q-learning: <b>the maximization step systematically overestimates value functions!</b>
</p>

<h3>2.1 The Mathematical Origin of Overestimation</h3>
<p>
  By Jensen's inequality and the convexity of the maximum function:
</p>
<div class="formula">
  \mathbb{E}\left[ \max_a \hat{Q}(s, a) \right] \ge \max_a \mathbb{E}\left[ \hat{Q}(s, a) \right] = \max_a Q^{\text{true}}(s, a)
</div>
<p>
  If the network randomly overestimates an action (e.g. violent downward slam), the $\max$ greedily selects it, causing value predictions to blow up toward $+10,000$.
</p>

<!-- SVG Diagram: Overestimation and Clipped Twin-Q -->
<div class="diagram-container">
<svg width="680" height="150" viewBox="0 0 680 150">
  <rect x="30" y="20" width="280" height="110" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="170" y="45" font-size="10.5" font-weight="700" fill="#991b1b" text-anchor="middle">Standard Q-Learning (Single Critic)</text>
  <text x="170" y="65" font-size="8.5" fill="#475569" text-anchor="middle">Takes max over noisy estimates</text>
  <text x="170" y="85" font-size="9" fill="#ef4444" text-anchor="middle">E[max Q] &gt; max E[Q]</text>
  <text x="170" y="105" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">Result: Q-Values explode to +10,000!</text>

  <rect x="370" y="20" width="280" height="110" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="510" y="45" font-size="10.5" font-weight="700" fill="#065f46" text-anchor="middle">Clipped Twin-Q (TD3 / SAC)</text>
  <text x="510" y="65" font-size="8.5" fill="#475569" text-anchor="middle">Trains Two Independent Critics Q_1, Q_2</text>
  <text x="510" y="85" font-size="9" fill="#047857" text-anchor="middle">Target: y = r + γ min(Q_1, Q_2)</text>
  <text x="510" y="105" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">Result: Bounded, pessimistic value targets</text>
</svg>
</div>

<h3>2.2 The Clipped Twin-Q Solution (Fujimoto et al., 2018)</h3>
<p>
  Maintain <b>two separate Critic networks</b> ($Q_{\phi_1}$ and $Q_{\phi_2}$) with independent initializations. When computing the Bellman target, always evaluate both and take the <b>minimum</b>:
</p>
<div class="formula" style="border: 2px solid #2563eb; background: #eff6ff;">
  $$y_t = r_t + \gamma \min \Big( Q_{\bar{\phi}_1}(s_{t+1}, \tilde{a}_{t+1}),\, Q_{\bar{\phi}_2}(s_{t+1}, \tilde{a}_{t+1}) \Big)$$
</div>
<p>
  Taking the minimum injects controlled pessimism, completely eliminating overestimation bias.
</p>

<div class="page-break"></div>

<!-- PART 3 -->
<h2>Part 3: Continuous Actions &amp; The Intractable Max</h2>
<p>
  <b>(Slides 43–58, Spoken Transcript 35:30–48:00)</b> How do we find $\arg\max_a Q(s, a)$ when action vector $\mathbf{a}_t \in \mathbb{R}^6$ is continuous?
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Approach</th>
      <th style="width: 35%;">Mechanism</th>
      <th style="width: 40%;">Pros &amp; Cons for Robotics</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Stochastic Optimization (CEM / CMA-ES)</b></td>
      <td>Sample 1,000 random actions, evaluate $Q(s, a)$, fit Gaussian to top 10%, repeat 3 times.</td>
      <td>Extremely slow in the inner loop; fails beyond 10–20 action dimensions; unacceptable for real-time 60 Hz execution.</td>
    </tr>
    <tr>
      <td><b>Analytical Q-Functions (NAF)</b></td>
      <td>Constrain $Q(s, a)$ to be strictly quadratic in $a$: $Q(s,a) = V(s) - \frac{1}{2}(a - \mu)^T P (a - \mu)$.</td>
      <td>Maximum is analytically $\mu(s)$, but restricts the Critic to simple parabolic shapes; cannot capture complex contact bifurcations.</td>
    </tr>
    <tr>
      <td><b>Learned Actor Maximizer (DDPG / SAC)</b></td>
      <td>Train a separate neural policy $\pi_\theta(s)$ whose explicit objective is to output the action that maximizes $Q(s, a)$.</td>
      <td><b>The Winning Approach:</b> Computing the maximum requires only a single forward pass through the Actor network $\pi_\theta(s)$!</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 4 -->
<h2>Part 4: Soft Actor-Critic (SAC) &amp; Maximum Entropy RL</h2>
<p>
  <b>(Slides 59–75 &amp; Spinning Up ch19)</b> Soft Actor-Critic modifies the objective to maximize both <b>reward</b> AND <b>policy entropy $\mathcal{H}(\pi)$</b>:
</p>

<div class="formula" style="border: 2px solid #c084fc; background: #fdf4ff;">
  J(\pi) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t) \sim \rho_\pi} \left[ r(s_t, a_t) + \alpha \, \mathcal{H}\big(\pi(\cdot | s_t)\big) \right]
</div>

<h3>4.1 The "Anti-Freezing" Phenomenon in Soft Fruit Slicing</h3>
<p>
  Touching a tomato risks incurring our $-15$ crushing penalty. Under standard RL, the policy collapses into a local minimum where the blade <b>hovers stationary 1 mm above the skin</b> to collect safe zero rewards.
  <b>Under Maximum Entropy SAC:</b> A frozen blade has zero entropy ($\mathcal{H} = 0$), which incurs a massive entropy penalty! The robot is compelled to keep vibrating and testing sawing actions, discovering that light lateral sawing punctures the skin cleanly without crushing.
</p>

<h3>4.2 Automatic Entropy Temperature Tuning ($\alpha$)</h3>
<p>
  Rather than keeping temperature $\alpha$ fixed, SAC formulates temperature optimization as a dual constrained problem targeting heuristic $\bar{\mathcal{H}} = -\dim(\mathcal{A}) = -6$:
</p>
<div class="formula">
  \mathcal{L}(\alpha) = \mathbb{E}_{a \sim \pi} \left[ -\alpha \big( \log \pi(a|s) + \bar{\mathcal{H}} \big) \right]
</div>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Sutton's "Deadly Triad" in Value-Based RL</h2>
<p>
  <b>(Slides 76–88, Spoken Transcript 1:09:00–1:20:15)</b> Rich Sutton proved that severe instability or divergence in reinforcement learning arises whenever three algorithmic elements are combined simultaneously:
</p>

<!-- SVG Diagram: The Deadly Triad -->
<div class="diagram-container">
<svg width="680" height="150" viewBox="0 0 680 150">
  <polygon points="340,15 170,125 510,125" fill="#fef2f2" stroke="#ef4444" stroke-width="2"/>
  
  <text x="340" y="45" font-size="11" font-weight="700" fill="#991b1b" text-anchor="middle">1. Function Approximation</text>
  <text x="340" y="60" font-size="8.5" fill="#475569" text-anchor="middle">Deep Neural Networks</text>

  <text x="210" y="110" font-size="11" font-weight="700" fill="#991b1b" text-anchor="middle">2. Bootstrapping</text>
  <text x="210" y="123" font-size="8.5" fill="#475569" text-anchor="middle">Bellman Target r + γQ'</text>

  <text x="470" y="110" font-size="11" font-weight="700" fill="#991b1b" text-anchor="middle">3. Off-Policy Learning</text>
  <text x="470" y="123" font-size="8.5" fill="#475569" text-anchor="middle">Experience Replay Buffer</text>

  <rect x="250" y="68" width="180" height="28" rx="4" fill="#ef4444"/>
  <text x="340" y="86" font-size="10" font-weight="800" fill="#ffffff" text-anchor="middle">THE DEADLY TRIAD</text>
</svg>
</div>

<div class="callout silent-bug">
  <div class="callout-title">Spinning Up Bug Alert: Buffer vs. Current Policy Actions</div>
  <p>
    Joshua Achiam highlights a frequent silent bug:
    In Critic loss, $Q(s, a)$ MUST evaluate historical actions sampled from the replay buffer ($a \sim \mathcal{D}$).
    In Actor loss, $Q(s, \tilde{a})$ MUST evaluate newly sampled actions from the current policy ($\tilde{a} \sim \pi_\theta(s)$).
    If you evaluate buffer actions in the Actor loss, gradients will not flow from the policy weights, completely freezing policy learning!
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 6 -->
<h2>Part 6: Paper 1 Implementation Blueprint: SAC Architecture</h2>

<div class="code-block">
import torch
import torch.nn as nn
import torch.nn.functional as F

def compute_sac_losses(actor, q1, q2, target_q1, target_q2, log_alpha, batch, gamma=0.99):
    states, actions, rewards, next_states, dones = batch
    alpha = log_alpha.exp()

    # 1. CRITIC LOSS: Bellman Target using Target Twin-Q
    with torch.no_grad():
        next_actions, next_log_pi = actor.sample(next_states)
        q1_target = target_q1(next_states, next_actions)
        q2_target = target_q2(next_states, next_actions)
        min_next_q = torch.min(q1_target, q2_target) - alpha * next_log_pi
        y = rewards + gamma * (1.0 - dones) * min_next_q

    q1_loss = F.mse_loss(q1(states, actions), y)
    q2_loss = F.mse_loss(q2(states, actions), y)
    critic_loss = q1_loss + q2_loss

    # 2. ACTOR LOSS: Reparameterized Gradient
    new_actions, log_pi = actor.sample(states)
    min_q = torch.min(q1(states, new_actions), q2(states, new_actions))
    actor_loss = (alpha.detach() * log_pi - min_q).mean()

    # 3. TEMPERATURE LOSS: Target entropy heuristic -dim(A)
    target_entropy = -float(actions.shape[-1])
    alpha_loss = -(log_alpha * (log_pi + target_entropy).detach()).mean()

    return critic_loss, actor_loss, alpha_loss
</div>

<div class="page-break"></div>

<!-- PART 7: SELF-TEST QUIZ -->
<h2>Part 7: Interactive Tablet Self-Test Quiz (Test Your Understanding)</h2>

<div class="quiz-box">
  <div class="quiz-q">Question 1: Why does Clipped Twin-Q use the minimum of two target Q-networks rather than their average?</div>
  <div class="quiz-a">
    <b>Answer:</b> Taking the average does not prevent overestimation bias; if both networks have positive noise, their average remains positively biased. Taking the minimum $\min(Q_1, Q_2)$ introduces a mild, controlled underestimation bias that acts as a conservative safety margin, preventing runaway value explosion during contact manipulation.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: In SAC, why is the target entropy heuristic set to $-\dim(\mathcal{A})$?</div>
  <div class="quiz-a">
    <b>Answer:</b> A standard Gaussian distribution $\mathcal{N}(0, I)$ has entropy $\frac{d}{2}(1 + \ln(2\pi))$. Haarnoja and Levine found empirically that setting target entropy $\bar{\mathcal{H}} = -d$ (where $d = \dim(\mathcal{A})$) scales linearly with action space dimensionality, ensuring sufficient exploration across all 6 motor degrees of freedom without overwhelming the task reward.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: How does Polyak averaging ($\tau = 0.005$) stabilize training on physical robots?</div>
  <div class="quiz-a">
    <b>Answer:</b> Polyak averaging smoothly blends target network weights with an exponential half-life of $\sim 138$ steps ($\bar{\theta} \leftarrow \tau \theta + (1-\tau)\bar{\theta}$). This prevents the sudden value step-discontinuities that occur during periodic hard target copies, eliminating violent torque spikes at robot arm joints.
  </div>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 8: THESIS DEFENSE -->
<h2>Part 8: Thesis Defense Master Cheatsheet (Lecture 8 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Q1: "Why does standard Deep Q-Networks (DQN) fail in continuous robotic manipulation?"</div>
  <p>
    <b>Answer:</b> "DQN selects actions via $\arg\max_a Q(s, a)$. In discrete games with 4 buttons, this requires 4 forward evaluations. In continuous multi-joint manipulation where the action space is $\mathbb{R}^6$ or $\mathbb{R}^{14}$, finding the continuous global maximum of an arbitrary neural network is an intractable non-convex optimization problem that cannot be solved within our 60 Hz control loop. Algorithms like DDPG and SAC solve this by training a dedicated Actor network to approximate the maximizer directly."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q2: "What causes Overestimation Bias in Q-learning, and how does Clipped Twin-Q eliminate it?"</div>
  <p>
    <b>Answer:</b> "Overestimation bias stems from Jensen's inequality and noise in neural network function approximation: taking the maximum over noisy estimates yields an expected value strictly greater than the true maximum ($\mathbb{E}[\max X] \ge \max \mathbb{E}[X]$). Clipped Twin-Q trains two independently initialized critics ($Q_1, Q_2$) and computes target values using their minimum $\min(Q_1, Q_2)$. This introduces a mild, controlled underestimation bias that completely prevents catastrophic value explosion."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q3: "Why is Maximum Entropy RL uniquely effective at preventing the robot from freezing?"</div>
  <p>
    <b>Answer:</b> "In delicate tasks like slicing soft fruit, touching the fruit introduces risk of incurring high crushing penalties. Standard RL policies frequently collapse into a trivial local minimum where the blade hovers stationary above the skin to collect 0 reward. Maximum Entropy RL augments the reward with an entropy bonus $\alpha \mathcal{H}(\pi)$. Because a stationary action has zero entropy, freezing is heavily penalized, compelling the policy to continuously explore compliant sawing motions until it masters skin puncture."
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
<div style="text-align: center; font-size: 8.5pt; color: #64748b;">
  CS 285 Lecture 8 Comprehensive Study Guide • Prepared for DEX-ROB Lab, Tianjin University
</div>

</body>
</html>
"""

output_path = "/home/omen/Downloads/CS285_Lecture8_Beginner_Guide.pdf"
backup_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture8_Beginner_Guide.pdf"

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_utils

render_utils.build_pdf(html_content, output_path, backup_path)

