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
  <span class="course-tag">CS285 Lecture 4 • Zero-to-Hero Field Manual</span>
  <h1>Value Functions &amp; The Bellman Equation</h1>
  <div class="subtitle">From Scratch to Mastery: Understanding How AI Estimates the Future, Evaluates Quality, and Solves Sequential Decisions</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Focus:</b> $V^\pi(s)$, $Q^\pi(s,a)$, Advantage $A(s,a)$, &amp; The Bellman Recursion</span>
  </div>
</div>

<!-- SECTION 1: CORE INTUITION & THE GPS ANALOGY -->
<h2>1. What is a Value Function? (The Everyday GPS Analogy)</h2>
<p>
  In Reinforcement Learning, the robot receives rewards at each step. But if an agent only cares about the reward <i>right now</i>, it will make terrible life decisions (like eating candy for breakfast or stopping the knife the millisecond it touches the tomato skin). 
  The agent needs an internal <b>fortune teller</b> to predict what the future holds. This is the <b>Value Function</b>.
</p>

<div class="callout intuition">
  <div class="callout-title">🗺️ The Everyday GPS Navigation Analogy</div>
  <p>
    Imagine you are driving home during rush hour:
  </p>
  <ul>
    <li><b>State Value $V(s)$:</b> You are stuck at Exit 4. Your GPS screen says: <i>"Estimated travel time: 42 minutes."</i> That single prediction is your State Value $V(s)$! It doesn't tell you how pretty Exit 4 is; it estimates the sum total of your entire future trip from here on.</li>
    <li><b>Action-Value $Q(s, a)$:</b> You glance at an off-ramp leading to a side street. You wonder: <i>"What happens if I take this specific turn right now?"</i> The GPS recalculates: <i>"Taking side street: 35 minutes."</i> That is $Q(s, \text{side-street})$! It evaluates picking a specific immediate action and then driving normally thereafter.</li>
    <li><b>Advantage $A(s, a) = Q(s, a) - V(s)$:</b> Taking the side street saves you 7 minutes compared to your default route ($42 - 35 = +7$). That $+7$ is your <b>Advantage</b>! If an action has positive advantage, it is better than your current habit; if negative, it is a blunder.</li>
  </ul>
</div>

<!-- DIAGRAM 1: THE V, Q, AND ADVANTAGE SLIDER -->
<div class="diagram-container">
<svg width="600" height="110" viewBox="0 0 600 110">
  <!-- State Box -->
  <rect x="20" y="30" width="130" height="55" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="85" y="52" font-size="10" font-weight="700" fill="#1e40af" text-anchor="middle">STATE $s$</text>
  <text x="85" y="68" font-size="8" fill="#475569" text-anchor="middle">Knife at tomato skin</text>

  <!-- Value Arrow -->
  <path d="M 150,57 L 220,30" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="220,30 210,30 215,38" fill="#2563eb"/>

  <!-- V(s) Box -->
  <rect x="220" y="10" width="160" height="40" rx="5" fill="#f8fafc" stroke="#64748b" stroke-width="1.5"/>
  <text x="300" y="27" font-size="9" font-weight="700" fill="#0f172a" text-anchor="middle">State Value $V(s) = 50.0$</text>
  <text x="300" y="42" font-size="7.5" fill="#64748b" text-anchor="middle">Average expected score from here</text>

  <!-- Action Arrow -->
  <path d="M 150,57 L 220,85" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <polygon points="220,85 215,77 210,85" fill="#f59e0b"/>

  <!-- Q(s, a) Box -->
  <rect x="220" y="65" width="160" height="40" rx="5" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="300" y="82" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">Action Value $Q(s, a) = 65.0$</text>
  <text x="300" y="97" font-size="7.5" fill="#78350f" text-anchor="middle">Score if you choose Sawing action</text>

  <!-- Difference Bracket: Advantage -->
  <path d="M 390,30 L 430,57 L 390,85" fill="none" stroke="#10b981" stroke-width="2"/>
  <rect x="440" y="35" width="140" height="45" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="510" y="54" font-size="9.5" font-weight="700" fill="#065f46" text-anchor="middle">Advantage $A(s, a)$</text>
  <text x="510" y="70" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">$65.0 - 50.0 = \mathbf{+15.0}$ (Great!)</text>
</svg>
</div>

<!-- SECTION 2: THE 4 CORE VALUE FUNCTIONS -->
<h2>2. The Four Fundamental Value Functions (Parameter Anatomy)</h2>
<p>
  Every value-based algorithm in deep RL revolves around four mathematical definitions:
</p>

<h3>2.1 The State-Value Function $V^\pi(s)$</h3>
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
      <td>Where the robot is right now.</td>
      <td>$z=4.2$ cm, $F_z=5$ N</td>
      <td>Input to network.</td>
    </tr>
    <tr>
      <td><b>$\pi$</b></td>
      <td>Current Policy</td>
      <td>The robot's current habit or decision rules.</td>
      <td>SkRL PPO policy network</td>
      <td>Conditioning factor.</td>
    </tr>
    <tr>
      <td><b>$\mathbb{E}_\pi [\dots]$</b></td>
      <td>Expectation Operator</td>
      <td>The average across thousands of stochastic simulation runs.</td>
      <td>Mean over 1,024 envs</td>
      <td>Smooths out noise.</td>
    </tr>
    <tr>
      <td><b>$\gamma^t$</b></td>
      <td>Discount Factor</td>
      <td>Multiplies rewards at step $t$. Exponentially discounts the distant future.</td>
      <td>$\gamma = 0.99$</td>
      <td>If $\gamma=0$, myopic; if $\gamma=1$, infinite sum.</td>
    </tr>
    <tr>
      <td><b>$r(s_t, a_t)$</b></td>
      <td>Instantaneous Reward</td>
      <td>The immediate point score received at step $t$.</td>
      <td>$+2.5$ (Sawing reward)</td>
      <td>Raw physical feedback.</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of $V^\pi(s)$</div>
  <p>
    <b>"If our robot starts in state $s$ and continues cutting using its current policy $\pi$, what is the total discounted score we expect it to collect by the time the cut finishes?"</b>
  </p>
</div>

<h3>2.2 The Action-Value Function $Q^\pi(s, a)$</h3>
<div class="formula">
  $$Q^\pi(s, a) = r(s, a) + \gamma \sum_{s' \in \mathcal{S}} P(s' \mid s, a) V^\pi(s')$$
</div>

<!-- PARAMETER ANATOMY TABLE 2 -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Parameter</th>
      <th style="width: 20%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 30%;">Physical Robotics Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$a$</b></td>
      <td>Immediate Action</td>
      <td>The trial action tested right now, regardless of what policy $\pi$ would normally do.</td>
      <td>Increase lateral sawing velocity by $+15$ mm/s.</td>
    </tr>
    <tr>
      <td><b>$r(s, a)$</b></td>
      <td>Immediate Payoff</td>
      <td>The instant reward generated by this trial action.</td>
      <td>Immediate shear friction bonus ($+3.0$).</td>
    </tr>
    <tr>
      <td><b>$P(s' \mid s, a)$</b></td>
      <td>Transition Probability</td>
      <td>Where the physical world lands in response to trial action $a$.</td>
      <td>PhysX 5 simulation contact response.</td>
    </tr>
    <tr>
      <td><b>$V^\pi(s')$</b></td>
      <td>Downstream Value</td>
      <td>The future value of the landing state $s'$.</td>
      <td>Remaining score to finish the tomato slice.</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of $Q^\pi(s, a)$</div>
  <p>
    <b>"If you take action $a$ right now, you pocket the immediate reward $r(s, a)$, and then you add the discounted value of wherever you land next ($s'$)."</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: THE BELLMAN EQUATION -->
<h2>3. The Bellman Equation: The Core Miracle of Reinforcement Learning</h2>
<p>
  How can an AI learn to predict the sum of 500 future steps without actually playing through all 500 steps every time? 
  The answer is the <b>Bellman Equation</b>, invented by Richard Bellman in 1957.
</p>

<div class="callout intuition">
  <div class="callout-title">💡 The Bank Account Analogy</div>
  <p>
    Suppose you want to know your total net worth at the end of the year. 
    Do you have to wait until December 31st to calculate it? 
    <b>No!</b> Your net worth at the end of the year is simply: 
    <br><code>(Your paycheck this month) + (Your net worth at the start of next month)</code>.
    <br>You broke a 12-month problem down into <b>1 month of reality + 1 prediction of the future</b>. That is exactly what the Bellman Equation does!
  </p>
</div>

<h3>3.1 The Bellman Optimality Equation</h3>
<div class="formula">
  $$Q^*(s, a) = r(s, a) + \gamma \max_{a' \in \mathcal{A}} Q^*(s', a')$$
</div>

<!-- PARAMETER ANATOMY TABLE 3 -->
<table>
  <thead>
    <tr>
      <th style="width: 18%;">Symbol</th>
      <th style="width: 25%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 22%;">Example Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$Q^*(s, a)$</b></td>
      <td>Optimal Action-Value</td>
      <td>The absolute highest score achievable by any possible robot controller.</td>
      <td>$+115.4$</td>
    </tr>
    <tr>
      <td><b>$r(s, a)$</b></td>
      <td>Immediate Reward</td>
      <td>Points earned right now on this step.</td>
      <td>$+4.2$</td>
    </tr>
    <tr>
      <td><b>$\gamma$</b></td>
      <td>Discount Factor</td>
      <td>Patience multiplier for future points.</td>
      <td>$0.99$</td>
    </tr>
    <tr>
      <td><b>$\max_{a'} Q^*(s', a')$</b></td>
      <td>Optimal Future Quality</td>
      <td>Assuming you play <i>perfectly</i> from state $s'$ onward, what is the best possible score?</td>
      <td>$+112.3$</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Bellman Optimality Equation</div>
  <p>
    <b>"The true optimal score of an action is the reward you get right now, plus the discounted value of the BEST action you could possibly take in the next state."</b>
  </p>
</div>

<!-- DIAGRAM 2: BELLMAN BACKUP TREE -->
<div class="diagram-container">
<svg width="600" height="130" viewBox="0 0 600 130">
  <!-- Current state node -->
  <circle cx="300" cy="18" r="14" fill="#3b82f6"/>
  <text x="300" y="22" font-size="9" font-weight="700" fill="#ffffff" text-anchor="middle">State $s$</text>

  <!-- Action branches -->
  <line x1="300" y1="32" x2="180" y2="58" stroke="#2563eb" stroke-width="2"/>
  <line x1="300" y1="32" x2="420" y2="58" stroke="#2563eb" stroke-width="2"/>

  <!-- Action nodes -->
  <circle cx="180" cy="58" r="8" fill="#f59e0b"/>
  <text x="140" y="62" font-size="8" font-weight="700" fill="#b45309">Action $a_1$</text>

  <circle cx="420" cy="58" r="8" fill="#f59e0b"/>
  <text x="460" y="62" font-size="8" font-weight="700" fill="#b45309">Action $a_2$</text>

  <!-- Immediate reward labels -->
  <text x="215" y="44" font-size="7.5" fill="#475569">Reward $r_1$</text>
  <text x="385" y="44" font-size="7.5" fill="#475569">Reward $r_2$</text>

  <!-- Transition to next states -->
  <line x1="180" y1="66" x2="130" y2="100" stroke="#64748b" stroke-width="1.5"/>
  <line x1="180" y1="66" x2="230" y2="100" stroke="#64748b" stroke-width="1.5"/>
  <line x1="420" y1="66" x2="370" y2="100" stroke="#64748b" stroke-width="1.5"/>
  <line x1="420" y1="66" x2="470" y2="100" stroke="#64748b" stroke-width="1.5"/>

  <!-- Next state nodes -->
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

<!-- SECTION 4: CURSE OF DIMENSIONALITY -->
<h2>4. Why Classical Matrix Math Fails on Real Robots</h2>
<p>
  If we know the transition matrix $P$ and reward vector $R$, we can solve for $V$ in closed form via linear algebra:
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
    This is why classical dynamic programming is completely dead for robotics, and why we use <b>Deep Neural Networks</b> to approximate $V_\phi(s)$ and $Q_\theta(s, a)$.
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 5: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>5. Concrete Numerical Walkthrough: 3-State Bellman Backup</h2>
<p>
  Let's calculate real numbers across a 3-step robot chain to see how the Bellman Equation propagates values backwards!
  Suppose discount factor <b>$\gamma = 0.90$</b>.
</p>

<table>
  <thead>
    <tr>
      <th style="width: 15%;">State</th>
      <th style="width: 30%;">Physical Meaning</th>
      <th style="width: 25%;">Immediate Reward $r$</th>
      <th style="width: 30%;">Bellman Value Calculation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$s_2$ (Goal)</b></td>
      <td>Blade slices through bottom skin, touches board cleanly.</td>
      <td><b>$r_2 = +100.0$</b></td>
      <td>Terminal state: $V(s_2) = \mathbf{100.0}$</td>
    </tr>
    <tr>
      <td><b>$s_1$</b></td>
      <td>Blade is halfway through pulp, sawing smoothly.</td>
      <td><b>$r_1 = +5.0$</b></td>
      <td>$V(s_1) = r_1 + \gamma V(s_2) = 5.0 + 0.9(100.0) = \mathbf{95.0}$</td>
    </tr>
    <tr>
      <td><b>$s_0$ (Start)</b></td>
      <td>Blade touches top tomato skin.</td>
      <td><b>$r_0 = +2.0$</b></td>
      <td>$V(s_0) = r_0 + \gamma V(s_1) = 2.0 + 0.9(95.0) = \mathbf{87.5}$</td>
    </tr>
  </tbody>
</table>

<div class="callout intuition">
  <div class="callout-title">💡 Notice the Backwards Diffusion of Value!</div>
  <p>
    Look at $V(s_0) = 87.5$. Even though the initial skin contact only gave $+2.0$ immediate points, the agent knows that being in state $s_0$ has an expected future value of $87.5$ because it leads to the $+100$ goal! 
    This gradient of value ($87.5 \to 95.0 \to 100.0$) acts like a magnetic pull guiding the robot toward the goal.
  </p>
</div>

<!-- SECTION 6: PYTORCH IMPLEMENTATION -->
<h2>6. PyTorch Value Function &amp; Bellman MSE Loss</h2>
<p>
  How do we train a neural network to learn $V(s)$ in Python? We train it to minimize the <b>Mean Squared Bellman Error (MSBE)</b>:
</p>

<div class="callout code-box">
  <div class="callout-title">🐍 PyTorch Value Network &amp; Bellman Loss</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn

# 1. Define Value Network: Takes 33D state, outputs scalar predicted value V(s)
class ValueNetwork(nn.Module):
    def __init__(self, state_dim=33):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 1)  # Single scalar output
        )
    def forward(self, state):
        return self.net(state)

# 2. Bellman Target & Loss Computation
def compute_value_loss(critic, states, rewards, next_states, dones, gamma=0.99):
    # Predict current value V(s)
    current_v = critic(states)  # Shape: (B, 1)

    # Compute 1-step Bellman Target: y = r + gamma * V(s') * (1 - done)
    with torch.no_grad():  # Crucial! Target must be detached
        next_v = critic(next_states)
        targets = rewards.unsqueeze(1) + gamma * next_v * (1.0 - dones.unsqueeze(1))

    # Mean Squared Error: Loss = 0.5 * (Target - Prediction)^2
    loss = 0.5 * nn.functional.mse_loss(current_v, targets)
    return loss
</pre>
</div>

<!-- SECTION 7: PRACTITIONER'S CHECKLIST -->
<h2>7. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Bug / Failure Mode</th>
      <th style="width: 35%;">The Silent Symptom</th>
      <th style="width: 40%;">How to Fix It</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Tensor Broadcasting Bug</b></td>
      <td><code>rewards</code> has shape <code>(B,)</code> while <code>next_v</code> has shape <code>(B, 1)</code>. PyTorch silently broadcasts them into a <code>(B, B)</code> matrix, allocating gigabytes of VRAM and crashing!</td>
      <td>Always verify shapes: <code>rewards.unsqueeze(1)</code> to ensure both operands are strictly <code>(B, 1)</code>.</td>
    </tr>
    <tr>
      <td><b>2. Forgetting to Detach Target</b></td>
      <td>If you don't use <code>torch.no_grad()</code> or <code>.detach()</code> on the target $y$, gradients flow into the target. The network chases a moving target, causing loss explosion.</td>
      <td>Always wrap target computation in <code>with torch.no_grad():</code>.</td>
    </tr>
    <tr>
      <td><b>3. Missing Terminal Masking</b></td>
      <td>When an episode ends (e.g. tomato crushed), there is no next state $s'$. If you still add $\gamma V(s')$, the network learns that crushing the tomato has infinite future value!</td>
      <td>Always multiply next state value by <code>(1.0 - done)</code>.</td>
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
