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
  <span class="course-tag">CS285 Lecture 1 • Zero-to-Hero Field Manual</span>
  <h1>Foundations of Reinforcement Learning &amp; The Closed Loop</h1>
  <div class="subtitle">A Comprehensive, Intuitive Textbook: Physical Actuation, State Representation, Markov Formulations, and Multi-Domain Case Studies</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Target Audience:</b> Complete Beginners to Advanced Robotics Practitioners</span>
  </div>
</div>

<!-- SECTION 1: THE CORE PHILOSOPHY -->
<h2>1. What is Reinforcement Learning? (The Bicycle Analogy)</h2>
<p>
  Imagine you want to teach a child how to ride a bicycle. How does the human brain actually learn?
</p>
<ul>
  <li><b>The Supervised Learning Fallacy:</b> You sit the child down in front of a whiteboard and show them 50,000 flashcards. 
    Flashcard #1: <i>"If your bike tilts 2.1° left, apply 14.5 Newtons of torque to the right handlebar."</i> 
    The child memorizes all 50,000 cards. But when they get on the bike, a gust of wind tilts them 2.3° left. 
    Because 2.3° was never on any flashcard, the child panics, freezes, and crashes.
  </li>
  <li><b>The Reinforcement Learning Way:</b> You put a helmet on the child and give them a gentle push. 
    The child pedals. When they balance and coast forward smoothly, their brain experiences a surge of dopamine (<b>Positive Reward</b>). 
    When they lean too far, lose balance, and scrape their knee on the pavement, it hurts (<b>Negative Reward / Penalty</b>). 
    Nobody explained the laws of angular momentum or gyroscopic precession to the child. 
    Through <b>interaction, consequence, and trial-and-error</b>, the child's nervous system automatically wires a feedback control loop.
  </li>
</ul>

<div class="callout intuition">
  <div class="callout-title">💡 Core Takeaway: Consequences vs Answers</div>
  <p>
    <b>Supervised learning teaches an AI what an expert would do. Reinforcement learning teaches an AI what happens when it acts.</b>
    In robotics, we don't know the "correct" millivolt command for every motor in every microsecond. We only know what goal we want to achieve (e.g., slice a tomato cleanly without squishing the pulp). RL allows the machine to discover the control law itself.
  </p>
</div>

<!-- DIAGRAM 1: THE CLOSED LOOP -->
<div class="diagram-container">
<svg width="600" height="110" viewBox="0 0 600 110">
  <rect x="30" y="20" width="200" height="70" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="130" y="45" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">AGENT (Robot Brain)</text>
  <text x="130" y="62" font-size="8.5" fill="#475569" text-anchor="middle">Neural Policy Network $\pi_\theta(a|s)$</text>
  <text x="130" y="76" font-size="7.5" fill="#64748b" text-anchor="middle">Runs on RTX GPU via PyTorch</text>

  <path d="M 230,40 L 360,40" fill="none" stroke="#2563eb" stroke-width="2.5"/>
  <polygon points="360,40 350,34 350,46" fill="#2563eb"/>
  <text x="295" y="32" font-size="9" font-weight="700" fill="#1d4ed8" text-anchor="middle">Action $a_t$</text>
  <text x="295" y="52" font-size="7.5" fill="#64748b" text-anchor="middle">(Torques, Feed Rates, Stiffness)</text>

  <rect x="370" y="20" width="200" height="70" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="470" y="45" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">ENVIRONMENT (Physical World)</text>
  <text x="470" y="62" font-size="8.5" fill="#475569" text-anchor="middle">Physics, Objects, Deformable Tissue</text>
  <text x="470" y="76" font-size="7.5" fill="#64748b" text-anchor="middle">NVIDIA Isaac Sim / Real World</text>

  <path d="M 370,80 L 230,80" fill="none" stroke="#10b981" stroke-width="2.5"/>
  <polygon points="230,80 240,74 240,86" fill="#10b981"/>
  <text x="300" y="73" font-size="9" font-weight="700" fill="#047857" text-anchor="middle">State $s_{t+1}$ &amp; Reward $r_t$</text>
  <text x="300" y="94" font-size="7.5" fill="#64748b" text-anchor="middle">(F/T Sensor, Kinematics, Score)</text>
</svg>
</div>

<div class="page-break"></div>

<!-- SECTION 2: HARDWARE-TO-RL PRIMER -->
<h2>2. Hardware-to-RL Primer: How Physical Robots Connect to Math</h2>
<p>
  Before writing equations, an engineer must understand how physical hardware actually interfaces with neural network tensors. 
  A robot does not "think" in abstract states—it has physical copper wire coils, optical encoder discs, and strain gauges.
</p>

<h3>2.1 The Actuation Hierarchy: From Voltage to Compliance</h3>
<p>
  When your neural network outputs an action $a_t \in [-1, 1]^6$, how does that number become physical movement? 
  Robots operate across a multi-layer control hierarchy:
</p>
<ul>
  <li><b>Level 0 (Pulse Width Modulation - PWM):</b> At the lowest level, transistors rapidly switch $24\text{V}$ or $48\text{V}$ DC power to the brushless motor windings at $20\text{ kHz}$.</li>
  <li><b>Level 1 (Field-Oriented Current Control):</b> Motor current is directly proportional to output motor torque: $\tau = K_t \cdot I$. Current loops run on dedicated embedded microcontrollers at $10\text{ kHz}$.</li>
  <li><b>Level 2 (Joint Impedance Control):</b> In delicate soft object manipulation (like tomato cutting), commanding raw torques causes violent instability, while commanding pure positions crushes the fruit. Instead, we use <b>Impedance Control</b>:
    <div class="formula">$$\tau = K_{\text{stiff}} \cdot (q_{\text{desired}} - q_{\text{actual}}) + D_{\text{damp}} \cdot (\dot{q}_{\text{desired}} - \dot{q}_{\text{actual}})$$</div>
    Here, the robot acts like a virtual spring-damper. If the blade hits a tough tomato skin, it pushes firmly; if the skin suddenly ruptures, the compliance prevents the knife from slamming into the table!
  </li>
  <li><b>Level 3 (The RL Policy Layer):</b> Your RL network runs at $50\text{ Hz}$ or $100\text{ Hz}$. It does not output raw voltages; it dynamically modulates the <b>desired feed velocity $\Delta v$</b> and <b>stiffness adjustments $\Delta K$</b>!</li>
</ul>

<!-- DIAGRAM: ACTUATION STACK -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <rect x="20" y="25" width="120" height="45" rx="5" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="44" font-size="8.5" font-weight="700" fill="#1e40af" text-anchor="middle">RL Policy (SkRL)</text>
  <text x="80" y="58" font-size="7.5" fill="#475569" text-anchor="middle">50 Hz • Action $a_t$</text>

  <path d="M 140,47 L 175,47" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="175,47 167,42 167,52" fill="#2563eb"/>

  <rect x="175" y="25" width="125" height="45" rx="5" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="237" y="44" font-size="8.5" font-weight="700" fill="#065f46" text-anchor="middle">Impedance Controller</text>
  <text x="237" y="58" font-size="7.5" fill="#475569" text-anchor="middle">1 kHz • $K \Delta x + D \Delta v$</text>

  <path d="M 300,47 L 335,47" fill="none" stroke="#10b981" stroke-width="2"/>
  <polygon points="335,47 327,42 327,52" fill="#10b981"/>

  <rect x="335" y="25" width="115" height="45" rx="5" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="392" y="44" font-size="8.5" font-weight="700" fill="#92400e" text-anchor="middle">Current / Torque Loop</text>
  <text x="392" y="58" font-size="7.5" fill="#475569" text-anchor="middle">10 kHz • $\tau = K_t I$</text>

  <path d="M 450,47 L 485,47" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <polygon points="485,47 477,42 477,52" fill="#f59e0b"/>

  <rect x="485" y="25" width="95" height="45" rx="5" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="532" y="44" font-size="8.5" font-weight="700" fill="#0f172a" text-anchor="middle">Motor Coils</text>
  <text x="532" y="58" font-size="7.5" fill="#64748b" text-anchor="middle">Physical Motion</text>
</svg>
</div>

<h3>2.2 Sensor Normalization: Why Raw Numbers Destroy Neural Networks</h3>
<p>
  In your robot, joint angles are measured in radians (typically $[-3.14, +3.14]$). 
  Meanwhile, contact forces are measured in Newtons (e.g. $[0, 45]$ N), and acoustic bursts are raw sensor counts (e.g. $[0, 32768]$).
</p>
<div class="callout warning-box">
  <div class="callout-title">⚠️ The Magnitude Trap</div>
  <p>
    If you pass raw unnormalized numbers into an MLP, the gradient with respect to the acoustic burst ($32,000$) will be <b>10,000 times larger</b> than the gradient for joint angles ($0.12$). 
    The network will completely ignore joint angles and become unstable. 
    <b>Every observation channel must be standardized</b>: subtract running mean $\mu_{\text{obs}}$ and divide by standard deviation $\sigma_{\text{obs}}$ so all inputs enter the network with mean $0$ and variance $1$.
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: THE IMITATION TRAP -->
<h2>3. The Imitation Trap &amp; Compounding Error (Covariate Shift)</h2>
<p>
  Why can't we simply collect human teleoperation demonstrations and train an imitation model? 
  This approach—<b>Behavioral Cloning</b>—fails because of an inevitable mathematical phenomenon: <b>Covariate Shift</b>.
</p>

<div class="callout warning-box">
  <div class="callout-title">🏎️ The Racecar Passenger Analogy</div>
  <p>
    Imagine you ride passenger with an elite racecar driver for 500 hours. The driver stays glued to the ideal racing line. 
    You record every steering angle. 
    Then, you sit in the driver's seat. On lap 1, you sneeze, and the car drifts <b>just 5 centimeters onto the wet gravel shoulder</b>.
    <br><br>
    What happens? <b>You crash immediately!</b> 
    Why? Because in 500 hours of watching the expert, <i>the expert never once drove onto the gravel shoulder</i>! 
    You have zero training data for gravel recovery. 
    You turn the wheel the wrong way, slide further, panic, and roll the car.
  </p>
</div>

<h3>3.1 Ross &amp; Bagnell Compounding Error Proof in Plain English</h3>
<p>
  In 2011, Stephane Ross and J. Andrew Bagnell published the seminal theorem proving why open-loop behavioral cloning fails over long horizons $T$:
</p>
<div class="formula">
  $$\text{Open-Loop Imitation Error} \le \frac{1}{2} \epsilon T^2 = \mathcal{O}(\epsilon T^2) \quad \text{vs.} \quad \text{Closed-Loop RL Error} \le \epsilon T = \mathcal{O}(\epsilon T)$$
</div>

<!-- PARAMETER ANATOMY TABLE 1 -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Parameter</th>
      <th style="width: 20%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 15%;">Example Value</th>
      <th style="width: 15%;">Physical Effect</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\epsilon$</b></td>
      <td>Per-Step Error Rate</td>
      <td>Probability that the policy makes a small mistake on any given single timestep.</td>
      <td>$0.01$ (1% error chance)</td>
      <td>Even an elite 99% accurate model has $\epsilon = 0.01$.</td>
    </tr>
    <tr>
      <td><b>$T$</b></td>
      <td>Episode Time Horizon</td>
      <td>Total number of control timesteps in the task.</td>
      <td>$500$ steps ($10$ seconds)</td>
      <td>As $T$ grows, $T^2$ explodes exponentially!</td>
    </tr>
    <tr>
      <td><b>$\mathcal{O}(\epsilon T^2)$</b></td>
      <td>Quadratic Compounding</td>
      <td>Once an error happens, all future steps are off-distribution, creating a snowball effect.</td>
      <td>For $T=100$: $\approx 50$ total mistakes!</td>
      <td>Guarantees catastrophic failure in continuous robotics.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{O}(\epsilon T)$</b></td>
      <td>Linear Error Bound</td>
      <td>Because RL practices recovery during training, mistakes do not compound.</td>
      <td>For $T=100$: $\approx 1$ mistake total!</td>
      <td>The fundamental mathematical reason RL is mandatory.</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Equation</div>
  <p>
    <b>"If an agent only mimics an expert without learning self-correction, a 1% error early on cascades into 50 mistakes by the end of the episode ($\mathcal{O}(\epsilon T^2)$). Reinforcement learning forces the robot to explore its own mistakes and learn recovery policies, keeping errors strictly proportional to time ($\mathcal{O}(\epsilon T)$)."</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 4: FOUR REAL-WORLD CASE STUDIES -->
<h2>4. Four Real-World Case Studies: How RL Formulates Diverse Problems</h2>
<p>
  To become a true RL expert, you must realize that <b>every sequential decision problem on Earth uses the exact same MDP framework</b>. 
  Below are four completely different engineering domains mapped side-by-side:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 16%;">Domain</th>
      <th style="width: 28%;">State Space ($s_t$)</th>
      <th style="width: 24%;">Action Space ($a_t$)</th>
      <th style="width: 32%;">Reward Function ($r_t$)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Soft Fruit Slicing (Our Lab's Research)</b></td>
      <td><b>$\mathbb{R}^{33}$ Vector:</b> Dual-arm joint angles/velocities (14), knife pose/velocity (9), tomato pose (7), TacBlade F/T (6), acoustic burst (1).</td>
      <td><b>$\mathbb{R}^6$ Continuous:</b> Downward feed rate $\Delta v_z$, lateral sawing speed $v_{\text{slice}}$, stiffness delta $\Delta K$, damping $\Delta D$, grip force.</td>
      <td>$+5.0 \times \text{Penetration} + 2.0 \times \text{Sawing} - 4.0 \times (\text{Force} - 8\text{N})^2 - 0.05 \times \text{Jitter} + 100 \times \text{Success}$.</td>
    </tr>
    <tr>
      <td><b>2. Autonomous Vehicle (Tesla / Waymo)</b></td>
      <td><b>Multimodal:</b> LiDAR point cloud, surround cameras, ego velocity $v$, acceleration $a$, distance to lane boundaries, lead vehicle speed.</td>
      <td><b>$\mathbb{R}^2$ Continuous:</b> Steering wheel angle $\delta \in [-30^\circ, +30^\circ]$, throttle/brake pedal pressure $\in [-1.0, +1.0]$.</td>
      <td>$+1.0 \times \text{Speed} - 10.0 \times \text{LaneDeparture} - 5.0 \times \text{Jerk} - 1000 \times \text{Collision}$.</td>
    </tr>
    <tr>
      <td><b>3. ChatGPT Alignment (RLHF / PPO)</b></td>
      <td><b>Discrete Tokens:</b> Conversation prompt history + tokens generated so far: $(w_1, w_2, \dots, w_k)$ embedded in $\mathbb{R}^{4096}$.</td>
      <td><b>Vocabulary Categorical:</b> Selection of next word token from a vocabulary of $50,000$ discrete token IDs.</td>
      <td>$\text{RewardModelScore}(x, y) - \beta \cdot D_{\text{KL}}(\pi_\theta \,\|\, \pi_{\text{ref}})$ (Helpfulness score minus drift from base model).</td>
    </tr>
    <tr>
      <td><b>4. Quadruped Locomotion (Boston Dynamics / Unitree)</b></td>
      <td><b>$\mathbb{R}^{48}$ Vector:</b> 12 joint positions &amp; velocities (24), base orientation quaternion &amp; gyro (7), commanded velocity (3), foot contacts (4).</td>
      <td><b>$\mathbb{R}^{12}$ Continuous:</b> Target joint motor position offsets commanded to PD motor controllers.</td>
      <td>$+2.0 \times \text{ForwardVelocity} - 1.0 \times \text{LateralDrift} - 0.5 \times \text{TorqueSquared} - 100 \times \text{Fall}$.</td>
    </tr>
  </tbody>
</table>

<div class="callout intuition">
  <div class="callout-title">💡 The Grand Synthesis</div>
  <p>
    Look closely at that table. Whether an AI is driving a 2-ton car at 70 mph, writing an essay in ChatGPT, making a four-legged robot run across rocky terrain, or delicately slicing a ripe tomato with a dual-arm robot: 
    <b>The underlying mathematical algorithm (PPO or SAC) is 100% IDENTICAL!</b> 
    Only the definitions of State, Action, and Reward change.
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 5: THE FORMAL MDP -->
<h2>5. The Markov Decision Process (MDP) Anatomy Dictionary</h2>
<p>
  Every reinforcement learning problem is formally specified as an MDP: $\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma, \rho_0 \rangle$.
</p>

<!-- PARAMETER ANATOMY TABLE 2 -->
<table>
  <thead>
    <tr>
      <th style="width: 12%;">Symbol</th>
      <th style="width: 18%;">Formal Name</th>
      <th style="width: 38%;">Plain English Meaning</th>
      <th style="width: 18%;">Example Value</th>
      <th style="width: 14%;">Tuning / Impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\mathcal{S}$</b></td>
      <td>State Space</td>
      <td>The complete physical snapshot of everything happening right now.</td>
      <td>$\mathbb{R}^{33}$ (Joints, Knife, Forces)</td>
      <td>Must include velocities!</td>
    </tr>
    <tr>
      <td><b>$\mathcal{A}$</b></td>
      <td>Action Space</td>
      <td>The motor controls available to the robot at this microsecond.</td>
      <td>$\mathbb{R}^6$ continuous actions</td>
      <td>Continuous for robots.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{P}$</b></td>
      <td>Transition Dynamics</td>
      <td>The rules of physics: where you land next after taking action $a$.</td>
      <td>$P(s_{t+1} \mid s_t, a_t)$</td>
      <td>Unknown in real world.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{R}$</b></td>
      <td>Reward Function</td>
      <td>The scoreboard: points awarded for progress, penalties for crushing.</td>
      <td>$r(s_t, a_t) \in [-10, +10]$</td>
      <td>Dense shaping needed.</td>
    </tr>
    <tr>
      <td><b>$\gamma$</b></td>
      <td>Discount Factor</td>
      <td><b>The Patience Meter:</b> how much future points matter relative to today.</td>
      <td>$\gamma = 0.99$</td>
      <td>High for long tasks.</td>
    </tr>
    <tr>
      <td><b>$\rho_0$</b></td>
      <td>Initial Distribution</td>
      <td>Where the world starts when an episode begins or resets.</td>
      <td>Tomato position $\pm 2$ cm</td>
      <td>Domain randomization.</td>
    </tr>
  </tbody>
</table>

<h3>5.1 The Markov Property: The "Goldfish Memory" Rule</h3>
<div class="callout intuition">
  <div class="callout-title">🐟 The Goldfish Memory Rule Explained</div>
  <p>
    A system has the <b>Markov Property</b> if:
  </p>
  <div class="formula">
    $$\mathbb{P}(s_{t+1} \mid s_t, a_t, s_{t-1}, a_{t-1}, \dots, s_0, a_0) = \mathbb{P}(s_{t+1} \mid s_t, a_t)$$
  </div>
  <p>
    <b>Plain English:</b> <i>"The future depends ONLY on where you are right now, NOT on the historical journey that brought you here."</i>
    <br><br>
    Imagine you look at a photograph of a baseball suspended in mid-air at coordinates $(x=10, y=5, z=2)$. 
    Can you predict where the ball will be in 0.1 seconds? 
    <b>No!</b> The ball could be flying forward at $95\text{ mph}$, dropping straight down, or rising from a bounce. 
    A photograph of position alone is <b>Non-Markovian</b>!
    <br><br>
    However, if your state includes position AND velocity vector $(\dot{x}, \dot{y}, \dot{z})$, you can calculate the exact parabola. 
    <b>In robotics, state vectors MUST contain first-order velocities ($\dot{q}, v$) and contact force rates ($\dot{F}$) to satisfy the Markov property!</b>
  </p>
</div>

<h3>5.2 Trajectory Probability Factorization</h3>
<div class="formula">
  $$\mathbb{P}(\tau \mid \theta) = \rho_0(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t \mid s_t) P(s_{t+1} \mid s_t, a_t)$$
</div>
<p>
  <b>Plain English Translation:</b> <i>"The probability of an entire 500-step robot experiment is simply the initial placement of the tomato, multiplied by every decision the robot chose, multiplied by how physics reacted at each step."</i>
</p>

<div class="page-break"></div>

<!-- SECTION 6: POMDP -->
<h2>6. Partially Observable MDPs (POMDPs): Driving with Fogged Glass</h2>
<p>
  In textbook theory, we assume the agent sees the true state $s_t$. 
  In real-world robotics, this is almost never true. Real robots operate in a <b>Partially Observable Markov Decision Process (POMDP)</b>.
</p>

<div class="callout warning-box">
  <div class="callout-title">🌫️ The Foggy Windshield Analogy</div>
  <p>
    Imagine driving a car in a blizzard where your windshield is 90% fogged over. 
    You cannot see the true physical state of the road. 
    You only receive <b>noisy observations $o_t$</b>: the blurred headlights of a car ahead and the vibration of the tires on ice.
    <br><br>
    In soft tomato slicing:
    <br>• <b>True State $s_t$ (Unobservable):</b> The exact internal viscoelastic stress tensor inside the tomato flesh, the micro-crack propagation in the skin cuticle, and the pulp turgor pressure.
    <br>• <b>Observation $o_t$ (What we actually measure):</b> A 6-axis F/T load cell reading at the blade root, an acoustic piezoelectric voltage, and an RGB-D camera view.
  </p>
</div>

<h3>6.1 The POMDP 8-Tuple: $\mathcal{M}_{\text{POMDP}} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \Omega, \mathcal{O}, \gamma, \rho_0 \rangle$</h3>
<table>
  <thead>
    <tr>
      <th style="width: 15%;">New Symbol</th>
      <th style="width: 25%;">Formal Name</th>
      <th style="width: 60%;">Physical Meaning in Robotics</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\Omega$</b></td>
      <td>Observation Space</td>
      <td>The space of sensory readings the robot can actually record through physical sensors.</td>
    </tr>
    <tr>
      <td><b>$\mathcal{O}(o_t \mid s_t)$</b></td>
      <td>Emission Probability</td>
      <td>Sensor noise model: <i>"Given the true physical state $s_t$, what noisy voltage reading $o_t$ will the sensor output?"</i></td>
    </tr>
  </tbody>
</table>

<h3>6.2 How Modern Robotics Solves Partial Observability</h3>
<p>
  How do we control a robot when we cannot see the true state? We use two standard engineering solutions:
</p>
<ol>
  <li><b>Frame Stacking / History Buffers:</b> Instead of feeding only the current sensor reading $o_t$, stack the last $K=3$ readings: $[o_t, o_{t-1}, o_{t-2}]$. This implicitly encodes velocity and acceleration!</li>
  <li><b>Recurrent Neural Networks (LSTM / GRU / Transformer):</b> The network maintains an internal hidden memory vector $h_t$ that acts as a <b>belief state</b>, remembering contact history across time.</li>
</ol>

<div class="page-break"></div>

<!-- SECTION 7: CONCRETE 5-STEP WALKTHROUGH -->
<h2>7. Concrete Numerical Walkthrough: 5 Timesteps in Robot Slicing</h2>
<p>
  Let's observe an actual robot executing 5 continuous steps with discount factor <b>$\gamma = 0.99$</b>:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 8%;">Step</th>
      <th style="width: 28%;">Sensor State $s_t$</th>
      <th style="width: 24%;">Action Executed $a_t$</th>
      <th style="width: 25%;">Physics Response</th>
      <th style="width: 15%;">Reward $r_t$</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$t=0$</b></td>
      <td>$z = 5.0$ cm, $v_z = 0.0$ mm/s<br>$F_z = 0.0$ N, $E_{\text{burst}} = 0.0$</td>
      <td>Feed: $+2.5$ mm/s<br>Sawing: $0.0$ mm/s</td>
      <td>Knife plunges through air. Zero resistance.</td>
      <td><b>$r_0 = +0.2$</b><br><small>(Approach bonus)</small></td>
    </tr>
    <tr>
      <td><b>$t=1$</b></td>
      <td>$z = 4.75$ cm, $v_z = -2.5$ mm/s<br>$F_z = 3.2$ N (Skin contact!)</td>
      <td>Feed: $+1.0$ mm/s<br>Sawing: $+20.0$ mm/s</td>
      <td>Blade engages tomato cuticle. Lateral shear begins.</td>
      <td><b>$r_1 = +2.4$</b><br><small>(Sawing progress)</small></td>
    </tr>
    <tr>
      <td><b>$t=2$</b></td>
      <td>$z = 4.65$ cm, $v_z = -1.0$ mm/s<br>$F_z = 6.8$ N, $E_{\text{burst}} = 0.1$</td>
      <td>Feed: $+1.5$ mm/s<br>Sawing: $+25.0$ mm/s</td>
      <td>High friction resistance. Skin stretches elastically.</td>
      <td><b>$r_2 = +2.8$</b><br><small>(Shear progress)</small></td>
    </tr>
    <tr>
      <td><b>$t=3$</b></td>
      <td>$z = 4.50$ cm, $v_z = -1.5$ mm/s<br>$F_z = 7.9$ N, $E_{\text{burst}} = \mathbf{0.95}$</td>
      <td>Feed: $+0.5$ mm/s (Softened!)<br>Sawing: $+30.0$ mm/s</td>
      <td><b>SKIN PUNCTURE BURST!</b> Acoustic sensor spikes. Knife penetrates cuticle without crushing!</td>
      <td><b>$r_3 = +15.0$</b><br><small>(Puncture triumph!)</small></td>
    </tr>
    <tr>
      <td><b>$t=4$</b></td>
      <td>$z = 4.20$ cm, $v_z = -3.0$ mm/s<br>$F_z = 2.1$ N (Pulp drop)</td>
      <td>Feed: $+3.0$ mm/s<br>Sawing: $+15.0$ mm/s</td>
      <td>Knife slices easily through soft locular pulp gel. Resistance drops 70%.</td>
      <td><b>$r_4 = +4.5$</b><br><small>(Pulp slicing)</small></td>
    </tr>
  </tbody>
</table>

<h3>7.1 Calculating Total Discounted Return $G_0$</h3>
<div class="formula">
  $$G_0 = \sum_{t=0}^4 \gamma^t r_t = 0.2 + (0.99 \times 2.4) + (0.99^2 \times 2.8) + (0.99^3 \times 15.0) + (0.99^4 \times 4.5)$$
</div>
<div class="formula">
  $$G_0 = 0.20 + 2.376 + 2.744 + 14.555 + 4.323 = \mathbf{+24.198}$$
</div>
<p>
  <b>Why this number matters:</b> Notice how the $+15.0$ puncture reward at step 3 contributed $+14.555$ to step 0. 
  Because $\gamma = 0.99$, the robot at step 0 knows that moving down into contact is extraordinarily valuable because it unlocks the puncture bonus at step 3!
</p>

<div class="page-break"></div>

<!-- SECTION 8: DIARY OF A TRAINING RUN -->
<h2>8. "Diary of a Training Run": What Actually Happens Inside the Computer</h2>
<p>
  When you launch <code>python train.py</code> in NVIDIA Isaac Lab, what does the agent experience over 1,000,000 steps? 
  Here is the chronological biography of a neural network learning to slice tomatoes:
</p>

<!-- TRAINING LOG TABLE -->
<table>
  <thead>
    <tr>
      <th style="width: 18%;">Training Phase</th>
      <th style="width: 27%;">Policy Behavior (The Robot)</th>
      <th style="width: 27%;">Critic Behavior (The Evaluator)</th>
      <th style="width: 28%;">Diagnostic Curve Sign</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Phase 1: Pure Chaos<br>(Steps 0 – 5,000)</b></td>
      <td>Weights are randomly initialized. The robot flails violently, slams the blade into the board, or shoots up into the air. 100% of tomatoes are crushed.</td>
      <td>Critic outputs random numbers near $0.0$. Has no idea what anything is worth. $V(s) \approx 0 \pm 0.5$.</td>
      <td><b>Entropy is high</b> ($\approx 2.5$). Reward is heavily negative ($\approx -50$). Value loss is small because targets are all noisy.</td>
    </tr>
    <tr>
      <td><b>Phase 2: The Coward Trap<br>(Steps 5,000 – 30,000)</b></td>
      <td>The robot discovers that crushing the tomato gives a huge penalty ($-50$). 
        To avoid this, <b>it freezes the blade 2 mm above the tomato skin</b>! It gets $+0.5$ approach reward and stops.</td>
      <td>Critic learns: <i>"Hovering above the fruit is great! Value = +5."</i></td>
      <td>Reward plateaus at a low positive value ($\approx +3.0$). <b>Local Minimum trap!</b> Entropy begins dropping.</td>
    </tr>
    <tr>
      <td><b>Phase 3: The First Puncture<br>(Steps 30,000 – 100,000)</b></td>
      <td>Due to entropy noise, one robot out of 1,024 accidentally saws laterally while pressing down, puncturing the skin (+15 reward!).</td>
      <td>Critic experiences a massive TD error ($\delta \approx +12$). Value estimates along that trajectory spike upward!</td>
      <td><b>KL divergence spikes</b> as policy rapidly shifts weights toward sawing motion. Reward jumps from $+3 \to +25$.</td>
    </tr>
    <tr>
      <td><b>Phase 4: Master Convergence<br>(Steps 100,000 – 500,000)</b></td>
      <td>Policy coordinates dual arms: holding arm stabilizes fruit compliance while cutting arm executes steady $25\text{ mm/s}$ sawing shear.</td>
      <td>Critic predictions match true discounted returns with 95% accuracy.</td>
      <td><b>Explained variance $\to 0.95$</b>. Policy loss stabilizes near zero. 99.2% cut success rate across all 1,024 parallel envs!</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 9: PYTORCH VECTORIZED CODE -->
<h2>9. PyTorch Vectorized Simulation Loop (Isaac Lab Production Blueprint)</h2>
<p>
  Below is the complete, production-grade Python script running 1,024 parallel environments on GPU:
</p>

<div class="callout code-box">
  <div class="callout-title">🐍 Complete Isaac Lab Parallel Stepping Loop (`run_simulation.py`)</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn

# 1. Configuration Constants
NUM_ENVS = 1024         # 1,024 parallel simulation instances on RTX GPU
STATE_DIM = 33          # 33-dimensional sensory observation vector
ACTION_DIM = 6          # 6-dimensional continuous motor actions
HORIZON = 500           # 500 steps per episode (10 seconds at 50 Hz)
GAMMA = 0.99            # Discount factor

# 2. Vectorized Observation Normalizer (Running Mean & Variance)
class RunningObservationNormalizer:
    def __init__(self, shape):
        self.mean = torch.zeros(shape, device="cuda")
        self.var = torch.ones(shape, device="cuda")
        self.count = 1e-4

    def normalize(self, obs):
        # Update running stats online
        batch_mean = obs.mean(dim=0)
        batch_var = obs.var(dim=0, unbiased=False)
        self.mean = 0.99 * self.mean + 0.01 * batch_mean
        self.var = 0.99 * self.var + 0.01 * batch_var
        return (obs - self.mean) / torch.sqrt(self.var + 1e-8)

# 3. Main Vectorized Execution Loop
def run_parallel_rollout(env, policy, normalizer):
    raw_obs = env.reset()  # Shape: (1024, 33)
    total_rewards = torch.zeros(NUM_ENVS, device="cuda")

    for step in range(HORIZON):
        # Standardize observations to mean 0, variance 1
        norm_obs = normalizer.normalize(raw_obs)

        # Policy forward pass: Generates continuous actions in [-1, +1]
        with torch.no_grad():
            actions = policy(norm_obs)  # Shape: (1024, 6)

        # Step physics forward by 20 milliseconds across all 1,024 envs simultaneously
        next_raw_obs, rewards, dones, info = env.step(actions)

        # Accumulate episodic scores
        total_rewards += rewards

        # Advance state pointer
        raw_obs = next_raw_obs

    print(f"Rollout complete! Mean return across 1024 robots: {total_rewards.mean().item():.2f}")
    return total_rewards
</pre>
</div>

<div class="page-break"></div>

<!-- SECTION 10: PRACTITIONER'S CHECKLIST -->
<h2>10. Practitioner's Failure Modes &amp; Debugging Checklist (Top 5 Traps)</h2>
<p>
  When training your first robot in Isaac Lab, 95% of issues trace back to these five classic bugs:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 22%;">Failure Mode</th>
      <th style="width: 38%;">The Silent Symptom (What Goes Wrong)</th>
      <th style="width: 40%;">How to Fix It Immediately</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Observation Scale Explosion</b></td>
      <td>Acoustic counts are $30,000$ while joint angles are $0.1$ radians. Gradients for acoustic counts blow up, joint gradients vanish.</td>
      <td>Always wrap observations in <code>RunningObservationNormalizer</code> to clamp inputs to $[-5.0, +5.0]$.</td>
    </tr>
    <tr>
      <td><b>2. The Horizon Mismatch Trap</b></td>
      <td>Setting $\gamma = 0.90$ gives an effective planning horizon of only $H = \frac{1}{1 - \gamma} = 10$ steps. The robot cannot plan a 300-step cut!</td>
      <td>Set <b>$\gamma = 0.99$</b> ($H = 100$ steps) or $\gamma = 0.995$ for long contact tasks.</td>
    </tr>
    <tr>
      <td><b>3. Partial Observability (POMDP) Violation</b></td>
      <td>Passing knife height $z$ without vertical velocity $\dot{z}$. The policy cannot tell if the blade is plunging downward or retracting upward.</td>
      <td>Always stack the last 3 observation frames: $[o_t, o_{t-1}, o_{t-2}]$ or include full velocity vectors.</td>
    </tr>
    <tr>
      <td><b>4. Reward Scale Asymmetry</b></td>
      <td>Penetration reward gives $+0.1$ per step, but crushing penalty gives $-100.0$. The robot becomes terrified and refuses to touch the fruit.</td>
      <td>Ensure reward components are balanced within the same order of magnitude (e.g. progress $\in [0, 5]$, penalty $\in [-4, 0]$).</td>
    </tr>
    <tr>
      <td><b>5. Asynchronous Tensor Device Bug</b></td>
      <td>Sim is running on <code>cuda:0</code>, but actions or observation normalizer are accidentally created on <code>cpu</code>. Causes massive host-device transfer bottlenecks, dropping FPS from $15,000$ to $200$.</td>
      <td>Ensure all tensors, buffers, and model weights are strictly instantiated on <code>device="cuda"</code>.</td>
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
