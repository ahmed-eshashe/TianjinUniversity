import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 5: Zero-to-Hero Guide to Policy Gradients & REINFORCE</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 5 • Zero-to-Hero Guide to Policy Gradients";
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
  <span class="course-tag">CS285 Lecture 5 • Zero-to-Hero Field Manual</span>
  <h1>Policy Gradients: Trial-and-Error Learning</h1>
  <div class="subtitle">A Comprehensive, Intuitive Textbook: Score Functions, Continuous Gaussian Control, Baselines, and Multi-Domain Architectures</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Target Audience:</b> Complete Beginners to Advanced Robotics Practitioners</span>
  </div>
</div>

<!-- SECTION 1: THE CORE PHILOSOPHY -->
<h2>1. Why Policy Gradients? (The Non-Differentiable World)</h2>
<p>
  In traditional deep learning (like computer vision), we compute gradients by differentiating through mathematical equations using the chain rule. 
  If an image is slightly too dark, backpropagation computes $\frac{\partial \mathcal{L}}{\partial W}$ and updates the convolution weights.
</p>
<div class="callout warning-box">
  <div class="callout-title">⚠️ The Physics Calculus Breakdown</div>
  <p>
    In robotics, your neural network commands a physical knife to touch a ripe tomato. 
    <b>A tomato skin tearing under a blade is a discontinuous physical fracture.</b> 
    Contact friction suddenly shifts between stick and slip regimes. 
    Viscoplastic pulp flows irreversibly.
    <br><br>
    If you attempt to write down the calculus derivative $\frac{\partial \text{FruitDamage}}{\partial \text{MotorVoltage}}$, the derivative is either <b>zero</b> (flat plateaus where nothing happens) or <b>undefined infinity</b> (the microsecond the skin ruptures). 
    Standard analytical backpropagation through physical contact is mathematically dead!
  </p>
</div>

<h3>1.1 The Breakthrough: Optimizing the Expected Return</h3>
<p>
  Instead of trying to differentiate through complex physics equations, <b>Policy Gradients</b> bypass physics entirely. 
  We treat the physical environment as a black box and directly optimize the <i>Expected Total Reward</i>:
</p>
<div class="formula">
  $$J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} [R(\tau)] = \int \mathbb{P}(\tau \mid \theta) R(\tau) d\tau$$
</div>

<div class="callout intuition">
  <div class="callout-title">🐶 The Puppy Training Analogy ("Good Boy!" Theorem)</div>
  <p>
    When you teach a puppy to sit on command:
  </p>
  <ul>
    <li>You cannot open the puppy's skull with a wrench and rewire its brain synapses directly.</li>
    <li>You say <i>"Sit!"</i>. The puppy tries random actions: it barks, rolls over, chases its tail, and wiggles.</li>
    <li>Eventually, by pure chance, the puppy's hind legs sit on the floor.</li>
    <li><b>Instant Reinforcement:</b> You shout <i>"GOOD BOY!"</i> and give it a piece of steak (Reward).</li>
    <li>The puppy's brain automatically strengthens the connection: <i>"Whenever I hear that command, sitting leads to steak!"</i></li>
  </ul>
  <p>
    <b>The Policy Gradient Theorem is the exact mathematical formulation of "Good Boy!"</b> 
    We let the robot execute trial actions. When an action produces positive reward, we nudge the neural network's weights to make that action more probable. When it produces a penalty, we push the weights in the opposite direction!
  </p>
</div>

<!-- DIAGRAM 1: PUPPY REINFORCEMENT LOOP -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <rect x="20" y="20" width="150" height="50" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="95" y="42" font-size="9.5" font-weight="700" fill="#1e40af" text-anchor="middle">TRIAL ACTION $a_t$</text>
  <text x="95" y="58" font-size="8" fill="#475569" text-anchor="middle">Sampled from $\pi_\theta(a|s)$</text>

  <path d="M 170,45 L 230,45" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="230,45 220,40 220,50" fill="#2563eb"/>

  <rect x="230" y="20" width="140" height="50" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="300" y="42" font-size="9.5" font-weight="700" fill="#065f46" text-anchor="middle">OUTCOME / SCORE</text>
  <text x="300" y="58" font-size="8" fill="#047857" text-anchor="middle">Advantage $\hat{Q}_t$</text>

  <path d="M 370,45 L 430,45" fill="none" stroke="#10b981" stroke-width="2"/>
  <polygon points="430,45 420,40 420,50" fill="#10b981"/>

  <rect x="430" y="15" width="150" height="60" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
  <text x="505" y="38" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">WEIGHT ADJUSTMENT</text>
  <text x="505" y="52" font-size="7.5" fill="#78350f" text-anchor="middle">$\hat{Q} &gt; 0 \implies$ Nudge Up</text>
  <text x="505" y="65" font-size="7.5" fill="#78350f" text-anchor="middle">$\hat{Q} &lt; 0 \implies$ Nudge Down</text>
</svg>
</div>

<div class="page-break"></div>

<!-- SECTION 2: THE POLICY GRADIENT EQUATION -->
<h2>2. The Policy Gradient Theorem (Exhaustive Parameter Anatomy)</h2>
<p>
  Here is the foundational mathematical equation derived by Ronald Williams in 1992 (the REINFORCE algorithm):
</p>
<div class="formula">
  $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \cdot \hat{Q}_t \right]$$
</div>

<!-- PARAMETER ANATOMY TABLE 1 -->
<table>
  <thead>
    <tr>
      <th style="width: 18%;">Symbol</th>
      <th style="width: 22%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 25%;">Physical Effect in Robotics</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\nabla_\theta J(\theta)$</b></td>
      <td>Policy Gradient Vector</td>
      <td>The compass direction in neural network weight space that maximizes total score.</td>
      <td>Updates policy weights: $\theta \leftarrow \theta + \alpha \nabla_\theta J$.</td>
    </tr>
    <tr>
      <td><b>$\pi_\theta(a_t \mid s_t)$</b></td>
      <td>Action Likelihood</td>
      <td>Probability of picking action $a_t$ in state $s_t$.</td>
      <td>Output of the robot's policy network.</td>
    </tr>
    <tr>
      <td><b>$\nabla_\theta \log \pi_\theta$</b></td>
      <td>Score Function</td>
      <td><b>The Steering Wheel:</b> <i>"Which direction in weight space makes action $a_t$ more probable?"</i></td>
      <td>Gives the sensitivity of action likelihood to network parameters.</td>
    </tr>
    <tr>
      <td><b>$\hat{Q}_t$</b></td>
      <td>Performance Multiplier</td>
      <td><b>The Gas Pedal &amp; Reverse Gear:</b> <i>"How good or bad was this action?"</i></td>
      <td>If $\hat{Q} > 0$, press gas pedal. If $\hat{Q} < 0$, put into reverse!</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Policy Gradient Equation</div>
  <p>
    <b>"For every action the robot executed, calculate the direction in neural network weights that would make that action MORE likely. Then multiply that direction by the action's score ($\hat{Q}$). If the action was great, nudge the weights to do it more often. If the action caused a crush penalty, nudge the weights in the exact opposite direction!"</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: FOUR REAL-WORLD CASE STUDIES -->
<h2>3. Four Real-World Case Studies for Policy Gradients</h2>
<p>
  Let's observe how Policy Gradients optimize decisions across four completely different engineering systems:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 18%;">Domain</th>
      <th style="width: 27%;">What is the Action ($a_t$)?</th>
      <th style="width: 27%;">What is the Score Multiplier ($\hat{Q}$)?</th>
      <th style="width: 28%;">What the Policy Gradient Does</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Soft Fruit Slicing (Our Lab's Research)</b></td>
      <td>Continuous downward feed delta $\Delta v_z$ and lateral sawing speed $v_{\text{slice}}$.</td>
      <td>Penetration progress ($+5$) minus skin crushing penalty ($-4 \times \text{ExcessForce}^2$).</td>
      <td>Pulls the mean sawing speed upward while softening vertical feed rate upon skin contact.</td>
    </tr>
    <tr>
      <td><b>2. Autonomous Car (Highway Driving)</b></td>
      <td>Steering wheel continuous angle $\delta \in [-30^\circ, +30^\circ]$ and brake pressure.</td>
      <td>Velocity tracking bonus ($+2$) minus lane departure penalty ($-50$) and jerk penalty.</td>
      <td>Reinforces gentle, anticipatory steering nudges while suppressing sharp swerving.</td>
    </tr>
    <tr>
      <td><b>3. ChatGPT Alignment (RLHF / PPO)</b></td>
      <td>Discrete token ID chosen from 50,000 vocabulary words at position $t$.</td>
      <td>Human feedback reward model score ($+8.5$) minus KL divergence penalty.</td>
      <td>Increases the probability of polite, helpful tokens and suppresses hallucinations.</td>
    </tr>
    <tr>
      <td><b>4. Quadruped Robot (Locomotion)</b></td>
      <td>12 joint motor target angles commanded to low-level PD controllers.</td>
      <td>Forward velocity reward ($+3$) minus foot slip penalty and motor torque heating.</td>
      <td>Nudges joint trajectories to synchronize into an energy-efficient trotting gait.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 4: CONTINUOUS GAUSSIAN POLICIES -->
<h2>4. Continuous Gaussian Policies: Controlling Real Robot Actuators</h2>
<p>
  In discrete games (like Pong), the network outputs a softmax over 2 buttons (Up/Down). 
  In your dual-arm setup, the robot commands continuous real-valued numbers (e.g. feed rate $v_z = 2.45$ mm/s, stiffness $\Delta K = 350$ N/m).
</p>
<p>
  How can a neural network output continuous numbers while still exploring? It outputs the parameters of a <b>Gaussian (Normal) Distribution</b>:
</p>
<div class="formula">
  $$\pi_\theta(a \mid s) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left( -\frac{(a - \mu_\theta(s))^2}{2\sigma^2} \right)$$
</div>

<!-- DIAGRAM 2: GAUSSIAN CURVE SHIFT -->
<div class="diagram-container">
<svg width="600" height="110" viewBox="0 0 600 110">
  <path d="M 50,90 Q 150,90 200,60 Q 250,15 300,15 Q 350,15 400,60 Q 450,90 550,90" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="300" y1="15" x2="300" y2="90" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="2,2"/>
  <text x="300" y="102" font-size="8" fill="#64748b" text-anchor="middle">Initial Mean $\mu = 2.0$ mm/s</text>

  <circle cx="380" cy="50" r="5" fill="#10b981"/>
  <text x="380" y="42" font-size="8" font-weight="700" fill="#047857" text-anchor="middle">Sampled Action $a = 2.8$</text>
  <text x="380" y="65" font-size="7.5" fill="#065f46" text-anchor="middle">(Clean Cut! Score $+12$)</text>

  <path d="M 110,90 Q 210,90 260,60 Q 310,15 360,15 Q 410,15 460,60 Q 510,90 590,90" fill="none" stroke="#10b981" stroke-width="2.5"/>
  <line x1="360" y1="15" x2="360" y2="90" stroke="#10b981" stroke-width="1.5"/>
  <text x="360" y="102" font-size="8" font-weight="700" fill="#047857" text-anchor="middle">New Mean $\mu' = 2.3$ mm/s (PULLED RIGHT!)</text>
</svg>
</div>

<h3>4.1 Analytical Gaussian Score Function</h3>
<p>
  When we differentiate the Gaussian log-probability with respect to the mean $\mu$, we obtain an extraordinarily elegant result:
</p>
<div class="formula">
  $$\nabla_{\mu} \log \pi_\theta(a \mid s) = \frac{a - \mu_\theta(s)}{\sigma^2}$$
</div>

<!-- PARAMETER ANATOMY TABLE 2 -->
<table>
  <thead>
    <tr>
      <th style="width: 20%;">Term</th>
      <th style="width: 30%;">Plain English Meaning</th>
      <th style="width: 25%;">Tomato Slicing Value</th>
      <th style="width: 25%;">Physical Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\mu_\theta(s)$</b></td>
      <td>The Robot's Intended Action (Mean)</td>
      <td>$\mu = 2.0$ mm/s feed rate</td>
      <td>What the robot thinks is best.</td>
    </tr>
    <tr>
      <td><b>$\sigma$</b></td>
      <td>Exploration Noise (Standard Dev)</td>
      <td>$\sigma = 0.5$ mm/s wiggle room</td>
      <td>How widely the robot experiments.</td>
    </tr>
    <tr>
      <td><b>$a - \mu$</b></td>
      <td>Exploration Deviation</td>
      <td>$2.8 - 2.0 = +0.8$ mm/s</td>
      <td>Did the robot push faster ($>0$) or slower ($<0$)?</td>
    </tr>
    <tr>
      <td><b>$\frac{a - \mu}{\sigma^2} \cdot \hat{Q}$</b></td>
      <td>Gradient Pull Force</td>
      <td>$\frac{+0.8}{0.25} \times (+12) = +38.4$</td>
      <td>Pulls the intended mean $\mu$ towards successful cuts!</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 5: THE BASELINE & GRADING ON A CURVE -->
<h2>5. The Baseline: Why We Must Grade on a Curve</h2>
<div class="callout intuition">
  <div class="callout-title">🎓 The College Exam Analogy (Why Raw Scores Deceive)</div>
  <p>
    Imagine an entire class takes an exam so easy that every student scores between 90 and 100 points. 
    If you score 91, did you do well? <b>No, you were in the bottom 5% of the class!</b>
    <br><br>
    In RL, if all rewards are positive (e.g. scores are $+100, +105, +95$):
    <br>• Raw policy gradients will <b>push UP every action</b>, even the terrible ones that only scored $+95$!
    <br>• The network becomes confused because it is being told to reinforce everything.
    <br><br>
    <b>The Fix (The Baseline):</b> We subtract the average expected score $b(s) = V(s)$:
  </p>
  <div class="formula">
    $$\hat{A}_t = Q(s_t, a_t) - V(s_t)$$
  </div>
  <p>
    Now, an action that scores $+95$ when the average was $+100$ gets an advantage of <b>$-5.0$</b>! 
    It gets suppressed, while an action that scores $+105$ gets <b>$+5.0$</b> and gets reinforced. 
    <b>Subtracting a baseline is mathematically 100% unbiased (by the EGLP Lemma), but reduces gradient variance by 90%!</b>
  </p>
</div>

<!-- SECTION 6: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>6. Concrete Numerical Walkthrough: Updating a Policy with Numbers</h2>
<p>
  Let's walk through an exact numerical calculation of one policy gradient step:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 10%;">Step</th>
      <th style="width: 30%;">Variable / Expression</th>
      <th style="width: 25%;">Numerical Value</th>
      <th style="width: 35%;">Physical Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Current Mean Policy $\mu_\theta(s)$</td>
      <td><b>$2.0$ mm/s</b></td>
      <td>Robot intends to push blade at $2.0$ mm/s.</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Exploration Noise $\sigma$</td>
      <td><b>$0.5$ mm/s</b></td>
      <td>Variance $\sigma^2 = 0.25$.</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Sampled Action $a$</td>
      <td><b>$2.6$ mm/s</b></td>
      <td>Random sample with noise $\epsilon = +1.2$.</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Observed Return $G$</td>
      <td><b>$+18.0$</b></td>
      <td>Blade cleanly punctured skin into pulp!</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Baseline Prediction $b(s) = V(s)$</td>
      <td><b>$+12.0$</b></td>
      <td>Critic expected average performance to be $+12.0$.</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Advantage Multiplier $\hat{A}$</td>
      <td>$18.0 - 12.0 = \mathbf{+6.0}$</td>
      <td>Action beat the curve by $+6.0$ points!</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Gaussian Score $\frac{a - \mu}{\sigma^2}$</td>
      <td>$\frac{2.6 - 2.0}{0.25} = \mathbf{+2.4}$</td>
      <td>Compass direction pointing toward faster feeds.</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Gradient Step ($\alpha = 0.01$)</td>
      <td>$\Delta \mu = 0.01 \times (2.4) \times (6.0) = \mathbf{+0.144}$</td>
      <td>Mean feed rate increases from <b>$2.0 \to 2.144$ mm/s</b>!</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 7: DIARY OF A TRAINING RUN -->
<h2>7. "Diary of a Training Run" for Policy Gradients</h2>
<table>
  <thead>
    <tr>
      <th style="width: 20%;">Iteration Phase</th>
      <th style="width: 40%;">Policy Behavioral Evolution</th>
      <th style="width: 40%;">TensorBoard Diagnostics</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Phase 1: High Variance<br>(Iters 0 – 50)</b></td>
      <td>Gradients swing wildly in direction. Mean feed rate oscillates violently between $-10$ and $+10$ mm/s.</td>
      <td>Policy loss fluctuates wildly. Standard deviation $\sigma$ remains wide ($0.8 - 1.0$).</td>
    </tr>
    <tr>
      <td><b>Phase 2: Baseline Lock-in<br>(Iters 50 – 200)</b></td>
      <td>The Critic learns accurate baseline values $V(s)$. Advantages become clean and zero-centered. Policy stabilizes.</td>
      <td>Gradient norm drops by 70%. Mean feed rate settles into positive cutting territory ($\approx 2.5$ mm/s).</td>
    </tr>
    <tr>
      <td><b>Phase 3: Standard Dev Decay<br>(Iters 200 – 1000)</b></td>
      <td>Robot becomes confident in its cutting trajectory. Exploration noise $\sigma$ gently decays from $0.5 \to 0.15$.</td>
      <td><b>Entropy drops steadily</b> toward optimal deterministic control. Cut success rate reaches 98%.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 8: PYTORCH IMPLEMENTATION -->
<h2>8. Production PyTorch Policy Gradient Implementation</h2>

<div class="callout code-box">
  <div class="callout-title">🐍 Complete PyTorch REINFORCE with Continuous Gaussian Policy &amp; Baseline</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn
from torch.distributions import Normal

class GaussianPolicy(nn.Module):
    def __init__(self, state_dim=33, action_dim=6):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 256), nn.Tanh(),
            nn.Linear(256, 256), nn.Tanh()
        )
        self.mean_head = nn.Linear(256, action_dim)
        # Learnable log-standard deviation parameter
        self.log_std = nn.Parameter(torch.zeros(action_dim))

    def forward(self, state):
        features = self.net(state)
        mean = self.mean_head(features)
        # Clamp log_std to prevent numerical explosion or standard dev collapse
        std = torch.exp(torch.clamp(self.log_std, min=-2.0, max=1.0))
        return Normal(mean, std)

def compute_policy_loss(dist, actions, advantages, c_entropy=0.01):
    # 1. Compute log-probability of taken actions: log pi(a|s)
    log_probs = dist.log_prob(actions).sum(dim=-1)

    # 2. Policy Gradient Objective: -E[ log pi(a|s) * Advantage ]
    policy_loss = -(log_probs * advantages.detach()).mean()

    # 3. Entropy Regularization: Prevents premature exploration collapse
    entropy_loss = -c_entropy * dist.entropy().sum(dim=-1).mean()

    return policy_loss + entropy_loss
</pre>
</div>

<div class="page-break"></div>

<!-- SECTION 9: PRACTITIONER'S CHECKLIST -->
<h2>9. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Failure Mode</th>
      <th style="width: 35%;">The Hidden Cause</th>
      <th style="width: 40%;">How to Fix It Immediately</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Standard Deviation Collapse</b></td>
      <td>The network figures out that setting $\sigma \to 0$ eliminates penalty risk. The policy freezes into a deterministic rut and stops exploring completely.</td>
      <td>Clamp $\log \sigma$ with a minimum floor: <code>torch.clamp(log_std, min=-2.0)</code> and add an <b>Entropy Bonus</b> (<code>c_entropy=0.01</code>).</td>
    </tr>
    <tr>
      <td><b>2. Forgetting to Detach Advantages</b></td>
      <td>If you don't call <code>advantages.detach()</code>, gradients flow backward through the Critic network into the policy loss, corrupting Critic weights.</td>
      <td>Always call <code>advantages.detach()</code> before multiplying by <code>log_probs</code>.</td>
    </tr>
    <tr>
      <td><b>3. Small Batch Size Noise</b></td>
      <td>Policy gradients on small batches (e.g. 32 steps) are mostly random noise. The policy takes erratic steps and diverges.</td>
      <td>Collect at least <b>2,048 to 4,096 parallel environment steps</b> before each policy gradient update.</td>
    </tr>
    <tr>
      <td><b>4. Exploding Learning Rates</b></td>
      <td>Setting learning rate $\alpha = 1\times 10^{-2}$ causes policy weights to jump into saturated Tanh regions where all gradients vanish.</td>
      <td>Use standard Adam step size: <b>$\alpha = 3\times 10^{-4}$</b>.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>CS285 Lecture 5 Zero-to-Hero Guide • DEX-ROB Lab (Tianjin University) • Prof. Shan An</i>
</div>

</body>
</html>
"""

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Lecture5_Beginner_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture5_Beginner_Guide.pdf"

render_utils.build_pdf(html_content, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
