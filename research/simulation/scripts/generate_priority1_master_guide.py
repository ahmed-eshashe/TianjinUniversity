import os
import sys

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Priority1_Master_Robotics_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Priority1_Master_Robotics_Guide.pdf"

html_doc = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Priority 1 Master Guide: Robotics Reinforcement Learning Blueprint</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {
      content: "CS285 Priority 1 Master Guide • Robotics RL Blueprint";
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
    line-height: 1.55;
    font-size: 9.6pt;
  }

  /* Cover Block */
  .cover-header {
    border-bottom: 3px solid #2563eb;
    padding-bottom: 16px;
    margin-bottom: 20px;
  }
  .series-tag {
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    font-weight: 700;
    font-size: 8.5pt;
    padding: 3px 10px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
  }
  h1 {
    color: #0f172a;
    font-size: 21pt;
    font-weight: 800;
    margin: 0 0 6px 0;
    line-height: 1.2;
  }
  .subtitle {
    color: #334155;
    font-size: 10.5pt;
    margin: 0 0 12px 0;
    font-weight: 500;
  }
  .meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    font-size: 8.5pt;
    color: #475569;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 8px 12px;
    border-radius: 6px;
  }

  /* Headings */
  h2 {
    color: #1e3a8a;
    font-size: 12.5pt;
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 10px;
    page-break-after: avoid;
  }
  .module-header {
    page-break-before: always;
    margin-top: 0;
    padding-top: 4px;
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

  /* Callout Boxes */
  .callout {
    padding: 8px 12px;
    margin: 9px 0;
    border-radius: 5px;
    font-size: 9.1pt;
    page-break-inside: avoid;
  }
  .callout p {
    margin: 0;
  }
  .callout-title {
    font-weight: 700;
    font-size: 8.7pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
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

  /* Formula display */
  .formula {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 6px 10px;
    margin: 7px 0;
    text-align: center;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 9.8pt;
    color: #0f172a;
    page-break-inside: avoid;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 9px 0;
    font-size: 8.6pt;
    page-break-inside: avoid;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 5px 7px;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 4px 7px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }
  tr:nth-child(even) td {
    background: #f8fafc;
  }

  .diagram-container {
    text-align: center;
    margin: 9px 0;
    page-break-inside: avoid;
  }

  .page-break {
    page-break-before: always;
  }

  .badge {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: 600;
  }
  .badge-code { background: #e2e8f0; color: #334155; font-family: monospace; }
</style>
</head>
<body>

<!-- Cover Block -->
<div class="cover-header">
  <span class="series-tag">UC Berkeley CS 185/285 • Priority 1 Complete Master Compendium</span>
  <h1>Robotics Reinforcement Learning Foundations</h1>
  <div class="subtitle">A Rigorous, Pedagogical Manual for Dual-Arm Robotic Manipulation &amp; Contact Control (Paper 1: Adaptive Soft Fruit Slicing with PPO / SAC in NVIDIA Isaac Lab via SkRL)</div>
  <div class="meta-grid">
    <div>
      <b>Lectures Unified:</b> CS285 L01, L04, L05, L06, L08, L10<br>
      <b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)
    </div>
    <div>
      <b>Research Lab:</b> DEX-ROB Lab, Tianjin University (Prof. Shan An)<br>
      <b>Environment &amp; Stack:</b> NVIDIA Isaac Lab / PhysX 5 • SkRL Framework • PyTorch
    </div>
  </div>
</div>

<!-- EXECUTIVE ROADMAP -->
<div class="callout intuition">
  <div class="callout-title">🧭 How This Master Guide Organizes Priority 1 Curriculum</div>
  <p>
    This master reference document synthesizes the six core lectures of UC Berkeley CS285 into an integrated, end-to-end framework. 
    It bridges theoretical foundations (Lectures 1 &amp; 4), direct policy optimization (Lecture 5), actor-critic variance reduction (Lecture 6), 
    off-policy continuous control (Lecture 8), and trust-region stabilization (Lecture 10). It culminates in a complete operational blueprint 
    for your dual-arm robotic slicing task, the 12-dimension algorithm comparison matrix, and a 10-question defense cheatsheet.
  </p>
</div>

<!-- MODULE 1: LECTURE 1 -->
<h2>Module 1: The Foundations &amp; The Robotics Closed Loop (Lecture 1)</h2>
<p>
  <b>(CS285 Lecture 1 • Video ID: DD8APgTEix4)</b> Welcome to the mathematical study of sequential decision making. 
  In traditional robotics, control laws are derived from explicit kinematic and dynamic models ($F = Ma$). 
  However, when interacting with non-linear, viscoelastic, fracturing materials (such as ripe fruits), analytical models fail.
</p>

<h3>1.1 Why Reinforcement Learning Over Supervised Imitation?</h3>
<p>
  In <b>Supervised Learning</b> (Behavioral Cloning), an expert teleoperates the robot and records state-action pairs $(s, a)$. The network minimizes $\mathcal{L}_{\text{BC}}(\theta) = \mathbb{E}_{(s, a) \sim \mathcal{D}_{\text{expert}}}[\|a - \pi_\theta(s)\|^2]$. While intuitive, this approach suffers from a catastrophic mathematical vulnerability: <b>Covariate Shift</b>.
</p>

<div class="callout math-box">
  <div class="callout-title">📐 Ross &amp; Bagnell (2011) Compounding Error Proof</div>
  <p>
    Let the probability of the learned policy making an $\epsilon$-mistake on the expert training distribution be $\epsilon$:
  </p>
  <div class="formula">
    $$\mathbb{P}_{s \sim d_{\pi^*}}(\pi_\theta(s) \neq \pi^*(s)) \le \epsilon$$
  </div>
  <p>
    Under open-loop behavioral cloning, if an error occurs at time step $t$, the robot enters an unvisited state space $s \notin \mathcal{D}_{\text{expert}}$. Because the policy was never trained on recovery actions, all subsequent actions can fail. The expected total trajectory error over time horizon $T$ compounds quadratically:
  </p>
  <div class="formula">
    $$\mathbb{E}[\text{Errors}_{1:T}] \le \sum_{t=1}^T \epsilon \cdot (T - t) \approx \frac{1}{2} \epsilon T^2 = \mathcal{O}(\epsilon T^2)$$
  </div>
  <p>
    In contrast, <b>Reinforcement Learning operates in closed-loop</b>, exploring its own induced distribution $d^{\pi_\theta}(s)$. When the knife slips or the fruit deforms unpredictably, the agent actively learns corrective policies, bounding error strictly to <b>$\mathcal{O}(\epsilon T)$</b>.
  </p>
</div>

<!-- Diagram: The RL Closed Loop in Isaac Lab -->
<div class="diagram-container">
<svg width="600" height="95" viewBox="0 0 600 95">
  <rect x="20" y="15" width="220" height="65" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="130" y="38" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">ROBOT BRAIN (Agent)</text>
  <text x="130" y="55" font-size="8.5" fill="#475569" text-anchor="middle">PyTorch Policy Network (SkRL)</text>
  <text x="130" y="68" font-size="8" fill="#64748b" text-anchor="middle">MLP [256, 256] on RTX 5060 GPU</text>

  <!-- Top Arrow: Action -->
  <path d="M 240,32 L 350,32" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="350,32 342,27 342,37" fill="#2563eb"/>
  <text x="295" y="24" font-size="8.5" font-weight="700" fill="#1d4ed8" text-anchor="middle">Action $a_t \in \mathbb{R}^6$</text>
  <text x="295" y="44" font-size="7.5" fill="#64748b" text-anchor="middle">(Feed rate, $\Delta K$, $\Delta D$)</text>

  <rect x="360" y="15" width="220" height="65" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="470" y="38" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">PHYSICAL WORLD (Env)</text>
  <text x="470" y="55" font-size="8.5" fill="#475569" text-anchor="middle">Isaac Lab / PhysX 5 Simulation</text>
  <text x="470" y="68" font-size="8" fill="#64748b" text-anchor="middle">Deformable Tomato &amp; Blade Contacts</text>

  <!-- Bottom Arrow: State & Reward -->
  <path d="M 360,68 L 240,68" fill="none" stroke="#10b981" stroke-width="2"/>
  <polygon points="240,68 248,63 248,73" fill="#10b981"/>
  <text x="300" y="82" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">Observation $s_t \in \mathbb{R}^{33}$ &amp; Reward $r_t$</text>
</svg>
</div>

<h3>1.2 The Credit Assignment Problem &amp; Dense Shaping</h3>
<p>
  Prof. Levine highlights the fundamental challenge of <b>Credit Assignment</b>: when an episode consists of 500 robot control steps, and the tomato bursts at step 480, which specific millisecond torque spike was responsible?
</p>
<div class="callout intuition">
  <div class="callout-title">💡 Plain English: The Exam Analogy</div>
  <p>
    If you study all semester and receive an <b>F</b> on the final exam, that single terminal letter grade does not tell you whether you failed because you slept late on Tuesday or because you misunderstood Chapter 3. In RL, sparse terminal rewards require millions of sample trajectories to backpropagate credit. We solve this through <b>Dense Progress Shaping</b> and <b>Value Functions</b> that score state quality at every microsecond.
  </p>
</div>

<div class="page-break"></div>

<!-- MODULE 2: LECTURE 4 -->
<h2 class="module-header">Module 2: The Core Mathematics &amp; MDP Formulation (Lecture 4)</h2>
<p>
  <b>(CS285 Lecture 4 • Video ID: FcpIul7rAEE)</b> Lecture 4 establishes the formal mathematical foundation of Reinforcement Learning. Every physical quantity in the robotics laboratory corresponds to a precise mathematical object.
</p>

<h3>2.1 The Markov Decision Process: $\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma, \rho_0 \rangle$</h3>
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Symbol</th>
      <th style="width: 25%;">Formal Math</th>
      <th style="width: 60%;">Your Paper 1 Physical Translation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>State ($s$)</b></td>
      <td>$s_t \in \mathcal{S}$</td>
      <td><b>33 numbers:</b> Dual-arm joint positions &amp; velocities (14), knife pose &amp; velocities (9), tomato pose (7), TacBlade F/T (6), acoustic burst (1).</td>
    </tr>
    <tr>
      <td><b>Action ($a$)</b></td>
      <td>$a_t \in \mathcal{A}$</td>
      <td><b>6 numbers:</b> Downward feed delta $\Delta v_z$, lateral sawing speed $v_{\text{slice}}$, vertical stiffness delta $\Delta K$, damping delta $\Delta D$, holding arm stabilization.</td>
    </tr>
    <tr>
      <td><b>Dynamics ($\mathcal{P}$)</b></td>
      <td>$P(s_{t+1} \mid s_t, a_t)$</td>
      <td><b>Isaac Sim PhysX 5 Engine:</b> Computes knife penetration, tomato deformation, friction, and outputs the next sensor state.</td>
    </tr>
    <tr>
      <td><b>Reward ($\mathcal{R}$)</b></td>
      <td>$r(s_t, a_t)$</td>
      <td><b>Scoring function:</b> Penetration progress + Sawing bonus - Crushing force penalty (&gt;8N) - Jitter penalty.</td>
    </tr>
    <tr>
      <td><b>Discount ($\gamma$)</b></td>
      <td>$\gamma = 0.99$</td>
      <td><b>Patience factor:</b> Ensures the policy plans for the complete cut rather than stopping on first skin contact.</td>
    </tr>
  </tbody>
</table>

<h3>2.2 The Markov Property &amp; Trajectory Probability Factorization</h3>
<p>
  A stochastic process satisfies the <b>Markov Property</b> if the conditional probability distribution of future states depends only upon the current state and action, and is conditionally independent of all historical states:
</p>
<div class="formula">
  $$\mathbb{P}(s_{t+1} \mid s_t, a_t, s_{t-1}, a_{t-1}, \dots, s_0, a_0) = \mathbb{P}(s_{t+1} \mid s_t, a_t)$$
</div>
<p>
  By applying the probability chain rule, the probability distribution of an entire trajectory $\tau = (s_0, a_0, s_1, a_1, \dots, s_T)$ factorizes cleanly:
</p>
<div class="formula">
  $$\mathbb{P}(\tau \mid \theta) = \rho_0(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t \mid s_t) P(s_{t+1} \mid s_t, a_t)$$
</div>

<h3>2.3 The Four Core Value Functions</h3>
<p>
  RL defines four fundamental value functions that measure future performance:
</p>
<ol>
  <li><b>State-Value Function $V^\pi(s)$:</b> Expected cumulative return starting from state $s$ following policy $\pi$:
    <div class="formula">$$V^\pi(s) = \mathbb{E}_\pi \left[ \sum_{t=0}^\infty \gamma^t r(s_t, a_t) \;\middle|\; s_0 = s \right]$$</div>
  </li>
  <li><b>Action-Value Function $Q^\pi(s, a)$:</b> Expected return starting from $s$, taking arbitrary action $a$, and thereafter following $\pi$:
    <div class="formula">$$Q^\pi(s, a) = r(s, a) + \gamma \mathbb{E}_{s' \sim P(\cdot|s,a)} [V^\pi(s')]$$</div>
  </li>
  <li><b>Optimal State-Value Function $V^*(s)$:</b> Maximum attainable return across all conceivable policies:
    <div class="formula">$$V^*(s) = \max_\pi V^\pi(s) = \max_{a \in \mathcal{A}} Q^*(s, a)$$</div>
  </li>
  <li><b>Advantage Function $A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$:</b> The relative superiority of taking action $a$ compared to the policy's average expected outcome in state $s$.
    <ul>
      <li>If <b>$A > 0$</b>: Action outperformed expectations $\rightarrow$ Increase selection probability.</li>
      <li>If <b>$A < 0$</b>: Action underperformed $\rightarrow$ Decrease selection probability.</li>
    </ul>
  </li>
</ol>

<div class="callout math-box">
  <div class="callout-title">📐 Bellman Contraction Operator &amp; Banach Fixed Point Proof</div>
  <p>
    Define the Bellman optimality backup operator $\mathcal{B}: \mathbb{R}^{|\mathcal{S}|} \to \mathbb{R}^{|\mathcal{S}|}$ on value vector $V$:
  </p>
  <div class="formula">
    $$(\mathcal{B} V)(s) = \max_{a \in \mathcal{A}} \left[ r(s, a) + \gamma \sum_{s' \in \mathcal{S}} P(s' \mid s, a) V(s') \right]$$
  </div>
  <p>
    For any two arbitrary value functions $u$ and $v$, evaluate the infinity norm difference $\|\mathcal{B} u - \mathcal{B} v\|_\infty$:
  </p>
  <div class="formula">
    $$|(\mathcal{B} u)(s) - (\mathcal{B} v)(s)| \le \gamma \max_{a \in \mathcal{A}} \sum_{s'} P(s' \mid s, a) |u(s') - v(s')| \le \gamma \|u - v\|_\infty \sum_{s'} P(s' \mid s, a) = \gamma \|u - v\|_\infty$$
  </div>
  <p>
    Taking the supremum over all states $s \in \mathcal{S}$ proves that <b>$\|\mathcal{B} u - \mathcal{B} v\|_\infty \le \gamma \|u - v\|_\infty$</b>. Since $\gamma \in [0, 1)$, $\mathcal{B}$ is a <b>strict $\gamma$-contraction mapping</b>. By the <i>Banach Fixed Point Theorem</i>, repeated application $\lim_{k \to \infty} \mathcal{B}^k V_0$ converges uniquely to the optimal value function $V^*$, independent of initial guess $V_0$.
  </p>
</div>

<div class="page-break"></div>

<!-- MODULE 3: LECTURE 5 -->
<h2 class="module-header">Module 3: Direct Policy Optimization &amp; Policy Gradients (Lecture 5)</h2>
<p>
  <b>(CS285 Lecture 5 • Video ID: S0D9REIVdg4)</b> How do we optimize neural network policy weights $\theta$ when the physical environment contains non-differentiable contact fractures? This is the core domain of <b>Policy Gradient Methods</b>.
</p>

<h3>3.1 The Fundamental Dilemma: Non-Smooth Contact Dynamics</h3>
<div class="callout warning-box">
  <div class="callout-title">⚠️ Why Analytical Backpropagation Through Physics Fails</div>
  <p>
    A tomato skin tearing under a sharp blade is an irreversible physical rupture. Dynamic friction switches discontinuously between stick and slip regimes. Attempting to backpropagate gradients $\frac{\partial s_{t+1}}{\partial a_t}$ through rigid-body contact solvers results in either zero gradients (flat plateaus) or infinite gradients (delta spikes). Policy gradients bypass this by treating the environment dynamics as a black box.
  </p>
</div>

<h3>3.2 Derivation of the Policy Gradient Theorem</h3>
<p>
  Let the expected total discounted return under policy $\pi_\theta$ be $J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} [R(\tau)] = \int \mathbb{P}(\tau \mid \theta) R(\tau) d\tau$. We differentiate directly:
</p>
<div class="formula">
  $$\nabla_\theta J(\theta) = \int \nabla_\theta \mathbb{P}(\tau \mid \theta) R(\tau) d\tau$$
</div>
<p>
  Applying the <b>Log-Derivative Trick</b> ($\nabla_\theta f(\theta) = f(\theta) \nabla_\theta \log f(\theta)$):
</p>
<div class="formula">
  $$\nabla_\theta J(\theta) = \int \mathbb{P}(\tau \mid \theta) \nabla_\theta \log \mathbb{P}(\tau \mid \theta) R(\tau) d\tau = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \nabla_\theta \log \mathbb{P}(\tau \mid \theta) R(\tau) \right]$$
</div>
<p>
  Substituting the trajectory log-probability $\log \mathbb{P}(\tau \mid \theta) = \log \rho_0(s_0) + \sum_{t=0}^{T-1} \log \pi_\theta(a_t \mid s_t) + \sum_{t=0}^{T-1} \log P(s_{t+1} \mid s_t, a_t)$, and noting that the initial distribution and transition dynamics do not depend on $\theta$:
</p>
<div class="formula">
  $$\nabla_\theta \log \mathbb{P}(\tau \mid \theta) = \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t)$$
</div>
<div class="formula">
  $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \cdot \sum_{t'=0}^{T-1} r(s_{t'}, a_{t'}) \right]$$
</div>

<h3>3.3 Continuous Gaussian Policy Score Function</h3>
<p>
  In dual-arm continuous impedance control, actions are continuous real vectors $a \sim \mathcal{N}(\mu_\theta(s), \Sigma_\theta(s))$. For a diagonal covariance matrix with $\sigma_i$:
</p>
<div class="formula">
  $$\log \pi_\theta(a \mid s) = -\frac{d}{2}\log(2\pi) - \sum_{i=1}^d \log \sigma_i - \frac{1}{2} \sum_{i=1}^d \frac{(a_i - \mu_i(s))^2}{\sigma_i^2}$$
</div>
<div class="formula">
  $$\nabla_{\mu} \log \pi_\theta(a \mid s) = \frac{a - \mu_\theta(s)}{\sigma^2}$$
</div>
<div class="callout intuition">
  <div class="callout-title">💡 Physical Interpretation of Gaussian Policy Gradients</div>
  <p>
    Notice the elegance of the gradient: $\frac{a - \mu_\theta(s)}{\sigma^2} \cdot \hat{Q}$. 
    If a trial action $a$ was higher than the mean $\mu$, and achieved positive advantage ($\hat{Q} > 0$), the product is positive, pulling the mean $\mu$ closer to $a$. If the action resulted in crushed pulp ($\hat{Q} < 0$), the product is negative, pushing the mean in the opposite direction.
  </p>
</div>

<h3>3.4 Essential Variance Reduction: Causality &amp; Optimal Baselines</h3>
<p>
  Raw REINFORCE suffers from excessive variance. Modern implementations enforce two mandatory structural transformations:
</p>
<ol>
  <li><b>Causality ("Reward-to-Go"):</b> Actions taken at step $t$ cannot influence past rewards $r_{t'}$ for $t' < t$. Past terms have expectation zero and are safely dropped:
    <div class="formula">$$\nabla_\theta J(\theta) = \mathbb{E} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \sum_{t'=t}^{T-1} \gamma^{t'-t} r(s_{t'}, a_{t'}) \right]$$</div>
  </li>
  <li><b>Expected Grad-Log-Prob (EGLP) Lemma &amp; Baselines:</b> Subtracting any state-dependent baseline $b(s)$ does not introduce bias:
    <div class="formula">$$\mathbb{E}_{a \sim \pi} [\nabla_\theta \log \pi_\theta(a \mid s) b(s)] = b(s) \int \pi_\theta(a \mid s) \frac{\nabla_\theta \pi_\theta(a \mid s)}{\pi_\theta(a \mid s)} da = b(s) \nabla_\theta \int \pi_\theta(a \mid s) da = b(s) \nabla_\theta (1) = 0$$</div>
  </li>
</ol>

<div class="page-break"></div>

<!-- MODULE 4: LECTURE 6 -->
<h2 class="module-header">Module 4: Actor-Critic Architectures &amp; GAE (Lecture 6)</h2>
<p>
  <b>(CS285 Lecture 6 • Video ID: MzIWiNzrCvw)</b> While baselines reduce variance, Monte Carlo returns still accumulate noise across long horizons. <b>Actor-Critic</b> architectures replace full rollouts with a learned Critic network.
</p>

<h3>4.1 The Dual-Network Topology</h3>
<!-- SVG Diagram: Actor-Critic Architecture -->
<div class="diagram-container">
<svg width="600" height="130" viewBox="0 0 600 130">
  <rect x="20" y="40" width="130" height="50" rx="6" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="85" y="62" font-size="10" font-weight="700" fill="#0f172a" text-anchor="middle">Sensor State $s_t$</text>
  <text x="85" y="77" font-size="8" fill="#64748b" text-anchor="middle">Vector in $\mathbb{R}^{33}$</text>

  <path d="M 150,55 L 210,25" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="210,25 201,23 206,31" fill="#2563eb"/>

  <path d="M 150,75 L 210,105" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <polygon points="210,105 206,99 201,107" fill="#f59e0b"/>

  <rect x="210" y="5" width="200" height="45" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="310" y="24" font-size="10" font-weight="700" fill="#1e40af" text-anchor="middle">THE ACTOR $\pi_\theta(a \mid s)$</text>
  <text x="310" y="38" font-size="7.5" fill="#475569" text-anchor="middle">Outputs continuous action $\mu$ and $\sigma$ ($\mathbb{R}^6$)</text>

  <rect x="210" y="80" width="200" height="45" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
  <text x="310" y="99" font-size="10" font-weight="700" fill="#92400e" text-anchor="middle">THE CRITIC $V_\phi(s)$</text>
  <text x="310" y="113" font-size="7.5" fill="#475569" text-anchor="middle">Outputs estimated future value $V(s)$ ($\mathbb{R}^1$)</text>

  <line x1="410" y1="27" x2="480" y2="27" stroke="#2563eb" stroke-width="2"/>
  <polygon points="480,27 472,22 472,32" fill="#2563eb"/>
  <text x="535" y="30" font-size="9" font-weight="700" fill="#1e40af">Robot Motors</text>

  <line x1="410" y1="102" x2="480" y2="102" stroke="#f59e0b" stroke-width="2"/>
  <polygon points="480,102 472,97 472,107" fill="#f59e0b"/>
  <text x="535" y="105" font-size="9" font-weight="700" fill="#92400e">Advantage $\hat{A}_t$</text>
</svg>
</div>

<h3>4.2 Temporal Difference (TD) Bootstrapping &amp; The Semi-Gradient Detach Rule</h3>
<p>
  The Critic approximates $V(s)$ by minimizing the mean squared Bellman error against a bootstrapped 1-step target:
</p>
<div class="formula">
  $$\mathcal{L}(\phi) = \frac{1}{2} \mathbb{E}_{(s_t, a_t, r_t, s_{t+1})} \left[ \left( r_t + \gamma V_{\phi^-}(s_{t+1}) - V_\phi(s_t) \right)^2 \right]$$
</div>
<div class="callout warning-box">
  <div class="callout-title">🛑 Crucial PyTorch Rule: Semi-Gradient Detach</div>
  <p>
    When backpropagating through the Critic loss, you must <b>detach</b> the target: <code>target = reward + gamma * critic(next_state).detach()</code>. 
    If you do not call <code>.detach()</code>, the optimizer updates the target network concurrently with the current value estimate, creating an unstable feedback loop where the network chases its own tail.
  </p>
</div>

<h3>4.3 Generalized Advantage Estimation (GAE-$\lambda$) Complete Derivation</h3>
<p>
  Define the 1-step TD residual error: $\delta_t^V = r_t + \gamma V(s_{t+1}) - V(s_t)$. Now observe the $k$-step advantage estimators:
</p>
<div class="formula">
  $$\hat{A}_t^{(1)} = \delta_t^V = r_t + \gamma V(s_{t+1}) - V(s_t)$$
  $$\hat{A}_t^{(2)} = \delta_t^V + \gamma \delta_{t+1}^V = r_t + \gamma r_{t+1} + \gamma^2 V(s_{t+2}) - V(s_t)$$
  $$\hat{A}_t^{(k)} = \sum_{l=0}^{k-1} \gamma^l \delta_{t+l}^V = \sum_{l=0}^{k-1} \gamma^l r_{t+l} + \gamma^k V(s_{t+k}) - V(s_t)$$
</div>
<p>
  GAE takes an exponentially decaying weighted average of all $k$-step estimators using parameter $\lambda \in [0, 1]$:
</p>
<div class="formula">
  $$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = (1 - \lambda) \sum_{k=1}^\infty \lambda^{k-1} \hat{A}_t^{(k)} = \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}^V$$
</div>
<div class="callout robotics">
  <div class="callout-title">⚙️ SkRL Tuning: The $\lambda = 0.95$ Sweet Spot</div>
  <p>
    Setting <b>$\lambda = 0$</b> yields pure TD(0) (minimal variance, but high bias from an imperfect critic). Setting <b>$\lambda = 1$</b> yields pure Monte Carlo (unbiased, but noisy). In your SkRL configuration, <code>gae_lambda: 0.95</code> captures 95% of the variance-reduction benefits of the Critic while eliminating persistent bootstrapping bias.
  </p>
</div>

<div class="page-break"></div>

<!-- MODULE 5: LECTURE 8 -->
<h2 class="module-header">Module 5: Continuous Control &amp; Soft Actor-Critic (Lecture 8)</h2>
<p>
  <b>(CS285 Lecture 8 • Video ID: lQaVa53pS-Q)</b> In discrete environments like Atari, Q-learning calculates $\arg\max_{a} Q(s, a)$ by simple enumeration. On continuous robotic arms, finding this maximum is a complex non-linear optimization problem.
</p>

<h3>5.1 The Continuous Action Maximization Crisis</h3>
<p>
  On a robot arm with 6-DoF continuous velocity commands $a \in [-1, 1]^6$, evaluating $\max_{a} Q(s, a)$ across infinite real vectors at 500 Hz is intractable. 
  Discretization scales exponentially ($K^6$), while sampling methods (Cross-Entropy Method) are too slow for real-time control.
</p>
<p>
  <b>The Modern Solution (Actor Maximizer):</b> Train an explicit Actor network $\pi_\theta(s)$ parameterized to directly output the action that maximizes the Critic: $\max_\theta \mathbb{E}_{s \sim \mathcal{D}} [Q_\phi(s, \pi_\theta(s))]$.
</p>

<h3>5.2 Sutton's Deadly Triad &amp; Stabilization Mechanisms</h3>
<p>
  Combining <b>Function Approximation</b> (Deep Nets), <b>Bootstrapping</b> (Bellman TD targets), and <b>Off-Policy Training</b> (Replay Buffer) leads to the <i>Deadly Triad</i>, often causing value estimates to diverge to infinity. Modern algorithms tame this via three structural pillars:
</p>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Mechanism</th>
      <th style="width: 35%;">Mathematical Formulation</th>
      <th style="width: 40%;">Physical Purpose in Robotics</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Polyak Soft Updates</b></td>
      <td>$\bar{\theta} \leftarrow \tau \theta + (1 - \tau) \bar{\theta}$ with $\tau = 0.005$</td>
      <td>Creates a stable, slow-moving target network with half-life $t_{1/2} = \frac{\ln 2}{\tau} \approx 138$ steps, preventing gradient explosion.</td>
    </tr>
    <tr>
      <td><b>Clipped Twin-Q (Double Q)</b></td>
      <td>$y = r + \gamma \min(Q_{\bar{\theta}_1}(s', a'), Q_{\bar{\theta}_2}(s', a'))$</td>
      <td>Overcomes positive maximization bias caused by Jensen's inequality: $\mathbb{E}[\max(X_1, X_2)] \ge \max(\mathbb{E}[X_1], \mathbb{E}[X_2])$.</td>
    </tr>
    <tr>
      <td><b>Experience Replay</b></td>
      <td>Sample $(s, a, r, s') \sim \mathcal{D}$</td>
      <td>Breaks high temporal correlation across sequential simulator frames, stabilizing gradient descent.</td>
    </tr>
  </tbody>
</table>

<h3>5.3 Soft Actor-Critic (SAC) &amp; Maximum Entropy Objective</h3>
<p>
  Standard RL maximizes expected reward. <b>Maximum Entropy RL</b> augments the reward with the Shannon entropy $\mathcal{H}(\pi(\cdot \mid s_t)) = \mathbb{E}_{a \sim \pi}[-\log \pi(a \mid s_t)]$ of the policy:
</p>
<div class="formula">
  $$J(\pi) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t) \sim \rho_\pi} \left[ r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot \mid s_t)) \right]$$
</div>
<div class="callout intuition">
  <div class="callout-title">💡 Plain English: Paying the Robot to Stay Curious</div>
  <p>
    In soft tomato slicing, an agent maximizing only reward easily gets trapped in a local minimum: it hovers the knife 1 mm above the tomato skin to avoid crushing penalties. The entropy temperature $\alpha$ rewards the robot for testing multiple blade orientations and speeds, discovering successful puncture techniques.
  </p>
</div>

<h3>5.4 The Reparameterization Trick &amp; Tanh Squashing Jacobian Correction</h3>
<p>
  To differentiate through stochastic actions, SAC samples Gaussian noise $\epsilon \sim \mathcal{N}(0, I)$ and transforms it: $u = \mu_\theta(s) + \sigma_\theta(s) \odot \epsilon$, bounded to $[-1, 1]$ via $a = \tanh(u)$. 
  Because $\tanh$ is non-linear, the probability density requires a Jacobian determinant correction:
</p>
<div class="formula">
  $$\log \pi(a \mid s) = \log \mu(u \mid s) - \sum_{i=1}^d \log(1 - \tanh^2(u_i))$$
</div>

<div class="page-break"></div>

<!-- MODULE 6: LECTURE 10 -->
<h2 class="module-header">Module 6: Advanced Policy Gradients &amp; PPO (Lecture 10)</h2>
<p>
  <b>(CS285 Lecture 10 • Video ID: m7IU5KBS4sw)</b> Proximal Policy Optimization (PPO) is the de-facto standard for GPU-accelerated robotics. This module explores why standard policy gradients suffer from policy collapse and how PPO guarantees monotonic policy improvement.
</p>

<h3>6.1 The Catastrophic Failure Mode: Policy Collapse</h3>
<div class="callout warning-box">
  <div class="callout-title">💥 Why Policy Collapse Occurs in Reinforcement Learning</div>
  <p>
    In supervised learning, an excessively large learning rate causes a momentary loss spike, but training recovers on subsequent batches. In RL, <b>the policy generates its own training distribution</b>. If an overly aggressive gradient step drives policy parameters into an unstable region, the robot executes erratic motions. The resulting trajectory batch contains zero successful cuts. Subsequent updates compute gradients on degenerate data, initiating an unrecoverable death spiral.
  </p>
</div>

<h3>6.2 Kakade-Langford Monotonic Improvement Theorem</h3>
<p>
  Kakade &amp; Langford (2002) proved that the performance difference between two arbitrary policies $\tilde{\pi}$ and $\pi$ is exactly governed by:
</p>
<div class="formula">
  $$\eta(\tilde{\pi}) - \eta(\pi) = \mathbb{E}_{\tau \sim \tilde{\pi}} \left[ \sum_{t=0}^\infty \gamma^t A^\pi(s_t, a_t) \right]$$
</div>
<p>
  Because sampling from the new policy $\tilde{\pi}$ during optimization is impossible, we optimize the surrogate objective $L_\pi(\tilde{\pi})$ using importance sampling, subject to a theoretical lower bound:
</p>
<div class="formula">
  $$\eta(\tilde{\pi}) \ge L_\pi(\tilde{\pi}) - C \cdot \max_{s} D_{\text{KL}}(\pi(\cdot \mid s) \,\|\, \tilde{\pi}(\cdot \mid s)) \quad \text{where} \quad C = \frac{2\epsilon\gamma}{(1-\gamma)^2}$$
</div>

<h3>6.3 The PPO Clipped Surrogate Objective</h3>
<p>
  While TRPO enforces the KL constraint using second-order natural gradients (Fisher Information Matrix), PPO enforces the trust region using a first-order clipped surrogate loss. Define the importance sampling probability ratio:
</p>
<div class="formula">
  $$r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)}$$
</div>
<div class="formula">
  $$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon) \hat{A}_t \right) \right]$$
</div>

<!-- SVG Diagram: The PPO Clipping Mechanism -->
<div class="diagram-container">
<svg width="600" height="95" viewBox="0 0 600 95">
  <line x1="50" y1="50" x2="550" y2="50" stroke="#94a3b8" stroke-width="2"/>

  <!-- Normal region -->
  <rect x="200" y="15" width="200" height="65" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5" stroke-dasharray="4,4"/>
  <text x="300" y="35" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">SAFE UPDATE ZONE (Normal Gradient)</text>
  <text x="300" y="55" font-size="8" fill="#047857" text-anchor="middle">Ratio $r_t(\theta) \in [0.8, 1.2]$</text>
  <text x="300" y="70" font-size="7" fill="#64748b" text-anchor="middle">Policy changes by $\le 20\%$</text>

  <!-- Left clipped -->
  <line x1="200" y1="12" x2="200" y2="88" stroke="#ef4444" stroke-width="2"/>
  <text x="120" y="45" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">CLIPPED TO ZERO</text>
  <text x="120" y="60" font-size="7.5" fill="#64748b" text-anchor="middle">$r_t(\theta) < 1 - \epsilon$ (0.8)</text>

  <!-- Right clipped -->
  <line x1="400" y1="12" x2="400" y2="88" stroke="#ef4444" stroke-width="2"/>
  <text x="480" y="45" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">CLIPPED TO ZERO</text>
  <text x="480" y="60" font-size="7.5" fill="#64748b" text-anchor="middle">$r_t(\theta) > 1 + \epsilon$ (1.2)</text>
</svg>
</div>

<h3>6.4 Complete 4-Quadrant PPO Dynamics</h3>
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Advantage</th>
      <th style="width: 25%;">Ratio Condition</th>
      <th style="width: 25%;">Objective Value</th>
      <th style="width: 35%;">Optimization Effect</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\hat{A} > 0$</b> (Good)</td>
      <td>$r_t(\theta) \le 1 + \epsilon$</td>
      <td>$r_t(\theta) \hat{A}_t$</td>
      <td><b>Standard Positive Gradient:</b> Increases probability of successful knife motion.</td>
    </tr>
    <tr>
      <td><b>$\hat{A} > 0$</b> (Good)</td>
      <td>$r_t(\theta) > 1 + \epsilon$</td>
      <td>$(1 + \epsilon) \hat{A}_t$</td>
      <td><b>Clipped (Zero Gradient):</b> Prevents policy from over-committing to an action.</td>
    </tr>
    <tr>
      <td><b>$\hat{A} < 0$</b> (Bad)</td>
      <td>$r_t(\theta) \ge 1 - \epsilon$</td>
      <td>$r_t(\theta) \hat{A}_t$</td>
      <td><b>Standard Negative Gradient:</b> Suppresses crushing action.</td>
    </tr>
    <tr>
      <td><b>$\hat{A} < 0$</b> (Bad)</td>
      <td>$r_t(\theta) < 1 - \epsilon$</td>
      <td>$(1 - \epsilon) \hat{A}_t$</td>
      <td><b>Clipped (Zero Gradient):</b> Prevents destructive gradient updates when probability is already low.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- MODULE 7: 12-DIMENSION COMPARISON MATRIX -->
<h2 class="module-header">Module 7: The Master 12-Dimension Algorithm Grand Comparison Matrix</h2>
<p>
  This authoritative reference matrix compares the six seminal reinforcement learning algorithms across twelve fundamental architectural, mathematical, and practical dimensions.
</p>

<table>
  <thead>
    <tr>
      <th style="width: 16%;">Dimension</th>
      <th style="width: 14%;">REINFORCE</th>
      <th style="width: 14%;">A2C</th>
      <th style="width: 14%;">DQN</th>
      <th style="width: 14%;">SAC</th>
      <th style="width: 14%;">TRPO</th>
      <th style="width: 14%;">PPO</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Paradigm</b></td>
      <td>On-Policy PG</td>
      <td>On-Policy AC</td>
      <td>Off-Policy TD</td>
      <td>Off-Policy MaxEnt AC</td>
      <td>On-Policy Trust Region</td>
      <td>On-Policy Clipped AC</td>
    </tr>
    <tr>
      <td><b>2. Policy Type</b></td>
      <td>Stochastic $\pi_\theta(a|s)$</td>
      <td>Stochastic $\pi_\theta(a|s)$</td>
      <td>Implicit $\arg\max Q$</td>
      <td>Stochastic Gaussian</td>
      <td>Stochastic Gaussian</td>
      <td>Stochastic Gaussian</td>
    </tr>
    <tr>
      <td><b>3. Action Space</b></td>
      <td>Discrete / Cont.</td>
      <td>Discrete / Cont.</td>
      <td>Discrete only</td>
      <td>Continuous only</td>
      <td>Discrete / Cont.</td>
      <td>Discrete / Cont.</td>
    </tr>
    <tr>
      <td><b>4. Sample Efficiency</b></td>
      <td>Very Low ($10^7$)</td>
      <td>Low ($10^7$)</td>
      <td>High ($10^5$)</td>
      <td>Very High ($10^5$)</td>
      <td>Moderate ($10^6$)</td>
      <td>Moderate ($10^6$)</td>
    </tr>
    <tr>
      <td><b>5. Wall-Clock Speed</b></td>
      <td>Slow</td>
      <td>Fast</td>
      <td>Moderate</td>
      <td>Moderate (Replay)</td>
      <td>Slow (Fisher Hessian)</td>
      <td>Fastest on GPU</td>
    </tr>
    <tr>
      <td><b>6. Objective Function</b></td>
      <td>$\mathbb{E}[\nabla \log \pi G_t]$</td>
      <td>$\mathbb{E}[\nabla \log \pi \hat{A}^{\text{TD}}]$</td>
      <td>$\mathbb{E}[(r + \gamma \max Q - Q)^2]$</td>
      <td>$\mathbb{E}[r + \alpha \mathcal{H}(\pi)]$</td>
      <td>$\max L_\pi \text{ s.t. } D_{\text{KL}} \le \delta$</td>
      <td>$\mathbb{E}[\min(r \hat{A}, \text{clip} \hat{A})]$</td>
    </tr>
    <tr>
      <td><b>7. Stability</b></td>
      <td>Extremely Low</td>
      <td>Moderate</td>
      <td>Moderate</td>
      <td>High (Twin-Q + Polyak)</td>
      <td>Very High</td>
      <td>Very High</td>
    </tr>
    <tr>
      <td><b>8. Replay Buffer</b></td>
      <td>No</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>No</td>
      <td>No</td>
    </tr>
    <tr>
      <td><b>9. Exploration</b></td>
      <td>Stochastic policy</td>
      <td>Entropy bonus</td>
      <td>$\epsilon$-greedy</td>
      <td>MaxEnt ($\alpha \mathcal{H}$)</td>
      <td>Stochastic policy</td>
      <td>Entropy loss scale</td>
    </tr>
    <tr>
      <td><b>10. Sim-to-Real</b></td>
      <td>Poor</td>
      <td>Moderate</td>
      <td>Poor (Continuous)</td>
      <td>High</td>
      <td>High</td>
      <td>Highest (Dominant)</td>
    </tr>
    <tr>
      <td><b>11. Parallel Sim</b></td>
      <td>Poor</td>
      <td>Good</td>
      <td>Poor (Async buffer)</td>
      <td>Moderate</td>
      <td>Poor (CG overhead)</td>
      <td>Optimal (Linear)</td>
    </tr>
    <tr>
      <td><b>12. Canonical Use</b></td>
      <td>Toy CartPole</td>
      <td>Atari 2600</td>
      <td>Video Games</td>
      <td>MuJoCo Continuous</td>
      <td>Robotics Locomotion</td>
      <td>Isaac Lab / Manipulation</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- MODULE 8: PAPER 1 BLUEPRINT -->
<h2 class="module-header">Module 8: Master Paper 1 Implementation Blueprint (Dual-Arm Slicing)</h2>
<p>
  Here is the comprehensive architectural and operational blueprint connecting CS285 Priority 1 directly to your Master's thesis methodology: 
  <b>Adaptive Dual-Arm Soft Object Slicing with PPO / SAC in NVIDIA Isaac Lab via SkRL</b>.
</p>

<h3>8.1 System Specifications &amp; Multi-Modal Sensory Integration</h3>
<p>
  The robotic slicing setup consists of two collaborative arms: a <b>Holding Arm</b> that stabilizes the soft tomato with gentle grasp force, 
  and a <b>Cutting Arm</b> equipped with a sensorized blade containing an <b>ATI Nano17 6-axis F/T transducer</b> and a <b>piezoelectric acoustic burst sensor</b>.
</p>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Subsystem</th>
      <th style="width: 15%;">Dimension</th>
      <th style="width: 35%;">Sensor / Physical Origin</th>
      <th style="width: 30%;">Normalization &amp; Noise Model</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Arm Kinematics</b></td>
      <td>$\mathbb{R}^{14}$</td>
      <td>Dual-arm joint positions $q$ (7) and velocities $\dot{q}$ (7).</td>
      <td>Normalized by joint limits; Gaussian noise $\sigma = 0.005$ rad.</td>
    </tr>
    <tr>
      <td><b>Blade Kinematics</b></td>
      <td>$\mathbb{R}^9$</td>
      <td>Blade tip 3D position $p$, linear velocity $v$, angular velocity $\omega$.</td>
      <td>Relative to cutting board frame; $\sigma_v = 0.01$ m/s.</td>
    </tr>
    <tr>
      <td><b>Tomato Geometry</b></td>
      <td>$\mathbb{R}^7$</td>
      <td>3D center of mass $p_{\text{fruit}}$ and orientation quaternion $q_{\text{fruit}}$.</td>
      <td>Sim: USD pose; Real: YOLOv8 + Depth camera.</td>
    </tr>
    <tr>
      <td><b>TacBlade F/T</b></td>
      <td>$\mathbb{R}^6$</td>
      <td>3-axis contact force ($F_x, F_y, F_z$) and torque ($T_x, T_y, T_z$).</td>
      <td>Filtered with 50 Hz Butterworth filter; $\sigma = 0.1$ N.</td>
    </tr>
    <tr>
      <td><b>Acoustic Burst</b></td>
      <td>$\mathbb{R}^1$</td>
      <td>RMS acoustic energy envelope ($100 \text{ Hz} - 5 \text{ kHz}$).</td>
      <td>Log-scale normalization; triggers puncture detection.</td>
    </tr>
    <tr style="background: #eff6ff;">
      <td><b>Total State $\mathcal{S}$</b></td>
      <td><b>$\mathbb{R}^{33}$</b></td>
      <td><b>Full Markovian observation vector fed to Actor &amp; Critic.</b></td>
      <td><b>Standardized via running mean and variance filter.</b></td>
    </tr>
  </tbody>
</table>

<h3>8.2 Continuous Action Parameterization ($\mathbb{R}^6$)</h3>
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Channel</th>
      <th style="width: 25%;">Physical Parameter</th>
      <th style="width: 20%;">Operational Range</th>
      <th style="width: 40%;">Robotic Function</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>$a_0$</td>
      <td>Downward Feed $\Delta v_z$</td>
      <td>$[-5.0, +5.0]$ mm/s</td>
      <td>Modulates vertical penetration rate based on contact resistance.</td>
    </tr>
    <tr>
      <td>$a_1$</td>
      <td>Sawing Velocity $v_{\text{slice}}$</td>
      <td>$[-30.0, +30.0]$ mm/s</td>
      <td>Lateral sawing motion reducing normal puncture force.</td>
    </tr>
    <tr>
      <td>$a_2$</td>
      <td>Vertical Stiffness $\Delta K_z$</td>
      <td>$[-500, +500]$ N/m</td>
      <td>Impedance modulation: softens blade upon initial contact to avoid crushing.</td>
    </tr>
    <tr>
      <td>$a_3$</td>
      <td>Vertical Damping $\Delta D_z$</td>
      <td>$[-20, +20]$ Ns/m</td>
      <td>Damps out high-frequency contact vibrations.</td>
    </tr>
    <tr>
      <td>$a_4$</td>
      <td>Grasp Normal Force $F_{\text{hold}}$</td>
      <td>$[1.0, 6.0]$ N</td>
      <td>Holding arm normal contact force preventing tomato slip.</td>
    </tr>
    <tr>
      <td>$a_5$</td>
      <td>Holding Compliance $\Delta K_{\text{hold}}$</td>
      <td>$[-300, +300]$ N/m</td>
      <td>Maintains adaptive grip on soft, deforming fruit pulp.</td>
    </tr>
  </tbody>
</table>

<h3>8.3 Multi-Objective Reward Function Formulation</h3>
<p>
  The reward function balances penetration efficiency, shear mechanics, tissue damage prevention, and motion smoothness:
</p>
<div class="formula">
  $$r_t = w_{\text{pen}} \cdot r_{\text{pen}} + w_{\text{slice}} \cdot r_{\text{slice}} + w_{\text{crush}} \cdot p_{\text{crush}} + w_{\text{smooth}} \cdot p_{\text{smooth}} + r_{\text{terminal}}$$
</div>

<div class="callout code-box">
  <div class="callout-title">🐍 PyTorch Tensorized Reward Implementation in Isaac Lab</div>
<pre style="margin: 0; padding: 0;">
def compute_rewards(self) -&gt; torch.Tensor:
    # 1. Penetration Progress: Reward downward displacement through tomato
    z_progress = torch.clamp(self.prev_knife_z - self.knife_z, min=0.0)
    r_pen = 6.0 * z_progress

    # 2. Lateral Sawing Shear: Reward sawing velocity only while blade is in contact
    v_slice = torch.abs(self.knife_vel[:, 0])
    in_contact = (self.blade_force[:, 2] &gt; 0.4).float()
    r_slice = 3.0 * v_slice * in_contact

    # 3. Crushing Penalty: Penalize normal force exceeding 8.0 N puncture threshold
    excess_force = torch.clamp(self.blade_force[:, 2] - 8.0, min=0.0)
    p_crush = -4.0 * torch.square(excess_force)

    # 4. Action Smoothness: Penalize high-frequency chatter in impedance delta
    action_diff = self.actions - self.prev_actions
    p_smooth = -0.05 * torch.sum(torch.square(action_diff), dim=-1)

    # 5. Terminal Conditions
    r_term = torch.zeros_like(r_pen)
    # Success: Blade reaches cutting board with zero excessive crushing
    r_term = torch.where(self.reached_board &amp; (excess_force == 0), r_term + 120.0, r_term)
    # Failure: Massive crush (&gt;22 N) destroys the tomato
    r_term = torch.where(self.blade_force[:, 2] &gt; 22.0, r_term - 60.0, r_term)

    return r_pen + r_slice + p_crush + p_smooth + r_term
</pre>
</div>

<div class="page-break"></div>

<h3>8.4 Domain Randomization Strategy for Sim-to-Real Transfer</h3>
<p>
  To ensure the policy trained in NVIDIA Isaac Lab transfers directly to physical Franka Emika robot arms without fine-tuning, 
  we randomize six physical and sensory properties across 1,024 parallel environments during training:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Randomized Parameter</th>
      <th style="width: 20%;">Nominal Value</th>
      <th style="width: 25%;">Randomization Range</th>
      <th style="width: 30%;">Physical Sim-to-Real Gap Targeted</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Tomato Bulk Stiffness ($K_s$)</b></td>
      <td>35 kPa</td>
      <td>$[15, 60]$ kPa (Uniform)</td>
      <td>Ripeness variation between green, firm, and over-ripe tomatoes.</td>
    </tr>
    <tr>
      <td><b>Skin Rupture Force ($F_{\text{rupt}}$)</b></td>
      <td>8.0 N</td>
      <td>$[5.5, 12.0]$ N (Gaussian)</td>
      <td>Cuticle thickness and localized pericarp toughness variations.</td>
    </tr>
    <tr>
      <td><b>Friction Coefficient ($\mu_{\text{contact}}$)</b></td>
      <td>0.25</td>
      <td>$[0.12, 0.45]$ (Uniform)</td>
      <td>Moisture and juice leakage lubricating the blade surface.</td>
    </tr>
    <tr>
      <td><b>Blade Sharpness Index ($S$)</b></td>
      <td>1.0 (New)</td>
      <td>$[0.6, 1.2]$ (Uniform)</td>
      <td>Blade edge degradation and serration wear across repeated cuts.</td>
    </tr>
    <tr>
      <td><b>Holding Gripper Compliance</b></td>
      <td>800 N/m</td>
      <td>$[400, 1400]$ N/m</td>
      <td>Variations in rubber finger pad elasticity and grip calibration.</td>
    </tr>
    <tr>
      <td><b>Sensor Latency ($\Delta t$)</b></td>
      <td>10 ms</td>
      <td>$[5, 25]$ ms (Stochastic)</td>
      <td>ROS 2 network jitter and USB-FT sensor communication delays.</td>
    </tr>
  </tbody>
</table>

<!-- MODULE 9: SKRL CODE -->
<h2>Module 9: Production SkRL &amp; PyTorch Model Architecture</h2>
<p>
  Below is the complete, modular PyTorch implementation of the Dual-Head Actor-Critic network configured for SkRL and Isaac Lab:
</p>

<div class="callout code-box">
  <div class="callout-title">🐍 PyTorch Dual-Head Actor-Critic Model (`models.py`)</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn
from skrl.models.torch import GaussianMixin, DeterministicMixin, Model

class SlicingActorCritic(GaussianMixin, DeterministicMixin, Model):
    def __init__(self, observation_space, action_space, device, clip_actions=False):
        Model.__init__(self, observation_space, action_space, device)
        GaussianMixin.__init__(self, clip_actions=clip_actions)
        DeterministicMixin.__init__(self)

        in_dim = observation_space.shape[0]   # 33
        out_dim = action_space.shape[0]       # 6

        # Shared representation backbone
        self.backbone = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.ELU(),
            nn.Linear(256, 256),
            nn.ELU()
        )
        # Actor head: Outputs continuous action mean
        self.actor_mean = nn.Linear(256, out_dim)
        self.log_std_parameter = nn.Parameter(torch.zeros(out_dim))

        # Critic head: Outputs scalar state-value V(s)
        self.critic_head = nn.Linear(256, 1)

    def act(self, inputs, role):
        features = self.backbone(inputs["states"])
        if role == "policy":
            mean = self.actor_mean(features)
            log_std = torch.clamp(self.log_std_parameter, min=-20.0, max=2.0)
            return mean, log_std, {}
        elif role == "value":
            value = self.critic_head(features)
            return value, {}
</pre>
</div>

<h3>9.1 Master SkRL Configuration (`ppo_cfg.yaml`)</h3>
<p>
  Every hyperparameter in SkRL is grounded in CS285 theoretical principles:
</p>
<div class="callout code-box">
  <div class="callout-title">⚙️ Production ppo_cfg.yaml Reference</div>
<pre style="margin: 0; padding: 0;">
algorithm:
  class: PPO
  clip_range: 0.2            # Lecture 10: Enforces trust region, preventing policy collapse
  gae_lambda: 0.95           # Lecture 6: Optimal exponential blend of TD(0) bias and MC variance
  discount_factor: 0.99      # Lecture 4: γ = 0.99 ensures credit assigned across 300+ cutting steps
  learning_rate: 3e-4        # Standard Adam step size
  learning_rate_scheduler: KLAdaptiveLR  # Adaptive step size scaling based on KL divergence
  entropy_loss_scale: 0.01   # Lecture 8: Encourages exploration of dynamic impedance angles
  value_loss_scale: 1.0      # Weight of Critic MSE regression loss
  epochs: 5                  # Lecture 10: Re-uses parallel rollout batches safely
  mini_batches: 4            # Subdivides 1,024 parallel environments into mini-batches
</pre>
</div>

<div class="page-break"></div>

<!-- MODULE 10: THESIS DEFENSE CHEATSHEET -->
<h2 class="module-header">Module 10: Thesis Defense Master Cheatsheet (Top 10 Q&amp;A)</h2>
<p>
  When defending your methodology before Prof. Shan An, thesis committees, or IEEE reviewers, be prepared for these 10 core theoretical questions:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 5%;">#</th>
      <th style="width: 45%;">Reviewer / Committee Question</th>
      <th style="width: 50%;">Your Bulletproof Academic Answer</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1</b></td>
      <td>Why use Reinforcement Learning instead of standard Impedance Control?</td>
      <td>Classical impedance control requires hand-tuning constant stiffness ($K$) and damping ($D$). Soft fruits exhibit non-linear viscoplastic fracture transitions where contact stiffness drops by over 80% within milliseconds upon skin puncture. RL dynamically modulates compliance parameters in response to real-time high-frequency tactile and acoustic signals.</td>
    </tr>
    <tr>
      <td><b>2</b></td>
      <td>Why is your task formulated as a Markov Decision Process (MDP)?</td>
      <td>Our 33-dimensional state vector contains both kinematics (joint and blade positions/velocities) and contact forces ($F/T$), meaning the transition to $s_{t+1}$ depends solely on the current state $s_t$ and action $a_t$, strictly satisfying the Markov conditional independence property.</td>
    </tr>
    <tr>
      <td><b>3</b></td>
      <td>Why did you choose PPO over Model-Based RL?</td>
      <td>Deformable viscoplastic fracture mechanics are notoriously difficult to model analytically. Model-based RL compounds model bias across extended horizons, causing sim-to-real transfer failure. PPO is model-free, highly robust, and directly optimizes the true multi-objective reward.</td>
    </tr>
    <tr>
      <td><b>4</b></td>
      <td>How do you address PPO's low sample efficiency?</td>
      <td>Through GPU-vectorized parallel physics simulation in NVIDIA Isaac Lab. By simulating 1,024 environments simultaneously on an RTX GPU, we collect over 10 million simulation transitions in under 45 minutes, rendering on-policy sample efficiency irrelevant.</td>
    </tr>
    <tr>
      <td><b>5</b></td>
      <td>What is the exact role of the Critic network?</td>
      <td>The Critic approximates the State-Value function $V(s)$ using Temporal Difference learning. It is used to compute the Advantage function $\hat{A}(s, a) = Q(s, a) - V(s)$, which dramatically reduces policy gradient variance compared to raw Monte Carlo rollouts.</td>
    </tr>
    <tr>
      <td><b>6</b></td>
      <td>Why is Generalized Advantage Estimation (GAE) with $\lambda = 0.95$ used?</td>
      <td>Pure TD learning ($\lambda = 0$) has minimal variance but introduces bias if the Critic is inaccurate. Pure rollouts ($\lambda = 1$) have zero bias but massive variance. GAE with $\lambda = 0.95$ achieves an optimal exponential blend of multi-step returns.</td>
    </tr>
    <tr>
      <td><b>7</b></td>
      <td>Why did you configure continuous action spaces instead of discrete?</td>
      <td>Robot joint motor torques, feed velocities, and compliance deltas ($\Delta K, \Delta D$) are continuous physical quantities. Discretizing them creates coarse, jerky motions that damage soft object skins.</td>
    </tr>
    <tr>
      <td><b>8</b></td>
      <td>What is the purpose of PPO's clipping mechanism?</td>
      <td>It bounds the probability ratio $r_t(\theta)$ between $[1-\epsilon, 1+\epsilon]$ (typically $\epsilon = 0.2$). This prevents policy collapse by discarding gradient steps that deviate too far from the policy that generated the trajectory data.</td>
    </tr>
    <tr>
      <td><b>9</b></td>
      <td>Why is lateral sawing velocity rewarded?</td>
      <td>Under fracture mechanics shear-stress coupling, lateral slicing motion significantly reduces the required normal downward force ($F_z$) to achieve fracture toughness ($K_{\text{Ic}}$), preventing fruit crushing.</td>
    </tr>
    <tr>
      <td><b>10</b></td>
      <td>How does Soft Actor-Critic (SAC) prevent local minima?</td>
      <td>By optimizing Maximum Entropy RL ($\text{Reward} + \alpha \cdot \text{Entropy}$). The entropy term encourages broad, stochastic exploration, preventing the robot from adopting timid policies that freeze above the tomato skin to avoid crushing penalties.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>DEX-ROB Lab (Tianjin University) Master's Research Program • Prof. Shan An • Created with Antigravity AI</i>
</div>

</body>
</html>
"""

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_utils

render_utils.build_pdf(html_doc, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
