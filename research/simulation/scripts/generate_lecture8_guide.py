import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 8: Zero-to-Hero Guide to Continuous Q-Learning, TD3, &amp; Soft Actor-Critic (SAC)</title>
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
    line-height: 1.54;
    font-size: 9.4pt;
  }

  .header-block {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 12px;
    margin-bottom: 16px;
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
    font-size: 18.5pt;
    font-weight: 800;
    margin: 0 0 6px 0;
    line-height: 1.25;
  }
  .subtitle {
    color: #475569;
    font-size: 10pt;
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
    font-size: 12pt;
    font-weight: 700;
    margin-top: 16px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    page-break-after: avoid;
  }

  h3 {
    color: #0f172a;
    font-size: 10pt;
    font-weight: 700;
    margin-top: 11px;
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
    padding: 9px 13px;
    margin: 9px 0;
    border-radius: 6px;
    font-size: 9.1pt;
    /* avoid */
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
    font-size: 7.9pt;
    /* avoid */
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
    font-size: 9.8pt;
    color: #0f172a;
    /* avoid */
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 9px 0;
    font-size: 8.5pt;
    /* avoid */
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
    margin: 9px 0;
    /* avoid */
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
  <h1>Continuous Q-Learning, TD3, &amp; Soft Actor-Critic (SAC)</h1>
  <div class="subtitle">From Scratch to Mastery: Conquering Continuous Robot Action Spaces, Overcoming the Deadly Triad, and Unleashing Entropy-Driven Curiosity</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Scope:</b> Continuous $\max Q$, Clipped Double-Q, Target Networks, Reparameterization, &amp; MaxEnt RL</span>
  </div>
</div>

<!-- SECTION 1: THE CONTINUOUS ACTION TRAP -->
<h2>1. Why Classic Q-Learning Fails on Physical Robots</h2>
<p>
  In 2015, DeepMind’s <b>Deep Q-Networks (DQN)</b> astonished computer science by learning to play 49 Atari 2600 video games directly from raw pixels, achieving superhuman performance on games like <i>Breakout</i>, <i>Pong</i>, and <i>Space Invaders</i>. 
  Naturally, robotics researchers immediately attempted to apply DQN directly to physical robotic arms, quadrupeds, and autonomous vehicles. 
  <b>Every single attempt failed catastrophically.</b>
</p>
<p>
  To understand why DQN conquered Atari but failed on physical hardware, we must examine the single mathematical operation at the absolute core of Q-learning:
</p>

<div class="formula">
  $$a^*(s) = \arg\max_{a \in \mathcal{A}} Q(s, a) \qquad \text{and} \qquad y = r(s, a) + \gamma \max_{a' \in \mathcal{A}} Q(s', a')$$
</div>

<div class="callout intuition">
  <div class="callout-title">🏖️ Everyday Analogy: The Restaurant Menu vs The Foggy Mountain Beach</div>
  <p>
    Think of the difference between discrete action spaces and continuous action spaces:
  </p>
  <ul>
    <li><b>Atari Video Game (The 4-Item Menu):</b> At any moment in <i>Pong</i>, you can only press 4 buttons: <code>[UP, DOWN, LEFT, RIGHT]</code>. 
      Evaluating $\max_a Q(s, a)$ is identical to reading a 4-item dinner menu. The neural network computes 4 scalar numbers: $[2.1, 4.5, 9.8, 1.2]$. 
      Your computer runs a trivial <code>torch.argmax()</code> in 0.0001 milliseconds and picks button 3.
    </li>
    <li><b>Robotic Arm / Dual-Arm Manipulation (The Foggy Mountain Beach):</b> In our dual-arm slicing robot, an action is not a button click. 
      It is a continuous 14-dimensional vector of real numbers specifying target joint motor torques:
      $$\mathbf{a} = [\tau_1, \tau_2, \dots, \tau_{14}] \in [-10.0, +10.0]^{14} \text{ Nm}$$
      There are no 4 choices. There are <b>uncountably infinite choices</b>!
      Evaluating $\max_a Q(s, a)$ is like being dropped blindfolded onto a massive, foggy mountain beach with endless rolling sand dunes, and being commanded to find the <i>single highest grain of sand</i> across the entire mountain range in under <b>1 millisecond</b>.
    </li>
  </ul>
</div>

<!-- DIAGRAM 1: DISCRETE MENU VS CONTINUOUS Q SURFACE -->
<div class="diagram-container">
<svg width="620" height="95" viewBox="0 0 620 95">
  <!-- Left: Discrete Selection -->
  <rect x="20" y="12" width="250" height="72" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="145" y="30" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">ATARI: 4 DISCRETE CHOICES</text>
  <text x="50" y="52" font-size="8.5" fill="#475569">Up: 4.2</text>
  <text x="105" y="52" font-size="8.5" fill="#475569">Down: 2.1</text>
  <text x="165" y="52" font-size="9" font-weight="700" fill="#10b981">Right: 9.8 (MAX!)</text>
  <text x="145" y="74" font-size="7.5" fill="#64748b" text-anchor="middle">Instantaneous <code>torch.argmax()</code> over 4 scalars</text>

  <!-- Arrow -->
  <text x="295" y="52" font-size="12" font-weight="700" fill="#64748b" text-anchor="middle">vs.</text>

  <!-- Right: Continuous Landscape -->
  <rect x="320" y="12" width="280" height="72" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="460" y="30" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">PHYSICAL ROBOT: 14-DoF CONTINUOUS SURFACE</text>
  <path d="M 340,65 Q 380,35 420,52 Q 460,25 490,48 Q 540,70 580,55" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <circle cx="460" cy="25" r="4.5" fill="#ef4444"/>
  <text x="460" y="19" font-size="7.5" font-weight="700" fill="#b91c1c" text-anchor="middle">Optimal Continuous Peak $a^*$</text>
  <text x="460" y="76" font-size="7.5" fill="#78350f" text-anchor="middle">An Actor network $\pi_\theta(s)$ is trained to climb directly to the peak!</text>
</svg>
</div>

<h3>1.1 Why Can't We Just Discretize the Robot's Actions?</h3>
<p>
  A naive engineer might say: <i>"Why not discretize each motor into 10 bins (e.g. -10, -8, -6, ..., +8, +10 Nm) and use standard DQN?"</i><br>
  Let's do the simple combinatorics. If a robot has $d$ joints and we divide each joint into $K$ bins, the total discrete action space size is:
</p>
<div class="formula">
  $$|\mathcal{A}_{\text{discrete}}| = K^d$$
</div>
<ul>
  <li><b>1 Joint ($d=1, K=10$):</b> $10^1 = 10$ choices. (Trivial).</li>
  <li><b>7-DoF Single Arm ($d=7, K=10$):</b> $10^7 = 10,000,000$ choices. To pick one action, DQN must run 10 million forward passes through the Q-network every 10 milliseconds. Impossible!</li>
  <li><b>14-DoF Dual-Arm Slicing System ($d=14, K=10$):</b> $10^{14} = \mathbf{100,000,000,000,000}$ choices (100 trillion discrete actions). Running $\arg\max$ across 100 trillion options would take a supercomputer several weeks for a single robot time-step!</li>
</ul>
<p>
  Furthermore, coarse discretization destroys dexterous robotic skills: if a knife needs exactly $3.45$ Nm of downward force to break a grape skin without crushing the pulp, a discretized choice between $2.0$ Nm (fails to puncture) and $5.0$ Nm (crushes into soup) means the robot can <i>never</i> perform the task successfully.
</p>



<!-- SECTION 2: THE ACTOR-MAXIMIZER EVOLUTION -->
<h2>2. The Actor-Maximizer Solution: The Evolution to Soft Actor-Critic</h2>
<p>
  To solve the continuous $\arg\max$ crisis without combinatorial explosion, the RL community developed the <b>Actor-Critic paradigm for continuous value learning</b> across three landmark algorithmic generations:
</p>

<!-- EVOLUTION TIMELINE TABLE -->
<table>
  <thead>
    <tr>
      <th style="width: 14%;">Algorithm</th>
      <th style="width: 16%;">Authors &amp; Year</th>
      <th style="width: 32%;">Core Breakthrough Mechanism</th>
      <th style="width: 38%;">Fatal Limitation / Why It Was Replaced</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>DDPG</b></td>
      <td>Lillicrap et al. (DeepMind, 2015)</td>
      <td><b>Deterministic Policy Gradient:</b> Trains a neural network Actor $\mu_\theta(s)$ to directly output the continuous action that maximizes the Critic $Q_\phi(s, a)$. Uses chain rule: $\nabla_\theta Q(s, \mu_\theta(s)) = \nabla_a Q \nabla_\theta \mu$.</td>
      <td><b>Severe Overestimation Bias &amp; Hyperparameter Fragility:</b> The Critic severely overestimates Q-values. If Q overestimates, the Actor chases hallucinated spikes and gets trapped in catastrophic policy collapse.</td>
    </tr>
    <tr>
      <td><b>TD3</b> (Twin Delayed DDPG)</td>
      <td>Fujimoto et al. (McGill, 2018)</td>
      <td><b>Clipped Double-Q &amp; Delayed Updates:</b> Trains two independent critics ($Q_1, Q_2$), takes their minimum for Bellman targets, delays policy updates, and adds target noise.</td>
      <td><b>Deterministic Policy Fragility:</b> While stable, TD3 is a deterministic policy with additive Gaussian exploration noise ($\epsilon \sim \mathcal{N}(0, \sigma)$). It cannot learn multi-modal policies and easily gets stuck in sub-optimal local minima.</td>
    </tr>
    <tr>
      <td><b>SAC</b> (Soft Actor-Critic)</td>
      <td>Haarnoja et al. (UC Berkeley, 2018)</td>
      <td><b>Maximum Entropy RL + Twin Critics:</b> Optimizes expected reward PLUS action entropy $\mathcal{H}(\pi)$. Uses the Reparameterization Trick and automatic temperature tuning.</td>
      <td><b>The Gold Standard of Continuous Robotics:</b> Unmatched sample efficiency, extreme robustness to hyperparameter changes, and continuous exploratory curiosity.</td>
    </tr>
  </tbody>
</table>

<h3>2.1 The Deterministic Policy Gradient (Chain Rule Parameter Anatomy)</h3>
<p>
  How does the Actor actually maximize the Critic without an exhaustive search? In DDPG and TD3, we update the Actor parameters $\theta$ using the chain rule:
</p>
<div class="formula">
  $$\nabla_\theta J(\theta) = \mathbb{E}_{s \sim \mathcal{D}} \left[ \nabla_a Q_\phi(s, a) \Big|_{a = \mu_\theta(s)} \cdot \nabla_\theta \mu_\theta(s) \right]$$
</div>

<table>
  <thead>
    <tr>
      <th style="width: 22%;">Mathematical Term</th>
      <th style="width: 20%;">Formal Identity</th>
      <th style="width: 38%;">Physical &amp; Intuitive Meaning</th>
      <th style="width: 20%;">Tensor Shape</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\nabla_a Q_\phi(s, a)\big|_{a=\mu_\theta(s)}$</b></td>
      <td>Critic Action Gradient</td>
      <td><b>The Critic's Uphill Compass:</b> Tells the robot: <i>"If you increase joint 3 torque by $+0.1$ Nm, your Q-value will rise by $+4.2$ points."</i> The slope of the Q-surface with respect to motor torques.</td>
      <td><code>[Batch, Act_Dim]</code> (e.g. $[256, 14]$)</td>
    </tr>
    <tr>
      <td><b>$\nabla_\theta \mu_\theta(s)$</b></td>
      <td>Actor Parameter Jacobian</td>
      <td><b>The Motor Control Levers:</b> Tells the robot how its internal neural network weights $\theta$ must shift in order to change the output motor torque in that requested uphill direction.</td>
      <td><code>[Batch, Act_Dim, Num_Weights]</code></td>
    </tr>
    <tr>
      <td><b>$\nabla_\theta J(\theta)$</b></td>
      <td>Policy Gradient Vector</td>
      <td>The combined gradient vector that nudges the actor's weights so that its next predicted actions slide directly uphill toward the peak of the critic's Q-landscape!</td>
      <td><code>[Num_Weights]</code></td>
    </tr>
  </tbody>
</table>

<div class="callout intuition">
  <div class="callout-title">🏔️ The Mountain Climber Analogy (Critic as Topographer, Actor as Climber)</div>
  <p>
    The Critic is an expert topographer looking down on the fog-covered mountain range, mapping where the high-altitude peaks and treacherous ravines lie. 
    The Actor is a hiker standing on the mountain slope. 
    Every time step, the Critic radios the hiker: <i>"Take two steps Northeast—that is the steepest uphill route!"</i> 
    The hiker takes two steps Northeast. No random guessing or exhaustive search is required; the hiker follows the gradient directly uphill!
  </p>
</div>



<!-- SECTION 3: 4 DIVERSE REAL-WORLD CASE STUDIES -->
<h2>3. Four Real-World Industrial Case Studies: Continuous Action Spaces</h2>
<p>
  Continuous control is not merely a theoretical construct; it is the universal language of physical robotics, aerospace, and real-world industrial infrastructure:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Application Domain</th>
      <th style="width: 22%;">Continuous Action Vector $\mathbf{a}$</th>
      <th style="width: 28%;">Continuous State Vector $\mathbf{s}$</th>
      <th style="width: 30%;">Why Discretization Fails Completely</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Dual-Arm Fruit Slicing</b> (Robotics Thesis)</td>
      <td>$14$ continuous joint motor torques: $\tau \in [-15.0, +15.0]$ Nm (7-DoF left arm holding fork + 7-DoF right arm holding knife).</td>
      <td>$28$ joint positions &amp; velocities $+ 12$ 6-axis F/T wrench signals $+ 3$ knife tip coordinates $+ 1$ pulp deformation scalar.</td>
      <td>If downward knife force discretizes to $[0, 5, 10]$ N, slicing a soft strawberry ($F_{\text{puncture}} \approx 2.3$ N) either skims the surface or pulverizes it into juice. Exact continuous compliance is mandatory.</td>
    </tr>
    <tr>
      <td><b>2. Autonomous Highway Merging</b> (Self-Driving Vehicles)</td>
      <td>$2$ continuous controls: Steering wheel angle $\delta \in [-30^\circ, +30^\circ]$ and brake/throttle pressure $u \in [-1.0, +1.0]$.</td>
      <td>$64$-dim vector: Ego vehicle velocity, acceleration, lane offset, plus relative $(x, y, v_x, v_y)$ of the 10 nearest highway vehicles.</td>
      <td>Discrete steering (e.g. $[-5^\circ, 0^\circ, +5^\circ]$) causes violent, jerky oscillations at 120 km/h, destabilizing vehicle chassis dynamics and triggering fatal rollovers.</td>
    </tr>
    <tr>
      <td><b>3. Quadruped Locomotion</b> (Unitree Go2 / ANYmal)</td>
      <td>$12$ continuous joint target angles $\theta_{\text{target}} \in [-\pi, +\pi]$ fed to low-level 500 Hz PD joint controllers.</td>
      <td>$48$-dim vector: Base orientation quaternion, angular velocity, linear velocity, 12 joint angles, 12 joint velocities, 4 foot contact flags.</td>
      <td>Landing dynamic backflips requires smooth continuous ground reaction force absorption. Discretized joint steps shatter gearbox teeth upon dynamic impact.</td>
    </tr>
    <tr>
      <td><b>4. Exothermic Chemical Reactor</b> (Process Engineering)</td>
      <td>$3$ continuous actuator setpoints: Coolant valve opening $\% \in [0.0, 100.0]$, reagent pump rate L/min, and agitator RPM.</td>
      <td>$16$ sensor readings: Core reactor temperature, jacket temperature, internal pressure, chemical concentration, pH, viscosity.</td>
      <td>Discretizing coolant flow by $10\%$ increments causes temperature hunting cycles that cross thermal runaway thresholds, resulting in explosive reactor overpressure.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 4: THE DEADLY TRIAD -->
<h2>4. The Deadly Triad &amp; Why Off-Policy Continuous RL Diverges</h2>
<p>
  Richard Sutton proved in 1988 that if a reinforcement learning algorithm combines three specific elements, the value function parameters can mathematically diverge to $+\infty$ or $-\infty$:
</p>

<!-- DIAGRAM 2: DEADLY TRIAD TRIANGLE -->
<div class="diagram-container">
<svg width="600" height="110" viewBox="0 0 600 110">
  <!-- Triangle Path -->
  <polygon points="300,15 150,95 450,95" fill="#fef2f2" stroke="#ef4444" stroke-width="2"/>
  
  <!-- Nodes -->
  <circle cx="300" cy="15" r="16" fill="#fee2e2" stroke="#ef4444" stroke-width="2"/>
  <text x="300" y="19" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">1</text>
  <text x="300" y="38" font-size="8.5" font-weight="700" fill="#991b1b" text-anchor="middle">Function Approx</text>
  <text x="300" y="48" font-size="7.5" fill="#7f1d1d" text-anchor="middle">(Neural Networks)</text>

  <circle cx="150" cy="95" r="16" fill="#fee2e2" stroke="#ef4444" stroke-width="2"/>
  <text x="150" y="99" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">2</text>
  <text x="150" y="118" font-size="8.5" font-weight="700" fill="#991b1b" text-anchor="middle">Bootstrapping</text>
  <text x="150" y="128" font-size="7.5" fill="#7f1d1d" text-anchor="middle">(Learning from Target Q)</text>

  <circle cx="450" cy="95" r="16" fill="#fee2e2" stroke="#ef4444" stroke-width="2"/>
  <text x="450" y="99" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">3</text>
  <text x="450" y="118" font-size="8.5" font-weight="700" fill="#991b1b" text-anchor="middle">Off-Policy Data</text>
  <text x="450" y="128" font-size="7.5" fill="#7f1d1d" text-anchor="middle">(Replay Buffer Memory)</text>

  <text x="300" y="75" font-size="10" font-weight="800" fill="#b91c1c" text-anchor="middle">THE DEADLY TRIAD</text>
  <text x="300" y="87" font-size="8" fill="#7f1d1d" text-anchor="middle">Values explode to $10^{12}$ or collapse to NaN</text>
</svg>
</div>

<p>
  Why does this deadly divergence happen?
</p>
<ol>
  <li><b>Function Approximation:</b> A deep neural network cannot memorize every state independently; changing the Q-value of state $s_1$ inadvertently shifts the Q-value of millions of nearby states $s_2, s_3, \dots$ due to shared hidden layer weights.</li>
  <li><b>Bootstrapping:</b> We update $Q(s, a)$ toward a target that <i>itself depends on the network's own output</i> ($r + \gamma Q(s', a')$). A slight error in $Q(s', a')$ feeds directly into the target for $Q(s, a)$.</li>
  <li><b>Off-Policy Learning:</b> The data sampled from the replay buffer was collected by old policies from 20,000 steps ago. The data distribution does not match the distribution of the current policy, creating unstable distribution shift.</li>
</ol>
<p>
  Together, these three create a vicious, self-amplifying feedback loop: an overestimation error in one state is generalized across the space, bootstrapped into future targets, and amplified exponentially until your Q-values hit $10^{15}$ and training collapses!
</p>



<!-- SECTION 5: THE THREE DEFENSIVE SUPER-WEAPONS -->
<h2>5. The Three Defensive Super-Weapons of SAC</h2>
<p>
  To tame the Deadly Triad and achieve bulletproof stability on continuous robots, SAC deploys three brilliant mathematical mechanisms:
</p>

<h3>5.1 Super-Weapon 1: Experience Replay Buffer (The Photo Album)</h3>
<div class="callout intuition">
  <div class="callout-title">📸 Everyday Analogy: The Photo Album vs Instant Amnesia</div>
  <p>
    Imagine learning to play tennis, but the moment you hit a ball, you suffer complete amnesia and forget what just happened. That is on-policy learning (PPO). 
    In contrast, an <b>Experience Replay Buffer</b> is a photographic memory album containing <b>1,000,000 snapshots</b> of every swing you ever took over the last 3 days—both aces and wild misses. 
    Every night, you shuffle through 256 random photos from across your entire history to study your technique.
  </p>
</div>

<table>
  <thead>
    <tr>
      <th style="width: 18%;">Buffer Parameter</th>
      <th style="width: 20%;">Standard Value</th>
      <th style="width: 42%;">Physical Function &amp; Purpose</th>
      <th style="width: 20%;">Tuning Danger</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Capacity $N$</b></td>
      <td>$10^6$ transitions</td>
      <td>Circular FIFO buffer holding recent $(s, a, r, s', d)$ tuples. Breaks temporal correlation across sequential video frames.</td>
      <td>Too small ($10^4$): Policy forgets early lessons; Too large ($10^7$): GPU RAM OOM crash.</td>
    </tr>
    <tr>
      <td><b>Batch Size $B$</b></td>
      <td>$256$ transitions</td>
      <td>Number of independent, uncorrelated transitions sampled uniformly at random for each stochastic gradient descent step.</td>
      <td>Too small ($32$): High gradient variance; Too large ($2048$): Slow computation per step.</td>
    </tr>
    <tr>
      <td><b>Warmup Steps</b></td>
      <td>$10,000$ steps</td>
      <td>Pure uniform random actions executed before any gradient updates begin. Fills the buffer with diverse boundary data.</td>
      <td>If 0: Critic severely overfits to the initial 50 steps, locking into immediate local minima.</td>
    </tr>
  </tbody>
</table>

<h3>5.2 Super-Weapon 2: Polyak Target Networks (The Patient Teacher)</h3>
<div class="callout intuition">
  <div class="callout-title">🎯 The Moving Bullseye Problem</div>
  <p>
    If you calculate Bellman targets using the <i>exact same network</i> you are currently updating, the target changes every single millisecond. 
    It is like trying to shoot an arrow at a target that vibrates violently every time you pull the bowstring!
  </p>
</div>
<p>
  SAC maintains a separate set of <b>Target Critic Weights $\bar{\theta}$</b>. Instead of copying weights abruptly, it updates them using an exponential moving average (Polyak averaging):
</p>
<div class="formula">
  $$\bar{\theta} \leftarrow \tau \theta + (1 - \tau) \bar{\theta} \qquad \text{where } \tau = 0.005$$
</div>
<p>
  <b>Target Weight Half-Life ($t_{1/2}$):</b> With $\tau = 0.005$, the target network updates by only <b>0.5% per gradient step</b>. 
  The time required for target weights to incorporate 50% of a change in online weights is:
</p>
<div class="formula">
  $$t_{1/2} = \frac{\ln(0.5)}{\ln(1 - \tau)} = \frac{-0.693}{\ln(0.995)} \approx \mathbf{138 \text{ gradient steps}}$$
</div>
<p>
  This sluggish target network acts as a calm, patient teacher, providing a Rock-of-Gibraltar stable target for the online critic to learn against.
</p>

<h3>5.3 Super-Weapon 3: Clipped Twin-Q Critics (The Two Skeptical Judges)</h3>
<p>
  Why do neural network critics inherently overestimate Q-values? Consider two independent noisy estimators $Q_1$ and $Q_2$ of a true value $V^* = 10.0$. Even if both estimators are zero-mean unbiased ($\mathbb{E}[Q_1] = \mathbb{E}[Q_2] = 10.0$), taking their maximum is mathematically guaranteed to be strictly greater than 10.0:
</p>
<div class="formula">
  $$\mathbb{E}[\max(Q_1, Q_2)] \ge \max(\mathbb{E}[Q_1], \mathbb{E}[Q_2]) \quad \text{(Jensen's Inequality)}$$
</div>
<p>
  In standard continuous Q-learning, the actor intentionally searches for actions that maximize $Q(s, a)$. It will naturally find the actions where the neural network suffered an accidental positive approximation error! 
  <b>The Fix:</b> Train <b>two completely independent critic networks</b> ($Q_{\phi_1}$ and $Q_{\phi_2}$). When computing the Bellman target, always take the <b>minimum</b> of the two target predictions:
</p>
<div class="formula">
  $$y = r(s, a) + \gamma \left( \min_{j=1,2} Q_{\bar{\phi}_j}(s', a') - \alpha \log \pi(a' \mid s') \right)$$
</div>

<!-- DIAGRAM 3: TWIN-Q MINIMUM -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <rect x="30" y="15" width="200" height="30" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="130" y="34" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">Critic 1: $Q_{\bar{\phi}_1}(s', a') = \mathbf{28.4}$ (Overestimated!)</text>

  <rect x="30" y="52" width="200" height="30" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="130" y="71" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">Critic 2: $Q_{\bar{\phi}_2}(s', a') = \mathbf{21.1}$ (Realistic)</text>

  <path d="M 235,48 L 305,48" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="305,48 297,44 297,52" fill="#2563eb"/>

  <rect x="315" y="25" width="265" height="46" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="447" y="44" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">Clipped Target: $\min(28.4, 21.1) = \mathbf{21.1}$</text>
  <text x="447" y="60" font-size="8" fill="#1d4ed8" text-anchor="middle">Overestimation bias is completely neutralized!</text>
</svg>
</div>



<!-- SECTION 6: MAXIMUM ENTROPY RL & SOFT ACTOR-CRITIC -->
<h2>6. Maximum Entropy RL: Soft Actor-Critic (SAC)</h2>
<p>
  Standard RL maximizes only expected discounted reward: $\sum_t \gamma^t r_t$. 
  In <b>Maximum Entropy RL</b>, we fundamentally change the objective: the agent is trained to maximize expected reward <b>PLUS the Shannon entropy of its policy</b>!
</p>

<div class="callout intuition">
  <div class="callout-title">🥐 The Curious Tourist in Paris Analogy</div>
  <p>
    Imagine you arrive in Paris for a 2-week vacation:
  </p>
  <ul>
    <li><b>Standard RL Agent (Reward Only):</b> On your first morning, you walk 20 meters from your hotel and find a corner bakery selling decent croissants (Reward $= +6$). 
      Because your algorithm only maximizes reward and has zero curiosity bonus, it concludes that eating this exact croissant every single morning for 14 days guarantees a high score. 
      You never explore Montmartre, never taste artisan sourdough, and never discover the world-class bakery 2 blocks away. You are trapped in a mediocre local optimum.
    </li>
    <li><b>Maximum Entropy RL Agent (Reward + Entropy Bonus):</b> You are paid a monetary bonus for being <b>unpredictable and adventurous</b>! 
      You want delicious food, but you also want high entropy (visiting diverse neighborhoods, testing different bakeries, trying macarons and crêpes). 
      Even after finding the decent croissant, your high entropy incentive pushes you to try other streets. 
      You quickly discover the 3-star Michelin bakery, achieving a far superior outcome!
    </li>
  </ul>
  <p>
    <b>Why this is mandatory for Robot Fruit Slicing:</b> If a robot only maximizes reward, early in training it experiences severe negative penalties whenever its knife slips or crushes the fruit. 
    A standard RL policy gets terrified: it learns to hold the knife frozen 2 millimeters above the fruit skin and never move, because doing nothing yields 0 penalty! 
    The <b>Entropy Bonus</b> pays the robot to keep trying different knife angles, velocities, and sawing compliance, preventing policy freeze!
  </p>
</div>

<h3>6.1 The Soft Bellman Objective &amp; Parameter Anatomy</h3>
<div class="formula">
  $$J(\pi) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t) \sim \rho_\pi} \left[ r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot \mid s_t)) \right] \quad \text{where} \quad \mathcal{H}(\pi) = \mathbb{E}_{a \sim \pi}[-\log \pi(a \mid s_t)]$$
</div>

<table>
  <thead>
    <tr>
      <th style="width: 16%;">Parameter</th>
      <th style="width: 22%;">Formal Name</th>
      <th style="width: 38%;">Plain English Meaning</th>
      <th style="width: 12%;">Example Value</th>
      <th style="width: 12%;">Tuning Impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$r(s_t, a_t)$</b></td>
      <td>Extrinsic Task Reward</td>
      <td>Physical progress points awarded by the environment (e.g. knife cutting depth minus pulp compression force).</td>
      <td>$+3.5$ points</td>
      <td>Primary task drive.</td>
    </tr>
    <tr>
      <td><b>$\alpha$</b></td>
      <td>Entropy Temperature</td>
      <td><b>The Curiosity Dial:</b> Determines the trade-off between task exploitation and wide exploratory diversity.</td>
      <td>$\alpha = 0.2$ (or auto-tuned)</td>
      <td>$\alpha \to 0$: Standard RL (freezes); $\alpha \to \infty$: Pure random noise.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{H}(\pi(\cdot \mid s_t))$</b></td>
      <td>Shannon Entropy</td>
      <td>A mathematical measure of how spread out and uncertain the action distribution is. A wide bell curve has high entropy; a sharp spike has low entropy.</td>
      <td>$2.4$ nats</td>
      <td>Higher entropy guarantees exploration across multiple distinct physical modes.</td>
    </tr>
    <tr>
      <td><b>$\log \pi(a \mid s_t)$</b></td>
      <td>Action Log-Probability</td>
      <td>Logarithm of the probability density of choosing action $a$. Because $\pi \le 1$, $\log \pi$ is negative, so $-\log \pi \ge 0$ acts as a positive bonus!</td>
      <td>$-1.5$</td>
      <td>Larger negative log-prob = rarer action = higher exploratory bonus.</td>
    </tr>
  </tbody>
</table>

<h3>6.2 Automatic Temperature Tuning (Dual Optimization of $\alpha$)</h3>
<p>
  Instead of hardcoding a fixed curiosity temperature $\alpha$, modern SAC treats $\alpha$ as a learnable parameter. 
  We specify a <b>Target Entropy $\bar{\mathcal{H}}$</b> (heuristically chosen as $\bar{\mathcal{H}} = -\dim(\mathcal{A})$, e.g. $-14$ for a 14-DoF robot). 
  We optimize the temperature loss:
</p>
<div class="formula">
  $$J(\alpha) = \mathbb{E}_{a_t \sim \pi_t} \left[ -\alpha \left( \log \pi_t(a_t \mid s_t) + \bar{\mathcal{H}} \right) \right] \qquad \Longrightarrow \qquad \nabla_\alpha J(\alpha) = - \left( \log \pi_t(a_t \mid s_t) + \bar{\mathcal{H}} \right)$$
</div>
<ul>
  <li><b>If policy entropy is too low ($\mathcal{H} &lt; \bar{\mathcal{H}}$, meaning the robot is collapsing into a rigid routine too early):</b> $\alpha$ automatically increases, injecting heavy exploration bonuses to force the robot to keep trying new actions.</li>
  <li><b>If policy entropy is too high ($\mathcal{H} &gt; \bar{\mathcal{H}}$, meaning the robot already knows what to do but is still jittering randomly):</b> $\alpha$ automatically decreases toward zero, letting the robot focus with laser precision on maximizing reward.</li>
</ul>



<!-- SECTION 7: REPARAMETERIZATION & TANH SQUASHING -->
<h2>7. The Reparameterization Trick &amp; Tanh Action Squashing</h2>
<p>
  How do we backpropagate gradients through a stochastic continuous actor network?
</p>

<h3>7.1 The Backpropagation Barrier</h3>
<p>
  A continuous actor outputs the parameters of a Gaussian distribution: mean $\mu_\theta(s)$ and standard deviation $\sigma_\theta(s)$. 
  If we sample an action directly:
</p>
<div class="formula">
  $$a \sim \mathcal{N}(\mu_\theta(s), \sigma_\theta(s)^2)$$
</div>
<p>
  The sampling operation is an <b>opaque random number generator</b>. Gradient backpropagation $\frac{\partial a}{\partial \theta}$ cannot pass through a random node! The computational graph is broken.
</p>

<h3>7.2 Kingma &amp; Welling's Reparameterization Trick</h3>
<p>
  Instead of sampling inside the computational graph, we isolate all stochasticity into an external, parameter-free noise variable $\epsilon \sim \mathcal{N}(0, \mathbf{I})$. We compute the pre-squashed action $u$ deterministically:
</p>
<div class="formula">
  $$u = \mu_\theta(s) + \sigma_\theta(s) \odot \epsilon, \qquad \text{where } \epsilon \sim \mathcal{N}(0, \mathbf{I})$$
</div>
<p>
  Now, $u$ is a fully differentiable function of $\theta$! Gradients from the Critic $Q(s, a)$ flow seamlessly through $u$, straight through $\mu_\theta$ and $\sigma_\theta$, and into the Actor's neural weights:
</p>
<div class="formula">
  $$\nabla_\theta Q(s, a) = \nabla_a Q(s, a) \cdot \nabla_u a \cdot \left[ \nabla_\theta \mu_\theta(s) + \epsilon \odot \nabla_\theta \sigma_\theta(s) \right]$$
</div>

<!-- DIAGRAM 4: REPARAMETERIZATION PATH -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <!-- Left: Standard Sampling (Broken) -->
  <rect x="25" y="10" width="240" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="145" y="26" font-size="8.5" font-weight="700" fill="#991b1b" text-anchor="middle">STANDARD SAMPLING (BROKEN)</text>
  <text x="145" y="44" font-size="8" fill="#7f1d1d" text-anchor="middle">$\theta \to [\mu, \sigma] \longrightarrow \text{Sample } a \sim \mathcal{N} \longrightarrow Q(s, a)$</text>
  <text x="145" y="66" font-size="8" font-weight="700" fill="#b91c1c" text-anchor="middle">❌ Gradient cannot flow through random node!</text>

  <!-- Right: Reparameterization (Clean) -->
  <rect x="310" y="10" width="270" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="445" y="26" font-size="8.5" font-weight="700" fill="#065f46" text-anchor="middle">REPARAMETERIZATION TRICK (CLEAN)</text>
  <text x="445" y="44" font-size="8" fill="#047857" text-anchor="middle">$\theta \to [\mu, \sigma] \longrightarrow u = \mu + \sigma \odot \epsilon \longrightarrow a = \tanh(u)$</text>
  <text x="445" y="66" font-size="8" font-weight="700" fill="#047857" text-anchor="middle">✔ Seamless backpropagation from Critic to Actor!</text>
</svg>
</div>

<h3>7.3 Enforcing Physical Motor Limits: Tanh Squashing &amp; The Jacobian Correction</h3>
<p>
  A Gaussian distribution has infinite tails: an unbounded sample could demand $+150.0$ Nm of torque from a motor rated for $\pm 10.0$ Nm, triggering hardware emergency shutdown. 
  To enforce strict hardware boundaries, SAC applies a <b>hyperbolic tangent squashing function</b>:
</p>
<div class="formula">
  $$a = \tanh(u) \in (-1, +1) \qquad \Longrightarrow \qquad a_{\text{robot}} = a_{\text{scale}} \cdot a + a_{\text{bias}}$$
</div>
<p>
  <b>The Critical Change-of-Variables Jacobian Correction:</b> Squashing non-linearly distorts probability densities. By the transformation theorem for continuous random variables:
</p>
<div class="formula">
  $$\pi(a \mid s) = \mu(u \mid s) \cdot \left| \det \left( \frac{da}{du} \right) \right|^{-1}$$
</div>
<p>
  Since $\frac{d \tanh(u)}{du} = 1 - \tanh^2(u)$, taking the logarithm yields the exact log-probability:
</p>
<div class="formula">
  $$\log \pi(a \mid s) = \log \mu(u \mid s) - \sum_{i=1}^d \log \left( 1 - \tanh^2(u_i) + \delta \right)$$
</div>
<div class="callout warning-box">
  <div class="callout-title">⚠️ The Numerical NaN Trap: Machine Epsilon ($\delta = 10^{-6}$)</div>
  <p>
    If $u_i \ge 10.0$, $\tanh(u_i) \to 1.0$, which causes $1 - \tanh^2(u_i) \to 0$. 
    Evaluating $\log(0)$ produces <b>$-\infty$</b>, resulting in immediate <b>NaN gradient explosion</b> that irreversibly corrupts your entire network! 
    In production code, always add a clamping safeguard: <code>log_prob -= torch.log(1 - a.pow(2) + 1e-6).sum(dim=-1, keepdim=True)</code>.
  </p>
</div>



<!-- SECTION 8: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>8. Concrete Step-by-Step Numerical Walkthrough: One Complete SAC Update</h2>
<p>
  Let us follow the exact floating-point calculations for a single transition sampled from the replay buffer in a dual-arm slicing task:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 8%;">Step</th>
      <th style="width: 25%;">Operation</th>
      <th style="width: 27%;">Equation / Code Formula</th>
      <th style="width: 15%;">Calculated Value</th>
      <th style="width: 25%;">Physical Interpretation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1</b></td>
      <td>Sampled Transition</td>
      <td>$(s, a, r, s', d) \sim \mathcal{D}$</td>
      <td>$r = +3.50$<br>$d = 0$ (alive)</td>
      <td>Knife penetrated 1.5 mm deeper with optimal blade shear angle; trial is ongoing.</td>
    </tr>
    <tr>
      <td><b>2</b></td>
      <td>Hyperparameters</td>
      <td>$\gamma, \alpha$</td>
      <td>$\gamma = 0.99$<br>$\alpha = 0.20$</td>
      <td>Standard discount factor and active entropy curiosity temperature.</td>
    </tr>
    <tr>
      <td><b>3</b></td>
      <td>Next Action Sampling</td>
      <td>$u' = \mu(s') + \sigma(s') \odot \epsilon$<br>$a' = \tanh(u')$</td>
      <td>$u' = [0.8, -0.4]$<br>$a' = [0.664, -0.380]$</td>
      <td>Actor evaluates state $s'$ and selects candidate continuous next action.</td>
    </tr>
    <tr>
      <td><b>4</b></td>
      <td>Squashed Log-Prob</td>
      <td>$\log \pi(a' \mid s') = \log \mu(u') - \sum \log(1 - a'^2)$</td>
      <td>$\log \pi(a' \mid s') = \mathbf{-1.45}$</td>
      <td>Negative log-probability. Entropy bonus: $-\alpha \log \pi = -0.2(-1.45) = \mathbf{+0.29}$.</td>
    </tr>
    <tr>
      <td><b>5</b></td>
      <td>Twin Target Critic Evaluation</td>
      <td>$Q_{\bar{\phi}_1}(s', a'), \; Q_{\bar{\phi}_2}(s', a')$</td>
      <td>$Q_1 = 34.20$<br>$Q_2 = 29.50$</td>
      <td>Critic 1 overestimates; Critic 2 is more conservative.</td>
    </tr>
    <tr>
      <td><b>6</b></td>
      <td>Clipped Soft Target $y$</td>
      <td>$y = r + \gamma (\min(Q_1, Q_2) - \alpha \log \pi(a' \mid s'))$</td>
      <td>$3.50 + 0.99(29.50 + 0.29)$<br>$= 3.50 + 29.49 = \mathbf{32.99}$</td>
      <td>Pessimistic target value used as ground truth label for critic regression.</td>
    </tr>
    <tr>
      <td><b>7</b></td>
      <td>Current Q Estimates</td>
      <td>$Q_{\phi_1}(s, a), \; Q_{\phi_2}(s, a)$</td>
      <td>$Q_1 = 31.20$<br>$Q_2 = 30.80$</td>
      <td>Online critic outputs for the actual sampled $(s, a)$ transition.</td>
    </tr>
    <tr>
      <td><b>8</b></td>
      <td>Critic Loss Computation</td>
      <td>$\mathcal{L}_Q = \frac{1}{2}[(Q_1 - y)^2 + (Q_2 - y)^2]$</td>
      <td>$\frac{1}{2}[(31.2 - 32.99)^2 + (30.8 - 32.99)^2]$<br>$= \frac{1}{2}[3.20 + 4.80] = \mathbf{4.00}$</td>
      <td>Mean squared Bellman error backpropagated into online critic weights $\phi_1, \phi_2$.</td>
    </tr>
    <tr>
      <td><b>9</b></td>
      <td>Actor Loss Computation</td>
      <td>$\mathcal{L}_\pi = \alpha \log \pi(\tilde{a} \mid s) - \min(Q_1(s, \tilde{a}), Q_2(s, \tilde{a}))$</td>
      <td>$0.20(-1.10) - 31.50$<br>$= -0.22 - 31.50 = \mathbf{-31.72}$</td>
      <td>Minimizing this loss pushes actor to simultaneously increase Q and increase entropy!</td>
    </tr>
    <tr>
      <td><b>10</b></td>
      <td>Polyak Target Update</td>
      <td>$\bar{\phi}_j \leftarrow 0.005\phi_j + 0.995\bar{\phi}_j$</td>
      <td>$0.005(1.20) + 0.995(1.00)$<br>$= \mathbf{1.001}$</td>
      <td>Target critic weights shift by a microscopic $0.5\%$, preserving target stability.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 9: DIARY OF A TRAINING RUN -->
<h2>9. Diary of an SAC Robot Training Run (0 to 1,000,000 Steps)</h2>
<p>
  What happens when you launch SAC on a dual-arm robot in NVIDIA Isaac Lab?
</p>
<ul>
  <li><b>Phase 1: Warmup &amp; Buffer Priming (Steps 0 – 10,000):</b> The robot executes pure uniform random motor torques. The arms flail randomly across 3D space, dropping knives and bumping into tables. No neural network weights are updated. 10,000 transitions populate the circular replay buffer.</li>
  <li><b>Phase 2: High Entropy Exploration (Steps 10,000 – 100,000):</b> Training starts. $\alpha$ is high ($\approx 0.20$). Critic loss is large ($\approx 15.0$) as it struggles to predict value. The entropy bonus prevents premature convergence. The robot accidentally touches the fruit and registers a $+2.0$ contact reward.</li>
  <li><b>Phase 3: Twin-Q Consolidation &amp; Coordination (Steps 100,000 – 400,000):</b> Twin critics converge; overestimation bias stays near zero. The actor learns coordinated dual-arm behavior: the left arm stabilizes the fruit with the fork while the right arm aligns the blade at a $15^\circ$ slicing tilt.</li>
  <li><b>Phase 4: Low Entropy Mastery (Steps 400,000 – 1,000,000):</b> $\alpha$ automatically decays to $\approx 0.02$. The policy transitions from exploratory searching to laser precision. The robot executes smooth 80 mm sawing strokes with sub-millimeter depth accuracy ($1.2 \pm 0.1$ mm/stroke) and minimal pulp crush ($F_z &lt; 3.0$ N). Success rate reaches $97\%$.</li>
</ul>



<!-- SECTION 10: COMPLETE PRODUCTION PYTORCH IMPLEMENTATION -->
<h2>10. Complete Production-Grade PyTorch SAC Implementation</h2>
<p>
  Here is the clean, self-contained implementation of the modern Soft Actor-Critic algorithm with Twin Critics, Tanh Squashing, and Automatic Temperature Tuning:
</p>

<div class="callout code-box">
  <div class="callout-title">🐍 Complete Production-Grade Soft Actor-Critic (PyTorch)</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn
from torch.distributions.normal import Normal

class ReparameterizedTanhGaussianActor(nn.Module):
    # Continuous policy network with reparameterization and Tanh squashing
    def __init__(self, state_dim, action_dim, hidden_dim=256, action_scale=1.0):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.mean_head = nn.Linear(hidden_dim, action_dim)
        self.log_std_head = nn.Linear(hidden_dim, action_dim)
        self.action_scale = action_scale

    def forward(self, state):
        features = self.net(state)
        mean = self.mean_head(features)
        # Clamping log_std prevents numerical explosion and distribution collapse
        log_std = torch.clamp(self.log_std_head(features), min=-20, max=2)
        return mean, log_std

    def sample(self, state):
        mean, log_std = self.forward(state)
        std = log_std.exp()
        # Reparameterization Trick: u = mean + std * epsilon
        dist = Normal(mean, std)
        u = dist.rsample()
        # Hyperbolic tangent action squashing
        action = torch.tanh(u)

        # Enforce change-of-variables Jacobian correction for log-probability
        log_prob = dist.log_prob(u) - torch.log(1.0 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(dim=-1, keepdim=True)
        return action * self.action_scale, log_prob


class TwinContinuousCritic(nn.Module):
    # Two independent Q-networks trained in parallel to defeat overestimation
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super().__init__()
        # Critic 1
        self.q1 = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        # Critic 2
        self.q2 = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, state, action):
        sa = torch.cat([state, action], dim=-1)
        return self.q1(sa), self.q2(sa)


class SACAgent:
    # Full Soft Actor-Critic agent with Twin-Q and Auto-Tuned Entropy
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, tau=0.005):
        self.gamma = gamma
        self.tau = tau
        self.actor = ReparameterizedTanhGaussianActor(state_dim, action_dim)
        self.critic = TwinContinuousCritic(state_dim, action_dim)
        self.critic_target = TwinContinuousCritic(state_dim, action_dim)
        self.critic_target.load_state_dict(self.critic.state_dict())

        self.actor_opt = torch.optim.Adam(self.actor.parameters(), lr=lr)
        self.critic_opt = torch.optim.Adam(self.critic.parameters(), lr=lr)

        # Automatic Entropy Temperature Tuning
        self.target_entropy = -float(action_dim)
        self.log_alpha = torch.zeros(1, requires_grad=True)
        self.alpha_opt = torch.optim.Adam([self.log_alpha], lr=lr)

    @property
    def alpha(self):
        return self.log_alpha.exp().item()

    def update(self, batch):
        states, actions, rewards, next_states, dones = batch

        # 1. CRITIC UPDATE: Clipped Twin-Q Bellman Target
        with torch.no_grad():
            next_actions, next_log_probs = self.actor.sample(next_states)
            q1_target, q2_target = self.critic_target(next_states, next_actions)
            min_q_target = torch.min(q1_target, q2_target) - self.alpha * next_log_probs
            y = rewards + (1.0 - dones) * self.gamma * min_q_target

        q1_current, q2_current = self.critic(states, actions)
        critic_loss = 0.5 * (nn.functional.mse_loss(q1_current, y) + 
                             nn.functional.mse_loss(q2_current, y))

        self.critic_opt.zero_grad()
        critic_loss.backward()
        self.critic_opt.step()

        # 2. ACTOR UPDATE: Maximize Expected Q + Entropy
        new_actions, log_probs = self.actor.sample(states)
        q1_new, q2_new = self.critic(states, new_actions)
        min_q_new = torch.min(q1_new, q2_new)
        actor_loss = (self.alpha * log_probs - min_q_new).mean()

        self.actor_opt.zero_grad()
        actor_loss.backward()
        self.actor_opt.step()

        # 3. ENTROPY TEMPERATURE UPDATE
        alpha_loss = -(self.log_alpha * (log_probs + self.target_entropy).detach()).mean()
        self.alpha_opt.zero_grad()
        alpha_loss.backward()
        self.alpha_opt.step()

        # 4. POLYAK TARGET UPDATE
        for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1.0 - self.tau) * target_param.data)
</pre>
</div>



<!-- SECTION 11: PRACTITIONER'S FIELD GUIDE -->
<h2>11. Practitioner's Field Guide: 6 Continuous RL Failure Modes &amp; Fixes</h2>
<p>
  When training continuous RL on physical or simulated robots, these 6 insidious bugs account for $95\%$ of all failed projects:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Failure Symptom</th>
      <th style="width: 38%;">The Hidden Root Cause</th>
      <th style="width: 42%;">The Production-Proven Fix</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Q-Values Explode to $+10^{8}$</b></td>
      <td>Polyak target parameter $\tau$ set too aggressively ($\tau=0.05$ instead of $0.005$) or Twin-Critic minimum was accidentally replaced with an average. The Deadly Triad triggers runaway positive feedback.</td>
      <td>Set $\tau \in [0.005, 0.01]$. Verify that target evaluation strictly takes <code>torch.min(q1, q2)</code> rather than <code>0.5*(q1 + q2)</code>.</td>
    </tr>
    <tr>
      <td><b>2. Policy Hits $\pm 1.0$ (Saturated Torques)</b></td>
      <td>Entropy temperature $\alpha$ decayed to zero prematurely, or rewards are scaled too high (e.g. $r = +500$). The network saturates motor limits in a desperate effort to maximize reward.</td>
      <td>Normalize environment rewards by multiplying by $0.1$ or $0.01$. Ensure automatic entropy tuning has target entropy $\bar{\mathcal{H}} = -\dim(\mathcal{A})$.</td>
    </tr>
    <tr>
      <td><b>3. Training NaNs at Step 45,000</b></td>
      <td>Jacobian correction evaluates $\log(1 - a^2)$ where $a = \pm 1.00000$, resulting in $\log(0) = -\infty$. Gradients multiply into NaNs, wiping out all neural weights.</td>
      <td>Always clamp inside log: <code>torch.log(1.0 - a.pow(2) + 1e-6)</code>. Also clamp policy <code>log_std</code> between $[-20, +2]$.</td>
    </tr>
    <tr>
      <td><b>4. Robot Freezes / Does Nothing</b></td>
      <td>Entropy bonus is too small or absent ($\alpha=0$). Robot incurs small negative penalties for moving, realizes that standing completely still yields $0$ penalty, and freezes forever.</td>
      <td>Initialize $\alpha = 0.2$ or higher. Provide small shaping rewards for progress towards the target to overcome initial inertia.</td>
    </tr>
    <tr>
      <td><b>5. Catastrophic Replay RAM OOM</b></td>
      <td>Storing high-dimensional float64 states or raw RGB camera images directly in Python lists causes CPU/GPU memory to leak and Linux OOM killer to terminate the script.</td>
      <td>Pre-allocate monolithic continuous <code>torch.float32</code> NumPy ring buffers. For vision, store compressed JPEG bytes or low-dimensional latent vectors.</td>
    </tr>
    <tr>
      <td><b>6. Cold-Start Policy Collapse</b></td>
      <td>Updating neural network parameters on step 1 when the replay buffer contains only 5 transitions. The critic severely overfits to 5 points and crashes.</td>
      <td>Always implement a strict <b>warmup phase</b>: execute 10,000 random exploration steps before calling <code>agent.update()</code> for the first time.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 12: CONTINUOUS ALGORITHM COMPARISON -->
<h2>12. Continuous RL Algorithm Selection Cheat Sheet</h2>
<table>
  <thead>
    <tr>
      <th style="width: 18%;">Feature / Property</th>
      <th style="width: 20%;">DDPG (2015)</th>
      <th style="width: 20%;">TD3 (2018)</th>
      <th style="width: 22%;">SAC (2018)</th>
      <th style="width: 20%;">PPO (Lecture 10)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Policy Type</b></td>
      <td>Deterministic</td>
      <td>Deterministic</td>
      <td><b>Stochastic (MaxEnt)</b></td>
      <td>Stochastic</td>
    </tr>
    <tr>
      <td><b>Sample Efficiency</b></td>
      <td>Moderate</td>
      <td>High</td>
      <td><b>Very High (Best in Class)</b></td>
      <td>Moderate (On-Policy)</td>
    </tr>
    <tr>
      <td><b>Exploration Mechanism</b></td>
      <td>Additive Gaussian noise</td>
      <td>Target policy smoothing</td>
      <td><b>Intrinsic Entropy Bonus $\alpha \mathcal{H}$</b></td>
      <td>Policy entropy penalty</td>
    </tr>
    <tr>
      <td><b>Overestimation Protection</b></td>
      <td>None (Severe bias)</td>
      <td>Clipped Double-Q</td>
      <td><b>Clipped Double-Q</b></td>
      <td>GAE Advantage Clipping</td>
    </tr>
    <tr>
      <td><b>Hyperparameter Tuning</b></td>
      <td>Extremely brittle</td>
      <td>Moderate</td>
      <td><b>Very Robust (Auto $\alpha$)</b></td>
      <td>Very Robust</td>
    </tr>
    <tr>
      <td><b>Ideal Robotics Application</b></td>
      <td>Deprecated / Historical</td>
      <td>Simple low-DoF joints</td>
      <td><b>Complex manipulation, soft contacts, high DoF</b></td>
      <td>Massively parallel sim (Isaac Lab locomotion)</td>
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
