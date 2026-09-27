import os
import weasyprint
import shutil

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering RL Basics & Continuous MDPs: Beginner's Guide to CS285 Lecture 4</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {
      content: "CS285 Lecture 4: RL Basics & Continuous MDPs";
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
    line-height: 1.58;
    font-size: 10pt;
  }

  .header-block {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 16px;
    margin-bottom: 20px;
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
    font-size: 10.5pt;
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
    font-size: 13pt;
    font-weight: 700;
    margin-top: 22px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    page-break-after: avoid;
  }

  h3 {
    color: #0f172a;
    font-size: 10.8pt;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 5px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 8px 0;
    text-align: justify;
  }

  .callout {
    padding: 10px 14px;
    margin: 11px 0;
    border-radius: 6px;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }
  .callout p { margin: 0; }
  .callout-title {
    font-weight: 700;
    font-size: 9pt;
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

  .formula {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 10px 0;
    text-align: center;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 10.8pt;
    color: #0f172a;
    page-break-inside: avoid;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9.2pt;
    page-break-inside: avoid;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 7px 10px;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 6px 10px;
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
    padding: 12px 14px;
    margin: 14px 0;
    page-break-inside: avoid;
  }
  .quiz-q { font-weight: 700; color: #0f172a; margin-bottom: 6px; }
  .quiz-a { color: #334155; font-size: 9.3pt; margin-top: 4px; border-top: 1px dashed #cbd5e1; padding-top: 4px; }

  .badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 8pt;
    font-weight: 600;
  }
  .badge-code { background: #e2e8f0; color: #334155; font-family: monospace; }

  .page-break { page-break-before: always; }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 4 Enhanced Study Guide</span>
  <h1>Mastering Reinforcement Learning Basics &amp; MDPs</h1>
  <div class="subtitle">Complete Beginner-Friendly Breakdown: Continuous Markov Decision Processes, Bellman Self-Consistency, Algorithm Anatomy &amp; Bi-Manual Slicing</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Companion:</b> DEX-ROB Lab, Tianjin University</span>
    <span><b>Frameworks:</b> Achiam (Spinning Up) + Levine Formalism</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The "Mental Map": Why Does Lecture 4 Exist?</h2>
<p>
  In previous lectures, you learned about <b>Imitation Learning</b> (Behavioral Cloning). Imitation learning is simple: you record a human operating the robot and train a neural network to mimic the human. But what if you <i>don't</i> have 200 hours of perfect human demonstrations? Or what if a human cannot accurately control high-frequency (1 kHz) knife impedance forces during tomato skin rupture?
</p>
<p>
  <b>This is why Reinforcement Learning (RL) exists.</b> Instead of copying a human, the robot discovers how to cut tomatoes on its own through simulated trial-and-error. Lecture 4 establishes the fundamental mathematical and conceptual language of RL: <i>Markov Decision Processes (MDPs), Cumulative Objectives, Value Functions, and the Algorithm Taxonomy</i>.
</p>

<!-- SVG Diagram: The 5 Pillars of Lecture 4 -->
<div class="diagram-container">
<svg width="680" height="90" viewBox="0 0 680 90">
  <rect x="5" y="10" width="125" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="67" y="38" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">PART 1: MDPs</text>
  <text x="67" y="54" font-size="8.5" fill="#475569" text-anchor="middle">States, Actions,</text>
  <text x="67" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Markov Property</text>

  <rect x="140" y="10" width="125" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="202" y="38" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">PART 2: Objective</text>
  <text x="202" y="54" font-size="8.5" fill="#475569" text-anchor="middle">Long-Term Returns,</text>
  <text x="202" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Discount Factor γ</text>

  <rect x="275" y="10" width="125" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="337" y="38" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">PART 3: Anatomy</text>
  <text x="337" y="54" font-size="8.5" fill="#475569" text-anchor="middle">Sample ➔ Evaluate</text>
  <text x="337" y="66" font-size="8.5" fill="#475569" text-anchor="middle">➔ Improve Loop</text>

  <rect x="410" y="10" width="125" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="472" y="38" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">PART 4: Values</text>
  <text x="472" y="54" font-size="8.5" fill="#475569" text-anchor="middle">V(s) &amp; Q(s,a)</text>
  <text x="472" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Advantage Function</text>

  <rect x="545" y="10" width="125" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="607" y="38" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">PART 5: Taxonomy</text>
  <text x="607" y="54" font-size="8.5" fill="#475569" text-anchor="middle">PPO vs SAC vs</text>
  <text x="607" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Model-Based</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: The Markov Decision Process (MDP) De-Mystified</h2>
<p>
  <b>(Slides 1–9)</b> At its core, RL models the interaction between an intelligent decision-maker (the robot's neural network) and the surrounding physical universe.
</p>

<h3>1.1 From Markov Chain to Markov Decision Process</h3>
<p>
  A <b>Markov Chain</b> is just a sequence of random events where no one has any control (e.g., the weather transitions from sunny to rainy). A <b>Markov Decision Process (MDP)</b> adds an active agent that takes actions to alter the future and receives rewards based on performance.
</p>

<div class="formula">
  MDP Tuple: &nbsp; &nbsp; <b>M = ⟨ S, A, T, R, γ ⟩</b>
</div>

<table>
  <thead>
    <tr>
      <th style="width: 15%;">Element</th>
      <th style="width: 25%;">Formal Math</th>
      <th style="width: 60%;">Plain-English Meaning in Your Tomato Cutting Paper</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>State (S)</b></td>
      <td><b>s</b><sub>t</sub> ∈ S</td>
      <td>The state vector (<b>33 numbers</b>): robot joint angles, knife 3D position &amp; velocity, TacBlade 6-axis contact forces, and acoustic vibration.</td>
    </tr>
    <tr>
      <td><b>Action (A)</b></td>
      <td><b>a</b><sub>t</sub> ∈ A</td>
      <td>The continuous motor commands (<b>6 numbers</b>): downward feed rate delta, lateral sawing velocity, and vertical stiffness/damping adjustments (ΔK, ΔD).</td>
    </tr>
    <tr>
      <td><b>Transitions (T)</b></td>
      <td>p(<b>s</b><sub>t+1</sub> | <b>s</b><sub>t</sub>, <b>a</b><sub>t</sub>)</td>
      <td>The <b>Physics Simulator (Isaac Sim / PhysX 5)</b>. It calculates how the tomato deforms and where the knife moves when you apply action <b>a</b><sub>t</sub>.</td>
    </tr>
    <tr>
      <td><b>Reward (R)</b></td>
      <td>r(<b>s</b><sub>t</sub>, <b>a</b><sub>t</sub>)</td>
      <td>The scoring formula: +points for slicing deeper and sawing, -penalties for squishing force (>8N).</td>
    </tr>
    <tr>
      <td><b>Discount (γ)</b></td>
      <td>γ ∈ [0, 1)</td>
      <td>Set to <b>0.99</b> in SkRL: tells the robot to care about finishing the complete cut rather than just touching the surface.</td>
    </tr>
  </tbody>
</table>

<h3>1.2 The "Goldfish Memory" Rule: The Markov Property</h3>
<div class="callout intuition">
  <div class="callout-title">Intuition: What is the Markov Property?</div>
  <p>
    A system is <b>Markovian</b> if the future depends <i>only</i> on what is happening right now (state <b>s</b><sub>t</sub> and action <b>a</b><sub>t</sub>), and <b>NOT</b> on the entire past history. The system has "goldfish memory"—it doesn't care what happened 10 seconds ago.
  </p>
</div>

<div class="callout robotics">
  <div class="callout-title">Direct Robotics Implication for Paper 1</div>
  <p>
    <b>Why did we design s<sub>t</sub> ∈ ℝ<sup>33</sup>?</b> If you only gave the neural network the knife's <i>position</i> (z), the system would <b>violate the Markov property</b>! Why? Because seeing a blade at height 5 cm tells you nothing about whether the knife is currently speeding downward at 50 mm/s or lifting upward. By adding <b>velocities (v<sub>knife</sub>)</b> and <b>rates of force change</b> into the state, step <b>s</b><sub>t</sub> holds all information needed to predict step <b>s</b><sub>t+1</sub>.
  </p>
</div>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: Defining the RL Objective &amp; The Markov Chain View</h2>
<p>
  <b>(Slides 10–16)</b> What does it mean for an algorithm to "learn"? It means tuning the neural network weights θ to maximize total expected reward.
</p>

<h3>2.1 The Objective: Why Immediate Greedy Actions Fail</h3>
<div class="formula">
  θ* = \arg\max_\theta \mathbb{E}_{\tau \sim p_\theta(\tau)} \left[ \sum_{t=1}^H r(\mathbf{s}_t, \mathbf{a}_t) \right]
</div>
<p>
  In Slide 11, Levine shows the car crash: if you drive at 100 km/h toward another car, slamming the brakes 1 meter away is the "best" immediate action, but you will still crash! The true mistake was made 5 seconds earlier.
</p>

<div class="callout robotics">
  <div class="callout-title">The Tomato Skin Fracture Analogy</div>
  <p>
    When cutting a ripe tomato, the knife presses against tough elastic skin. If the robot acts greedily to maximize downward motion, it pushes down with 15 Newtons. At <b>t = 50</b>, the skin suddenly pops (rupture fracture). Because downward resistance vanishes in under 5 milliseconds, the knife violently slams into the cutting board and explodes the tomato. 
    <br><b>RL solves this:</b> It trains the policy to start sawing laterally and increasing damping (ΔD) <i>before</i> the fracture point, because RL optimizes for the <b>total cut quality</b>, not just the current millisecond!
  </p>
</div>

<h3>2.2 The Markov Chain View: Unpacking Slide 12 &amp; 13</h3>
<p>
  In Slide 12, Levine asks: <i>"Is there a simpler way to write this?"</i> Instead of treating the entire 500-step trajectory τ as one giant joint probability distribution, we use the <b>linearity of expectation</b>:
</p>
<div class="formula">
  \mathbb{E}_{\tau \sim p_\theta(\tau)} \left[ \sum_t r(\mathbf{s}_t, \mathbf{a}_t) \right] = \sum_{t=1}^H \mathbb{E}_{(\mathbf{s}_t, \mathbf{a}_t) \sim p_\theta(\mathbf{s}_t, \mathbf{a}_t)} \left[ r(\mathbf{s}_t, \mathbf{a}_t) \right]
</div>
<p>
  <b>Plain English:</b> <i>"The average total score of the cut equals the sum of the average scores at each individual second."</i> We can bundle state and action into a single unit (<b>s</b><sub>t</sub>, <b>a</b><sub>t</sub>) and step forward like links in a chain.
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

<!-- PART 3 -->
<h2>Part 3: The Anatomy of an RL Algorithm</h2>
<p>
  <b>(Slides 17–21)</b> Every modern RL algorithm in existence—from simple DQN to the advanced PPO and SAC you run in SkRL—is made of the exact same 3-step loop:
</p>

<!-- SVG Diagram 2: The 3-Step Engine -->
<div class="diagram-container">
<svg width="620" height="130" viewBox="0 0 620 130">
  <rect x="10" y="35" width="180" height="60" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="100" y="58" font-size="10" font-weight="700" fill="#1e40af" text-anchor="middle">1. GENERATE SAMPLES</text>
  <text x="100" y="74" font-size="8.5" fill="#475569" text-anchor="middle">Run policy in Isaac Lab</text>
  <text x="100" y="86" font-size="8.5" fill="#475569" text-anchor="middle">(Parallel GPU Rollouts)</text>

  <line x1="190" y1="65" x2="220" y2="65" stroke="#94a3b8" stroke-width="2"/>
  <polygon points="220,65 212,60 212,70" fill="#94a3b8"/>

  <rect x="220" y="35" width="180" height="60" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
  <text x="310" y="58" font-size="10" font-weight="700" fill="#92400e" text-anchor="middle">2. EVALUATE RETURN</text>
  <text x="310" y="74" font-size="8.5" fill="#475569" text-anchor="middle">Fit Value Function V(s)</text>
  <text x="310" y="86" font-size="8.5" fill="#475569" text-anchor="middle">or estimate Advantage A(s,a)</text>

  <line x1="400" y1="65" x2="430" y2="65" stroke="#94a3b8" stroke-width="2"/>
  <polygon points="430,65 422,60 422,70" fill="#94a3b8"/>

  <rect x="430" y="35" width="180" height="60" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="520" y="58" font-size="10" font-weight="700" fill="#065f46" text-anchor="middle">3. IMPROVE POLICY</text>
  <text x="520" y="74" font-size="8.5" fill="#475569" text-anchor="middle">PPO Clipping Gradient /</text>
  <text x="520" y="86" font-size="8.5" fill="#475569" text-anchor="middle">Actor-Critic Weight Update</text>

  <path d="M 520,95 L 520,118 L 100,118 L 100,95" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="4,4"/>
  <polygon points="100,95 95,103 105,103" fill="#2563eb"/>
  <text x="310" y="113" font-size="8" fill="#2563eb" text-anchor="middle">Repeat for 500,000 steps until tomato slicing converges</text>
</svg>
</div>

<h3>3.1 Which Part is the Bottleneck? (Slide 21)</h3>
<ul>
  <li><b>On a Real Physical Robot:</b> Step 1 is the painful bottleneck! You have to physically wait in real time (1x). If a tomato cut takes 10 seconds, collecting 100,000 cuts takes <b>11.5 days</b> of continuous robot wear-and-tear!</li>
  <li><b>In Isaac Lab (Your Setup):</b> We solve this bottleneck by running <b>1,024 to 4,096 parallel robot arms simultaneously on your RTX GPU</b>. Physics runs at <b>1,000x to 10,000x real time</b>, allowing your robot to experience 10 years of cutting practice in just 45 minutes!</li>
</ul>

<div class="page-break"></div>

<!-- PART 4 -->
<h2>Part 4: Value Functions, Q-Functions &amp; Bellman Self-Consistency</h2>
<p>
  <b>(Slides 22–26 &amp; Spinning Up ch07)</b> In *Spinning Up in Deep RL*, Joshua Achiam emphasizes that value functions are central because they obey <b>Bellman Self-Consistency</b>: the value of your starting point equals the immediate reward plus the value of wherever you land.
</p>

<h3>4.1 The 4 Core Value Functions</h3>
<table>
  <thead>
    <tr>
      <th style="width: 22%;">Function</th>
      <th style="width: 38%;">Mathematical Definition</th>
      <th style="width: 40%;">Physical Role in Dual-Arm Slicing</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>On-Policy State Value $V^\pi(s)$</b></td>
      <td>$\mathbb{E}_{\tau \sim \pi} \left[ \sum_{t=0}^\infty \gamma^t r_t \;\Big|\; s_0 = s \right]$</td>
      <td>Expected total cut score if the knife is currently at state $s$ and continues following policy $\pi$.</td>
    </tr>
    <tr>
      <td><b>On-Policy Action Value $Q^\pi(s, a)$</b></td>
      <td>$\mathbb{E}_{\tau \sim \pi} \left[ \sum_{t=0}^\infty \gamma^t r_t \;\Big|\; s_0 = s, a_0 = a \right]$</td>
      <td>Expected score if the knife takes specific action $a$ right now, and then continues following policy $\pi$.</td>
    </tr>
    <tr>
      <td><b>Optimal State Value $V^*(s)$</b></td>
      <td>$\max_\pi V^\pi(s) = \max_a Q^*(s, a)$</td>
      <td>The absolute highest achievable cut quality possible from state $s$ under the perfect policy.</td>
    </tr>
    <tr>
      <td><b>Optimal Action Value $Q^*(s, a)$</b></td>
      <td>$\max_\pi Q^\pi(s, a)$</td>
      <td>The highest achievable score starting from state $s$, taking action $a$, and acting optimally thereafter.</td>
    </tr>
  </tbody>
</table>

<h3>4.2 The Bellman Equations</h3>
<div class="formula" style="border: 2px solid #3b82f6; background: #eff6ff;">
  <b>Bellman Expectation Equation for V:</b><br>
  $$V^\pi(s) = \mathbb{E}_{a \sim \pi, s' \sim P} \left[ r(s, a) + \gamma V^\pi(s') \right]$$
</div>
<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>Bellman Optimality Equation for Q:</b><br>
  $$Q^*(s, a) = \mathbb{E}_{s' \sim P} \left[ r(s, a) + \gamma \max_{a'} Q^*(s', a') \right]$$
</div>

<div class="callout silent-bug">
  <div class="callout-title">Spinning Up Bug Alert: The [N] vs [N, 1] Tensor Broadcasting Trap</div>
  <p>
    Joshua Achiam highlights this as the #1 silent bug in RL implementations:
    If `rewards` has shape `[N]` (1D) and `next_values` has shape `[N, 1]` (2D), computing `targets = rewards + gamma * next_values` in PyTorch does NOT raise an error! Instead, Python broadcasts the two shapes into an <b>[N, N] matrix</b>! The Critic trains on random pairwise broadcasted values, loss stays finite, but the policy never learns. Always ensure shapes are strictly aligned using `.view(-1, 1)` or `.squeeze()`.
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 5 -->
<h2>Part 5: Taxonomy of RL Algorithms — Which One for Your Paper?</h2>
<p>
  <b>(Slides 27–41)</b> Levine organizes all model-free algorithms along two fundamental trade-offs: <b>Sample Efficiency</b> and <b>Stability</b>.
</p>

<!-- SVG Diagram: The Spectrum -->
<div class="diagram-container">
<svg width="640" height="110" viewBox="0 0 640 110">
  <line x1="50" y1="45" x2="590" y2="45" stroke="#cbd5e1" stroke-width="4"/>

  <!-- Left: Model-Based -->
  <circle cx="80" cy="45" r="9" fill="#0284c7"/>
  <text x="80" y="25" font-size="9" font-weight="700" fill="#0369a1" text-anchor="middle">Model-Based</text>
  <text x="80" y="70" font-size="7.5" fill="#475569" text-anchor="middle">Dyna, MBPO</text>
  <text x="80" y="82" font-size="7.5" fill="#059669" text-anchor="middle">Most Efficient</text>

  <!-- Mid-Left: Off-policy Q-learning -->
  <circle cx="230" cy="45" r="9" fill="#3b82f6"/>
  <text x="230" y="25" font-size="9" font-weight="700" fill="#1d4ed8" text-anchor="middle">Off-Policy Q-Learning</text>
  <text x="230" y="70" font-size="7.5" fill="#475569" text-anchor="middle">DQN, TD3</text>
  <text x="230" y="82" font-size="7.5" fill="#d97706" text-anchor="middle">Can Diverge</text>

  <!-- Center: Actor-Critic (SAC) -->
  <circle cx="380" cy="45" r="11" fill="#10b981" stroke="#047857" stroke-width="2"/>
  <text x="380" y="22" font-size="9.5" font-weight="800" fill="#047857" text-anchor="middle">Actor-Critic (SAC)</text>
  <text x="380" y="70" font-size="7.5" fill="#475569" text-anchor="middle">Soft Actor-Critic</text>
  <text x="380" y="82" font-size="7.5" fill="#047857" font-weight="700" text-anchor="middle">★ Great for Robots</text>

  <!-- Right: On-Policy Policy Gradients (PPO) -->
  <circle cx="530" cy="45" r="11" fill="#10b981" stroke="#047857" stroke-width="2"/>
  <text x="530" y="22" font-size="9.5" font-weight="800" fill="#047857" text-anchor="middle">Policy Gradient (PPO)</text>
  <text x="530" y="70" font-size="7.5" fill="#475569" text-anchor="middle">PPO / SkRL</text>
  <text x="530" y="82" font-size="7.5" fill="#047857" font-weight="700" text-anchor="middle">★ Most Stable / Standard</text>
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
      <td><b>Moderate:</b> Needs careful tuning of entropy temperature α and target network updates to avoid overestimating Q-values.</td>
    </tr>
    <tr>
      <td><b>Pure Q-Learning (DQN)</b></td>
      <td>Moderate</td>
      <td><b>Unstable on Continuous Arms:</b> Computing argmax over continuous actions (torques) is mathematically intractable.</td>
    </tr>
    <tr>
      <td><b>Model-Based RL</b></td>
      <td><b>Highest:</b> Tries to learn a neural network predicting squashy tomato physics.</td>
      <td><b>Brittle:</b> Compounding model simulation errors lead to physical exploitation and catastrophic real-world failure.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- PART 6: BLUEPRINT & QUIZ -->
<h2>Part 6: Interactive Tablet Self-Test Quiz (Test Your Understanding)</h2>

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

<!-- PART 7: THESIS DEFENSE -->
<h2>Part 7: Thesis Defense Master Cheatsheet (Lecture 4 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Q1: "Why is your tomato slicing task formulated as an MDP rather than a POMDP?"</div>
  <p>
    <b>Answer:</b> "While internal fruit tissue state is not directly visible, our multi-modal sensor fusion—combining TacBlade 6-axis forces, tactile contact patch distribution, acoustic emission, and end-effector kinematics—provides a sufficiently rich 33-dimensional state representation such that the Markov property is preserved for continuous compliant control."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q2: "What is the physical interpretation of setting discount factor $\gamma = 0.99$?"</div>
  <p>
    <b>Answer:</b> "At 60 Hz control frequency, an effective time horizon is $1 / (1 - \gamma) \approx 100$ steps (approx. 1.6 seconds). This ensures the robot policy plans ahead for the complete skin rupture and tissue sawing cycle, preventing short-sighted greedy downward thrusts."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q3: "How does the Advantage function $A(s, a)$ protect the tomato from violent motor commands?"</div>
  <p>
    <b>Answer:</b> "In delicate pre-puncture states ($V(s) \approx +50$), an action that applies excessive downward pressure causes bruising and fluid leakage, yielding $Q(s, a) \approx -30$. The resulting negative advantage ($A = -80$) suppresses this violent command in the policy gradient update, steering the policy toward compliant lateral sawing."
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
<div style="text-align: center; font-size: 8.5pt; color: #64748b;">
  CS 285 Lecture 4 Comprehensive Study Guide • Prepared for DEX-ROB Lab, Tianjin University
</div>

</body>
</html>
"""

output_path = "/home/omen/Downloads/CS285_Lecture4_Beginner_Guide.pdf"
backup_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture4_Beginner_Guide.pdf"

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_utils

render_utils.build_pdf(html_content, output_path, backup_path)

