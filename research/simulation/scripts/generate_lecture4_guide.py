import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 4: Zero-to-Hero Guide to Value Functions & The Bellman Equation</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 4 • Zero-to-Hero Guide to Value Functions";
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
    font-size: 9.5pt;
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
  <span class="course-tag">CS285 Lecture 4 • Zero-to-Hero Field Manual</span>
  <h1>Value Functions &amp; The Bellman Equation</h1>
  <div class="subtitle">A Comprehensive, Intuitive Textbook: Predicting the Future, The Bellman Recursion, Curse of Dimensionality, and Multi-Domain Architectures</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Target Audience:</b> Complete Beginners to Advanced Robotics Practitioners</span>
  </div>
</div>

<!-- SECTION 1: CORE INTUITION -->
<h2>1. What is a Value Function? (The Everyday GPS Analogy)</h2>
<p>
  In Reinforcement Learning, the agent receives an immediate reward $r_t$ at every step. 
  However, optimizing only for the immediate reward leads to catastrophic, short-sighted behavior. 
  An agent needs an internal <b>fortune teller</b> to estimate the long-term future. This is the <b>Value Function</b>.
</p>

<div class="callout intuition">
  <div class="callout-title">🗺️ The Everyday GPS Navigation Analogy</div>
  <p>
    Imagine you are driving home during evening rush hour:
  </p>
  <ul>
    <li><b>State Value $V^\pi(s)$:</b> You are stuck at Exit 4. Your dashboard GPS display reads: <i>"Estimated travel time remaining: 42 minutes."</i> 
      That single number is your State Value $V(s)$! 
      It does not tell you if Exit 4 has nice scenery; it predicts the sum total of your entire future commute from here onward following your usual highway route.
    </li>
    <li><b>Action-Value $Q^\pi(s, a)$:</b> You notice an off-ramp leading to a side street. You wonder: <i>"What happens if I take this specific turn right now?"</i> 
      The GPS recalculates: <i>"Taking side street: 35 minutes."</i> 
      That is $Q(s, \text{side-street})$! It evaluates picking a specific immediate action and then continuing normally thereafter.
    </li>
    <li><b>Advantage $A(s, a) = Q(s, a) - V(s)$:</b> Taking the side street saves you 7 minutes compared to your default route ($42 - 35 = +7$). 
      That $+7$ is your <b>Advantage</b>! If an action has positive advantage, it is better than your habitual policy; if negative, it is a blunder.
    </li>
  </ul>
</div>

<!-- DIAGRAM 1: V, Q, ADVANTAGE VISUAL SLIDER -->
<div class="diagram-container">
<svg width="600" height="110" viewBox="0 0 600 110">
  <rect x="20" y="30" width="130" height="55" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="85" y="52" font-size="10" font-weight="700" fill="#1e40af" text-anchor="middle">STATE $s$</text>
  <text x="85" y="68" font-size="8" fill="#475569" text-anchor="middle">Knife at tomato skin</text>

  <path d="M 150,57 L 220,30" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="220,30 210,30 215,38" fill="#2563eb"/>

  <rect x="220" y="10" width="160" height="40" rx="5" fill="#f8fafc" stroke="#64748b" stroke-width="1.5"/>
  <text x="300" y="27" font-size="9" font-weight="700" fill="#0f172a" text-anchor="middle">State Value $V(s) = 50.0$</text>
  <text x="300" y="42" font-size="7.5" fill="#64748b" text-anchor="middle">Average expected future score</text>

  <path d="M 150,57 L 220,85" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <polygon points="220,85 215,77 210,85" fill="#f59e0b"/>

  <rect x="220" y="65" width="160" height="40" rx="5" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="300" y="82" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">Action Value $Q(s, a) = 65.0$</text>
  <text x="300" y="97" font-size="7.5" fill="#78350f" text-anchor="middle">Score if you choose Sawing action</text>

  <path d="M 390,30 L 430,57 L 390,85" fill="none" stroke="#10b981" stroke-width="2"/>
  <rect x="440" y="35" width="140" height="45" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="510" y="54" font-size="9.5" font-weight="700" fill="#065f46" text-anchor="middle">Advantage $A(s, a)$</text>
  <text x="510" y="70" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">$65.0 - 50.0 = \mathbf{+15.0}$ (Great!)</text>
</svg>
</div>

<div class="page-break"></div>

<!-- SECTION 2: WHY REWARDS AREN'T ENOUGH -->
<h2>2. Why Rewards Aren't Enough (The Effective Horizon)</h2>
<p>
  Beginners often ask: <i>"Why do we need complex Value Functions if we already have the Reward Function?"</i>
</p>
<div class="callout warning-box">
  <div class="callout-title">🍬 The Marshmallow Test in Robotics</div>
  <p>
    Imagine offering a 4-year-old child one marshmallow right now, or two marshmallows if they wait 15 minutes. 
    A greedy child grabs the single marshmallow immediately.
    <br><br>
    In robotic tomato slicing:
    <br>• If a robot only looks at immediate reward $r_t$, it discovers that stopping the blade 1 mm above the skin gives $+0.5$ approach reward with <b>zero risk of crushing</b>. 
    It freezes forever!
    <br>• Slicing through the tough skin requires temporarily taking on high contact force risk in order to reach the massive $+100.0$ reward of a completed cut. 
    <b>A robot must have patience.</b>
  </p>
</div>

<h3>2.1 The Mathematics of Patience: The Effective Planning Horizon</h3>
<p>
  The discount factor $\gamma \in [0, 1)$ mathematically determines the agent's <b>Effective Planning Horizon $H_{\text{eff}}$</b>:
</p>
<div class="formula">
  $$H_{\text{eff}} = \sum_{t=0}^\infty \gamma^t = \frac{1}{1 - \gamma}$$
</div>

<!-- HORIZON TABLE -->
<table>
  <thead>
    <tr>
      <th style="width: 20%;">Discount Factor ($\gamma$)</th>
      <th style="width: 25%;">Effective Horizon ($H_{\text{eff}}$)</th>
      <th style="width: 55%;">Behavioral Impact on the Robot</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\gamma = 0.50$</b></td>
      <td>$2$ steps ($0.04$ sec)</td>
      <td><b>Ultra-Myopic:</b> Cares only about what happens in the next 40 milliseconds. Completely incapable of completing multi-step tasks.</td>
    </tr>
    <tr>
      <td><b>$\gamma = 0.90$</b></td>
      <td>$10$ steps ($0.2$ sec)</td>
      <td><b>Short-Sighted:</b> Good for toy CartPole balance, but fails in manipulation tasks requiring extended contact phases.</td>
    </tr>
    <tr>
      <td><b>$\gamma = 0.99$</b></td>
      <td>$100$ steps ($2.0$ sec)</td>
      <td><b>Standard Robotics Sweet Spot:</b> Balances patience across the full 300-step slicing trajectory without gradient explosion.</td>
    </tr>
    <tr>
      <td><b>$\gamma = 0.995$</b></td>
      <td>$200$ steps ($4.0$ sec)</td>
      <td><b>Long-Horizon Mastery:</b> Used for delicate surgical manipulation, multi-stage peg insertion, and quadruped path traversal.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 3: THE 4 CORE VALUE FUNCTIONS -->
<h2>3. The Four Core Value Functions (Exhaustive Parameter Anatomy)</h2>
<p>
  Every value-based algorithm in deep RL is built upon four rigorous mathematical definitions:
</p>

<h3>3.1 The State-Value Function $V^\pi(s)$</h3>
<div class="formula">
  $$V^\pi(s) = \mathbb{E}_\pi \left[ \sum_{t=0}^\infty \gamma^t r(s_t, a_t) \;\middle|\; s_0 = s \right]$$
</div>

<!-- PARAMETER ANATOMY TABLE 1 -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Parameter</th>
      <th style="width: 20%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 15%;">Example Value</th>
      <th style="width: 15%;">Tuning / Impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$s$</b></td>
      <td>Current State</td>
      <td>The sensory snapshot of the robot and environment right now.</td>
      <td>$z=4.2$ cm, $F_z=5.1$ N</td>
      <td>Input to network.</td>
    </tr>
    <tr>
      <td><b>$\pi$</b></td>
      <td>Policy</td>
      <td>The robot's current habit or decision strategy.</td>
      <td>PyTorch MLP network</td>
      <td>Conditioning factor.</td>
    </tr>
    <tr>
      <td><b>$\mathbb{E}_\pi [\dots]$</b></td>
      <td>Expectation</td>
      <td>Average score across thousands of stochastic simulation episodes.</td>
      <td>Mean across 1,024 envs</td>
      <td>Smooths physics noise.</td>
    </tr>
    <tr>
      <td><b>$\gamma^t$</b></td>
      <td>Discount Multiplier</td>
      <td>Exponentially decays the weight of distant future rewards.</td>
      <td>$\gamma = 0.99$</td>
      <td>Ensures finite sums.</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of $V^\pi(s)$</div>
  <p>
    <b>"If our robot starts in state $s$ and continues executing its current policy $\pi$, what is the total discounted score we expect it to collect by the time the cut finishes?"</b>
  </p>
</div>

<h3>3.2 The Action-Value Function $Q^\pi(s, a)$</h3>
<div class="formula">
  $$Q^\pi(s, a) = r(s, a) + \gamma \mathbb{E}_{s' \sim P(\cdot|s,a)} [V^\pi(s')]$$
</div>
<p>
  <b>Plain English Translation:</b> <i>"If you choose action $a$ right now, you pocket the immediate reward $r(s, a)$, and then you add the discounted value of wherever you land next ($s'$)."</i>
</p>

<h3>3.3 The Optimal Value Functions $V^*(s)$ &amp; $Q^*(s, a)$</h3>
<div class="formula">
  $$V^*(s) = \max_{\pi} V^\pi(s) = \max_{a \in \mathcal{A}} Q^*(s, a)$$
</div>
<p>
  <b>Plain English Translation:</b> <i>"The optimal state value $V^*(s)$ is the score achieved by a theoretical god-tier robot controller that never makes a mistake."</i>
</p>

<div class="page-break"></div>

<!-- SECTION 4: FOUR MULTI-DOMAIN CASE STUDIES -->
<h2>4. Four Real-World Case Studies for Value Functions</h2>
<p>
  Let's observe what Value Functions actually look like across four diverse engineering systems:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 18%;">Domain</th>
      <th style="width: 25%;">State Scenario ($s$)</th>
      <th style="width: 27%;">Predicted State Value $V(s)$</th>
      <th style="width: 30%;">Trial Action-Value $Q(s, a)$</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Soft Fruit Slicing</b></td>
      <td>Blade contacting tomato skin ($z=4.8$ cm, $F_z=4.0$ N).</td>
      <td><b>$V(s) = +45.0$</b><br><small>(High probability of clean slice)</small></td>
      <td>• $Q(s, \text{Sawing}) = \mathbf{+65.0}$ (Great!)<br>• $Q(s, \text{Plunge}) = \mathbf{-20.0}$ (Crush risk!)</td>
    </tr>
    <tr>
      <td><b>2. Autonomous Car</b></td>
      <td>Cruising at 65 mph, lead car brakes gently 40m ahead.</td>
      <td><b>$V(s) = +85.0$</b><br><small>(Safe cruising condition)</small></td>
      <td>• $Q(s, \text{SmoothBrake}) = \mathbf{+88.0}$ (Optimal)<br>• $Q(s, \text{Swerve}) = \mathbf{-150.0}$ (Roll risk)</td>
    </tr>
    <tr>
      <td><b>3. ChatGPT Alignment</b></td>
      <td>User asks: <i>"How do I hotwire a car?"</i></td>
      <td><b>$V(s) = +10.0$</b><br><small>(Sensitive safety boundary state)</small></td>
      <td>• $Q(s, \text{Refusal}) = \mathbf{+50.0}$ (Aligned)<br>• $Q(s, \text{Tutorial}) = \mathbf{-500.0}$ (Jailbreak penalty)</td>
    </tr>
    <tr>
      <td><b>4. Quadruped Robot</b></td>
      <td>Rear left foot slips on wet mud during trot.</td>
      <td><b>$V(s) = +12.0$</b><br><small>(Threatened balance state)</small></td>
      <td>• $Q(s, \text{WidenStance}) = \mathbf{+40.0}$ (Recovered)<br>• $Q(s, \text{StepForward}) = \mathbf{-80.0}$ (Fall!)</td>
    </tr>
  </tbody>
</table>

<div class="callout intuition">
  <div class="callout-title">💡 Why $Q(s, a)$ Enables Instant Control</div>
  <p>
    Notice how $Q(s, a)$ immediately solves the control problem: 
    <b>To pick the optimal action, the robot simply evaluates $Q(s, a)$ for candidate actions and picks the action with the highest number!</b>
    In the autonomous car, $Q(s, \text{SmoothBrake}) = +88 > Q(s, \text{Swerve}) = -150$, so the vehicle brakes smoothly without panic.
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 5: THE BELLMAN EQUATION -->
<h2>5. The Bellman Equation: The Core Miracle of Reinforcement Learning</h2>
<div class="callout intuition">
  <div class="callout-title">🏦 The Bank Account Analogy</div>
  <p>
    Suppose you want to know your total wealth at the end of the year. 
    Do you have to wait until December 31st to calculate it? 
    <b>No!</b> Your net worth at the end of the year is simply: 
    <br><code>(Your savings this month) + (Your projected net worth at the start of next month)</code>.
    <br>You broke an impossible 12-month problem down into <b>1 month of reality + 1 forecast of the future</b>. That is exactly what Richard Bellman discovered in 1957.
  </p>
</div>

<h3>5.1 The Bellman Optimality Equation</h3>
<div class="formula">
  $$Q^*(s, a) = r(s, a) + \gamma \max_{a' \in \mathcal{A}} Q^*(s', a')$$
</div>

<!-- PARAMETER ANATOMY TABLE 2 -->
<table>
  <thead>
    <tr>
      <th style="width: 18%;">Symbol</th>
      <th style="width: 22%;">Formal Name</th>
      <th style="width: 38%;">Plain English Meaning</th>
      <th style="width: 22%;">Example Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$Q^*(s, a)$</b></td>
      <td>Optimal Quality</td>
      <td>The absolute highest score achievable by any possible robot controller.</td>
      <td>$+115.4$ points</td>
    </tr>
    <tr>
      <td><b>$r(s, a)$</b></td>
      <td>Immediate Reward</td>
      <td>Points earned right now on this single microsecond step.</td>
      <td>$+4.2$ points</td>
    </tr>
    <tr>
      <td><b>$\gamma$</b></td>
      <td>Discount Factor</td>
      <td>Patience meter for future rewards.</td>
      <td>$0.99$</td>
    </tr>
    <tr>
      <td><b>$\max_{a'} Q^*(s', a')$</b></td>
      <td>Optimal Future Value</td>
      <td>Assuming the robot acts <i>perfectly</i> from the next state onward, what is the best score?</td>
      <td>$+112.3$ points</td>
    </tr>
  </tbody>
</table>

<!-- DIAGRAM 2: BELLMAN BACKUP TREE -->
<div class="diagram-container">
<svg width="600" height="130" viewBox="0 0 600 130">
  <circle cx="300" cy="18" r="14" fill="#3b82f6"/>
  <text x="300" y="22" font-size="9" font-weight="700" fill="#ffffff" text-anchor="middle">State $s$</text>

  <line x1="300" y1="32" x2="180" y2="58" stroke="#2563eb" stroke-width="2"/>
  <line x1="300" y1="32" x2="420" y2="58" stroke="#2563eb" stroke-width="2"/>

  <circle cx="180" cy="58" r="8" fill="#f59e0b"/>
  <text x="135" y="62" font-size="8" font-weight="700" fill="#b45309">Action $a_1$</text>

  <circle cx="420" cy="58" r="8" fill="#f59e0b"/>
  <text x="465" y="62" font-size="8" font-weight="700" fill="#b45309">Action $a_2$</text>

  <text x="215" y="44" font-size="7.5" fill="#475569">Reward $r_1$</text>
  <text x="385" y="44" font-size="7.5" fill="#475569">Reward $r_2$</text>

  <line x1="180" y1="66" x2="130" y2="100" stroke="#64748b" stroke-width="1.5"/>
  <line x1="180" y1="66" x2="230" y2="100" stroke="#64748b" stroke-width="1.5"/>
  <line x1="420" y1="66" x2="370" y2="100" stroke="#64748b" stroke-width="1.5"/>
  <line x1="420" y1="66" x2="470" y2="100" stroke="#64748b" stroke-width="1.5"/>

  <circle cx="130" cy="100" r="10" fill="#10b981"/>
  <text x="130" y="103" font-size="7.5" fill="#ffffff" text-anchor="middle">$s'_1$</text>
  <text x="130" y="120" font-size="7" fill="#047857" text-anchor="middle">$\gamma V(s'_1)$</text>

  <circle cx="230" cy="100" r="10" fill="#10b981"/>
  <text x="230" y="103" font-size="7.5" fill="#ffffff" text-anchor="middle">$s'_2$</text>
  <text x="230" y="120" font-size="7" fill="#047857" text-anchor="middle">$\gamma V(s'_2)$</text>

  <circle cx="370" cy="100" r="10" fill="#10b981"/>
  <text x="370" y="103" font-size="7.5" fill="#ffffff" text-anchor="middle">$s'_3$</text>
  <text x="370" y="120" font-size="7" fill="#047857" text-anchor="middle">$\gamma V(s'_3)$</text>

  <circle cx="470" cy="100" r="10" fill="#10b981"/>
  <text x="470" y="103" font-size="7.5" fill="#ffffff" text-anchor="middle">$s'_4$</text>
  <text x="470" y="120" font-size="7" fill="#047857" text-anchor="middle">$\gamma V(s'_4)$</text>
</svg>
</div>

<div class="page-break"></div>

<!-- SECTION 6: CURSE OF DIMENSIONALITY -->
<h2>6. Why Classical Matrix Math Fails on Real Robots</h2>
<p>
  In small discrete board games (like Tic-Tac-Toe), you can solve for value functions in closed form via linear algebra:
</p>
<div class="formula">
  $$V^\pi = (I - \gamma P^\pi)^{-1} R^\pi$$
</div>

<div class="callout warning-box">
  <div class="callout-title">🏖️ The Grain of Sand Analogy (Curse of Dimensionality)</div>
  <p>
    Inverting a matrix with $|S|$ states requires <b>$\mathcal{O}(|S|^3)$</b> operations.
    <br><br>
    Suppose you have a 7-DoF robot arm. To represent its joints, you divide each joint's rotation into 100 discrete angles. 
    How many total states is that? 
    <br>$$|S| = 100^7 = 10^{14} \text{ states (100 trillion states!)}$$
    Inverting a $10^{14} \times 10^{14}$ matrix would require $(10^{14})^3 = 10^{42}$ operations. 
    <b>There are more states in a simple robot arm than grains of sand on all the beaches on Earth!</b> 
    This is why classical dynamic programming is completely dead for robotics, and why we use <b>Deep Neural Networks</b> as function approximators ($V_\phi(s)$) to compress continuous state spaces!
  </p>
</div>

<!-- SECTION 7: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>7. Concrete Numerical Walkthrough: 5-Step Backwards Value Diffusion</h2>
<p>
  Let's observe how the Bellman Equation diffuses value backwards across a 5-step robot slicing trajectory with discount factor <b>$\gamma = 0.90$</b>:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 12%;">State</th>
      <th style="width: 32%;">Physical Stage</th>
      <th style="width: 24%;">Immediate Reward $r$</th>
      <th style="width: 32%;">Bellman Calculation: $V(s) = r + \gamma V(s')$</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$s_4$ (Goal)</b></td>
      <td>Blade cleanly touches cutting board. Cut complete!</td>
      <td><b>$r_4 = +100.0$</b></td>
      <td>Terminal State: $V(s_4) = \mathbf{100.0}$</td>
    </tr>
    <tr>
      <td><b>$s_3$</b></td>
      <td>Blade slicing through bottom pericarp skin.</td>
      <td><b>$r_3 = +8.0$</b></td>
      <td>$V(s_3) = 8.0 + 0.90(100.0) = \mathbf{98.0}$</td>
    </tr>
    <tr>
      <td><b>$s_2$</b></td>
      <td>Blade halfway through pulp gel, sawing smoothly.</td>
      <td><b>$r_2 = +5.0$</b></td>
      <td>$V(s_2) = 5.0 + 0.90(98.0) = \mathbf{93.2}$</td>
    </tr>
    <tr>
      <td><b>$s_1$</b></td>
      <td>Blade engaging top tomato skin, lateral shear active.</td>
      <td><b>$r_1 = +3.0$</b></td>
      <td>$V(s_1) = 3.0 + 0.90(93.2) = \mathbf{86.88}$</td>
    </tr>
    <tr>
      <td><b>$s_0$ (Start)</b></td>
      <td>Blade positioned in air 1 cm above tomato.</td>
      <td><b>$r_0 = +0.5$</b></td>
      <td>$V(s_0) = 0.5 + 0.90(86.88) = \mathbf{78.69}$</td>
    </tr>
  </tbody>
</table>

<div class="callout intuition">
  <div class="callout-title">💡 The Magnetic Value Gradient</div>
  <p>
    Look at the progression: $V(s_0)=78.7 \to V(s_1)=86.9 \to V(s_2)=93.2 \to V(s_3)=98.0 \to V(s_4)=100.0$.
    <br>The Bellman equation creates a <b>smooth, rising gradient of value</b> pulling the robot forward. Even though initial state $s_0$ only offers $+0.5$ immediate reward, the agent knows that entering $s_0$ has an expected future value of $78.69$ because it leads to the goal!
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 8: DIARY OF A VALUE TRAINING RUN -->
<h2>8. "Diary of a Training Run" for Value Networks</h2>
<p>
  When training a Critic network $V_\phi(s)$ in PyTorch, what do the loss curves actually mean?
</p>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Iteration Window</th>
      <th style="width: 40%;">Critic Learning Behavior</th>
      <th style="width: 40%;">Diagnostic Metric on TensorBoard</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Iter 0 – 100</b></td>
      <td>Critic weights are random noise. Values are completely uncorrelated with true returns.</td>
      <td><b>Explained Variance $\approx 0.0$</b>. Loss is erratic. Predictions hover around $0 \pm 1$.</td>
    </tr>
    <tr>
      <td><b>Iter 100 – 500</b></td>
      <td>Critic learns the terminal rewards first! States near the cutting board spike to $+100$.</td>
      <td>Value loss spikes temporarily as errors propagate backward through the Bellman graph.</td>
    </tr>
    <tr>
      <td><b>Iter 500 – 2,000</b></td>
      <td>Values smoothly diffuse back to the initial state. Critic accurately predicts returns across 90% of episodes.</td>
      <td><b>Explained Variance rises to $0.85 - 0.95$</b>. Mean squared Bellman error drops by 80%.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 9: PYTORCH IMPLEMENTATION -->
<h2>9. Production PyTorch Value Network &amp; MSBE Loss</h2>

<div class="callout code-box">
  <div class="callout-title">🐍 Complete Value Network &amp; Bellman MSE Loss Implementation</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn

class ValueCritic(nn.Module):
    def __init__(self, state_dim=33):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 256), nn.ELU(),
            nn.Linear(256, 256), nn.ELU(),
            nn.Linear(256, 1)  # Outputs scalar expected future return V(s)
        )
    def forward(self, state):
        return self.net(state)

def compute_bellman_loss(critic, states, rewards, next_states, dones, gamma=0.99):
    # 1. Current value prediction V(s)
    current_values = critic(states)  # Shape: (B, 1)

    # 2. 1-Step Bellman Target: y = r + gamma * V(s') * (1 - done)
    with torch.no_grad():  # Crucial! Target must never pass gradients to itself
        next_values = critic(next_states)
        # Ensure proper shape alignment: (B, 1) to prevent broadcasting bugs
        targets = rewards.unsqueeze(1) + gamma * next_values * (1.0 - dones.unsqueeze(1).float())

    # 3. Mean Squared Bellman Error Loss
    loss = 0.5 * nn.functional.mse_loss(current_values, targets)
    return loss
</pre>
</div>

<!-- SECTION 10: PRACTITIONER'S CHECKLIST -->
<h2>10. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Failure Mode</th>
      <th style="width: 35%;">The Hidden Bug</th>
      <th style="width: 40%;">How to Fix It</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Tensor Broadcasting Trap</b></td>
      <td><code>rewards</code> has shape <code>(B,)</code> while <code>next_values</code> has shape <code>(B, 1)</code>. PyTorch silently expands them into a massive <code>(B, B)</code> matrix, crashing VRAM!</td>
      <td>Always call <code>rewards.unsqueeze(1)</code> and assert shape <code>(B, 1)</code>.</td>
    </tr>
    <tr>
      <td><b>2. Target Gradient Leakage</b></td>
      <td>Failing to wrap target calculation in <code>torch.no_grad()</code> causes gradients to flow into the target. The network chases a vibrating target, causing loss explosion.</td>
      <td>Always compute targets inside <code>with torch.no_grad():</code>.</td>
    </tr>
    <tr>
      <td><b>3. Missing Terminal Mask</b></td>
      <td>When an episode finishes (e.g. tomato crushed), there is no future. Adding $\gamma V(s')$ teaches the agent that crushing tomatoes gives infinite points!</td>
      <td>Always multiply next values by <code>(1.0 - done.float())</code>.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>CS285 Lecture 4 Zero-to-Hero Guide • DEX-ROB Lab (Tianjin University) • Prof. Shan An</i>
</div>

</body>
</html>
"""

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Lecture4_Beginner_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture4_Beginner_Guide.pdf"

render_utils.build_pdf(html_content, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
