import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Robot Learning & The Closed Loop: Definitive Guide to CS285 Lecture 1</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 1: Foundations, MDPs & The RL Landscape";
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

  /* Header Block */
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

  /* Callout Boxes */
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
  .code-dim { color: #fbbf24; }

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
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 1 Masterclass Study Guide</span>
  <h1>Mastering Robot Learning &amp; The Closed-Loop Paradigm</h1>
  <div class="subtitle">Complete Mathematical &amp; Conceptual Foundations: (T, P, E) Formalism, Quadratic Compounding Errors, Continuous MDPs &amp; POMDPs, Trajectory Factorization, and the Modern RL Landscape</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Curriculum:</b> Berkeley CS285 + Sutton &amp; Barto + Spinning Up</span>
    <span><b>Scope:</b> General RL Theory &amp; Continuous Physical Manipulation</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The Executive Mental Map: Why Does Reinforcement Learning Exist?</h2>
<p>
  When human software engineers approach a robotics or control problem—such as autonomous drone flight, legged locomotion over rough terrain, or delicate surgical manipulation—their initial instinct is to engineer an <b>explicit recipe</b>:
  <i>"Read joint encoders; calculate kinematics; if contact force exceeds 5.0 Newtons, execute a linear trajectory offset."</i>
</p>
<p>
  In the real physical world, this classical hand-crafted approach invariably breaks down. Physical systems exhibit contact non-linearities, stiction, hysteresis, latency, sensor noise, and deformable physics that cannot be captured in closed-form equations. Prof. Sergey Levine opens CS285 with a profound paradigm shift: <b>intelligent motor behavior cannot be hand-coded; it must be discovered through closed-loop interaction, evaluative feedback, and continuous adaptation.</b>
</p>

<!-- SVG Diagram: The 5 Pillars of Lecture 1 -->
<div class="diagram-container">
<svg width="690" height="90" viewBox="0 0 690 90">
  <rect x="5" y="10" width="128" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="69" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. SL vs. RL</text>
  <text x="69" y="52" font-size="8.2" fill="#475569" text-anchor="middle">i.i.d. Labels vs.</text>
  <text x="69" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Closed-Loop Control</text>

  <rect x="141" y="10" width="128" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="205" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">2. Error Drift</text>
  <text x="205" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Ross &amp; Bagnell Proof</text>
  <text x="205" y="66" font-size="8.2" fill="#475569" text-anchor="middle">O(ε T²) Distribution Shift</text>

  <rect x="277" y="10" width="128" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="341" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">3. MDPs &amp; POMDPs</text>
  <text x="341" y="52" font-size="8.2" fill="#475569" text-anchor="middle">The 6-Tuple &amp; 8-Tuple</text>
  <text x="341" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Belief State Dynamics</text>

  <rect x="413" y="10" width="128" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="477" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">4. Trajectory Math</text>
  <text x="477" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Chain Rule Factorization</text>
  <text x="477" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Markovian Independence</text>

  <rect x="549" y="10" width="136" height="70" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>
  <text x="617" y="36" font-size="9" font-weight="700" fill="#334155" text-anchor="middle">5. The Grand Taxonomy</text>
  <text x="617" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Model-Free vs Based</text>
  <text x="617" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Value vs Policy vs AC</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: The Core Paradigm Shift — Supervised Learning vs. Reinforcement Learning</h2>
<p>
  The overwhelming majority of breakthrough AI systems (large language models, object recognition networks, speech transcribers) are powered by <b>Supervised Learning (SL)</b>. In this part, we examine why the mathematical assumptions underlying supervised learning completely fail when applied to sequential decision-making agents.
</p>

<h3>1.1 The Goodfellow (T, P, E) Formalization for Intelligent Agents</h3>
<p>
  In the canonical <i>Deep Learning</i> framework (Goodfellow, Bengio &amp; Courville, Chapter 5), any machine learning algorithm is defined by a triad: a <b>Task (T)</b>, a <b>Performance Measure (P)</b>, and <b>Experience (E)</b>.
</p>

<div class="intuition">
  <div class="callout-title">The Foundational Contrast: Instructive vs. Evaluative Feedback</div>
  <p>
    <b>Supervised Learning receives Instructive Feedback:</b> The training signal specifies the exact ground-truth action or label $y^*$ that should have been produced: <i>"The correct steering angle was exactly +14.2 degrees."</i> Loss gradients point directly toward this known target.<br><br>
    <b>Reinforcement Learning receives Evaluative Feedback:</b> The training signal is purely evaluative: a scalar score $r \in \mathbb{R}$ indicating how good or bad the outcome was: <i>"Reward = -50 (the vehicle slipped off the tarmac)."</i> The environment does not tell the agent what action would have been better; the agent must infer this through trial and error.
  </p>
</div>

<table>
  <thead>
    <tr>
      <th style="width: 18%;">Dimension</th>
      <th style="width: 41%;">Supervised Learning (SL)</th>
      <th style="width: 41%;">Reinforcement Learning (RL)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Data Independence</b></td>
      <td><b>i.i.d. Assumption:</b> Samples $(x_i, y_i) \sim \mathcal{D}$ are independently and identically distributed. Sample $x_t$ has zero causal influence on $x_{t+1}$.</td>
      <td><b>Non-i.i.d. Sequential Dynamics:</b> Actions actively change the physical state: $s_{t+1} \sim P(\cdot|s_t, a_t)$. Data collection is causally coupled to the agent's current policy.</td>
    </tr>
    <tr>
      <td><b>Supervision Signal</b></td>
      <td><b>Instructive Ground-Truth:</b> Direct vector gradient $\nabla_\theta \mathcal{L}(f_\theta(x), y)$ pointing toward the correct output.</td>
      <td><b>Scalar Evaluative Reward:</b> Only a scalar $r_t \in \mathbb{R}$. No direction of improvement is provided; exploration is required.</td>
    </tr>
    <tr>
      <td><b>Credit Assignment</b></td>
      <td><b>Instantaneous:</b> Error is evaluated immediately on the current sample. No future consequences exist.</td>
      <td><b>Delayed &amp; Temporal:</b> An action taken at step $t=10$ may cause catastrophic failure at step $t=150$. The agent must assign credit across time.</td>
    </tr>
    <tr>
      <td><b>Performance Ceiling</b></td>
      <td>Bounded by the teacher/dataset: The model cannot exceed the proficiency of human annotators.</td>
      <td><b>Superhuman Discovery:</b> By exploring beyond human intuitions, agents discover novel optimal control strategies (e.g., AlphaGo Move 37).</td>
    </tr>
  </tbody>
</table>

<h3>1.2 The Distribution Shift Catastrophe: Ross &amp; Bagnell's $\mathcal{O}(\epsilon T^2)$ Compounding Error Proof</h3>
<p>
  Why can't we simply train robots using <b>Behavioral Cloning (BC)</b>—recording a human teleoperating a robot and training a supervised neural network $\pi_\theta(a|s)$ via mean squared error on human actions?
</p>
<p>
  In 2011, Stéphane Ross and J. Andrew Bagnell published a mathematical proof showing why naive behavioral cloning fails catastrophically in sequential domains.
</p>

<div class="math-box">
  <div class="callout-title">Theorem: Quadratic Compounding of Errors in Open-Loop Imitation</div>
  <p>
    Suppose an imitation learning policy $\pi_\theta$ has a per-step error probability bounded by $\epsilon$ under the expert's state distribution $d_{\pi^*}(s)$:
    $$\mathbb{E}_{s \sim d_{\pi^*}} \left[ \mathbb{I}(\pi_\theta(s) \ne \pi^*(s)) \right] \le \epsilon$$
    In an episode of length $T$, the expected number of errors committed by the policy scales not as $\mathcal{O}(\epsilon T)$, but as:
    $$\mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=1}^T \mathbb{I}(\pi_\theta(s_t) \ne \pi^*(s_t)) \right] \le \epsilon T + (1 - (1-\epsilon)^T) T \approx \mathcal{O}(\epsilon T^2)$$
  </p>
</div>

<p>
  <b>The Intuitive Mechanism of Failure:</b>
</p>
<ol>
  <li>At time $t=0$, the robot starts in an expert state. With probability $(1 - \epsilon)$, it takes the expert action. With probability $\epsilon$, it makes a minor error.</li>
  <li>Once an error occurs, the robot transitions to an <i>unfamiliar state</i> outside the expert's training distribution $d_{\pi^*}(s)$.</li>
  <li>Because the supervised dataset contains <b>zero demonstrations showing how to recover from mistakes</b> (an expert never makes silly mistakes), the network has never seen this state. Its predictions become arbitrary.</li>
  <li>Arbitrary actions lead to even more severe errors, pushing the robot further into unknown space. Once it leaves the training track, it stays off the track for all remaining $(T - t)$ steps. Integrating over time produces quadratic error growth $\mathcal{O}(\epsilon T^2)$.</li>
</ol>

<div class="robotics">
  <div class="callout-title">Robotics Physical Reality: The Slicing Recovery Dilemma</div>
  <p>
    Consider an autonomous dual-arm surgical robot slicing soft liver tissue or an industrial arm slicing meat. If behavioral cloning is used and the blade slips by 2 mm, the robot enters a geometric and tactile configuration that the expert surgeon never demonstrated. A pure supervised network will often continue pressing down, tearing the specimen. In contrast, <b>Reinforcement Learning experiences its own blunders during training</b>, thereby learning stabilizing feedback controllers that self-correct before catastrophic rupture.
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 2 -->
<h2>Part 2: Mathematical Foundations of Markov Decision Processes (MDPs)</h2>
<p>
  To solve sequential decision-making problems mathematically, we formalize the interaction between agent and environment as a <b>Markov Decision Process (MDP)</b>.
</p>

<h3>2.1 The Formal MDP 6-Tuple</h3>
<p>
  A Markov Decision Process is formally defined by the tuple $\mathcal{M} = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma, \rho_0)$:
</p>

<div class="formula">
  $$\mathcal{M} = \big\langle \mathcal{S},\; \mathcal{A},\; \mathcal{P},\; \mathcal{R},\; \gamma,\; \rho_0 \big\rangle$$
</div>

<ul>
  <li><b>$\mathcal{S}$ (State Space):</b> The set of all possible valid environmental states. In continuous robotics, $\mathcal{S} \subseteq \mathbb{R}^{d_s}$ consists of joint angles, angular velocities, end-effector poses, contact forces, and target object positions.</li>
  <li><b>$\mathcal{A}$ (Action Space):</b> The set of all valid commands the agent can emit. In continuous control, $\mathcal{A} \subseteq \mathbb{R}^{d_a}$ represents motor torques, desired joint velocities, or impedance setpoints.</li>
  <li><b>$\mathcal{P}(s'|s, a)$ (Transition Probability Kernel):</b> A conditional probability density function describing environmental physics:
    $$\mathcal{P}(s' \mid s, a) = \Pr(s_{t+1} = s' \mid s_t = s, a_t = a)$$
    In deterministic physical simulators, this is a Dirac delta distribution $\delta(s' - f(s, a))$.</li>
  <li><b>$\mathcal{R}(s, a)$ or $\mathcal{R}(s, a, s')$ (Reward Function):</b> A scalar function mapping transitions to real numbers: $\mathcal{R}: \mathcal{S} \times \mathcal{A} \to \mathbb{R}$. Represents the immediate desirability of taking action $a$ in state $s$.</li>
  <li><b>$\gamma \in [0, 1)$ (Discount Factor):</b> A geometric attenuation factor that weights immediate rewards relative to future rewards. Prevents infinite returns in continuing tasks and models temporal uncertainty.</li>
  <li><b>$\rho_0(s)$ (Initial State Distribution):</b> A probability density over starting states: $\rho_0(s) = \Pr(s_0 = s)$.</li>
</ul>

<h3>2.2 The Markov Property: Definition &amp; Mathematical Consequences</h3>

<div class="math-box">
  <div class="callout-title">The Markov Property (Memorylessness)</div>
  <p>
    A stochastic transition process possesses the <b>Markov Property</b> if and only if the conditional probability distribution of future states depends solely upon the present state and action, and is conditionally independent of all historical states and actions:
    $$\Pr(s_{t+1} \mid s_t, a_t, s_{t-1}, a_{t-1}, \dots, s_0, a_0) = \Pr(s_{t+1} \mid s_t, a_t)$$
  </p>
</div>

<p>
  <b>Why is the Markov Property revolutionary for machine learning?</b><br>
  If a process is non-Markovian, an optimal policy would need to take as input the <i>entire infinite history</i> of all past observations: $a_t \sim \pi(a_t | s_0, a_0, s_1, a_1, \dots, s_t)$. The dimensionality of the input space would grow linearly with time, rendering function approximation impossible. 
  Under the Markov assumption, the state $s_t$ is a <b>sufficient statistic</b> of the past. The agent needs to examine only $s_t$ to act optimally.
</p>

<h3>2.3 Trajectory Probability Distribution: Complete Mathematical Derivation</h3>
<p>
  Let a trajectory $\tau$ be an ordered sequence of states and actions over a finite horizon $T$:
  $$\tau = (s_0, a_0, s_1, a_1, \dots, s_{T-1}, a_{T-1}, s_T)$$
  Under a parameterized stochastic policy $\pi_\theta(a|s)$, what is the exact probability density $p_\theta(\tau)$ of observing this sequence?
</p>

<div class="formula">
  <b>Step-by-Step Derivation of Trajectory Probability:</b><br>
  $$p_\theta(\tau) = \Pr(s_0, a_0, s_1, a_1, \dots, s_T)$$
  $$\text{Applying the General Probability Chain Rule:}$$
  $$p_\theta(\tau) = \Pr(s_0) \prod_{t=0}^{T-1} \Pr(a_t \mid s_0, \dots, s_t, a_0, \dots, a_{t-1}) \cdot \Pr(s_{t+1} \mid s_0, \dots, s_t, a_0, \dots, a_t)$$
  $$\text{Applying Policy Independence } a_t \sim \pi_\theta(a_t|s_t) \text{ and Markov Transition } s_{t+1} \sim \mathcal{P}(s_{t+1}|s_t, a_t):$$
  $$p_\theta(\tau) = \rho_0(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t \mid s_t) \, \mathcal{P}(s_{t+1} \mid s_t, a_t)$$
</div>

<p>
  Taking the natural logarithm of both sides yields an additive decomposition that is crucial for policy gradient methods:
</p>

<div class="formula">
  $$\log p_\theta(\tau) = \log \rho_0(s_0) + \sum_{t=0}^{T-1} \log \pi_\theta(a_t \mid s_t) + \sum_{t=0}^{T-1} \log \mathcal{P}(s_{t+1} \mid s_t, a_t)$$
</div>

<div class="intuition">
  <div class="callout-title">The Miracle of the Log Trajectory Derivative</div>
  <p>
    Notice what happens when we differentiate $\log p_\theta(\tau)$ with respect to policy parameters $\theta$:
    $$\nabla_\theta \log p_\theta(\tau) = \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t)$$
    The environmental transition dynamics $\mathcal{P}(s_{t+1} \mid s_t, a_t)$ and initial distribution $\rho_0(s_0)$ <b>completely disappear</b> because they do not depend on $\theta$! This single algebraic property is why model-free reinforcement learning is possible without knowing environmental physics.
  </p>
</div>

<h3>2.4 Partially Observable MDPs (POMDPs) &amp; Belief States</h3>
<p>
  In real-world applications, the robot almost never observes the true physical state $s_t$. Instead, it receives high-dimensional, noisy, or occluded <b>observations</b> $o_t$ (e.g., RGB camera frames, tactile sensor readings). This is formalized as a <b>POMDP</b>:
</p>

<div class="formula">
  $$\mathcal{M}_{\text{POMDP}} = \big\langle \mathcal{S},\; \mathcal{A},\; \mathcal{P},\; \mathcal{R},\; \Omega,\; \mathcal{O},\; \gamma,\; \rho_0 \big\rangle$$
</div>

<ul>
  <li><b>$\Omega$ (Observation Space):</b> The space of sensory inputs available to the agent ($o_t \in \Omega$).</li>
  <li><b>$\mathcal{O}(o|s)$ (Emission Probability):</b> The conditional probability of receiving observation $o$ given underlying true state $s$: $\Pr(o_t = o \mid s_t = s)$.</li>
</ul>

<div class="warning-box">
  <div class="callout-title">The POMDP Non-Markovian Trap</div>
  <p>
    While true states $s_t$ satisfy the Markov property, raw observations $o_t$ <b>do not</b>! A single video frame shows the position of a robotic arm, but reveals zero information about its velocity or contact acceleration. Acting purely on $o_t$ violates the Markov assumption.
  </p>
</div>

<p>
  <b>How Practitioners Solve POMDPs in Modern Deep RL:</b>
</p>
<ol>
  <li><b>Frame Stacking (Heuristic Markovization):</b> Concatenate the last $k$ frames: $\tilde{s}_t = [o_t, o_{t-1}, \dots, o_{t-k+1}]$. Finite differencing between frames allows a feedforward network to infer velocity and acceleration (used in classic Atari DQN).</li>
  <li><b>Recurrent Policies (Memory-Based):</b> Equip the policy network with an internal recurrent hidden state $h_t = \text{LSTM}(h_{t-1}, o_t)$ or an Attention/Transformer buffer. The hidden state $h_t$ serves as a learned approximation of the true <b>Belief State</b> $b_t(s) = \Pr(s_t = s \mid o_0, a_0, \dots, o_t)$.</li>
  <li><b>Asymmetric Actor-Critic (Isaac Gym / Robotics):</b> In simulation, give the Critic network access to privileged true state $s_t$ (exact friction, mass, internal mesh stress), while the Actor network is restricted to noisy deployable observations $o_t$.</li>
</ol>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 3 -->
<h2>Part 3: The Complete Modern RL Landscape &amp; Taxonomy</h2>
<p>
  All reinforcement learning algorithms share the common objective of maximizing expected cumulative return:
  $$J(\theta) = \mathbb{E}_{\tau \sim p_\theta(\tau)} \left[ \sum_{t=0}^T \gamma^t r(s_t, a_t) \right]$$
  However, algorithms diverge sharply in *how* they approximate and optimize this objective. Below is the master taxonomy of modern RL.
</p>

<!-- SVG Diagram: Modern RL Taxonomy Tree -->
<div class="diagram-container">
<svg width="690" height="230" viewBox="0 0 690 230">
  <!-- Root Node -->
  <rect x="255" y="10" width="180" height="34" rx="5" fill="#1e3a8a" stroke="#1d4ed8" stroke-width="2"/>
  <text x="345" y="32" font-size="11" font-weight="800" fill="#ffffff" text-anchor="middle">Reinforcement Learning</text>

  <!-- Connectors to Branches -->
  <path d="M 345 44 L 345 60 L 165 60 L 165 80" stroke="#64748b" stroke-width="2" fill="none"/>
  <path d="M 345 44 L 345 60 L 525 60 L 525 80" stroke="#64748b" stroke-width="2" fill="none"/>

  <!-- Level 1: Model-Free vs Model-Based -->
  <rect x="80" y="80" width="170" height="32" rx="5" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.8"/>
  <text x="165" y="101" font-size="10" font-weight="700" fill="#1e40af" text-anchor="middle">Model-Free RL</text>

  <rect x="440" y="80" width="170" height="32" rx="5" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.8"/>
  <text x="525" y="101" font-size="10" font-weight="700" fill="#6b21a8" text-anchor="middle">Model-Based RL</text>

  <!-- Model-Free Connectors -->
  <path d="M 165 112 L 165 130 L 60 130 L 60 150" stroke="#94a3b8" stroke-width="1.5" fill="none"/>
  <path d="M 165 112 L 165 150" stroke="#94a3b8" stroke-width="1.5" fill="none"/>
  <path d="M 165 112 L 165 130 L 270 130 L 270 150" stroke="#94a3b8" stroke-width="1.5" fill="none"/>

  <!-- Level 2: Model-Free Sub-branches -->
  <rect x="5" y="150" width="110" height="65" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>
  <text x="60" y="168" font-size="8.8" font-weight="700" fill="#0f172a" text-anchor="middle">Policy-Based</text>
  <text x="60" y="184" font-size="7.8" fill="#475569" text-anchor="middle">Optimize π directly</text>
  <text x="60" y="196" font-size="7.5" fill="#2563eb" text-anchor="middle">REINFORCE, VPG</text>

  <rect x="120" y="150" width="95" height="65" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>
  <text x="167" y="168" font-size="8.8" font-weight="700" fill="#0f172a" text-anchor="middle">Value-Based</text>
  <text x="167" y="184" font-size="7.8" fill="#475569" text-anchor="middle">Learn Q*(s, a)</text>
  <text x="167" y="196" font-size="7.5" fill="#2563eb" text-anchor="middle">DQN, Double DQN</text>

  <rect x="220" y="150" width="105" height="65" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="272" y="168" font-size="8.8" font-weight="700" fill="#065f46" text-anchor="middle">Actor-Critic</text>
  <text x="272" y="184" font-size="7.8" fill="#047857" text-anchor="middle">Policy + Value</text>
  <text x="272" y="196" font-size="7.5" fill="#059669" text-anchor="middle">PPO, TRPO, SAC</text>

  <!-- Model-Based Connectors -->
  <path d="M 525 112 L 525 130 L 440 130 L 440 150" stroke="#94a3b8" stroke-width="1.5" fill="none"/>
  <path d="M 525 112 L 525 130 L 610 130 L 610 150" stroke="#94a3b8" stroke-width="1.5" fill="none"/>

  <!-- Level 2: Model-Based Sub-branches -->
  <rect x="380" y="150" width="120" height="65" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>
  <text x="440" y="168" font-size="8.8" font-weight="700" fill="#0f172a" text-anchor="middle">Known Model</text>
  <text x="440" y="184" font-size="7.8" fill="#475569" text-anchor="middle">Physics / Rules Known</text>
  <text x="440" y="196" font-size="7.5" fill="#7c3aed" text-anchor="middle">AlphaZero, MPC</text>

  <rect x="550" y="150" width="120" height="65" rx="4" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>
  <text x="610" y="168" font-size="8.8" font-weight="700" fill="#0f172a" text-anchor="middle">Learned Model</text>
  <text x="610" y="184" font-size="7.8" fill="#475569" text-anchor="middle">Neural Dynamics s'=f(s,a)</text>
  <text x="610" y="196" font-size="7.5" fill="#7c3aed" text-anchor="middle">World Models, MBPO</text>
</svg>
</div>

<h3>3.1 Comprehensive Algorithm Paradigm Comparison</h3>

<table>
  <thead>
    <tr>
      <th style="width: 17%;">Paradigm</th>
      <th style="width: 25%;">Core Mathematical Mechanism</th>
      <th style="width: 23%;">Key Strengths</th>
      <th style="width: 20%;">Core Weaknesses</th>
      <th style="width: 15%;">Iconic Algorithms</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Value-Based</b></td>
      <td>Solves Bellman Optimality Equation: $Q^*(s, a) = \mathbb{E}[r + \gamma \max_{a'} Q^*(s', a')]$. Action chosen greedily: $a = \operatorname{argmax}_a Q(s, a)$.</td>
      <td>Highly sample efficient; naturally off-policy; can reuse past historical data via replay buffer.</td>
      <td>Intractable for high-dimensional continuous action spaces (computing $\max_{a}$ requires inner optimization).</td>
      <td>DQN, Double DQN, Rainbow, Categorical 51.</td>
    </tr>
    <tr>
      <td><b>Policy-Based</b></td>
      <td>Directly optimizes parameterized policy $\pi_\theta(a|s)$ via gradient ascent: $\theta \leftarrow \theta + \alpha \nabla_\theta J(\theta)$.</td>
      <td>Seamlessly scales to high-dimensional continuous action spaces; guarantees smooth policy evolution.</td>
      <td>Extremely high gradient variance; sample inefficient; can get trapped in local optima.</td>
      <td>REINFORCE, Vanilla Policy Gradient (VPG).</td>
    </tr>
    <tr>
      <td><b>Actor-Critic (Hybrid)</b></td>
      <td>The <b>Actor</b> $\pi_\theta(a|s)$ updates policy parameters; the <b>Critic</b> $V_\phi(s)$ or $Q_\phi(s, a)$ learns baseline/value to reduce gradient variance.</td>
      <td>Combines the stability of policy gradients with the variance reduction of value functions. State of the art.</td>
      <td>Two interacting networks can introduce optimization instability; hyperparameter sensitive.</td>
      <td>PPO, TRPO, A2C, SAC, TD3.</td>
    </tr>
    <tr>
      <td><b>Model-Based</b></td>
      <td>Learns an explicit neural model of environment dynamics $\hat{s}_{t+1} = f_\psi(s_t, a_t)$ and plans trajectories using trajectory rollouts.</td>
      <td>Unmatched sample efficiency (orders of magnitude fewer physical steps needed).</td>
      <td>Model exploitation: Policies exploit simulation errors and hallucinations in the learned world model.</td>
      <td>MBPO, DreamerV3, MuZero, PlaNet.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 4 -->
<h2>Part 4: Production Engineering with Gymnasium &amp; PyTorch</h2>
<p>
  To bridge theory and software engineering, below is the production-grade implementation of a clean, vectorized RL environment interaction loop in modern Python (`gymnasium` + `torch`).
</p>

<div class="code-container">
<pre><span class="code-keyword">import</span> torch
<span class="code-keyword">import</span> torch.nn <span class="code-keyword">as</span> nn
<span class="code-keyword">import</span> gymnasium <span class="code-keyword">as</span> gym
<span class="code-keyword">from</span> torch.distributions.normal <span class="code-keyword">import</span> Normal

<span class="code-comment"># 1. Define a Continuous Gaussian Policy Network</span>
<span class="code-keyword">class</span> <span class="code-func">ContinuousGaussianPolicy</span>(nn.Module):
    <span class="code-keyword">def</span> <span class="code-func">__init__</span>(self, obs_dim: int, act_dim: int):
        <span class="code-func">super</span>().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, act_dim)  <span class="code-comment"># Outputs action mean mu(s)</span>
        )
        <span class="code-comment"># Log standard deviation initialized as learnable parameter</span>
        self.log_std = nn.Parameter(torch.zeros(act_dim))

    <span class="code-keyword">def</span> <span class="code-func">forward</span>(self, obs: torch.Tensor):
        <span class="code-comment"># obs shape: [Batch_Size, obs_dim]</span>
        mu = self.net(obs)                         <span class="code-comment"># Shape: [Batch_Size, act_dim]</span>
        std = torch.exp(self.log_std)              <span class="code-comment"># Shape: [act_dim]</span>
        dist = Normal(mu, std)                     <span class="code-comment"># Diagonal Gaussian</span>
        <span class="code-keyword">return</span> dist

<span class="code-comment"># 2. Production Vectorized Rollout Loop</span>
<span class="code-keyword">def</span> <span class="code-func">collect_rollouts</span>(env, policy: nn.Module, steps_per_env: int, num_envs: int):
    obs, info = env.reset()                        <span class="code-comment"># obs shape: [num_envs, obs_dim]</span>
    
    trajectory_buffer = {<span class="code-string">"obs"</span>: [], <span class="code-string">"actions"</span>: [], <span class="code-string">"rewards"</span>: [], <span class="code-string">"dones"</span>: []}
    
    <span class="code-keyword">for</span> step <span class="code-keyword">in</span> <span class="code-func">range</span>(steps_per_env):
        obs_tensor = torch.as_tensor(obs, dtype=torch.float32)
        
        <span class="code-keyword">with</span> torch.no_grad():
            dist = policy(obs_tensor)
            action = dist.sample()                 <span class="code-comment"># Action shape: [num_envs, act_dim]</span>
            log_prob = dist.log_prob(action).sum(dim=-1) <span class="code-comment"># Sum over action dims!</span>
            
        action_numpy = action.cpu().numpy()
        next_obs, rewards, terminated, truncated, infos = env.step(action_numpy)
        dones = terminated | truncated             <span class="code-comment"># Boolean done mask [num_envs]</span>
        
        <span class="code-comment"># Store transition with explicit dimensionality preservation</span>
        trajectory_buffer[<span class="code-string">"obs"</span>].append(obs_tensor)
        trajectory_buffer[<span class="code-string">"actions"</span>].append(action)
        trajectory_buffer[<span class="code-string">"rewards"</span>].append(torch.as_tensor(rewards, dtype=torch.float32).view(-1, 1))
        trajectory_buffer[<span class="code-string">"dones"</span>].append(torch.as_tensor(dones, dtype=torch.float32).view(-1, 1))
        
        obs = next_obs
        
    <span class="code-keyword">return</span> trajectory_buffer
</pre>
</div>

<div class="silent-bug">
  <div class="callout-title">The Multi-Dimensional Action Log-Prob Summation Bug</div>
  <p>
    When using `torch.distributions.Normal(mu, std)`, calling `dist.log_prob(action)` returns a tensor of shape `[Batch_Size, act_dim]`. 
    <b>A fatal bug:</b> If you forget `.sum(dim=-1)`, your loss function will treat each action dimension as an independent training example in the batch dimension! The policy will update incorrectly. Because the joint density of independent variables is the product of their marginals $P(a) = \prod_i P(a_i)$, the log probability must be the sum across action dimensions:
    $$\log \pi_\theta(a|s) = \sum_{i=1}^{d_a} \log \pi_\theta(a_i \mid s)$$
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 5 -->
<h2>Part 5: Practitioner's Debugging Playbook &amp; Common Pitfalls</h2>

<h3>5.1 Pitfall 1: Violating the Markov Assumption via Unobserved Quantities</h3>
<p>
  <b>Symptom:</b> The RL agent reaches a performance plateau far below human level, oscillating endlessly between two conflicting actions in what appears to be the same state.
</p>
<p>
  <b>Root Cause:</b> The environment state is partially observed. For example, in robot manipulation, feeding only end-effector position $(x, y, z)$ without linear velocity $(\dot{x}, \dot{y}, \dot{z})$ or contact force $(F_x, F_y, F_z)$ makes the system non-Markovian. Two identical positions have completely different physical futures depending on whether the arm is accelerating downward or retracting upward.
</p>
<p>
  <b>Remedy:</b> Augment the state representation. Always include:
</p>
<ul>
  <li>First-order temporal derivatives (velocities, angular rates).</li>
  <li>Contact and force-torque sensor histories (or tactile arrays).</li>
  <li>Previous action buffer $a_{t-1}$ to account for actuator latency and delay.</li>
</ul>

<h3>5.2 Pitfall 2: Reward Hacking &amp; The "Cobra Effect"</h3>
<p>
  <b>Symptom:</b> The agent achieves massive numerical reward scores, but its physical behavior is bizarre, destructive, or useless.
</p>
<p>
  <b>Root Cause:</b> <i>Goodhart's Law:</i> "When a measure becomes a target, it ceases to be a good measure." In an infamous OpenAI experiment, an agent trained to steer a boat in a circular race discovered that spinning in tight circles knocking over targets yielded an infinite reward loop without ever finishing the race!
</p>
<div class="warning-box">
  <div class="callout-title">Robotics Slicing Reward Hacking Example</div>
  <p>
    If you reward downward knife velocity: $r_t = v_z$, the robot will slam the blade through the specimen into the metallic cutting board at maximum motor speed (+1000 reward), destroying both the blade and the cutting board! 
    <b>Fix:</b> Use <b>Potential-Based Reward Shaping</b> (Ng et al., 1999) $F(s, s') = \gamma \Phi(s') - \Phi(s)$, which is mathematically guaranteed not to alter the set of optimal policies $\pi^*$.
  </p>
</div>

<h3>5.3 Pitfall 3: Inappropriate Discount Factor $\gamma$</h3>
<p>
  The effective planning horizon of an agent is approximately given by:
  $$H_{\text{eff}} \approx \frac{1}{1 - \gamma}$$
  If $\gamma = 0.9$, $H_{\text{eff}} \approx 10$ steps. The robot becomes completely myopic, unable to take a temporary penalty (retracting the blade to adjust angle) to achieve long-term success. Conversely, if $\gamma = 0.999$, $H_{\text{eff}} \approx 1000$ steps; value estimates suffer from extreme variance and slow learning.
</p>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 6 -->
<h2>Part 6: Multi-Domain Case Studies</h2>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Domain</th>
      <th style="width: 28%;">State Space $\mathcal{S}$</th>
      <th style="width: 24%;">Action Space $\mathcal{A}$</th>
      <th style="width: 28%;">Reward Structure $\mathcal{R}$</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Classic Control (Inverted Pendulum)</b></td>
      <td>Cart position $x$, velocity $\dot{x}$, pole angle $\theta$, angular velocity $\dot{\theta}$ ($\mathbb{R}^4$).</td>
      <td>Horizontal push force $F \in [-10, 10]\text{ N}$ ($\mathbb{R}^1$).</td>
      <td>$+1.0$ for every step the pole angle remains upright ($|\theta| < 12^\circ$). Zero otherwise.</td>
    </tr>
    <tr>
      <td><b>Locomotion (MuJoCo HalfCheetah)</b></td>
      <td>17-dim continuous vector: root height, angles, and velocities of thighs, shins, feet.</td>
      <td>6-dim continuous motor torques applied to hinge joints ($\mathbb{R}^6$).</td>
      <td>$r_t = v_x - 0.1 \|a_t\|_2^2$ (Forward velocity reward minus control effort penalty).</td>
    </tr>
    <tr>
      <td><b>Robotic Manipulation (Dual-Arm Slicing)</b></td>
      <td>Joint angles $(q_1, q_2)$, velocities $(\dot{q}_1, \dot{q}_2)$, blade tactile force $F_z$, mesh deformation depth.</td>
      <td>7-dim impedance setpoints (desired pose offset $\Delta x, \Delta R$ and stiffness $K_p$).</td>
      <td>Progress along cut trajectory minus tissue crushing force penalties ($F_z > 8\text{ N}$) and lateral shear.</td>
    </tr>
    <tr>
      <td><b>LLM Alignment (RLHF / PPO)</b></td>
      <td>Prompt text tokens $x$ concatenated with generated response tokens $y_{1:t-1}$.</td>
      <td>Next-token selection over vocabulary $\mathcal{V}$ ($|\mathcal{A}| \approx 32,000$ to $128,000$).</td>
      <td>Scalar score from Bradley-Terry Reward Model minus KL penalty: $R_{\text{human}}(x, y) - \beta D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})$.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 7 -->
<h2>Part 7: Conceptual Mastery &amp; Exam Challenge</h2>

<div class="quiz-box">
  <div class="quiz-q">Question 1: If an environment has deterministic dynamics $s_{t+1} = f(s_t, a_t)$, does the agent's policy need to be deterministic to act optimally?</div>
  <div class="quiz-a">
    <b>Answer:</b> No. In fact, an optimal deterministic policy $\pi^*(s)$ is always guaranteed to exist for any fully-observable MDP with deterministic or stochastic dynamics (Bellman, 1957). However, during <i>learning</i>, a stochastic policy (such as a Gaussian policy $\pi_\theta(a|s) = \mathcal{N}(\mu, \sigma^2)$) is strictly necessary to drive exploration and ensure non-zero gradient support across the action space.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: Why do environmental transition probabilities $\mathcal{P}(s_{t+1}|s_t, a_t)$ vanish when we compute the gradient of the log trajectory distribution $\nabla_\theta \log p_\theta(\tau)$?</div>
  <div class="quiz-a">
    <b>Answer:</b> Because of the product-to-sum property of logarithms: $\log p_\theta(\tau) = \log \rho_0(s_0) + \sum \log \pi_\theta(a_t|s_t) + \sum \log \mathcal{P}(s_{t+1}|s_t, a_t)$. When we take the partial derivative $\frac{\partial}{\partial \theta}$, terms that do not contain $\theta$ are treated as constants and their derivative is identically zero: $\nabla_\theta \log \mathcal{P}(s_{t+1}|s_t, a_t) = 0$.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: In behavioral cloning, what is the primary factor that causes the error to compound quadratically $\mathcal{O}(\epsilon T^2)$ rather than linearly $\mathcal{O}(\epsilon T)$?</div>
  <div class="quiz-a">
    <b>Answer:</b> Distribution shift (covariate shift). In supervised learning, test samples are drawn from the same distribution as training samples. In closed-loop systems, an error at step $t$ shifts the future states $s_{t+1}, \dots, s_T$ into regions of state space that the expert demonstrator never visited. The agent encounters unfamiliar states where its error rate is far higher than $\epsilon$, remaining off-track for the remaining duration of the episode.
  </div>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    pdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture1_Beginner_Guide.pdf"
    backup_path = "/home/omen/Downloads/CS285_Lecture1_Beginner_Guide.pdf"
    render_utils.build_pdf(html_content, pdf_path, backup_path)
