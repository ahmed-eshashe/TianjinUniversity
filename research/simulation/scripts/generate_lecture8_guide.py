import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Continuous Q-Learning & Soft Actor-Critic: Definitive Guide to CS285 Lecture 8</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
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
    line-height: 1.56;
    font-size: 9.8pt;
  }

  .header-block {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 14px;
    margin-bottom: 18px;
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
    font-size: 10.2pt;
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
    font-size: 12.5pt;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    page-break-after: avoid;
  }

  h3 {
    color: #0f172a;
    font-size: 10.5pt;
    font-weight: 700;
    margin-top: 14px;
    margin-bottom: 5px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 8px 0;
    text-align: justify;
  }

  .callout {
    padding: 10px 14px;
    margin: 10px 0;
    border-radius: 6px;
    font-size: 9.3pt;
    page-break-inside: avoid;
  }
  .callout p { margin: 0; }
  .callout-title {
    font-weight: 700;
    font-size: 8.8pt;
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

  .code-container {
    background: #0f172a;
    color: #e2e8f0;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0;
    font-family: "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace;
    font-size: 8.4pt;
    line-height: 1.45;
    page-break-inside: avoid;
    overflow-x: auto;
  }
  .code-container pre { margin: 0; }
  .code-comment { color: #94a3b8; font-style: italic; }
  .code-keyword { color: #38bdf8; font-weight: bold; }
  .code-func { color: #a78bfa; }
  .code-string { color: #4ade80; }

  .algorithm-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #475569;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
    page-break-inside: avoid;
  }
  .algorithm-header {
    font-weight: 800;
    font-size: 9.5pt;
    color: #0f172a;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 6px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .formula {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 10px 0;
    text-align: center;
    font-size: 10.5pt;
    color: #0f172a;
    page-break-inside: avoid;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 8.8pt;
    page-break-inside: avoid;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 7px 9px;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 6px 9px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #f8fafc; }

  .diagram-container {
    text-align: center;
    margin: 12px 0;
    page-break-inside: avoid;
  }

  .quiz-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 12px 0;
    page-break-inside: avoid;
  }
  .quiz-q { font-weight: 700; color: #0f172a; margin-bottom: 5px; }
  .quiz-a { color: #334155; font-size: 9pt; margin-top: 4px; border-top: 1px dashed #cbd5e1; padding-top: 4px; }

  .page-break { page-break-before: always; }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 8 Masterclass Study Guide</span>
  <h1>Mastering Continuous Q-Learning &amp; Soft Actor-Critic</h1>
  <div class="subtitle">Complete Mathematical &amp; Algorithmic Foundations: Target Networks, Polyak Averaging, Jensen's Overestimation Bias Proof, Clipped Twin-Q, Maximum Entropy RL Derivation, Dueling Architectures, and Production SAC</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Curriculum:</b> Berkeley CS285 + Haarnoja &amp; Levine (SAC) + Achiam (Spinning Up)</span>
    <span><b>Scope:</b> General Continuous Off-Policy Control &amp; Robotics Slicing</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The Executive Mental Map: Why Does Lecture 8 Exist?</h2>
<p>
  In Lecture 6, we studied on-policy Actor-Critic methods (like A2C and PPO). On-policy algorithms collect a batch of data, execute gradient updates, and <b>immediately discard the entire dataset</b>.
</p>
<p>
  <b>The Sample Inefficiency Dilemma:</b> Discarding data is acceptable in GPU simulators where data is virtually free. But on a physical robot or in expensive high-fidelity finite-element simulations, throwing away transitions $(s, a, r, s')$ after one glance is unacceptable. We need <b>Off-Policy algorithms</b> that store millions of historical interactions in an <b>Experience Replay Buffer</b> and reuse them thousands of times.
</p>
<p>
  <b>Lecture 8 solves the off-policy puzzle for continuous control:</b> We examine why naive deep Q-learning explodes, how Target Networks and Double Q-learning stabilize optimization, and how <b>Soft Actor-Critic (SAC)</b> blends Q-learning with Maximum Entropy to create the gold-standard off-policy robotics algorithm.
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 8 -->
<div class="diagram-container">
<svg width="690" height="90" viewBox="0 0 690 90">
  <rect x="5" y="10" width="128" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="69" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. Target Networks</text>
  <text x="69" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Polyak Averaging</text>
  <text x="69" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Freezing Moving Targets</text>

  <rect x="141" y="10" width="128" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="205" y="36" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">2. Overestimation</text>
  <text x="205" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Jensen's Inequality</text>
  <text x="205" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Clipped Twin-Q Solution</text>

  <rect x="277" y="10" width="128" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="341" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">3. Continuous Max</text>
  <text x="341" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Intractable argmax_a</text>
  <text x="341" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Actor Maximizer (DDPG/SAC)</text>

  <rect x="413" y="10" width="128" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="477" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">4. Max Entropy RL</text>
  <text x="477" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Reward + α H(π)</text>
  <text x="477" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Anti-Freezing Exploration</text>

  <rect x="549" y="10" width="136" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="617" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">5. The Deadly Triad</text>
  <text x="617" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Bootstrapping +</text>
  <text x="617" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Buffer + Function Approx</text>
</svg>
</div>

<div class="page-break"></div>

<!-- PART 1 -->
<h2>Part 1: Stabilizing Q-Learning — Target Networks &amp; Polyak Averaging</h2>
<p>
  <b>(Slides 1–25)</b> In exact tabular Q-learning, the Bellman optimality update is mathematically guaranteed to converge. But when we replace the table with a Deep Neural Network $Q_\theta(s, a)$, training frequently explodes. Why?
</p>

<h3>1.1 The "Chasing Your Own Tail" Problem</h3>
<div class="formula">
  $$\mathcal{L}(\theta) = \mathbb{E}_{(s, a, r, s') \sim \mathcal{D}} \left[ \left( Q_\theta(s, a) - \left[ r + \gamma \max_{a'} Q_\theta(s', a') \right] \right)^2 \right]$$
</div>
<p>
  Notice that network parameters $\theta$ appear in <b>both</b> the prediction $Q_\theta(s, a)$ and the target $r + \gamma \max_{a'} Q_\theta(s', a')$. Every gradient step taken to update the prediction simultaneously shifts the target itself!
  To break this destabilizing feedback loop, we maintain a secondary set of weights $\bar{\theta}$ called the <b>Target Network</b>:
  $$y_t = r_t + \gamma \max_{a'} Q_{\bar{\theta}}(s_{t+1}, a')$$
</p>

<!-- SVG Diagram: Polyak Averaging -->
<div class="diagram-container">
<svg width="680" height="120" viewBox="0 0 680 120">
  <rect x="50" y="15" width="220" height="65" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="160" y="38" font-size="10.5" font-weight="700" fill="#1e40af" text-anchor="middle">Online Critic Q_θ(s, a)</text>
  <text x="160" y="54" font-size="8.2" fill="#3b82f6" text-anchor="middle">Updated via SGD at every step</text>
  <text x="160" y="68" font-size="8.2" fill="#475569" text-anchor="middle">Fast-moving parameter set</text>

  <path d="M 280 48 L 400 48" stroke="#10b981" stroke-width="2.5"/>
  <text x="340" y="38" font-size="9" font-weight="700" fill="#047857" text-anchor="middle">Polyak Averaging (τ = 0.005)</text>
  <text x="340" y="68" font-size="8" fill="#64748b" text-anchor="middle">θ̄ ‹- τ θ + (1 - τ) θ̄</text>

  <rect x="410" y="15" width="220" height="65" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="520" y="38" font-size="10.5" font-weight="700" fill="#065f46" text-anchor="middle">Target Critic Q_θ̄(s, a)</text>
  <text x="520" y="54" font-size="8.2" fill="#047857" text-anchor="middle">Slowly tracks online network</text>
  <text x="520" y="68" font-size="8.2" fill="#475569" text-anchor="middle">Generates stable Bellman targets</text>
</svg>
</div>

<h3>1.2 Polyak Soft Updates vs. Hard Periodic Copies</h3>
<p>
  Instead of hard-copying weights every 10,000 steps (as in original Atari DQN), continuous control algorithms smoothly blend target weights after every training step:
  $$\bar{\theta} \leftarrow \tau \theta + (1 - \tau) \bar{\theta} \qquad (\text{with } \tau = 0.005)$$
  This corresponds to an exponential decay half-life of:
  $$t_{\text{half}} = \frac{\ln(2)}{\tau} = \frac{0.693}{0.005} \approx 138 \text{ gradient steps}$$
  This prevents abrupt target discontinuities, ensuring smooth impedance gain transitions on physical robotic hardware.
</p>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: Overestimation Bias &amp; Clipped Double Q-Learning</h2>
<p>
  <b>(Slides 26–42)</b> A profound mathematical flaw exists in standard Q-learning: <b>the maximization step systematically overestimates value functions!</b>
</p>

<h3>2.1 Mathematical Origin of Overestimation (Jensen's Inequality)</h3>
<div class="math-box">
  <div class="callout-title">Theorem: Maximization Over Random Variables Induces Positive Bias</div>
  <p>
    Let $X_1, X_2, \dots, X_m$ be independent random variables representing noisy value estimates of true values $\mu_1, \dots, \mu_m$, where $X_i = \mu_i + \epsilon_i$ with zero-mean noise $\mathbb{E}[\epsilon_i] = 0$.
    Because the maximum function $f(x) = \max_i x_i$ is strictly convex, by <b>Jensen's Inequality</b>:
    $$\mathbb{E}\left[ \max_i X_i \right] \ge \max_i \mathbb{E}[X_i] = \max_i \mu_i$$
  </p>
</div>

<p>
  <b>Numerical Demonstration:</b> Suppose two actions have identical true value $Q(s, a_1) = Q(s, a_2) = 0$. Due to function approximation error, the neural network predicts noisy estimates $X_1 \sim \mathcal{N}(0, 1)$ and $X_2 \sim \mathcal{N}(0, 1)$.
  $$\mathbb{E}[\max(X_1, X_2)] = \frac{1}{\sqrt{\pi}} \approx +0.564 > 0$$
  Every single Bellman update injects positive error $+0.564$. Bootstrapping propagates this error forward exponentially:
  $V(s) \to V(s) + \gamma \Delta + \gamma^2 \Delta + \dots \implies$ Q-values explode to $+10,000$, destroying policy gradients!
</p>

<h3>2.2 The Clipped Twin-Q Solution (Fujimoto et al., 2018 / Haarnoja et al., SAC)</h3>
<p>
  To solve overestimation, maintain <b>two completely independent Critic networks</b> ($Q_{\phi_1}$ and $Q_{\phi_2}$) with separate initializations. When computing the Bellman target, evaluate both and take the <b>minimum</b>:
</p>

<div class="formula" style="border: 2px solid #2563eb; background: #eff6ff;">
  $$y_t = r_t + \gamma \min \Big( Q_{\bar{\phi}_1}(s_{t+1}, \tilde{a}_{t+1}),\, Q_{\bar{\phi}_2}(s_{t+1}, \tilde{a}_{t+1}) \Big)$$
</div>
<p>
  Taking the minimum injects controlled pessimism, completely neutralizing overestimation bias without requiring slow optimization.
</p>

<div class="page-break"></div>

<!-- PART 3 -->
<h2>Part 3: Continuous Actions &amp; The Intractable Max</h2>
<p>
  <b>(Slides 43–58)</b> In discrete environments (Atari), finding $\max_a Q(s, a)$ requires evaluating the network across 4 actions. In continuous robotics with $a \in \mathbb{R}^6$ (joint torques), finding the continuous global maximum is a non-convex optimization problem that cannot be solved in real-time.
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
      <td>Constrain $Q(s, a)$ to be quadratic in $a$: $Q(s,a) = V(s) - \frac{1}{2}(a - \mu)^T P (a - \mu)$.</td>
      <td>Maximum is analytically $\mu(s)$, but restricts the Critic to simple parabolic shapes; cannot capture contact bifurcations.</td>
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
  <b>(Slides 59–75 &amp; Spinning Up ch19)</b> Soft Actor-Critic modifies the standard objective to maximize both <b>expected reward</b> AND <b>policy entropy $\mathcal{H}(\pi)$</b>:
</p>

<div class="formula" style="border: 2px solid #c084fc; background: #fdf4ff;">
  $$J(\pi) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t) \sim \rho_\pi} \left[ r(s_t, a_t) + \alpha \, \mathcal{H}\big(\pi(\cdot \mid s_t)\big) \right]$$
</div>

<h3>4.1 The "Anti-Freezing" Phenomenon in Soft Tissue Manipulation</h3>
<p>
  Touching delicate biological tissue risks incurring severe negative penalties for crushing or excessive force ($F_z > 8\text{ N}$). Under standard RL, the policy frequently gets trapped in a local minimum where the blade <b>hovers stationary 1 mm above the tissue</b> to collect zero penalties.
  <br><b>Under Maximum Entropy SAC:</b> A frozen stationary blade has zero entropy ($\mathcal{H} = 0$), which incurs a massive entropy penalty! The robot is compelled to keep vibrating and testing sawing actions, discovering that light lateral sawing punctures the skin cleanly without crushing.
</p>

<h3>4.2 Automatic Entropy Temperature Tuning ($\alpha$)</h3>
<p>
  Rather than keeping temperature $\alpha$ fixed, SAC formulates temperature optimization as a dual constrained optimization problem targeting a heuristic $\bar{\mathcal{H}} = -\dim(\mathcal{A})$:
</p>
<div class="formula">
  $$\mathcal{L}(\alpha) = \mathbb{E}_{a \sim \pi} \left[ -\alpha \big( \log \pi(a \mid s) + \bar{\mathcal{H}} \big) \right]$$
</div>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Sutton's Deadly Triad &amp; Production SAC Implementation</h2>
<p>
  <b>(Slides 76–88)</b> Richard Sutton proved that divergence in reinforcement learning arises whenever three algorithmic elements are combined simultaneously:
</p>
<ol>
  <li><b>Function Approximation:</b> Deep Neural Networks estimating continuous value landscapes.</li>
  <li><b>Bootstrapping:</b> Updating value estimates based on other value estimates: $y = r + \gamma Q(s', a')$.</li>
  <li><b>Off-Policy Learning:</b> Training on historical replay buffer data $\mathcal{D}$ generated by older policies.</li>
</ol>
<p>
  <i>SAC survives the Deadly Triad through four anchors: 1) Target networks, 2) Clipped Twin-Q pessimism, 3) Polyak averaging, and 4) Entropy regularization.</i>
</p>

<div class="code-container">
<pre><span class="code-keyword">import</span> torch
<span class="code-keyword">import</span> torch.nn <span class="code-keyword">as</span> nn
<span class="code-keyword">import</span> torch.nn.functional <span class="code-keyword">as</span> F

<span class="code-keyword">def</span> <span class="code-func">compute_sac_losses</span>(actor, q1, q2, target_q1, target_q2, log_alpha, batch, gamma=0.99):
    states, actions, rewards, next_states, dones = batch
    alpha = log_alpha.exp()

    <span class="code-comment"># 1. CRITIC LOSS: Bellman Target using Target Twin-Q</span>
    <span class="code-keyword">with</span> torch.no_grad():
        next_actions, next_log_pi = actor.sample(next_states)
        q1_target = target_q1(next_states, next_actions)
        q2_target = target_q2(next_states, next_actions)
        min_next_q = torch.min(q1_target, q2_target) - alpha * next_log_pi
        y = rewards + gamma * (1.0 - dones) * min_next_q

    q1_loss = F.mse_loss(q1(states, actions), y)
    q2_loss = F.mse_loss(q2(states, actions), y)
    critic_loss = q1_loss + q2_loss

    <span class="code-comment"># 2. ACTOR LOSS: Reparameterized Gradient</span>
    new_actions, log_pi = actor.sample(states)
    min_q = torch.min(q1(states, new_actions), q2(states, new_actions))
    actor_loss = (alpha.detach() * log_pi - min_q).mean()

    <span class="code-comment"># 3. TEMPERATURE LOSS: Target entropy heuristic -dim(A)</span>
    target_entropy = -float(actions.shape[-1])
    alpha_loss = -(log_alpha * (log_pi + target_entropy).detach()).mean()

    <span class="code-keyword">return</span> critic_loss, actor_loss, alpha_loss
</pre>
</div>

<div class="page-break"></div>

<!-- PART 6 -->
<h2>Part 6: Interactive Tablet Self-Test Quiz</h2>

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

<!-- PART 7: THESIS DEFENSE MASTER CHEATSHEET -->
<h2>Part 7: Thesis Defense Master Cheatsheet (Lecture 8 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Q1: "Why does standard Deep Q-Networks (DQN) fail in continuous robotic manipulation?"</div>
  <p>
    <b>Answer:</b> "DQN selects actions via $\arg\max_a Q(s, a)$. In discrete games with 4 buttons, this requires 4 forward evaluations. In continuous multi-joint manipulation where the action space is $\mathbb{R}^6$ or $\mathbb{R}^{14}$, finding the continuous global maximum of an arbitrary neural network is an intractable non-convex optimization problem that cannot be solved within our 60 Hz control loop. Algorithms like DDPG and SAC solve this by training a dedicated Actor network to approximate the maximizer directly."
  </p>
</div>

<div class="callout robotics">
  <div class="callout-title">Q2: "Why is Soft Actor-Critic (SAC) considered the gold standard for sample-efficient real-world robot learning?"</div>
  <p>
    <b>Answer:</b> "SAC is an off-policy algorithm that reuses historical interactions from an experience replay buffer, requiring orders of magnitude fewer physical environment samples than on-policy PPO. By integrating Maximum Entropy RL with Clipped Twin-Q targets and soft Polyak averaging, SAC maintains active exploration, avoids premature policy freezing, and guarantees robust convergence in contact-rich physical tasks."
  </p>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    pdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture8_Beginner_Guide.pdf"
    backup_path = "/home/omen/Downloads/CS285_Lecture8_Beginner_Guide.pdf"
    render_utils.build_pdf(html_content, pdf_path, backup_path)
