import os
import weasyprint
import shutil

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Robot Learning & The Closed Loop: Beginner's Guide to CS285 Lecture 1</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {
      content: "CS285 Lecture 1: Foundations & Robotics Closed Loop";
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

  /* Header Block */
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

  /* Callout Boxes */
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

  /* Math display */
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

  /* Tables */
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

  .page-break { page-break-before: always; }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 1 Enhanced Study Guide</span>
  <h1>Mastering Robot Learning &amp; The Closed Loop</h1>
  <div class="subtitle">Deep Foundations: (T, P, E) Formulation, Compounding Errors, Daniel Wolpert's Motor Control, The Bitter Lesson &amp; Bi-Manual Tomato Slicing</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Companion:</b> DEX-ROB Lab, Tianjin University</span>
    <span><b>Frameworks:</b> Goodfellow (T, P, E) + Achiam (Spinning Up)</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The "Mental Map": Why Does Lecture 1 Matter for Robotics?</h2>
<p>
  When engineers first attempt to program robots for delicate manipulation tasks—like grasping a slippery fruit, peeling an egg, or slicing a soft tomato—their instinct is to design an <b>explicit recipe</b>: <i>"Move down 10 millimeters, measure force, if force exceeds 5 Newtons, pause and slide sideways."</i>
</p>
<p>
  In the real physical world, this classical engineering approach collapses. Tomatoes differ in skin cuticle toughness, internal turgor pressure, flesh viscoelasticity, and curvature. Prof. Sergey Levine opens CS 285 with a radical paradigm shift: <b>we should not hardcode robotic behavior; robots must learn from trial, error, and physical sensory feedback.</b>
</p>

<!-- SVG Diagram: The 4 Themes of Lecture 1 -->
<div class="diagram-container">
<svg width="680" height="90" viewBox="0 0 680 90">
  <rect x="5" y="10" width="155" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="82" y="36" font-size="9.5" font-weight="700" fill="#1e40af" text-anchor="middle">1. SL vs. RL</text>
  <text x="82" y="52" font-size="8.5" fill="#475569" text-anchor="middle">i.i.d. Labels vs.</text>
  <text x="82" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Closed-Loop Control</text>

  <rect x="175" y="10" width="155" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="252" y="36" font-size="9.5" font-weight="700" fill="#6b21a8" text-anchor="middle">2. Philosophy of Movement</text>
  <text x="252" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Daniel Wolpert &amp;</text>
  <text x="252" y="66" font-size="8.5" fill="#475569" text-anchor="middle">The Bitter Lesson</text>

  <rect x="345" y="10" width="155" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="422" y="36" font-size="9.5" font-weight="700" fill="#065f46" text-anchor="middle">3. The Feedback Loop</text>
  <text x="422" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Observations, Actions &amp;</text>
  <text x="422" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Sensory Feedback</text>

  <rect x="515" y="10" width="155" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="592" y="36" font-size="9.5" font-weight="700" fill="#92400e" text-anchor="middle">4. Credit Assignment</text>
  <text x="592" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Why Rupturing at t=180</text>
  <text x="592" y="66" font-size="8.5" fill="#475569" text-anchor="middle">is Blamed on t=80</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: Supervised Learning vs. Reinforcement Learning</h2>
<p>
  <b>(Slides 8–18, Spoken Transcript 05:10–14:20)</b> The vast majority of modern AI (ChatGPT, computer vision, voice recognition) is built upon <b>Supervised Learning</b>. Levine explains why supervised learning fundamentally fails when applied to autonomous robot manipulation.
</p>

<h3>1.1 The Goodfellow (T, P, E) Formalization for Robotics</h3>
<p>
  In the *Deep Learning* textbook (Goodfellow, Bengio &amp; Courville, ch05), every learning system is rigorously formalized by three elements: <b>Task (T)</b>, <b>Performance Measure (P)</b>, and <b>Experience (E)</b>.
</p>
<ul>
  <li><b>Task (T):</b> Control a dual-arm manipulator equipped with a TacBlade knife to slice through deformable organic tomatoes without causing crushing, bruising, or fluid rupture.</li>
  <li><b>Performance Measure (P):</b> $J(\pi) = \mathbb{E}[\sum r_t]$, where rewards reward downward penetration depth while severely penalizing high compressive forces ($F_z > 8\text{ N}$) and volumetric deformation.</li>
  <li><b>Experience (E):</b> Closed-loop physical trajectories $\tau = (s_0, a_0, r_0, s_1, \dots)$ generated via interaction in GPU simulation (Isaac Lab).</li>
</ul>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Dimension</th>
      <th style="width: 40%;">Supervised Machine Learning</th>
      <th style="width: 40%;">Reinforcement Learning (RL)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Data Assumption</b></td>
      <td><b>i.i.d.</b> (Independent &amp; Identically Distributed). Each image or text token has no causal impact on the next sample.</td>
      <td><b>Non-i.i.d. &amp; Sequential.</b> Every action chosen by the robot alters the physical world, dictating what sensor reading comes next.</td>
    </tr>
    <tr>
      <td><b>Supervision Signal</b></td>
      <td><b>Direct Ground-Truth Labels:</b> A human tells the network the exact target class (e.g., "Cat" or "Dog").</td>
      <td><b>Scalar Evaluative Reward:</b> No one tells the robot what motor torque was correct; it only receives a numerical score indicating success or failure.</td>
    </tr>
    <tr>
      <td><b>Error Compounding</b></td>
      <td>Errors are localized: $\text{Error} \propto \epsilon T$.</td>
      <td><b>Quadratic Compounding:</b> Ross &amp; Bagnell proved errors compound quadratically $\mathcal{O}(\epsilon T^2)$ under distribution shift!</td>
    </tr>
    <tr>
      <td><b>Autonomous Discovery</b></td>
      <td>Limited by human demonstrations. The model cannot exceed the skill of the teacher.</td>
      <td><b>Emergent Strategies:</b> Discovers novel, counter-intuitive physical techniques (like "Move 37" in AlphaGo).</td>
    </tr>
  </tbody>
</table>

<div class="callout intuition">
  <div class="callout-title">Plain-English Intuition: The Math Exam vs. The Bicycle</div>
  <p>
    <b>Supervised learning</b> is like studying for an exam with an answer key: you guess an answer, check the back of the book, and correct your mistake. 
    <b>Reinforcement learning</b> is like learning to ride a bicycle. Nobody can hand you a mathematical answer key for how many micro-Newtons of force your left leg should exert when leaning 3 degrees to the right. You must get on the bike, wobble, feel your balance, fall over (negative reward), adjust, and eventually discover equilibrium through trial-and-error.
  </p>
</div>

<div class="callout warning-box">
  <div class="callout-title">The Compounding Error Theorem (Ross &amp; Bagnell, 2011)</div>
  <p>
    If an imitation learning policy makes an error with probability $\epsilon$ at each step, the expected number of mistakes over a trajectory of length $T$ is not $\epsilon T$, but $\mathcal{O}(\epsilon T^2)$. Why? The first small mistake drives the knife into an unobserved contact angle; because the policy was never trained on recovering from this angle, it makes another mistake immediately, cascading exponentially until the tomato explodes.
  </p>
</div>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: The Philosophy of Movement &amp; The Bitter Lesson</h2>
<p>
  <b>(Slides 24–35, Spoken Transcript 15:30–28:45)</b> Sergey Levine touches upon two profound intellectual pillars that justify why robotic reinforcement learning is the ultimate testbed for artificial intelligence.
</p>

<h3>2.1 Daniel Wolpert's Motor Control Postulate</h3>
<p>
  Neuroscientist Daniel Wolpert posed a famous biological question: <i>"Why do trees not have brains, while sea squirts and humans do?"</i>
</p>
<p>
  The juvenile sea squirt swims freely through the ocean looking for a suitable rock to attach to. It possesses a rudimentary nervous system and brain. However, the moment it anchors itself permanently to a rock, <b>it digests its own brain</b>. Why? Because it will never move again!
</p>
<div class="formula">
  <b>Wolpert's Principle:</b> "The brain exists for one reason and one reason only: to produce adaptable and complex movement."
</div>
<p>
  Sensory perception (vision, touch, sound) is completely useless unless it influences an action that changes the physical world. In robotics, vision and tactile sensing exist solely to guide the motors.
</p>

<!-- SVG Diagram: Sea Squirt to Dual-Arm Robot -->
<div class="diagram-container">
<svg width="680" height="120" viewBox="0 0 680 120">
  <rect x="20" y="15" width="190" height="90" rx="8" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="115" y="40" font-size="11" font-weight="700" fill="#334155" text-anchor="middle">The Sea Squirt</text>
  <text x="115" y="60" font-size="9" fill="#64748b" text-anchor="middle">Swims ➔ Has Brain</text>
  <text x="115" y="78" font-size="9" fill="#ef4444" text-anchor="middle">Anchors ➔ Consumes Brain</text>
  <text x="115" y="94" font-size="8" fill="#94a3b8" text-anchor="middle">(No movement = No brain needed)</text>

  <line x1="220" y1="60" x2="250" y2="60" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="255" y="15" width="190" height="90" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="350" y="40" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">Sensory Perception</text>
  <text x="350" y="60" font-size="9" fill="#1e3a8a" text-anchor="middle">TacBlade Tactile Array</text>
  <text x="350" y="78" font-size="9" fill="#1e3a8a" text-anchor="middle">Acoustic Audio Burst</text>
  <text x="350" y="94" font-size="8" fill="#3b82f6" text-anchor="middle">(Sensing without action is useless)</text>

  <line x1="455" y1="60" x2="485" y2="60" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="490" y="15" width="180" height="90" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="580" y="40" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">Active Motor Control</text>
  <text x="580" y="60" font-size="9" fill="#047857" text-anchor="middle">Modulate Feed Rate</text>
  <text x="580" y="78" font-size="9" fill="#047857" text-anchor="middle">Vary Joint Impedance</text>
  <text x="580" y="94" font-size="8" fill="#10b981" text-anchor="middle">(Adaptable Physical Impact)</text>
</svg>
</div>

<h3>2.2 Rich Sutton's "Bitter Lesson" (2019)</h3>
<p>
  Rich Sutton (the father of modern RL) observed that 70 years of AI history prove a painful truth: <b>human engineering heuristics always lose in the long run to methods that leverage general computation, learning, and search.</b>
</p>
<ul>
  <li>In Computer Vision: Handcrafted SIFT and HOG features were crushed by Deep Convolutional Networks.</li>
  <li>In Chess &amp; Go: Deep Blue's hand-tuned evaluation functions were crushed by AlphaZero's self-play RL search.</li>
  <li>In Robotics: Hand-crafted PID tables and finite state machines for contact transitions are consistently outperformed by end-to-end deep RL policies trained in massive GPU simulations (Isaac Lab).</li>
</ul>

<div class="callout math-box">
  <div class="callout-title">The Bitter Lesson Formula for Robotics</div>
  <p>
    <b>Intelligence = Scalable Representation Learning (Deep Nets) + General Optimization (Reinforcement Learning)</b><br>
    Instead of handcrafting rules like <i>"If skin is hard, saw at 4 Hz"</i>, provide the robot with rich multi-modal sensors (TacBlade + Force + Sound) and let policy gradient optimization discover the optimal sawing dynamics.
  </p>
</div>

<div class="page-break"></div>

<!-- PART 3 -->
<h2>Part 3: The Sensorimotor Closed Loop in Continuous Robotics</h2>
<p>
  <b>(Slides 18–23, Spoken Transcript 29:00–41:10)</b> Sergey Levine defines the formal feedback loop governing reinforcement learning. Every robotic task is modeled as an ongoing dialogue between the <b>Agent</b> (the policy) and the <b>Environment</b> (the physics engine or physical hardware).
</p>

<!-- SVG Diagram: The Full Robotic Feedback Loop -->
<div class="diagram-container">
<svg width="680" height="200" viewBox="0 0 680 200">
  <!-- Agent Box -->
  <rect x="230" y="15" width="220" height="65" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="340" y="40" font-size="12" font-weight="700" fill="#1e40af" text-anchor="middle">AGENT (Neural Policy π_θ)</text>
  <text x="340" y="58" font-size="9" fill="#3b82f6" text-anchor="middle">SkRL MLP: 33-dim State ➔ 6-dim Action</text>

  <!-- Environment Box -->
  <rect x="230" y="120" width="220" height="65" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="2"/>
  <text x="340" y="145" font-size="12" font-weight="700" fill="#0f172a" text-anchor="middle">ENVIRONMENT (Physical World)</text>
  <text x="340" y="163" font-size="9" fill="#64748b" text-anchor="middle">Isaac Lab / Real Dual Arms + Tomato Flesh</text>

  <!-- Action Arrow -->
  <path d="M 450 48 L 560 48 L 560 152 L 450 152" fill="none" stroke="#2563eb" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
  <text x="575" y="95" font-size="10" font-weight="700" fill="#2563eb" text-anchor="start">ACTION a_t</text>
  <text x="575" y="110" font-size="8.5" fill="#475569" text-anchor="start">Δz feed, v_saw,</text>
  <text x="575" y="123" font-size="8.5" fill="#475569" text-anchor="start">Impedance ΔK, ΔD</text>

  <!-- Observation & Reward Arrow -->
  <path d="M 230 152 L 120 152 L 120 48 L 230 48" fill="none" stroke="#10b981" stroke-width="2.5" marker-end="url(#arrow-green)"/>
  <text x="105" y="85" font-size="10" font-weight="700" fill="#047857" text-anchor="end">OBSERVATION s_t+1</text>
  <text x="105" y="100" font-size="8.5" fill="#475569" text-anchor="end">EE Pose, TacBlade F/T,</text>
  <text x="105" y="113" font-size="8.5" fill="#475569" text-anchor="end">Acoustic Rupture Burst</text>
  <text x="105" y="130" font-size="10" font-weight="700" fill="#d97706" text-anchor="end">REWARD r_t</text>
  <text x="105" y="145" font-size="8.5" fill="#475569" text-anchor="end">Progress - Crush Penalty</text>

  <defs>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981"/>
    </marker>
  </defs>
</svg>
</div>

<h3>3.1 The 4 Components of the Robotics Loop</h3>
<ol>
  <li>
    <b>The State / Observation ($s_t \in \mathcal{S}$):</b> The snapshot of sensory reality at time-step $t$. In your research, this includes robot joint encoders, end-effector pose, 6-axis forces from the knife blade, tactile contact patch distribution, and the acoustic microphone signal.
  </li>
  <li>
    <b>The Action ($a_t \in \mathcal{A}$):</b> The motor commands chosen by the neural network. In low-level robotics, this can be raw joint torques; in compliant manipulation, it is task-space velocity adjustments and impedance controller stiffness/damping offsets.
  </li>
  <li>
    <b>The Transition Dynamics ($\mathcal{P}(s_{t+1} | s_t, a_t)$):</b> The laws of physics governing how the knife interacts with the fruit. In simulation, this is simulated via FEM / mesh particles in Isaac Lab. In the real world, it is the physical mechanics of soft tissue rupture.
  </li>
  <li>
    <b>The Reward Function ($r_t = \mathcal{R}(s_t, a_t, s_{t+1})$):</b> The engineering metric that scores performance. It rewards downward tissue penetration and penalizes excessive lateral deformation (crushing) and high contact forces.
  </li>
</ol>

<div class="callout silent-bug">
  <div class="callout-title">Spinning Up Diagnostic: The Silent Failure of Static Trajectories</div>
  <p>
    Joshua Achiam warns: *Broken RL code runs fine; the agent just never learns.* In robotics, if your environment omits the knife's velocity or force rates from the observation vector, the Markov property is violated. The policy cannot distinguish whether a 5 N force is a gentle initial touch or a dangerous crushing surge. The code runs without crashing, but the robot's performance will plateau permanently at near-zero reward!
  </p>
</div>

<div class="page-break"></div>

<!-- PART 4 -->
<h2>Part 4: The Credit Assignment Problem Unpacked</h2>
<p>
  <b>(Slides 36–42, Spoken Transcript 42:15–53:30)</b> Sergey Levine identifies the <b>Credit Assignment Problem</b> as the central mathematical and practical hurdle in reinforcement learning.
</p>

<h3>4.1 The Anatomy of Delayed Consequences</h3>
<p>
  In a standard cutting episode lasting 200 time-steps (approx. 3.3 seconds at 60 Hz control frequency):
</p>
<ul>
  <li><b>Time-steps 1 to 30:</b> The knife approaches the tomato and touches the surface cuticle gently ($r_t \approx +0.1$).</li>
  <li><b>Time-steps 31 to 90:</b> The knife presses down. The cuticle stretches elastically. The policy chooses <i>not</i> to saw laterally, merely pushing down with increasing force.</li>
  <li><b>Time-steps 91 to 140:</b> Internal hydrostatic pressure builds inside the tomato pulp. Normal force exceeds 12 Newtons.</li>
  <li><b>Time-step 180:</b> The skin suddenly rips unpredictably along the side wall, spilling seeds and juice. The tomato collapses into pulp. The episode terminates with a catastrophic failure penalty ($r_{180} = -50$).</li>
</ul>

<!-- SVG Diagram: The Credit Assignment Timeline -->
<div class="diagram-container">
<svg width="680" height="150" viewBox="0 0 680 150">
  <!-- Timeline Line -->
  <line x1="40" y1="70" x2="640" y2="70" stroke="#94a3b8" stroke-width="3"/>

  <!-- Step t=10 -->
  <circle cx="90" cy="70" r="8" fill="#3b82f6"/>
  <text x="90" y="50" font-size="9.5" font-weight="700" fill="#1e40af" text-anchor="middle">t = 10</text>
  <text x="90" y="95" font-size="8.5" fill="#475569" text-anchor="middle">Touch Skin</text>
  <text x="90" y="108" font-size="8.5" fill="#10b981" text-anchor="middle">r = +0.1</text>

  <!-- Step t=80 -->
  <circle cx="270" cy="70" r="10" fill="#f59e0b"/>
  <text x="270" y="45" font-size="9.5" font-weight="700" fill="#b45309" text-anchor="middle">t = 80 (CRITICAL ERROR)</text>
  <text x="270" y="95" font-size="8.5" fill="#475569" text-anchor="middle">Overpressured Downward</text>
  <text x="270" y="108" font-size="8.5" fill="#d97706" text-anchor="middle">Zero Sawing Action!</text>

  <!-- Step t=140 -->
  <circle cx="450" cy="70" r="8" fill="#64748b"/>
  <text x="450" y="50" font-size="9.5" font-weight="700" fill="#334155" text-anchor="middle">t = 140</text>
  <text x="450" y="95" font-size="8.5" fill="#475569" text-anchor="middle">Pressure Surges</text>
  <text x="450" y="108" font-size="8.5" fill="#64748b" text-anchor="middle">r = 0.0</text>

  <!-- Step t=180 -->
  <circle cx="590" cy="70" r="11" fill="#ef4444"/>
  <text x="590" y="45" font-size="9.5" font-weight="700" fill="#991b1b" text-anchor="middle">t = 180 (CATASTROPHE)</text>
  <text x="590" y="95" font-size="8.5" fill="#ef4444" text-anchor="middle">Tomato Explodes!</text>
  <text x="590" y="108" font-size="8.5" fill="#ef4444" font-weight="700" text-anchor="middle">r = -50.0</text>

  <!-- Attribution Arrow -->
  <path d="M 580 30 C 450 -10, 350 -10, 280 30" fill="none" stroke="#dc2626" stroke-width="2" stroke-dasharray="4" marker-end="url(#arrow-red)"/>
  <text x="410" y="12" font-size="9" font-weight="700" fill="#dc2626" text-anchor="middle">Credit Assignment: Blame propagated back to t=80</text>

  <defs>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>
    </marker>
  </defs>
</svg>
</div>

<h3>4.2 Why Naive Learning Fails</h3>
<p>
  If you use a simple trial-and-error method without temporal credit assignment, the algorithm will see the $-50$ penalty at $t=180$ and penalize whatever action was taken at $t=180$ (e.g., a tiny blade adjustment). But the action at $t=180$ was innocent! The true culprit was the policy's failure to begin sawing at $t=80$.
</p>
<p>
  <b>How CS 285 Solves This:</b> In upcoming lectures, we will see that RL algorithms solve credit assignment using two mathematical tools:
</p>
<ol>
  <li><b>Reward-to-Go (Lecture 5):</b> Discounting future returns backward so actions are judged by everything that occurs after them.</li>
  <li><b>Value Functions &amp; Temporal Difference Learning (Lectures 6 &amp; 8):</b> Training a "Critic" neural network to predict expected future disaster before it happens, providing immediate step-by-step guidance.</li>
</ol>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Master Case Study for Paper 1 (Dual-Arm Slicing)</h2>
<p>
  How does the foundation laid in Lecture 1 directly translate to your Master's thesis at Tianjin University?
</p>

<h3>5.1 The Dual-Arm Setup</h3>
<p>
  In your experimental and simulation framework:
</p>
<ul>
  <li><b>Primary Arm (Manipulator):</b> Holds the custom instrumented <b>TacBlade</b> sensory knife. Responsible for vertical feed, lateral high-frequency sawing, and roll angle adjustments.</li>
  <li><b>Secondary Arm (Support):</b> Holds a soft/compliant gripper that stabilizes the tomato. Must apply sufficient normal force to prevent slipping, but not so much force that it squishes the lateral flesh.</li>
</ul>

<!-- SVG Diagram: Dual Arm Setup -->
<div class="diagram-container">
<svg width="680" height="160" viewBox="0 0 680 160">
  <!-- Left Arm Box -->
  <rect x="30" y="20" width="180" height="120" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="120" y="45" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">Primary Arm (Knife)</text>
  <text x="120" y="65" font-size="8.5" fill="#334155" text-anchor="middle">• TacBlade F/T Sensing</text>
  <text x="120" y="80" font-size="8.5" fill="#334155" text-anchor="middle">• Acoustic Microphones</text>
  <text x="120" y="95" font-size="8.5" fill="#334155" text-anchor="middle">• Δz Feed + v_saw Speed</text>
  <text x="120" y="110" font-size="8.5" fill="#2563eb" text-anchor="middle">Task-Space Impedance</text>

  <!-- Middle Fruit Box -->
  <rect x="250" y="35" width="180" height="90" rx="45" fill="#fee2e2" stroke="#ef4444" stroke-width="2"/>
  <text x="340" y="75" font-size="12" font-weight="800" fill="#991b1b" text-anchor="middle">Deformable Tomato</text>
  <text x="340" y="92" font-size="8.5" fill="#b91c1c" text-anchor="middle">Skin Cuticle + Pulp FEM</text>

  <!-- Right Arm Box -->
  <rect x="470" y="20" width="180" height="120" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="560" y="45" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">Secondary Arm (Gripper)</text>
  <text x="560" y="65" font-size="8.5" fill="#334155" text-anchor="middle">• Tactile Grip Fingers</text>
  <text x="560" y="80" font-size="8.5" fill="#334155" text-anchor="middle">• F_hold Normal Force</text>
  <text x="560" y="95" font-size="8.5" fill="#334155" text-anchor="middle">• Adaptive Counter-Torque</text>
  <text x="560" y="110" font-size="8.5" fill="#059669" text-anchor="middle">Slip Prevention</text>
</svg>
</div>

<h3>5.2 Translating the 4 Dilemmas into RL Specifications</h3>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Lecture 1 Dilemma</th>
      <th style="width: 35%;">Physical Tomato Cutting Manifestation</th>
      <th style="width: 40%;">Isaac Lab / SkRL Engineering Solution</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Non-i.i.d. Dynamics</b></td>
      <td>Depressing the blade creates internal fluid pressure; previous feed rates alter current tissue elasticity.</td>
      <td>Include past force derivative $\dot{F}_z$ and feed velocity $v_z$ in the 33-dimensional observation vector.</td>
    </tr>
    <tr>
      <td><b>Compounding Distribution Shift</b></td>
      <td>A slight knife tilt creates asymmetric cutting drag; human demonstration replay jams the blade.</td>
      <td>Train policy with Domain Randomization across 4,096 parallel Isaac Lab environments (randomize tomato stiffness, size, friction).</td>
    </tr>
    <tr>
      <td><b>Credit Assignment</b></td>
      <td>Tomato ruptures at step 180 because holding force at step 30 was too loose, causing the fruit to roll.</td>
      <td>Use GAE-$\lambda$ ($\lambda=0.95$) with discount factor $\gamma=0.99$ to correctly credit early stabilizing actions.</td>
    </tr>
    <tr>
      <td><b>Emergent Behaviors</b></td>
      <td>Human engineers cannot formulate the exact frequency to alternate sawing directions during cuticle breach.</td>
      <td>RL autonomously discovers the resonant sawing frequency that minimizes vertical penetration force.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- PART 6: SELF-TEST QUIZ -->
<h2>Part 6: Interactive Tablet Self-Test Quiz (Test Your Understanding)</h2>
<p>
  Before proceeding to Lecture 4, answer these 3 diagnostic questions. Tap to check your mental model:
</p>

<div class="quiz-box">
  <div class="quiz-q">Question 1: Why does a standard supervised imitation policy (trained on 100 human demonstrations) fail when cutting a tomato that is 10% softer than the training set?</div>
  <div class="quiz-a">
    <b>Answer:</b> Under softer fruit, the knife indents deeper under identical feed velocity. This places the robot in an out-of-distribution state never seen in human demonstrations. Because supervised learning does not reason about consequences, errors compound quadratically ($\mathcal{O}(\epsilon T^2)$), driving the knife into unrecoverable crushing forces.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: According to Daniel Wolpert's motor control thesis, what would happen if a robot had a trillion parameters of vision models but no closed-loop motor action feedback?</div>
  <div class="quiz-a">
    <b>Answer:</b> Like the anchored sea squirt, the perception system is functionally useless. Intelligence in biological and robotic systems exists solely to produce adaptable movements that alter the physical environment. High-dimensional sensing (TacBlade) is justified only because its real-time signals modulate motor impedance at 60 Hz.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: If an RL policy receives a reward of -50 at step 180 when the fruit collapses, why is it mathematically invalid to simply penalize the action taken at step 180?</div>
  <div class="quiz-a">
    <b>Answer:</b> Due to the Credit Assignment Problem: the structural collapse at step 180 was caused by excessive compressive loading at step 80 without adequate lateral sawing. Penalizing step 180 punishes an innocent blade micro-adjustment while leaving the true causal error uncorrected. Temporal discounting ($\gamma$) and value functions ($V(s)$) are required to propagate blame backward.
  </div>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 7: THESIS DEFENSE -->
<h2>Part 7: Thesis Defense Master Cheatsheet (Lecture 1 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Q1: "Why not use classical Model-Predictive Control (MPC) with an analytical physics model?"</div>
  <p>
    <b>Answer:</b> "Classical MPC requires an accurate, differentiable mathematical model of system dynamics. Soft fruit slicing involves elastoplastic finite deformation, fracture mechanics of the skin cuticle, non-linear fluid extrusion, and complex friction transitions. Creating an analytical model accurate enough for 1 kHz MPC is mathematically intractable. Reinforcement learning treats the physics as a black-box simulator, learning closed-loop sensorimotor coordination directly through trial-and-error."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q2: "Why not use Behavioral Cloning (Imitation Learning) from human teleoperation?"</div>
  <p>
    <b>Answer:</b> "Behavioral cloning suffers from cascading compounding errors. When a human teleoperates the robot, they operate at 5–10 Hz visual feedback, which is too slow to capture the sub-millisecond tactile and acoustic rupture dynamics. Furthermore, if a physical tomato deviates even slightly from the human demonstration, the imitation policy encounters an out-of-distribution state and fails catastrophically without corrective recovery behaviors."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q3: "How does your system address the Credit Assignment problem during the 200-step slicing trajectory?"</div>
  <p>
    <b>Answer:</b> "We address credit assignment through two mechanisms: (1) a multi-objective dense reward formulation that rewards incremental penetration progress while penalizing excessive compressive force and radial deformation at every control step, and (2) Generalized Advantage Estimation (GAE) within PPO, which propagates terminal success or failure back through intermediate states using a learned Critic value function."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q4: "What is Daniel Wolpert's postulate and how does it justify your TacBlade sensory design?"</div>
  <p>
    <b>Answer:</b> "Wolpert established that biological nervous systems evolved exclusively to produce adaptable physical movements. In our robotic system, the TacBlade tactile array and acoustic sensors are not mere passive observation tools; their real-time signals are fed directly into the RL policy at 60 Hz to dynamically alter the impedance parameters ($K_z, D_z$) and sawing velocity, proving that high-dimensional perception is tightly coupled to active closed-loop motor control."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q5: "How does Rich Sutton's 'Bitter Lesson' apply to your Isaac Lab simulation pipeline?"</div>
  <p>
    <b>Answer:</b> "The Bitter Lesson proves that general methods leveraging massive computation and learning outperform handcrafted domain rules. Rather than manually tuning PID gains for 10 different tomato varieties, we leverage 4,096 parallel environments in Isaac Lab on an NVIDIA GPU, allowing the RL policy to search across millions of simulated cuts and autonomously discover robust, emergent slicing strategies."
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
<div style="text-align: center; font-size: 8.5pt; color: #64748b;">
  CS 285 Lecture 1 Comprehensive Study Guide • Prepared for DEX-ROB Lab, Tianjin University
</div>

</body>
</html>
"""

output_path = "/home/omen/Downloads/CS285_Lecture1_Beginner_Guide.pdf"
backup_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture1_Beginner_Guide.pdf"

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_utils

render_utils.build_pdf(html_content, output_path, backup_path)

