import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering RL Basics & Continuous MDPs: Definitive Guide to CS285 Lecture 4</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 4: RL Basics, Continuous MDPs & Bellman Equations";
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
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 4 Masterclass Study Guide</span>
  <h1>Mastering Reinforcement Learning Basics &amp; Continuous MDPs</h1>
  <div class="subtitle">Complete Foundations: Markov Decision Processes, The Markov Chain View, The Universal Algorithm Anatomy, Continuous Gaussian Policies, Bellman Self-Consistency, and Tensor Broadcasting Traps</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Curriculum:</b> Berkeley CS285 + Achiam (Spinning Up) + Sutton &amp; Barto</span>
    <span><b>Scope:</b> General Continuous RL Theory &amp; Robotics Slicing</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The "Mental Map": Why Does Lecture 4 Exist?</h2>
<p>
  In previous lectures, we examined <b>Imitation Learning</b> (Behavioral Cloning). Imitation learning is straightforward: record a human operator and train a neural network to mimic human control actions via supervised learning. But imitation learning has severe limits:
</p>
<ul>
  <li>What if you do not have 500 hours of perfect human demonstrations?</li>
  <li>What if a human operator cannot react quickly enough to regulate high-frequency (1 kHz) contact impedance during fracture events?</li>
  <li>What if the human demonstrator is sub-optimal?</li>
</ul>
<p>
  <b>This is why Reinforcement Learning exists.</b> Instead of copying a human, the agent discovers optimal behavior autonomously through trial, error, and physical reward signals. Lecture 4 provides the foundational mathematical engine of RL: <i>Markov Decision Processes, Cumulative Return Objectives, Algorithm Anatomy, Value Functions, and Bellman Self-Consistency</i>.
</p>

<!-- SVG Diagram: The 5 Pillars of Lecture 4 -->
<div class="diagram-container">
<svg width="690" height="90" viewBox="0 0 690 90">
  <rect x="5" y="10" width="128" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="69" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. MDPs &amp; States</text>
  <text x="69" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Markov Chains to MDPs</text>
  <text x="69" y="66" font-size="8.2" fill="#475569" text-anchor="middle">State Sufficiency</text>

  <rect x="141" y="10" width="128" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="205" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">2. The Objective</text>
  <text x="205" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Expected Return J(θ)</text>
  <text x="205" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Markov Chain View</text>

  <rect x="277" y="10" width="128" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="341" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">3. Algorithm Anatomy</text>
  <text x="341" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Sample ➔ Evaluate ➔</text>
  <text x="341" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Improve Iterative Loop</text>

  <rect x="413" y="10" width="128" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="477" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">4. Bellman Consistency</text>
  <text x="477" y="52" font-size="8.2" fill="#475569" text-anchor="middle">The 4 Value Functions</text>
  <text x="477" y="66" font-size="8.2" fill="#475569" text-anchor="middle">1-Step Lookahead Target</text>

  <rect x="549" y="10" width="136" height="70" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>
  <text x="617" y="36" font-size="9" font-weight="700" fill="#334155" text-anchor="middle">5. RL Taxonomy</text>
  <text x="617" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Sample Efficiency vs.</text>
  <text x="617" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Stability Trade-Off</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: The Markov Decision Process (MDP) De-Mystified</h2>
<p>
  <b>(Slides 3–9)</b> To optimize decisions with mathematics, we must model the world as a mathematical object. Prof. Levine builds this up in three progressive stages:
</p>
<ol>
  <li><b>Markov Chain:</b> A sequence of random states $s_1, s_2, \dots$ governed by a transition matrix $\mathcal{P}(s_{t+1}|s_t)$. No actions, no rewards—just physics rolling forward.</li>
  <li><b>Markov Decision Process (MDP):</b> Add an agent that injects decisions $a_t \sim \pi(a_t|s_t)$ and receives scalar rewards $r(s_t, a_t)$.</li>
  <li><b>Partially Observable MDP (POMDP):</b> The agent cannot see the true state $s_t$; it only receives imperfect sensory observations $o_t \sim \mathcal{O}(o_t|s_t)$.</li>
</ol>

<h3>1.1 The "Goldfish Memory" Rule: The Markov Property</h3>
<div class="math-box">
  <div class="callout-title">The Formal Markov Property</div>
  <p>
    A system satisfies the Markov Property if the transition probability to the next state depends <b>only on the current state and action</b>, and is conditionally independent of all historical states and actions:
    $$\Pr(s_{t+1} \mid s_t, a_t, s_{t-1}, a_{t-1}, \dots, s_0, a_0) = \Pr(s_{t+1} \mid s_t, a_t)$$
  </p>
</div>

<div class="robotics">
  <div class="callout-title">Robotics Implication: State Representation Engineering</div>
  <p>
    If you only feed your neural network the robot blade's Cartesian position $(x, y, z)$, <b>you violate the Markov property!</b> Why? Because seeing a blade at height $z = 3\text{ cm}$ tells the policy nothing about whether the knife is currently speeding downward at $50\text{ mm/s}$ or retracting upward. 
    To make the state strictly Markovian, you must include <b>first-order velocities</b> $(\dot{x}, \dot{y}, \dot{z})$, joint angular rates $\dot{q}$, and contact force derivatives $\dot{F}_z$.
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 2 -->
<h2>Part 2: Defining the RL Objective &amp; The Markov Chain View</h2>
<p>
  <b>(Slides 10–16)</b> What does it mean for an algorithm to "learn"? It means tuning policy network parameters $\theta$ to maximize the expected total return over entire trajectories $\tau$:
</p>

<div class="formula">
  $$\theta^* = \arg\max_\theta J(\theta) = \arg\max_\theta \mathbb{E}_{\tau \sim p_\theta(\tau)} \left[ \sum_{t=0}^T r(s_t, a_t) \right]$$
</div>

<h3>2.1 Why Immediate Greedy Actions Fail</h3>
<p>
  In Slide 11, Levine illustrates this with an autonomous vehicle crash: if a car is traveling at 120 km/h toward a concrete wall, slamming the brakes 2 meters away is the "best" immediate action, but the vehicle will still crash! The fatal error was committed 10 seconds earlier when the car decided to accelerate into a blind corner.
</p>

<div class="robotics">
  <div class="callout-title">Robotics Slicing: The Cuticle Rupture Analogy</div>
  <p>
    When slicing soft fruit or biological tissue, the blade presses against elastic skin. If the policy acts greedily to maximize instantaneous downward penetration, it pushes down with 15 Newtons. At step $t = 50$, the cuticle suddenly fractures. Because mechanical resistance vanishes in under 5 milliseconds, the knife violently accelerates downward, crushing the specimen.
    <b>RL prevents this:</b> It trains the policy to modulate impedance, initiate sawing motions, and increase damping <i>before</i> the fracture point because RL optimizes for the <b>cumulative trajectory reward</b>, not the instantaneous step reward.
  </p>
</div>

<h3>2.2 The Markov Chain View: Trajectory Distribution vs. State Marginal</h3>
<p>
  In Slide 12, Levine asks: <i>"Is there another way to write the objective without sampling entire trajectories?"</i>
  By the <b>linearity of expectation</b>, the expectation of a sum equals the sum of the expectations:
</p>

<div class="formula">
  $$J(\theta) = \mathbb{E}_{\tau \sim p_\theta(\tau)} \left[ \sum_{t=0}^T r(s_t, a_t) \right] = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t) \sim p_\theta(s_t, a_t)} \big[ r(s_t, a_t) \big]$$
</div>

<p>
  In infinite-horizon discounted problems, we can define the <b>discounted state-action stationary distribution</b>:
  $$\rho_\theta(s, a) = (1 - \gamma) \sum_{t=0}^\infty \gamma^t \Pr(s_t = s, a_t = a \mid \pi_\theta)$$
  This allows rewriting the entire RL objective as an expectation over a single stationary distribution:
  $$J(\theta) = \frac{1}{1 - \gamma} \mathbb{E}_{(s, a) \sim \rho_\theta(s, a)} \big[ r(s, a) \big]$$
</p>

<!-- SVG Diagram: Trajectory Chain -->
<div class="diagram-container">
<svg width="600" height="75" viewBox="0 0 600 75">
  <rect x="20" y="10" width="100" height="55" rx="6" fill="#f1f5f9" stroke="#475569" stroke-width="1.5"/>
  <text x="70" y="32" font-size="11" font-weight="700" fill="#0f172a" text-anchor="middle">Step t = 1</text>
  <text x="70" y="52" font-size="9.5" fill="#2563eb" text-anchor="middle">(s₁, a₁)</text>

  <line x1="120" y1="37" x2="220" y2="37" stroke="#0284c7" stroke-width="2"/>
  <polygon points="220,37 212,32 212,42" fill="#0284c7"/>
  <text x="170" y="28" font-size="8" fill="#64748b" text-anchor="middle">Physics × Policy</text>

  <rect x="220" y="10" width="100" height="55" rx="6" fill="#f1f5f9" stroke="#475569" stroke-width="1.5"/>
  <text x="270" y="32" font-size="11" font-weight="700" fill="#0f172a" text-anchor="middle">Step t = 2</text>
  <text x="270" y="52" font-size="9.5" fill="#2563eb" text-anchor="middle">(s₂, a₂)</text>

  <line x1="320" y1="37" x2="420" y2="37" stroke="#0284c7" stroke-width="2"/>
  <polygon points="420,37 412,32 412,42" fill="#0284c7"/>
  <text x="370" y="28" font-size="8" fill="#64748b" text-anchor="middle">Physics × Policy</text>

  <rect x="420" y="10" width="100" height="55" rx="6" fill="#f1f5f9" stroke="#475569" stroke-width="1.5"/>
  <text x="470" y="32" font-size="11" font-weight="700" fill="#0f172a" text-anchor="middle">Step t = 3</text>
  <text x="470" y="52" font-size="9.5" fill="#2563eb" text-anchor="middle">(s₃, a₃)</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 2.3 -->
<h3>2.3 Continuous Action Parametrization &amp; The Tanh Change of Variables</h3>
<p>
  In physical robotics, actions are continuous torques or velocity setpoints $a \in \mathbb{R}^{d_a}$. We parameterize the policy as a multivariate Gaussian $\pi_\theta(u|s) = \mathcal{N}(\mu_\theta(s), \Sigma_\theta(s))$.
  To enforce real-world physical limits (e.g. joint torques bounded in $[-1, 1]$), we apply an invertible nonlinear squashing function: $a = \tanh(u)$.
</p>

<div class="math-box">
  <div class="callout-title">Mathematical Derivation: Density Under Tanh Squashing</div>
  <p>
    By the multidimensional <b>Change of Variables Theorem</b> for continuous random variables:
    $$P(a \mid s) = P(u \mid s) \cdot \left| \det \left( \frac{\partial a}{\partial u} \right) \right|^{-1}$$
    Since the squashing transformation $a_i = \tanh(u_i)$ acts element-wise, the Jacobian matrix $J = \frac{\partial a}{\partial u}$ is purely diagonal:
    $$J_{ii} = \frac{d}{du_i} \tanh(u_i) = 1 - \tanh^2(u_i)$$
    The determinant of a diagonal matrix is simply the product of its diagonal entries:
    $$\det(J) = \prod_{i=1}^{d_a} \big( 1 - \tanh^2(u_i) \big)$$
    Taking the natural logarithm yields the exact log-probability correction:
    $$\log \pi(a \mid s) = \log \mu(u \mid s) - \sum_{i=1}^{d_a} \log \big( 1 - \tanh^2(u_i) + \epsilon \big)$$
    where $\epsilon = 10^{-6}$ provides numerical stabilization against floating point underflow.
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 3 -->
<h2>Part 3: The Anatomy of an RL Algorithm</h2>
<p>
  <b>(Slides 17–21)</b> Every RL algorithm operates on a 3-step engine:
</p>

<!-- SVG Diagram: The 3-Step Engine -->
<div class="diagram-container">
<svg width="640" height="120" viewBox="0 0 640 120">
  <rect x="10" y="25" width="185" height="65" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="102" y="48" font-size="9.5" font-weight="800" fill="#1e40af" text-anchor="middle">1. GENERATE SAMPLES</text>
  <text x="102" y="65" font-size="8.2" fill="#475569" text-anchor="middle">Run policy in environment</text>
  <text x="102" y="78" font-size="8" fill="#64748b" text-anchor="middle">Collect D = {(s, a, r, s')}</text>

  <line x1="195" y1="57" x2="230" y2="57" stroke="#94a3b8" stroke-width="2"/>
  <polygon points="230,57 222,52 222,62" fill="#94a3b8"/>

  <rect x="230" y="25" width="185" height="65" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
  <text x="322" y="48" font-size="9.5" font-weight="800" fill="#92400e" text-anchor="middle">2. EVALUATE RETURN</text>
  <text x="322" y="65" font-size="8.2" fill="#475569" text-anchor="middle">Fit Value Function V(s)</text>
  <text x="322" y="78" font-size="8" fill="#64748b" text-anchor="middle">or estimate Advantage A(s,a)</text>

  <line x1="415" y1="57" x2="450" y2="57" stroke="#94a3b8" stroke-width="2"/>
  <polygon points="450,57 442,52 442,62" fill="#94a3b8"/>

  <rect x="450" y="25" width="185" height="65" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="542" y="48" font-size="9.5" font-weight="800" fill="#065f46" text-anchor="middle">3. IMPROVE POLICY</text>
  <text x="542" y="65" font-size="8.2" fill="#475569" text-anchor="middle">Policy Gradient Ascent or</text>
  <text x="542" y="78" font-size="8" fill="#64748b" text-anchor="middle">Argmax over Q(s, a)</text>

  <path d="M 542,90 L 542,110 L 102,110 L 102,90" fill="none" stroke="#2563eb" stroke-width="1.8" stroke-dasharray="4,4"/>
  <polygon points="102,90 97,98 107,98" fill="#2563eb"/>
</svg>
</div>

<h3>3.1 Where is the Computational Bottleneck?</h3>
<ul>
  <li><b>On a Real Physical Robot:</b> Step 1 (Sampling) is the catastrophic bottleneck. Time runs at $1\times$ real speed. Collecting 100,000 physical cuts requires <b>11.5 days</b> of non-stop operation, blade wear, and mechanical overheating.</li>
  <li><b>In GPU Physics Simulators (Isaac Lab / Isaac Gym):</b> Step 1 is parallelized across <b>4,096 parallel GPU environments</b>, running at <b>10,000× real time</b>. The bottleneck shifts entirely to Step 2 and Step 3: PyTorch gradient backpropagation on the tensor cores!</li>
</ul>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 4 -->
<h2>Part 4: Value Functions, Q-Functions &amp; Bellman Self-Consistency</h2>
<p>
  <b>(Slides 22–26 &amp; Spinning Up ch07)</b> In *Spinning Up in Deep RL*, Joshua Achiam emphasizes that value functions are central because they obey <b>Bellman Self-Consistency</b>: the value of your starting point equals the immediate reward plus the value of wherever you land.
</p>

<h3>4.1 The 4 Core Value Functions</h3>
<table>
  <thead>
    <tr>
      <th style="width: 20%;">Function</th>
      <th style="width: 32%;">Mathematical Definition</th>
      <th style="width: 48%;">Physical Role in Robotic Manipulation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>On-Policy State Value</b><br>$V^\pi(s)$</td>
      <td>$$\mathbb{E}_{\tau \sim \pi} \left[ \sum_{t=0}^\infty \gamma^t r_t \;\middle|\; s_0 = s \right]$$</td>
      <td>Expected total cut score if the knife is currently at state $s$ and continues following current policy $\pi$.</td>
    </tr>
    <tr>
      <td><b>On-Policy Action Value</b><br>$Q^\pi(s, a)$</td>
      <td>$$\mathbb{E}_{\tau \sim \pi} \left[ \sum_{t=0}^\infty \gamma^t r_t \;\middle|\; s_0 = s, a_0 = a \right]$$</td>
      <td>Expected score if the knife takes specific action $a$ right now, and then continues following policy $\pi$.</td>
    </tr>
    <tr>
      <td><b>Optimal State Value</b><br>$V^*(s)$</td>
      <td>$$\max_\pi V^\pi(s) = \max_a Q^*(s, a)$$</td>
      <td>The absolute highest achievable cut quality possible from state $s$ under the perfect policy $\pi^*$.</td>
    </tr>
    <tr>
      <td><b>Optimal Action Value</b><br>$Q^*(s, a)$</td>
      <td>$$\max_\pi Q^\pi(s, a)$$</td>
      <td>The highest achievable score starting from state $s$, taking action $a$, and acting optimally thereafter.</td>
    </tr>
  </tbody>
</table>

<h3>4.2 The Bellman Equations</h3>
<div class="formula" style="border: 2px solid #3b82f6; background: #eff6ff;">
  <b>Bellman Expectation Equation for V:</b><br>
  $$V^\pi(s) = \mathbb{E}_{a \sim \pi(\cdot|s),\, s' \sim \mathcal{P}(\cdot|s, a)} \left[ r(s, a) + \gamma V^\pi(s') \right]$$
</div>
<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>Bellman Optimality Equation for Q:</b><br>
  $$Q^*(s, a) = \mathbb{E}_{s' \sim \mathcal{P}(\cdot|s, a)} \left[ r(s, a) + \gamma \max_{a'} Q^*(s', a') \right]$$
</div>

<h3>4.3 Theoretical Proof: Bellman Contraction Mapping &amp; Geometric Convergence</h3>
<p>
  Why does repeatedly applying the Bellman equation converge to the true value function?
  Define the <b>Bellman Expectation Operator</b> $\mathcal{T}^\pi: \mathbb{R}^{|\mathcal{S}|} \to \mathbb{R}^{|\mathcal{S}|}$:
  $$(\mathcal{T}^\pi V)(s) = \sum_{a} \pi(a \mid s) \left[ \mathcal{R}(s, a) + \gamma \sum_{s'} \mathcal{P}(s' \mid s, a) V(s') \right]$$
</p>

<div class="math-box">
  <div class="callout-title">Theorem: γ-Contraction in Infinity Norm</div>
  <p>
    For any two arbitrary value functions $V_1, V_2 \in \mathbb{R}^{|\mathcal{S}|}$:
    $$\| \mathcal{T}^\pi V_1 - \mathcal{T}^\pi V_2 \|_\infty \le \gamma \| V_1 - V_2 \|_\infty$$
    <b>Proof:</b> For any state $s$:
    $$|(\mathcal{T}^\pi V_1)(s) - (\mathcal{T}^\pi V_2)(s)| = \left| \gamma \sum_a \pi(a|s) \sum_{s'} \mathcal{P}(s'|s,a) [V_1(s') - V_2(s')] \right|$$
    $$\le \gamma \sum_a \pi(a|s) \sum_{s'} \mathcal{P}(s'|s,a) |V_1(s') - V_2(s')| \le \gamma \|V_1 - V_2\|_\infty \sum_a \pi(a|s) \sum_{s'} \mathcal{P}(s'|s,a)$$
    Since probabilities sum to 1, the sums evaluate to 1:
    $$|(\mathcal{T}^\pi V_1)(s) - (\mathcal{T}^\pi V_2)(s)| \le \gamma \|V_1 - V_2\|_\infty$$
    Taking the supremum over all $s$ gives $\| \mathcal{T}^\pi V_1 - \mathcal{T}^\pi V_2 \|_\infty \le \gamma \| V_1 - V_2 \|_\infty$.
  </p>
</div>

<p>
  By the <b>Banach Fixed-Point Theorem</b>, any contraction mapping on a complete metric space possesses a <b>unique fixed point</b> $V^\pi$ such that $\mathcal{T}^\pi V^\pi = V^\pi$, and iterative application converges at an exponential geometric rate:
  $$\| V_k - V^\pi \|_\infty \le \gamma^k \| V_0 - V^\pi \|_\infty$$
</p>

<h3>4.4 Matrix Formulation &amp; Closed-Form Analytical Solution</h3>
<p>
  In finite/tabular MDPs with $|\mathcal{S}|$ states, the Bellman expectation equation can be written as a compact matrix-vector linear equation:
  $$V^\pi = R^\pi + \gamma P^\pi V^\pi$$
  where $R^\pi \in \mathbb{R}^{|\mathcal{S}|}$ has entries $R^\pi(s) = \sum_a \pi(a|s) \mathcal{R}(s, a)$, and $P^\pi \in \mathbb{R}^{|\mathcal{S}| \times |\mathcal{S}|}$ has entries $P^\pi(s, s') = \sum_a \pi(a|s) \mathcal{P}(s'|s, a)$.
  Rearranging gives:
  $$(I - \gamma P^\pi) V^\pi = R^\pi \implies V^\pi = (I - \gamma P^\pi)^{-1} R^\pi$$
  Because $P^\pi$ is a row-stochastic matrix (eigenvalues $\le 1$) and $\gamma < 1$, the matrix $(I - \gamma P^\pi)$ is strictly invertible!
</p>

<div class="callout silent-bug">
  <div class="callout-title">Spinning Up Bug Alert: The [N] vs [N, 1] Tensor Broadcasting Trap</div>
  <p>
    Joshua Achiam highlights this as the #1 silent bug in RL implementations:
    If `rewards` has shape `[N]` (1D) and `next_values` has shape `[N, 1]` (2D), computing `targets = rewards + gamma * next_values` in PyTorch does NOT raise an error! Instead, Python broadcasts the two shapes into an <b>[N, N] matrix</b>! The Critic trains on random pairwise broadcasted values, loss stays finite, but the policy never learns. Always ensure shapes are strictly aligned using `.view(-1, 1)` or `.squeeze()`.
  </p>
</div>

<h3>4.5 The Deadly Triad in Value Estimation</h3>
<p>
  Richard Sutton and Andrew Barto formalized the <b>Deadly Triad</b>: when an RL algorithm combines three elements simultaneously, value estimation can diverge to infinity:
</p>
<ol>
  <li><b>Function Approximation:</b> Using neural networks $V_\phi(s)$ instead of tabular lookup tables.</li>
  <li><b>Bootstrapping:</b> Updating value estimates based on other value estimates: $y = r + \gamma V_\phi(s')$ (as in TD learning and Bellman equations).</li>
  <li><b>Off-Policy Training:</b> Training on data generated by an older or different behavior policy $\beta(a|s) \ne \pi(a|s)$ (as in replay buffers).</li>
</ol>
<p>
  <i>Understanding the Deadly Triad is why modern algorithms require specific stabilization anchors: target networks, double Q-learning, and clipping (explored in Lectures 8 and 10).</i>
</p>

<div class="code-container">
<pre><span class="code-comment"># Complete Safe Bellman Target Implementation</span>
<span class="code-keyword">import</span> torch

<span class="code-keyword">def</span> <span class="code-func">compute_bellman_targets</span>(rewards: torch.Tensor, next_values: torch.Tensor, dones: torch.Tensor, gamma: float):
    rewards = rewards.view(-1, 1)
    next_values = next_values.view(-1, 1)
    dones = dones.view(-1, 1)
    <span class="code-keyword">assert</span> rewards.shape == next_values.shape == dones.shape, \
        <span class="code-string">f"Shape mismatch: {rewards.shape} vs {next_values.shape}"</span>
    <span class="code-keyword">return</span> rewards + gamma * (1.0 - dones) * next_values
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 5 -->
<h2>Part 5: Taxonomy of RL Algorithms — Which One for Your Robotics Setup?</h2>
<p>
  <b>(Slides 27–41)</b> Levine organizes all model-free algorithms along two fundamental axes: <b>Sample Efficiency</b> and <b>Stability</b>.
</p>

<!-- SVG Diagram: The Spectrum -->
<div class="diagram-container">
<svg width="660" height="110" viewBox="0 0 660 110">
  <line x1="50" y1="45" x2="610" y2="45" stroke="#cbd5e1" stroke-width="4"/>

  <circle cx="80" cy="45" r="9" fill="#0284c7"/>
  <text x="80" y="25" font-size="9" font-weight="700" fill="#0369a1" text-anchor="middle">Model-Based</text>
  <text x="80" y="70" font-size="7.5" fill="#475569" text-anchor="middle">Dyna, MBPO</text>
  <text x="80" y="82" font-size="7.5" fill="#059669" text-anchor="middle">Most Efficient</text>

  <circle cx="240" cy="45" r="9" fill="#3b82f6"/>
  <text x="240" y="25" font-size="9" font-weight="700" fill="#1d4ed8" text-anchor="middle">Off-Policy Q-Learning</text>
  <text x="240" y="70" font-size="7.5" fill="#475569" text-anchor="middle">DQN, TD3</text>
  <text x="240" y="82" font-size="7.5" fill="#d97706" text-anchor="middle">Can Diverge</text>

  <circle cx="400" cy="45" r="11" fill="#10b981" stroke="#047857" stroke-width="2"/>
  <text x="400" y="22" font-size="9.5" font-weight="800" fill="#047857" text-anchor="middle">Actor-Critic (SAC)</text>
  <text x="400" y="70" font-size="7.5" fill="#475569" text-anchor="middle">Soft Actor-Critic</text>
  <text x="400" y="82" font-size="7.5" fill="#047857" font-weight="700" text-anchor="middle">★ Great for Robots</text>

  <circle cx="560" cy="45" r="11" fill="#10b981" stroke="#047857" stroke-width="2"/>
  <text x="560" y="22" font-size="9.5" font-weight="800" fill="#047857" text-anchor="middle">Policy Gradient (PPO)</text>
  <text x="560" y="70" font-size="7.5" fill="#475569" text-anchor="middle">PPO / SkRL</text>
  <text x="560" y="82" font-size="7.5" fill="#047857" font-weight="700" text-anchor="middle">★ Most Stable / Standard</text>
</svg>
</div>

<h3>5.1 The Two Fundamental Trade-Offs</h3>
<table>
  <thead>
    <tr>
      <th style="width: 22%;">Dimension</th>
      <th style="width: 38%;">Sample Efficiency</th>
      <th style="width: 40%;">Stability &amp; Convergence</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>On-Policy (PPO)</b></td>
      <td><b>Lowest:</b> Discards data after each batch. Needs millions of simulator steps.</td>
      <td><b>Highest:</b> True gradient ascent on clipped objective. Extremely forgiving to tune. <i>(Isaac Lab compensates via 4,096 parallel GPU envs!)</i></td>
    </tr>
    <tr>
      <td><b>Off-Policy (SAC)</b></td>
      <td><b>High:</b> Re-uses old trajectories from a replay buffer over and over.</td>
      <td><b>Moderate:</b> Needs careful tuning of entropy temperature $\alpha$ and target network updates to avoid overestimating Q-values.</td>
    </tr>
    <tr>
      <td><b>Pure Q-Learning (DQN)</b></td>
      <td>Moderate</td>
      <td><b>Unstable on Continuous Arms:</b> Computing argmax over continuous actions (torques) is mathematically intractable.</td>
    </tr>
    <tr>
      <td><b>Model-Based RL</b></td>
      <td><b>Highest:</b> Tries to learn a neural network predicting physics transitions.</td>
      <td><b>Brittle:</b> Compounding model simulation errors lead to physical exploitation and catastrophic real-world failure.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 6 -->
<h2>Part 6: Interactive Tablet Self-Test Quiz</h2>

<div class="quiz-box">
  <div class="quiz-q">Question 1: If an environment state consists only of the knife's 3D Cartesian position [x, y, z], does this satisfy the Markov property for cutting soft fruit?</div>
  <div class="quiz-a">
    <b>Answer:</b> No. A static position does not tell the robot whether the knife is accelerating downward or moving laterally, nor does it capture the accumulated elastic strain inside the tomato cuticle. To satisfy the Markov property, the state must include knife velocity ($\dot{z}$), lateral sawing speed, and TacBlade force derivatives ($\dot{F}_z$).
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: In Bellman equations, what is the conceptual difference between $V^\pi(s)$ and $Q^\pi(s, a)$?</div>
  <div class="quiz-a">
    <b>Answer:</b> $V^\pi(s)$ is the expected return from state $s$ when following policy $\pi$ immediately. $Q^\pi(s, a)$ evaluates taking a specific designated action $a$ first, and only following policy $\pi$ on subsequent steps. The difference $A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$ tells us whether action $a$ was superior to the policy's average choice.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: Why does Isaac Lab prefer on-policy PPO over off-policy SAC, despite PPO being less sample-efficient?</div>
  <div class="quiz-a">
    <b>Answer:</b> On GPU simulators like Isaac Lab, sample generation is virtually free (generating 260,000 steps in 50 ms across 4,096 parallel environments). PPO's stability, lack of memory-heavy replay buffers, and clipped objective allow straightforward scaling to massive parallel streams, whereas off-policy SAC causes GPU memory bottlenecks when managing replay buffers for 4,096 concurrent environments.
  </div>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 7: THESIS DEFENSE MASTER CHEATSHEET -->
<h2>Part 7: Thesis Defense Master Cheatsheet (Lecture 4 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Question: "Why did you use Reinforcement Learning instead of standard Model Predictive Control (MPC)?"</div>
  <p>
    <b>The Flawless Answer:</b> <i>"MPC requires an exact real-time analytical physics model of the tissue contact dynamics: $\dot{x} = f(x, u)$. When slicing soft deformable fruits or biological tissues, finite element modeling (FEM) or non-linear viscoelastic constitutive laws cannot be computed in real time at 100 Hz. RL bypasses the need for an explicit analytical model: it learns a parameterized feedback policy $\pi_\theta(a|s)$ entirely through simulated interaction and evaluative reward feedback, while training in Isaac Lab across thousands of parallel environments."</i>
  </p>
</div>

<div class="callout robotics">
  <div class="callout-title">Question: "Why is your policy trained on Value Functions rather than pure Monte Carlo Rollouts?"</div>
  <p>
    <b>The Flawless Answer:</b> <i>"Pure Monte Carlo rollouts (like REINFORCE) exhibit massive gradient variance because they must sum rewards all the way to episode termination ($T=500$). By utilizing Bellman Self-Consistency, the Critic $V_\phi(s)$ provides a 1-step bootstrapping target: $y_t = r_t + \gamma V_\phi(s_{t+1})$. This dramatically shrinks variance, enabling stable training with orders of magnitude fewer environment interactions."</i>
  </p>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    pdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture4_Beginner_Guide.pdf"
    backup_path = "/home/omen/Downloads/CS285_Lecture4_Beginner_Guide.pdf"
    render_utils.build_pdf(html_content, pdf_path, backup_path)
