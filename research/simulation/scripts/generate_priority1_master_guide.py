import os
import sys

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Priority1_Master_Robotics_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Priority1_Master_Robotics_Guide.pdf"

html_doc = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Priority 1 Master Guide: Zero-to-Hero Robotics Reinforcement Learning Blueprint</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {
      content: "CS285 Priority 1 Master Guide • Zero-to-Hero Robotics RL Blueprint";
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
    font-size: 20pt;
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
    padding: 9px 13px;
    margin: 10px 0;
    border-radius: 6px;
    font-size: 9.1pt;
    page-break-inside: avoid;
  }
  .callout p { margin: 0; }
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
    border-radius: 6px;
    padding: 7px 12px;
    margin: 8px 0;
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

<!-- Cover Block -->
<div class="cover-header">
  <span class="series-tag">UC Berkeley CS 185/285 • Priority 1 Complete Master Compendium</span>
  <h1>Robotics Reinforcement Learning Foundations: Zero to Hero</h1>
  <div class="subtitle">An Intuitive, Parameter-Explained, Visual Field Manual for Dual-Arm Soft Object Slicing (Paper 1: Adaptive Tomato Slicing with PPO / SAC in NVIDIA Isaac Lab via SkRL)</div>
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
  <div class="callout-title">🧭 The Zero-to-Hero Learning Journey</div>
  <p>
    This master compendium is designed to take an absolute beginner with zero prior knowledge of Reinforcement Learning and guide them to true conceptual and practical mastery. 
    Rather than getting lost in dry mathematical calculus, every equation is broken down into a <b>Parameter Anatomy Table</b> explaining what every symbol means in plain English, paired with vivid everyday analogies, rich visual schemas, and concrete numerical examples.
  </p>
</div>

<!-- MODULE 1: LECTURE 1 -->
<h2>Module 1: The Foundations &amp; The Closed Loop (Lecture 1)</h2>
<p>
  <b>(CS285 Lecture 1 • Video ID: DD8APgTEix4)</b> Welcome to the science of teaching computers to make decisions. 
  Traditional machine learning (supervised learning) works like flashcards: you show an AI an image, and you tell it the right answer. 
  In robotics, the physical world has no answer key!
</p>

<h3>1.1 Why Not Just Copy Human Experts? (The Passenger in the Racecar)</h3>
<div class="callout warning-box">
  <div class="callout-title">🚗 The Racecar Passenger Analogy (Covariate Shift)</div>
  <p>
    Suppose you spend 100 hours watching a Formula 1 champion drive. You memorize their steering motions. 
    Now you drive. On turn 3, your hands shake slightly, and the car drifts <b>5 cm onto the dirt shoulder</b>. 
    You crash. Why? <b>Because in 100 hours of watching the expert, they never once drove on the dirt shoulder!</b> 
    You never learned how to recover.
    <br><br>
    This is the mathematical flaw of <b>Behavioral Cloning</b> (Ross &amp; Bagnell, 2011). In open-loop imitation, errors compound quadratically:
  </p>
  <div class="formula">
    $$\text{Open-Loop Imitation Error} \le \mathcal{O}(\epsilon T^2) \quad \text{vs.} \quad \text{Closed-Loop RL Error} \le \mathcal{O}(\epsilon T)$$
  </div>
  <p>
    <b>Parameter Anatomy:</b> $\epsilon$ is the small 1% mistake chance per step; $T$ is the 500-step episode horizon. 
    In open loop, $T^2 = 250,000$ error accumulation! In closed-loop RL, the robot practices recovering from its own mistakes, bounding error strictly to $\epsilon T$.
  </p>
</div>

<!-- DIAGRAM 1: CLOSED LOOP -->
<div class="diagram-container">
<svg width="600" height="95" viewBox="0 0 600 95">
  <rect x="20" y="15" width="220" height="65" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="130" y="38" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">ROBOT BRAIN (Agent)</text>
  <text x="130" y="55" font-size="8.5" fill="#475569" text-anchor="middle">Policy Network $\pi_\theta(a|s)$</text>
  <text x="130" y="68" font-size="8" fill="#64748b" text-anchor="middle">Outputs motor commands</text>

  <path d="M 240,32 L 350,32" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="350,32 342,27 342,37" fill="#2563eb"/>
  <text x="295" y="24" font-size="8.5" font-weight="700" fill="#1d4ed8" text-anchor="middle">Action $a_t \in \mathbb{R}^6$</text>

  <rect x="360" y="15" width="220" height="65" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="470" y="38" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">PHYSICAL WORLD (Env)</text>
  <text x="470" y="55" font-size="8.5" fill="#475569" text-anchor="middle">Isaac Lab / PhysX 5</text>
  <text x="470" y="68" font-size="8" fill="#64748b" text-anchor="middle">Blade-Tomato Contact Forces</text>

  <path d="M 360,68 L 240,68" fill="none" stroke="#10b981" stroke-width="2"/>
  <polygon points="240,68 248,63 248,73" fill="#10b981"/>
  <text x="300" y="82" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">State $s_{t+1} \in \mathbb{R}^{33}$ &amp; Reward $r_t$</text>
</svg>
</div>

<h3>1.2 The Markov Decision Process (MDP) Anatomy</h3>
<p>
  Every RL problem is formally specified as an MDP: $\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma, \rho_0 \rangle$.
</p>
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Symbol</th>
      <th style="width: 20%;">Formal Name</th>
      <th style="width: 40%;">Plain English Meaning</th>
      <th style="width: 25%;">Tomato Slicing Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\mathcal{S}$</b></td>
      <td>State Space</td>
      <td>The current sensory snapshot of the world.</td>
      <td>33 numbers: Joint angles, knife pose, forces, acoustic burst.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{A}$</b></td>
      <td>Action Space</td>
      <td>The motor commands chosen by the robot.</td>
      <td>6 numbers: Feed rate, sawing speed, compliance $\Delta K, \Delta D$.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{P}$</b></td>
      <td>Transition Dynamics</td>
      <td>The laws of physics: where you land next after taking action $a$.</td>
      <td>PhysX 5 simulation of deformable fruit tissue.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{R}$</b></td>
      <td>Reward Function</td>
      <td>The scoreboard: points earned on this step.</td>
      <td>Penetration progress minus crushing force penalty.</td>
    </tr>
    <tr>
      <td><b>$\gamma$</b></td>
      <td>Discount Factor</td>
      <td><b>Patience meter:</b> how much you care about the future.</td>
      <td>$\gamma = 0.99$: Plans for the entire 300-step cut.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- MODULE 2: LECTURE 4 -->
<h2 class="module-header">Module 2: The Core Mathematics &amp; Value Functions (Lecture 4)</h2>
<p>
  <b>(CS285 Lecture 4 • Video ID: FcpIul7rAEE)</b> An agent that only looks at the immediate reward $r_t$ is hopelessly myopic. 
  It needs an internal fortune teller: the <b>Value Function</b>.
</p>

<h3>2.1 The GPS Navigation Analogy: $V(s)$ vs $Q(s, a)$ vs $A(s, a)$</h3>
<div class="callout intuition">
  <div class="callout-title">🗺️ The Everyday GPS Analogy</div>
  <p>
    • <b>State Value $V^\pi(s)$:</b> You are stuck at Exit 4. Your GPS says: <i>"Estimated travel time: 42 minutes."</i> That is $V(s)$! It predicts your total remaining journey under your normal driving habits.
    <br>• <b>Action Value $Q^\pi(s, a)$:</b> You look at an off-ramp. <i>"What if I take this specific side street?"</i> GPS recalculates: <i>"35 minutes."</i> That is $Q(s, \text{side-street})$!
    <br>• <b>Advantage $A(s, a) = Q(s, a) - V(s)$:</b> The side street saves you 7 minutes ($42 - 35 = +7$). That $+7$ is your <b>Advantage</b>! Positive advantage means you made a smart choice.
  </p>
</div>

<h3>2.2 The Bellman Equation: Breaking the Future into Two Pieces</h3>
<div class="formula">
  $$Q^*(s, a) = r(s, a) + \gamma \max_{a' \in \mathcal{A}} Q^*(s', a')$$
</div>
<p>
  <b>Parameter Anatomy:</b> $r(s, a)$ is the cash in your pocket right now; $\gamma$ is your patience meter ($0.99$); $\max_{a'} Q^*(s', a')$ is the best possible score you could achieve tomorrow from the landing state $s'$.
  <br><b>Plain English Translation:</b> <i>"The true value of an action is the reward you get right now, plus the discounted value of the BEST action you can take in the next state."</i>
</p>

<!-- MODULE 3: LECTURE 5 -->
<h2 class="module-header">Module 3: Direct Policy Optimization &amp; Policy Gradients (Lecture 5)</h2>
<p>
  <b>(CS285 Lecture 5 • Video ID: S0D9REIVdg4)</b> You cannot differentiate tomato skin rupture with standard calculus. Policy gradients solve this by treating physics as a black box and learning through trial and error.
</p>

<h3>3.1 The Puppy Training Analogy</h3>
<div class="callout intuition">
  <div class="callout-title">🐶 The "Good Boy!" Theorem</div>
  <p>
    When teaching a puppy to sit, you wait until it randomly happens to sit, and you instantly shout: <i>"GOOD BOY!"</i> and give it bacon.
    <br><br>
    The <b>Policy Gradient Theorem</b> is literally the mathematical formula for "Good Boy!":
  </p>
  <div class="formula">
    $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \cdot \hat{Q}_t \right]$$
  </div>
  <p>
    • <b>$\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ (The Steering Wheel):</b> Points in the direction of neural network weights that makes action $a_t$ more likely.
    <br>• <b>$\hat{Q}_t$ (The Gas Pedal):</b> How good was the action? If $\hat{Q} > 0$, push forward! If $\hat{Q} < 0$, put in reverse!
  </p>
</div>

<h3>3.2 Continuous Gaussian Policies &amp; The Baseline</h3>
<p>
  For continuous robot control, the network outputs mean $\mu$ and standard deviation $\sigma$. 
  The Gaussian score function is $\nabla_\mu \log \pi = \frac{a - \mu}{\sigma^2}$. 
  If a sampled action $a > \mu$ achieved positive reward, it pulls $\mu$ upward towards $a$!
  <br><br>
  <b>Grading on a Curve (The Baseline $b(s)$):</b> If all rewards are positive ($+100, +102, +98$), raw policy gradients push UP every single action. 
  By subtracting the average expected score $b(s) = V(s)$, an action scoring $+98$ gets advantage $\hat{A} = 98 - 100 = \mathbf{-2.0}$, properly suppressing mediocre actions!
</p>

<div class="page-break"></div>

<!-- MODULE 4: LECTURE 6 -->
<h2 class="module-header">Module 4: Actor-Critic Architectures &amp; GAE (Lecture 6)</h2>
<p>
  <b>(CS285 Lecture 6 • Video ID: MzIWiNzrCvw)</b> Full rollouts (Monte Carlo) are noisy. Actor-Critic replaces full rollouts with a learned Critic network to provide immediate microsecond feedback.
</p>

<h3>4.1 The Theater Director &amp; The Road Trip</h3>
<div class="callout intuition">
  <div class="callout-title">🎭 The Stage Actor &amp; The Theater Director</div>
  <p>
    Instead of waiting until midnight for the newspaper review of a 3-hour play (Monte Carlo), the theater director sits in the front row and whispers instant advice after every single line: <i>"Great line cadence!"</i> (+Advantage) or <i>"Too quiet!"</i> (-Advantage).
    <br><br>
    The Critic updates using <b>Temporal Difference (TD) learning</b>:
  </p>
  <div class="formula">
    $$\delta_t = r(s_t, a_t) + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$$
  </div>
  <p>
    <b>The Road Trip Traffic Jam:</b> You estimate a 4-hour drive. 1 hour in, you hit a massive traffic jam and your GPS updates to 6 hours. You don't wait 6 hours to realize your initial estimate was wrong; you update your estimate <b>right now</b>! That surprise factor is the TD residual $\delta_t$.
  </p>
</div>

<h3>4.2 Generalized Advantage Estimation (GAE-$\lambda$): The Blending Slider</h3>
<p>
  Pure TD learning ($\lambda = 0$) has low variance but high bias from an imperfect Critic. Pure rollouts ($\lambda = 1$) have zero bias but huge variance. 
  <b>GAE blends them using parameter $\lambda = 0.95$</b>:
</p>
<div class="formula">
  $$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}$$
</div>
<p>
  <b>Plain English:</b> Advantage today is 100% of today's surprise $\delta_t$, plus 95% of tomorrow's surprise $\delta_{t+1}$, plus 90% of the day after... Capturing long-term reality while eliminating short-term noise!
</p>

<!-- MODULE 5: LECTURE 8 -->
<h2 class="module-header">Module 5: Continuous Control &amp; Soft Actor-Critic (Lecture 8)</h2>
<p>
  <b>(CS285 Lecture 8 • Video ID: lQaVa53pS-Q)</b> In continuous robotics, finding $\arg\max_a Q(s, a)$ is impossible by brute force. SAC solves this through an Actor Maximizer and Maximum Entropy exploration.
</p>

<h3>5.1 The Tourist in Paris (Maximum Entropy RL)</h3>
<div class="callout intuition">
  <div class="callout-title">🥐 The Curious Tourist Analogy</div>
  <p>
    A tourist in Paris who only cares about reward finds one decent croissant on Day 1 and eats croissants at the exact same bakery for 14 days straight. 
    <b>Maximum Entropy RL pays the tourist a bonus for being curious and trying new streets!</b>
  </p>
  <div class="formula">
    $$J(\pi) = \mathbb{E} \left[ r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot \mid s_t)) \right]$$
  </div>
  <p>
    In tomato slicing, entropy temperature $\alpha = 0.2$ stops the robot from freezing above the tomato skin out of fear, encouraging it to explore diverse sawing speeds and angles.
  </p>
</div>

<h3>5.2 The Three Stabilization Super-Weapons of SAC</h3>
<ul>
  <li><b>Replay Buffer (Photo Album):</b> Stores 1,000,000 past steps; samples random batches to break temporal correlation.</li>
  <li><b>Target Networks (Patient Teacher):</b> Target weights update slowly ($\tau = 0.005$, half-life $\approx 138$ steps) so the network isn't chasing a vibrating bullseye.</li>
  <li><b>Clipped Twin-Q (Two Skeptical Judges):</b> Trains two independent critics $Q_1$ and $Q_2$ and takes $\min(Q_1, Q_2)$, eliminating delusional overestimation bias!</li>
</ul>

<div class="page-break"></div>

<!-- MODULE 6: LECTURE 10 -->
<h2 class="module-header">Module 6: Advanced Policy Gradients &amp; PPO (Lecture 10)</h2>
<p>
  <b>(CS285 Lecture 10 • Video ID: m7IU5KBS4sw)</b> Proximal Policy Optimization (PPO) is the king of modern GPU robotics. It prevents the catastrophic failure mode of RL: <b>Policy Collapse</b>.
</p>

<h3>6.1 Burning Textbooks &amp; Bowling Bumpers</h3>
<div class="callout warning-box">
  <div class="callout-title">💥 Policy Collapse vs Bowling Bumpers</div>
  <p>
    <b>The Catastrophe:</b> A medical student tries a new study method on Friday, does poorly on a practice test on Saturday, and in a panic, <b>burns all their textbooks and forgets how to read</b>! In RL, an oversized gradient step produces garbage trajectories, creating a permanent death spiral.
    <br><br>
    <b>PPO's Bowling Bumpers:</b> PPO places inflatable bumpers on policy updates. The probability of an action is never allowed to change by more than <b>20% ($\epsilon = 0.2$)</b>:
  </p>
  <div class="formula">
    $$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon) \hat{A}_t \right) \right]$$
  </div>
  <p>
    <b>The 10x Speedup Secret in Isaac Lab:</b> Because clipping guarantees stability, you can train for <b>5 epochs</b> on the exact same batch of 1,024 parallel GPU simulation rollouts, speeding up training by 10x!
  </p>
</div>

<!-- MODULE 7: 12-DIMENSION COMPARISON MATRIX -->
<h2 class="module-header">Module 7: The Master 12-Dimension Algorithm Grand Comparison Matrix</h2>
<p>
  The authoritative reference comparison across all six foundational reinforcement learning algorithms:
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
  Here is the complete operational blueprint connecting CS285 Priority 1 directly to your Master's thesis methodology: 
  <b>Adaptive Dual-Arm Soft Object Slicing with PPO / SAC in NVIDIA Isaac Lab via SkRL</b>.
</p>

<h3>8.1 Multi-Modal State Space Mapping ($\mathbb{R}^{33}$)</h3>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Subsystem</th>
      <th style="width: 15%;">Dimension</th>
      <th style="width: 35%;">Sensor / Physical Origin</th>
      <th style="width: 25%;">Normalization Range</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Arm Kinematics</b></td>
      <td>$\mathbb{R}^{14}$</td>
      <td>Dual-arm joint angles $q$ (7) and velocities $\dot{q}$ (7).</td>
      <td>Normalized by physical joint limits.</td>
    </tr>
    <tr>
      <td><b>Blade Kinematics</b></td>
      <td>$\mathbb{R}^9$</td>
      <td>Blade tip 3D position $p$, linear velocity $v$, angular velocity $\omega$.</td>
      <td>Relative to cutting board frame.</td>
    </tr>
    <tr>
      <td><b>Tomato Geometry</b></td>
      <td>$\mathbb{R}^7$</td>
      <td>3D center of mass $p$ and orientation quaternion $q$.</td>
      <td>USD pose in sim; YOLO/RGB-D in real.</td>
    </tr>
    <tr>
      <td><b>TacBlade F/T</b></td>
      <td>$\mathbb{R}^6$</td>
      <td>3-axis force ($F_x, F_y, F_z$) and torque ($T_x, T_y, T_z$).</td>
      <td>Filtered 50 Hz; $F_z \in [0, 25]$ N.</td>
    </tr>
    <tr>
      <td><b>Acoustic Burst</b></td>
      <td>$\mathbb{R}^1$</td>
      <td>RMS acoustic energy envelope ($100 \text{ Hz} - 5 \text{ kHz}$).</td>
      <td>Detects exact millisecond of skin puncture.</td>
    </tr>
    <tr style="background: #eff6ff;">
      <td><b>Total State $\mathcal{S}$</b></td>
      <td><b>$\mathbb{R}^{33}$</b></td>
      <td><b>Full Markovian observation vector fed to Actor &amp; Critic.</b></td>
      <td><b>Standardized via running mean and variance.</b></td>
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
      <td>Impedance modulation: softens blade upon contact to avoid crushing.</td>
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

<h3>8.3 PyTorch Multi-Objective Reward Function</h3>
<div class="callout code-box">
  <div class="callout-title">🐍 Vectorized PyTorch Reward Function (`tomato_cutting_env.py`)</div>
<pre style="margin: 0; padding: 0;">
def compute_rewards(self) -&gt; torch.Tensor:
    # 1. Penetration progress: Downward movement through tomato height
    z_progress = torch.clamp(self.prev_knife_z - self.knife_z, min=0.0)
    r_pen = 6.0 * z_progress

    # 2. Sawing shear: Reward sawing velocity only while blade is in contact
    v_slice = torch.abs(self.knife_vel[:, 0])
    in_contact = (self.blade_force[:, 2] &gt; 0.4).float()
    r_slice = 3.0 * v_slice * in_contact

    # 3. Crushing penalty: Penalize normal force exceeding 8.0 N puncture threshold
    excess_force = torch.clamp(self.blade_force[:, 2] - 8.0, min=0.0)
    p_crush = -4.0 * torch.square(excess_force)

    # 4. Action smoothness: Penalize high-frequency chatter in motor torques
    action_diff = self.actions - self.prev_actions
    p_smooth = -0.05 * torch.sum(torch.square(action_diff), dim=-1)

    # 5. Terminal Conditions: Success (+120) vs Catastrophic Pulp Destroy (-60)
    r_term = torch.zeros_like(r_pen)
    r_term = torch.where(self.reached_board &amp; (excess_force == 0), r_term + 120.0, r_term)
    r_term = torch.where(self.blade_force[:, 2] &gt; 22.0, r_term - 60.0, r_term)

    return r_pen + r_slice + p_crush + p_smooth + r_term
</pre>
</div>

<div class="page-break"></div>

<!-- MODULE 9: SKRL CODE -->
<h2>Module 9: Production SkRL &amp; PyTorch Architecture</h2>

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
            nn.Linear(in_dim, 256), nn.ELU(),
            nn.Linear(256, 256), nn.ELU()
        )
        self.actor_mean = nn.Linear(256, out_dim)
        self.log_std_parameter = nn.Parameter(torch.zeros(out_dim))
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
<div class="callout code-box">
  <div class="callout-title">⚙️ Production ppo_cfg.yaml Reference</div>
<pre style="margin: 0; padding: 0;">
algorithm:
  class: PPO
  clip_range: 0.2            # Lecture 10: Bowling bumpers preventing policy collapse
  gae_lambda: 0.95           # Lecture 6: Optimal exponential blend of TD(0) and MC
  discount_factor: 0.99      # Lecture 4: γ = 0.99 ensures planning across 300+ steps
  learning_rate: 3e-4        # Standard Adam step size
  learning_rate_scheduler: KLAdaptiveLR  # Scales LR based on policy KL divergence
  entropy_loss_scale: 0.01   # Lecture 8: Encourages exploration of impedance parameters
  value_loss_scale: 1.0      # Weight of Critic MSE regression loss
  epochs: 5                  # Lecture 10: Safely re-uses parallel GPU rollout batches
  mini_batches: 4            # Subdivides 1,024 parallel envs into mini-batches
</pre>
</div>

<!-- MODULE 10: THESIS DEFENSE CHEATSHEET -->
<h2>Module 10: Thesis Defense Master Cheatsheet (Top 10 Q&amp;A)</h2>
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
