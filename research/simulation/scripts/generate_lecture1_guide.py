import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 1: Zero-to-Hero Guide to Reinforcement Learning & The Closed Loop</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 1 • Zero-to-Hero Guide to Reinforcement Learning";
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

  /* Callout Boxes */
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

  /* Formula display */
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

  .badge {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: 600;
  }
  .badge-blue { background: #dbeafe; color: #1e40af; }
  .badge-green { background: #d1fae5; color: #065f46; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-red { background: #fee2e2; color: #991b1b; }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">CS285 Lecture 1 • Zero-to-Hero Field Manual</span>
  <h1>Foundations of Reinforcement Learning &amp; The Closed Loop</h1>
  <div class="subtitle">From Absolute Beginner to Master: Intuition, Parameter Anatomy, Everyday Analogies, and The Core Mathematics of Decision Making</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Focus:</b> Closed-Loop Control, MDPs, POMDPs, &amp; The Modern RL Landscape</span>
  </div>
</div>

<!-- SECTION 1: THE CORE INTUITION -->
<h2>1. What is Reinforcement Learning? (The "Zero-to-Hero" Intuition)</h2>
<p>
  Imagine you want to teach a toddler how to ride a bicycle. How would you do it?
</p>
<ul>
  <li><b>The Supervised Learning Way:</b> You sit the child at a desk and show them 10,000 flashcards. Card 1: <i>"If you lean 2° left, contract your right quadricep by 14 Newtons."</i> The child memorizes all the cards, sits on the bicycle, wobbles 2.1° to the left, enters a situation not on any flashcard, panics, and crashes.</li>
  <li><b>The Reinforcement Learning Way:</b> You put a helmet on the child and hold the seat. The child pushes the pedals. When they balance and coast forward, they feel a rush of excitement (<b>Reward</b>). When they wobble and scrape their knee, it hurts (<b>Penalty</b>). Nobody gave the child mathematical formulas for gyroscopic precession. Through <i>trial, error, and feedback</i>, the child's brain automatically builds an intuitive control policy.</li>
</ul>

<div class="callout intuition">
  <div class="callout-title">💡 The Core Philosophy: Learning by Interaction</div>
  <p>
    <b>Reinforcement Learning is not about memorizing answers. It is about learning consequences.</b> 
    In supervised learning, an external teacher tells you the "correct answer" for every input. 
    In RL, there is no teacher. There is only a <i>scorekeeper</i> (the environment) that gives you a numerical reward or penalty after you act. The agent must figure out which actions caused the reward.
  </p>
</div>

<!-- DIAGRAM 1: THE AGENT-ENVIRONMENT CLOSED LOOP -->
<div class="diagram-container">
<svg width="600" height="110" viewBox="0 0 600 110">
  <!-- Agent Box -->
  <rect x="30" y="20" width="200" height="70" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="130" y="45" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">AGENT (Robot Brain)</text>
  <text x="130" y="62" font-size="8.5" fill="#475569" text-anchor="middle">Neural Network Policy $\pi_\theta(a|s)$</text>
  <text x="130" y="76" font-size="7.5" fill="#64748b" text-anchor="middle">Learns from experience</text>

  <!-- Forward Arrow: Action -->
  <path d="M 230,40 L 360,40" fill="none" stroke="#2563eb" stroke-width="2.5"/>
  <polygon points="360,40 350,34 350,46" fill="#2563eb"/>
  <text x="295" y="32" font-size="9" font-weight="700" fill="#1d4ed8" text-anchor="middle">Action $a_t$</text>
  <text x="295" y="52" font-size="7.5" fill="#64748b" text-anchor="middle">(Torque, Velocity, Steering)</text>

  <!-- Environment Box -->
  <rect x="370" y="20" width="200" height="70" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="470" y="45" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">ENVIRONMENT (Physical World)</text>
  <text x="470" y="62" font-size="8.5" fill="#475569" text-anchor="middle">Physics, Objects, Sensors</text>
  <text x="470" y="76" font-size="7.5" fill="#64748b" text-anchor="middle">NVIDIA Isaac Sim / Real World</text>

  <!-- Feedback Arrow: State & Reward -->
  <path d="M 370,80 L 230,80" fill="none" stroke="#10b981" stroke-width="2.5"/>
  <polygon points="230,80 240,74 240,86" fill="#10b981"/>
  <text x="300" y="73" font-size="9" font-weight="700" fill="#047857" text-anchor="middle">State $s_{t+1}$ &amp; Reward $r_t$</text>
  <text x="300" y="94" font-size="7.5" fill="#64748b" text-anchor="middle">(Sensory observations &amp; score)</text>
</svg>
</div>

<!-- SECTION 2: WHY IMITATION FAILS -->
<h2>2. Why Not Just Copy Human Experts? (The Imitation Trap)</h2>
<p>
  A common beginner question is: <i>"Why don't we just record a human expert operating the robot and train a neural network to mimic the human?"</i> 
  This is called <b>Behavioral Cloning (Imitation Learning)</b>. While it sounds simple, it suffers from a fatal mathematical problem: <b>Covariate Shift</b>.
</p>

<div class="callout warning-box">
  <div class="callout-title">🚗 The Passenger in the Racecar Analogy</div>
  <p>
    Imagine you spend 100 hours watching a Formula 1 champion drive around a track. The champion drives perfectly, staying exactly on the racing line. You memorize every steering motion.
    <br><br>
    Now you get behind the wheel. On turn 3, your hands shake slightly, and the car drifts <b>just 5 cm onto the dirt shoulder</b>. 
    You freeze. Why? <b>Because in 100 hours of watching the champion, you never once saw what to do on the dirt shoulder!</b> The champion never made a mistake, so you never learned how to recover from one. You slide into the wall.
  </p>
</div>

<!-- DIAGRAM 2: DRIFT OF DOOM VS CLOSED LOOP -->
<div class="diagram-container">
<svg width="600" height="120" viewBox="0 0 600 120">
  <!-- Open Loop: Behavioral Cloning -->
  <text x="140" y="18" font-size="9.5" font-weight="700" fill="#b91c1c" text-anchor="middle">Behavioral Cloning: Compounding Drift $\mathcal{O}(\epsilon T^2)$</text>
  <path d="M 30,50 Q 80,45 130,48" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="4,4"/>
  <text x="60" y="40" font-size="7.5" fill="#64748b">Expert Path</text>
  <!-- Robot drifting off -->
  <path d="M 30,50 Q 70,55 110,75 Q 150,105 240,115" fill="none" stroke="#ef4444" stroke-width="2.5"/>
  <circle cx="110" cy="75" r="4" fill="#ef4444"/>
  <text x="145" y="70" font-size="7.5" font-weight="700" fill="#b91c1c">Tiny 2mm error!</text>
  <text x="210" y="105" font-size="8" font-weight="700" fill="#dc2626">CATASTROPHIC CRASH</text>

  <!-- Vertical separator -->
  <line x1="290" y1="10" x2="290" y2="115" stroke="#cbd5e1" stroke-width="1.5"/>

  <!-- Closed Loop: Reinforcement Learning -->
  <text x="445" y="18" font-size="9.5" font-weight="700" fill="#047857" text-anchor="middle">Reinforcement Learning: Closed-Loop Recovery $\mathcal{O}(\epsilon T)$</text>
  <path d="M 320,50 Q 420,45 560,48" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="4,4"/>
  <text x="350" y="40" font-size="7.5" fill="#64748b">Desired Target Path</text>
  <!-- RL path with self-correction -->
  <path d="M 320,50 Q 360,65 400,68 Q 440,70 480,52 Q 520,45 560,48" fill="none" stroke="#10b981" stroke-width="2.5"/>
  <circle cx="400" cy="68" r="4" fill="#f59e0b"/>
  <text x="400" y="85" font-size="7.5" font-weight="700" fill="#d97706">Wobble detected</text>
  <text x="490" y="40" font-size="7.5" font-weight="700" fill="#047857">Active Recovery!</text>
</svg>
</div>

<h3>2.1 The Mathematics of Compounding Error: Ross &amp; Bagnell (2011)</h3>
<p>
  Ross &amp; Bagnell formally proved why open-loop imitation learning fails over long horizons $T$:
</p>
<div class="formula">
  $$\text{Open-Loop Imitation Error} \le \frac{1}{2} \epsilon T^2 = \mathcal{O}(\epsilon T^2) \quad \text{vs.} \quad \text{Closed-Loop RL Error} \le \epsilon T = \mathcal{O}(\epsilon T)$$
</div>

<!-- PARAMETER ANATOMY TABLE 1 -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Symbol</th>
      <th style="width: 20%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 15%;">Example Value</th>
      <th style="width: 15%;">Impact of Parameter</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\epsilon$</b></td>
      <td>Per-Step Error Rate</td>
      <td>The probability that the policy makes a small mistake on any given single timestep.</td>
      <td>$0.01$ (1% chance per step)</td>
      <td>Lower is better, but in the real world $\epsilon$ is never zero due to sensor noise.</td>
    </tr>
    <tr>
      <td><b>$T$</b></td>
      <td>Episode Time Horizon</td>
      <td>The total number of control steps from start to finish.</td>
      <td>$500$ steps ($10$ seconds at $50$ Hz)</td>
      <td>As $T$ grows, open-loop error explodes quadratically ($T^2$), while RL stays linear!</td>
    </tr>
    <tr>
      <td><b>$\mathcal{O}(\epsilon T^2)$</b></td>
      <td>Quadratic Compounding</td>
      <td>Once an error happens, all future steps are off-distribution, creating a snowball effect.</td>
      <td>For $T=100$: $\approx 50$ total mistakes!</td>
      <td>Guarantees failure in complex robotics tasks like peeling, slicing, or peg insertion.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{O}(\epsilon T)$</b></td>
      <td>Linear Bounded Error</td>
      <td>Because the policy learned closed-loop recovery, each error is corrected immediately.</td>
      <td>For $T=100$: $\approx 1$ mistake total!</td>
      <td>The fundamental reason RL succeeds where behavioral cloning fails.</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Equation</div>
  <p>
    <b>"If a robot does not know how to correct its own mistakes, a 1% error at step 10 will ruin the entire 500-step task ($T^2$). Reinforcement learning forces the robot to practice recovering from mistakes, keeping total errors strictly proportional to time ($T$)."</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: THE MDP FORMALISM -->
<h2>3. The Language of RL: The Markov Decision Process (MDP)</h2>
<p>
  To solve problems with math, we need a standardized language. Every reinforcement learning problem on Earth is modeled as a <b>Markov Decision Process (MDP)</b>, defined by a 6-tuple: $\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma, \rho_0 \rangle$.
</p>

<!-- PARAMETER ANATOMY TABLE 2: MDP TUPLE -->
<table>
  <thead>
    <tr>
      <th style="width: 12%;">Symbol</th>
      <th style="width: 18%;">Formal Name</th>
      <th style="width: 38%;">Plain English Meaning</th>
      <th style="width: 32%;">Real-World Robotics Example (Tomato Slicing)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\mathcal{S}$</b></td>
      <td>State Space ($s_t$)</td>
      <td>The complete snapshot of everything happening in the environment right now.</td>
      <td>33 numbers: Dual-arm joint angles, knife position, blade contact forces, acoustic burst.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{A}$</b></td>
      <td>Action Space ($a_t$)</td>
      <td>The choices available to the robot at this microsecond.</td>
      <td>6 numbers: Downward feed rate, sawing velocity, stiffness delta $\Delta K$, damping delta $\Delta D$.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{P}$</b></td>
      <td>Transition Dynamics $P(s_{t+1} \mid s_t, a_t)$</td>
      <td>The rules of physics. <i>"If the world is in state $s$ and you take action $a$, where will you end up next?"</i></td>
      <td>Isaac Sim PhysX 5 solver: Computes friction, fruit deformation, and blade penetration.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{R}$</b></td>
      <td>Reward Function $r(s_t, a_t)$</td>
      <td>The scorecard. A single number telling the robot how well it did on this exact step.</td>
      <td>$+5.0$ for cutting downward, $+2.0$ for sawing shear, $-4.0$ for crushing forces $>8$ N.</td>
    </tr>
    <tr>
      <td><b>$\gamma$</b></td>
      <td>Discount Factor ($\gamma \in [0, 1)$)</td>
      <td>The <b>Patience Meter</b>. How much does the robot care about future rewards versus immediate rewards?</td>
      <td>$\gamma = 0.99$: The robot values completing the cut at step 300 almost as much as step 1.</td>
    </tr>
    <tr>
      <td><b>$\rho_0$</b></td>
      <td>Initial State Distribution</td>
      <td>Where does the world start when an episode resets?</td>
      <td>Randomized tomato placement on cutting board $\pm 2$ cm, initial blade height $5$ cm.</td>
    </tr>
  </tbody>
</table>

<h3>3.1 The Markov Property: The "Goldfish Memory" Rule</h3>
<div class="callout intuition">
  <div class="callout-title">🐟 The Goldfish Memory Rule Explained</div>
  <p>
    A system has the <b>Markov Property</b> if:
  </p>
  <div class="formula">
    $$\mathbb{P}(s_{t+1} \mid s_t, a_t, s_{t-1}, a_{t-1}, \dots, s_0, a_0) = \mathbb{P}(s_{t+1} \mid s_t, a_t)$$
  </div>
  <p>
    <b>Plain English:</b> <i>"The future depends ONLY on where you are right now, NOT on how you got here."</i>
    <br><br>
    Imagine you are driving a car and you see a snapshot of the speedometer reading <b>60 mph</b>. 
    Can you predict where the car will be in 1 second? <b>Yes!</b> You don't need to know if the car started in Paris, New York, or Beijing 3 hours ago. The current speed and heading contain everything needed to predict the next second.
    <br><br>
    <b>Crucial Robotics Rule:</b> If your robot state only included knife position $z=4.0$ cm, you do <i>not</i> know if the blade is plunging downward at high speed or retracting upward! To satisfy the Markov property, your state <b>must include velocities and contact forces</b> ($\dot{q}, v, F_z$).
  </p>
</div>

<h3>3.2 Trajectory Probability Factorization</h3>
<p>
  A complete episode (trajectory) is a sequence of states and actions: $\tau = (s_0, a_0, s_1, a_1, \dots, s_T)$. Using the chain rule of probability and the Markov property:
</p>
<div class="formula">
  $$\mathbb{P}(\tau \mid \theta) = \rho_0(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t \mid s_t) P(s_{t+1} \mid s_t, a_t)$$
</div>

<!-- PARAMETER ANATOMY TABLE 3 -->
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Component</th>
      <th style="width: 35%;">Who Controls It?</th>
      <th style="width: 40%;">Plain English Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\rho_0(s_0)$</b></td>
      <td>Environment (Nature)</td>
      <td>Where the robot starts at timestep zero.</td>
    </tr>
    <tr>
      <td><b>$\pi_\theta(a_t \mid s_t)$</b></td>
      <td><b>The Robot Brain (YOU!)</b></td>
      <td>The probability that your neural network chooses action $a_t$ given sensor state $s_t$.</td>
    </tr>
    <tr>
      <td><b>$P(s_{t+1} \mid s_t, a_t)$</b></td>
      <td>Environment (Physics)</td>
      <td>How the physical world responds to your action. (Usually unknown and non-differentiable!).</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Equation</div>
  <p>
    <b>"The total probability of an entire 500-step robot experiment is simply the probability of where it started, multiplied by every decision the robot made, multiplied by how the laws of physics responded at each step."</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 4: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>4. Concrete Numerical Walkthrough: 3 Steps in a Robot Slicing Episode</h2>
<p>
  Let's see actual numbers! Suppose our robot is cutting a tomato with discount factor <b>$\gamma = 0.99$</b>.
</p>

<!-- STEP-BY-STEP TABLE -->
<table>
  <thead>
    <tr>
      <th style="width: 8%;">Step ($t$)</th>
      <th style="width: 28%;">Current State $s_t$</th>
      <th style="width: 24%;">Action Chosen $a_t$</th>
      <th style="width: 25%;">Physics Outcome &amp; Sensor Feedback</th>
      <th style="width: 15%;">Reward $r_t$</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$t=0$</b></td>
      <td>$z = 5.0$ cm (Above fruit)<br>$v_z = 0.0$ m/s, $F_z = 0.0$ N</td>
      <td>Feed rate: $+2.0$ mm/s<br>Stiffness: $1000$ N/m</td>
      <td>Knife moves downward in free air. No contact yet.</td>
      <td><b>$r_0 = +0.2$</b><br><small>(Approach reward)</small></td>
    </tr>
    <tr>
      <td><b>$t=1$</b></td>
      <td>$z = 4.8$ cm (Skin contact)<br>$v_z = -2.0$ mm/s, $F_z = 3.5$ N</td>
      <td>Feed: $+1.5$ mm/s<br>Sawing: $+25.0$ mm/s</td>
      <td>Lateral sawing initiates! Skin shear stress concentrates at blade edge.</td>
      <td><b>$r_1 = +2.5$</b><br><small>(Sawing progress bonus)</small></td>
    </tr>
    <tr>
      <td><b>$t=2$</b></td>
      <td>$z = 4.6$ cm (Tough skin resistance)<br>$v_z = -1.0$ mm/s, $F_z = 9.8$ N</td>
      <td>Feed: $+3.0$ mm/s (Too aggressive!)<br>Stiffness: $1200$ N/m</td>
      <td><b>Excess force penalty!</b> $F_z = 9.8$ N exceeds $8.0$ N threshold. Tomato pulp squishes slightly.</td>
      <td><b>$r_2 = -1.8$</b><br><small>(Pulp crush penalty)</small></td>
    </tr>
  </tbody>
</table>

<h3>4.1 Calculating the Total Discounted Return ($G_0$)</h3>
<p>
  How good was this 3-step sequence for the robot? We compute the <b>Discounted Return $G_0$</b> starting from step 0:
</p>
<div class="formula">
  $$G_0 = r_0 + \gamma \cdot r_1 + \gamma^2 \cdot r_2 = 0.2 + (0.99 \times 2.5) + (0.99^2 \times -1.8)$$
</div>
<div class="formula">
  $$G_0 = 0.2 + 2.475 - 1.764 = \mathbf{+0.911}$$
</div>
<p>
  <b>Why $\gamma = 0.99$?</b> Notice that $\gamma^2 = 0.9801$. The penalty at step 2 was multiplied by $0.9801$, so the robot cares almost as much about step 2 as step 0. If $\gamma = 0.1$, the penalty would be multiplied by $0.01 = -0.018$, making the robot myopic and careless about future crushing!
</p>

<!-- SECTION 5: THE COMPLETE RL FAMILY TREE -->
<h2>5. The Landscape of Modern RL: Where Does Everything Fit?</h2>
<p>
  When reading papers, you will hear terms like <i>Model-Free, Actor-Critic, Q-Learning, PPO, SAC</i>. Here is how they all connect:
</p>

<!-- DIAGRAM 3: RL TAXONOMY TREE -->
<div class="diagram-container">
<svg width="600" height="150" viewBox="0 0 600 150">
  <!-- Root -->
  <rect x="230" y="5" width="140" height="28" rx="5" fill="#1e293b" stroke="#0f172a" stroke-width="1.5"/>
  <text x="300" y="23" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle">REINFORCEMENT LEARNING</text>

  <!-- Level 1: Model-Free vs Model-Based -->
  <line x1="300" y1="33" x2="160" y2="52" stroke="#64748b" stroke-width="1.5"/>
  <line x1="300" y1="33" x2="440" y2="52" stroke="#64748b" stroke-width="1.5"/>

  <rect x="80" y="52" width="160" height="26" rx="4" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="160" y="69" font-size="9" font-weight="700" fill="#1d4ed8" text-anchor="middle">MODEL-FREE RL (Our Focus!)</text>

  <rect x="360" y="52" width="160" height="26" rx="4" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="440" y="69" font-size="9" font-weight="700" fill="#475569" text-anchor="middle">MODEL-BASED RL</text>

  <!-- Level 2: Three Branches of Model-Free -->
  <line x1="160" y1="78" x2="60" y2="100" stroke="#3b82f6" stroke-width="1.5"/>
  <line x1="160" y1="78" x2="160" y2="100" stroke="#3b82f6" stroke-width="1.5"/>
  <line x1="160" y1="78" x2="260" y2="100" stroke="#3b82f6" stroke-width="1.5"/>

  <!-- Policy-Based -->
  <rect x="10" y="100" width="100" height="42" rx="4" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>
  <text x="60" y="116" font-size="8" font-weight="700" fill="#b45309" text-anchor="middle">Policy-Based</text>
  <text x="60" y="128" font-size="7" fill="#78350f" text-anchor="middle">Lecture 5</text>
  <text x="60" y="138" font-size="6.5" fill="#92400e" text-anchor="middle">(REINFORCE)</text>

  <!-- Value-Based -->
  <rect x="115" y="100" width="90" height="42" rx="4" fill="#ecfdf5" stroke="#059669" stroke-width="1.2"/>
  <text x="160" y="116" font-size="8" font-weight="700" fill="#047857" text-anchor="middle">Value-Based</text>
  <text x="160" y="128" font-size="7" fill="#065f46" text-anchor="middle">Lectures 4 &amp; 8</text>
  <text x="160" y="138" font-size="6.5" fill="#064e3b" text-anchor="middle">(Q-Learning, DQN)</text>

  <!-- Actor-Critic -->
  <rect x="210" y="100" width="110" height="42" rx="4" fill="#fce7f3" stroke="#db2777" stroke-width="1.5"/>
  <text x="265" y="116" font-size="8" font-weight="700" fill="#be185d" text-anchor="middle">Actor-Critic (Hybrid)</text>
  <text x="265" y="128" font-size="7" fill="#9d174d" text-anchor="middle">Lectures 6 &amp; 10</text>
  <text x="265" y="138" font-size="6.5" font-weight="700" fill="#831843" text-anchor="middle">(PPO &amp; SAC!)</text>
</svg>
</div>

<div class="page-break"></div>

<!-- SECTION 6: PYTORCH IMPLEMENTATION -->
<h2>6. The Vectorized Simulation Loop in PyTorch (Isaac Lab Style)</h2>
<p>
  How does this look in real Python code? In modern robotics (NVIDIA Isaac Lab), we run <b>1,024 parallel environments simultaneously on one GPU</b>:
</p>

<div class="callout code-box">
  <div class="callout-title">🐍 Vectorized Gym / Isaac Lab Stepping Loop</div>
<pre style="margin: 0; padding: 0;">
import torch

# 1. Initialize 1,024 parallel robot environments on GPU
num_envs = 1024
states = env.reset()  # Shape: (1024, 33) -> 1,024 robots observing 33 sensor channels

total_rewards = torch.zeros(num_envs, device="cuda")

for step in range(500):  # 500-step episode (10 seconds)
    # 2. Policy forward pass: Robot Brain chooses 6-DoF continuous motor actions
    with torch.no_grad():
        actions = policy_network(states)  # Shape: (1024, 6)

    # 3. Step physics simulation forward by 20 milliseconds (50 Hz)
    next_states, rewards, dones, infos = env.step(actions)
    # next_states: (1024, 33), rewards: (1024,), dones: (1024,) bool

    # 4. Accumulate rewards across all parallel environments
    total_rewards += rewards

    # 5. Reset environments that finished (knife hit board or tomato crushed)
    states = next_states

print(f"Average Return across 1024 robots: {total_rewards.mean().item():.2f}")
</pre>
</div>

<!-- SECTION 7: PRACTITIONER'S CHECKLIST -->
<h2>7. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<p>
  When training your first RL agent in Isaac Lab, 90% of failures stem from these three classic beginner traps:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Failure Mode</th>
      <th style="width: 35%;">Why It Happens</th>
      <th style="width: 40%;">How to Fix It Immediately</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Observation Scale Explosion</b></td>
      <td>Joint angles are in radians $[-3, +3]$, but contact forces are in Newtons $[0, 50]$ N. The neural network ignores joint angles and fixates on the large force numbers.</td>
      <td><b>Standardize observations:</b> Use a running mean and variance wrapper (e.g., <code>RunningMeanStd</code>) so every state dimension has mean $0$ and variance $1$.</td>
    </tr>
    <tr>
      <td><b>2. The Discount Factor Horizon Trap</b></td>
      <td>Setting $\gamma = 0.9$ means the effective planning horizon is only $H = \frac{1}{1 - \gamma} = \frac{1}{0.1} = 10$ steps. The robot cannot plan a 300-step cut!</td>
      <td>Set <b>$\gamma = 0.99$</b> for slicing tasks ($H = 100$ steps), or $\gamma = 0.995$ for long manipulation trajectories.</td>
    </tr>
    <tr>
      <td><b>3. Partial Observability (POMDP) Trap</b></td>
      <td>Passing only blade position $z$ without velocity $\dot{z}$ violates the Markov property. The agent cannot distinguish moving down from retracting up.</td>
      <td>Always include <b>first-order velocities</b> ($\dot{q}, v_{\text{knife}}$) and <b>historical observation buffers</b> (e.g., stacking last 3 frames).</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>CS285 Lecture 1 Zero-to-Hero Guide • DEX-ROB Lab (Tianjin University) • Prof. Shan An</i>
</div>

</body>
</html>
"""

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Lecture1_Beginner_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture1_Beginner_Guide.pdf"

render_utils.build_pdf(html_content, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
