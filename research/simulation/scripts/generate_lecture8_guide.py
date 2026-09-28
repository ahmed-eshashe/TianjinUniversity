import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 8: Zero-to-Hero Guide to Continuous Q-Learning & Soft Actor-Critic (SAC)</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 8 • Zero-to-Hero Guide to Continuous Control & SAC";
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
    font-size: 9.6pt;
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
    font-size: 19pt;
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
    margin-top: 18px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    page-break-after: avoid;
  }

  h3 {
    color: #0f172a;
    font-size: 10.2pt;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 4px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 8px 0;
    text-align: justify;
  }

  ul, ol {
    margin: 0 0 8px 0;
    padding-left: 18px;
  }
  li {
    margin-bottom: 3px;
  }

  .callout {
    padding: 10px 14px;
    margin: 10px 0;
    border-radius: 6px;
    font-size: 9.2pt;
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

  .code-box {
    background: #f1f5f9;
    border-left: 4px solid #64748b;
    color: #1e293b;
    font-family: "SFMono-Regular", Consolas, Menlo, monospace;
    font-size: 8pt;
    page-break-inside: avoid;
  }
  .code-box .callout-title { color: #475569; }

  .formula {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 12px;
    margin: 8px 0;
    text-align: center;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 10pt;
    color: #0f172a;
    page-break-inside: avoid;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 8.6pt;
    page-break-inside: avoid;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 5px 8px;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 5px 8px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }
  tr:nth-child(even) td { background: #f8fafc; }

  .diagram-container {
    text-align: center;
    margin: 10px 0;
    page-break-inside: avoid;
  }

  .page-break {
    page-break-before: always;
  }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">CS285 Lecture 8 • Zero-to-Hero Field Manual</span>
  <h1>Continuous Q-Learning &amp; Soft Actor-Critic (SAC)</h1>
  <div class="subtitle">From Scratch to Mastery: Conquering Continuous Robot Action Spaces, Overcoming the Deadly Triad, and Unleashing Entropy-Driven Curiosity</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Focus:</b> Continuous $\max Q$, Clipped Double-Q, Target Networks, &amp; MaxEnt RL</span>
  </div>
</div>

<!-- SECTION 1: THE CONTINUOUS ACTION TRAP -->
<h2>1. Why Classic Q-Learning Fails on Robots (The Menu vs The Beach)</h2>
<p>
  In 2015, DeepMind shocked the world with <b>DQN</b> (Deep Q-Networks), beating humans at Atari 2600 video games. 
  Naturally, roboticists rushed to use DQN on robotic arms. <b>It failed completely.</b> Why?
</p>

<div class="callout intuition">
  <div class="callout-title">🏖️ The Restaurant Menu vs The Infinite Beach Analogy</div>
  <p>
    In Q-learning, the optimal decision rule is: <b>$a^* = \arg\max_{a} Q(s, a)$</b>.
  </p>
  <ul>
    <li><b>In Atari Games (The Restaurant Menu):</b> There are only 4 controller buttons (Up, Down, Left, Right). Finding the $\max$ is like picking dinner from a 4-item menu. You evaluate all 4, find that Pizza has score $9.5$, and order Pizza. Easy!</li>
    <li><b>On a Robotic Arm (The Infinite Beach):</b> Actions are continuous 6-dimensional vectors of real numbers (e.g. torques $\in [-10.0, +10.0]$ Nm). 
      Finding the highest $Q$-value is like being dropped on an infinitely large, foggy beach with rolling sand dunes, and being told to find the single highest grain of sand in under <b>1 millisecond</b>! 
      You cannot check infinite grains of sand in real time!
    </li>
  </ul>
  <p>
    <b>The Modern Fix (Actor Maximizer):</b> Instead of searching for the highest grain of sand by brute force, train a dedicated <b>Actor network $\pi_\theta(s)$</b> that acts as a compass, outputting the exact coordinates of the highest peak!
  </p>
</div>

<!-- DIAGRAM 1: DISCRETE MENU VS CONTINUOUS Q SURFACE -->
<div class="diagram-container">
<svg width="600" height="95" viewBox="0 0 600 95">
  <!-- Left: Discrete Selection -->
  <rect x="30" y="15" width="220" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="140" y="32" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">ATARI: 4 DISCRETE CHOICES</text>
  <text x="60" y="55" font-size="8" fill="#475569">Up: 4.2</text>
  <text x="120" y="55" font-size="8" fill="#475569">Down: 2.1</text>
  <text x="175" y="55" font-size="8.5" font-weight="700" fill="#10b981">Right: 9.8 (MAX!)</text>
  <text x="140" y="75" font-size="7.5" fill="#64748b" text-anchor="middle">Simple <code>torch.argmax()</code> across 4 numbers</text>

  <!-- Arrow -->
  <text x="280" y="52" font-size="12" font-weight="700" fill="#64748b" text-anchor="middle">vs.</text>

  <!-- Right: Continuous Landscape -->
  <rect x="310" y="15" width="260" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="440" y="32" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">ROBOT: INFINITE CONTINUOUS SURFACE</text>
  <path d="M 330,65 Q 370,35 410,50 Q 450,25 480,45 Q 520,70 550,55" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <circle cx="450" cy="25" r="4" fill="#ef4444"/>
  <text x="450" y="20" font-size="7.5" font-weight="700" fill="#b91c1c" text-anchor="middle">True Peak $a^*$</text>
  <text x="440" y="78" font-size="7.5" fill="#78350f" text-anchor="middle">Actor network $\pi_\theta(s)$ climbs directly to the peak!</text>
</svg>
</div>

<!-- SECTION 2: MAXIMUM ENTROPY RL -->
<h2>2. Soft Actor-Critic (SAC) &amp; Maximum Entropy Exploration</h2>
<div class="callout intuition">
  <div class="callout-title">🥐 The Curious Tourist in Paris Analogy</div>
  <p>
    Imagine you visit Paris for two weeks:
  </p>
  <ul>
    <li><b>Standard RL (Reward Only):</b> On your first morning, you find a bakery with decent croissants (Reward $= +5$). You decide this is safe and eat croissants at this exact bakery every single morning for 14 days. You never try baguettes, macarons, or escargot. You get stuck in a boring, mediocre routine.</li>
    <li><b>Maximum Entropy RL (Reward + Entropy):</b> We pay you a bonus for being <b>curious and unpredictable</b>! You get points for good food, PLUS extra points for trying new alleys and testing diverse bakeries.</li>
  </ul>
  <p>
    <b>Why this is mandatory for robot soft tomato slicing:</b> If a robot only cares about reward, it gets terrified of crushing penalties and freezes the blade 1 mm above the skin! 
    The <b>Entropy Bonus</b> pays the robot to keep trying different blade angles, sawing speeds, and contact compliance until it discovers clean puncture mechanics!
  </p>
</div>

<h3>2.1 The Soft Bellman Objective (Parameter Anatomy)</h3>
<div class="formula">
  $$J(\pi) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t)} \left[ r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot \mid s_t)) \right] \quad \text{where} \quad \mathcal{H}(\pi) = \mathbb{E}_{a \sim \pi}[-\log \pi(a \mid s_t)]$$
</div>

<!-- PARAMETER ANATOMY TABLE 1 -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Parameter</th>
      <th style="width: 20%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 15%;">Example Value</th>
      <th style="width: 15%;">Tuning Impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$r(s_t, a_t)$</b></td>
      <td>Physical Task Reward</td>
      <td>Points earned for cutting the tomato cleanly without crushing.</td>
      <td>$+3.5$ points</td>
      <td>Primary task objective.</td>
    </tr>
    <tr>
      <td><b>$\alpha$</b></td>
      <td>Entropy Temperature</td>
      <td><b>The Curiosity Dial:</b> How much does the robot prioritize exploration versus exploitation?</td>
      <td>$\alpha = 0.2$ (or auto-tuned)</td>
      <td>If $\alpha \to 0$, standard RL (freezes); if $\alpha \to \infty$, pure chaotic noise.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{H}(\pi)$</b></td>
      <td>Shannon Entropy</td>
      <td>A mathematical measure of how wide, random, and diverse the action distribution is.</td>
      <td>$1.5$ nats</td>
      <td>High entropy = wide exploration; Low entropy = laser focus.</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Soft RL Objective</div>
  <p>
    <b>"Do your job as best as possible (maximize reward), but keep your actions as random and diverse as possible (maximize entropy) so you never get stuck in a timid local rut!"</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: THE THREE SUPER-WEAPONS OF SAC -->
<h2>3. The Three Practical Super-Weapons of SAC</h2>
<p>
  Richard Sutton proved that combining <i>Function Approximation</i> + <i>Bootstrapping</i> + <i>Off-Policy Learning</i> creates the <b>Deadly Triad</b>, causing value functions to diverge to infinity. 
  SAC overcomes the Deadly Triad using three engineering breakthroughs:
</p>

<h3>3.1 Super-Weapon 1: Experience Replay (The Photo Album)</h3>
<p>
  Instead of discarding transitions immediately, SAC saves <b>1,000,000 past transitions</b> $(s_t, a_t, r_t, s_{t+1})$ into a circular buffer. 
  During training, it samples random mini-batches (e.g. 256 transitions). 
  This breaks temporal correlation: the network doesn't just learn from what happened 2 milliseconds ago; it remembers mistakes made 30 minutes ago!
</p>

<h3>3.2 Super-Weapon 2: Polyak Target Networks (The Patient Teacher)</h3>
<div class="callout intuition">
  <div class="callout-title">🎯 The Moving Target Analogy</div>
  <p>
    If you train a neural network using its own predictions as the target ($y = r + \gamma Q(s', a')$), the target shifts every single gradient update. 
    It is like trying to shoot a bullseye that vibrates frantically.
    <br><br>
    <b>The Polyak Fix:</b> Maintain a separate target network weights $\bar{\theta}$, updated ultra-slowly:
    <br>$$\bar{\theta} \leftarrow \tau \theta + (1 - \tau) \bar{\theta} \quad \text{with} \quad \tau = 0.005$$
    Every step, the target moves by only <b>0.5%</b>. The target moves like molasses ($t_{1/2} \approx 138$ steps), giving the network a crystal-clear, steady bullseye to aim at.
  </p>
</div>

<h3>3.3 Super-Weapon 3: Clipped Twin-Q (The Two Skeptical Judges)</h3>
<div class="formula">
  $$y = r(s, a) + \gamma \left( \min_{j=1,2} Q_{\bar{\theta}_j}(s', a') - \alpha \log \pi(a' \mid s') \right)$$
</div>

<!-- DIAGRAM 2: CLIPPED DOUBLE-Q MINIMUM -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <!-- Critic 1 -->
  <rect x="50" y="15" width="180" height="30" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="140" y="34" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">Critic 1: $Q_1(s', a') = \mathbf{28.0}$ (Delusional!)</text>

  <!-- Critic 2 -->
  <rect x="50" y="50" width="180" height="30" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="140" y="69" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">Critic 2: $Q_2(s', a') = \mathbf{22.0}$ (Realistic)</text>

  <!-- Arrow to Min -->
  <path d="M 230,47 L 310,47" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="310,47 302,42 302,52" fill="#2563eb"/>

  <!-- Min Box -->
  <rect x="320" y="25" width="240" height="45" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="440" y="44" font-size="9.5" font-weight="700" fill="#1e40af" text-anchor="middle">Clipped Target: $\min(28.0, 22.0) = \mathbf{22.0}$</text>
  <text x="440" y="60" font-size="8" fill="#1d4ed8" text-anchor="middle">Overestimation bias is instantly eliminated!</text>
</svg>
</div>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of Clipped Twin-Q</div>
  <p>
    <b>"Train two independent Critic networks. When computing future value, always pick the MORE PESSIMISTIC of the two. If one network hallucinates that a risky blade slam is worth 100 points, the second network grounds it back to reality!"</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 4: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>4. Concrete Numerical Walkthrough: One SAC Bellman Target Update</h2>
<p>
  Let's calculate the exact Bellman target for a transition sampled from the replay buffer:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 10%;">Step</th>
      <th style="width: 30%;">Variable / Expression</th>
      <th style="width: 20%;">Value</th>
      <th style="width: 40%;">Physical Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Sampled Reward $r$</td>
      <td><b>$+4.0$</b></td>
      <td>Blade penetrated 2 mm deeper into fruit.</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Discount Factor $\gamma$</td>
      <td><b>$0.99$</b></td>
      <td>Patience meter for future rewards.</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Entropy Temperature $\alpha$</td>
      <td><b>$0.2$</b></td>
      <td>Curiosity weighting factor.</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Critic 1 Target $Q_{\bar{\theta}_1}(s', a')$</td>
      <td><b>$32.5$</b></td>
      <td>First critic's future prediction.</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Critic 2 Target $Q_{\bar{\theta}_2}(s', a')$</td>
      <td><b>$28.0$</b></td>
      <td>Second critic's more conservative prediction.</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Next Action Log-Prob $\log \pi(a' \mid s')$</td>
      <td><b>$-1.5$</b></td>
      <td>Entropy bonus: $-\alpha \log \pi = -0.2(-1.5) = \mathbf{+0.3}$.</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Clipped Soft Target $y$</td>
      <td>$4.0 + 0.99(28.0 + 0.3) = \mathbf{32.017}$</td>
      <td>Target used to train Critic weights via MSE loss!</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 5: PYTORCH IMPLEMENTATION -->
<h2>5. PyTorch SAC Loss Implementation</h2>

<div class="callout code-box">
  <div class="callout-title">🐍 Complete PyTorch Soft Actor-Critic Loss Computation</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn

def compute_sac_losses(actor, critic1, critic2, target1, target2, batch, alpha=0.2, gamma=0.99):
    states, actions, rewards, next_states, dones = batch

    # 1. CRITIC LOSS: Compute Bellman Target using Target Twin-Q
    with torch.no_grad():
        next_actions, next_log_probs = actor.sample(next_states)
        q1_target = target1(next_states, next_actions)
        q2_target = target2(next_states, next_actions)
        # Take minimum across twin critics to stop overestimation
        min_q_target = torch.min(q1_target, q2_target) - alpha * next_log_probs
        y = rewards + gamma * min_q_target * (1.0 - dones)

    # Current Q-values
    q1_current = critic1(states, actions)
    q2_current = critic2(states, actions)
    critic_loss = 0.5 * (nn.functional.mse_loss(q1_current, y) + nn.functional.mse_loss(q2_current, y))

    # 2. ACTOR LOSS: Maximize expected Q + Entropy
    new_actions, log_probs = actor.sample(states)
    q_new = torch.min(critic1(states, new_actions), critic2(states, new_actions))
    actor_loss = (alpha * log_probs - q_new).mean()

    return critic_loss, actor_loss
</pre>
</div>

<!-- SECTION 6: PRACTITIONER'S CHECKLIST -->
<h2>6. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Failure Mode</th>
      <th style="width: 35%;">The Hidden Cause</th>
      <th style="width: 40%;">How to Fix It</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Target Update Too Fast</b></td>
      <td>Setting $\tau = 0.05$ instead of $0.005$ moves target networks 10x too quickly. Values diverge to $10^{6}$ within 20,000 steps.</td>
      <td>Keep $\tau \in [0.005, 0.01]$. In robotics, slower target updates always mean higher stability.</td>
    </tr>
    <tr>
      <td><b>2. Replay Buffer Starvation</b></td>
      <td>Starting gradient descent before the buffer has collected enough transitions causes the policy to overfit to the first 50 random steps.</td>
      <td>Collect at least <b>10,000 random exploration steps</b> before starting the first neural network update.</td>
    </tr>
    <tr>
      <td><b>3. Action Bounds Violation</b></td>
      <td>Continuous robotic motor torques must be strictly bounded to $[-1, +1]$. Forgetting <code>torch.tanh()</code> causes motor commands to spike to infinity.</td>
      <td>Always use <b>Tanh-squashed Gaussian distributions</b> with proper Jacobian log-prob correction.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>CS285 Lecture 8 Zero-to-Hero Guide • DEX-ROB Lab (Tianjin University) • Prof. Shan An</i>
</div>

</body>
</html>
"""

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Lecture8_Beginner_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture8_Beginner_Guide.pdf"

render_utils.build_pdf(html_content, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
