import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 6: Zero-to-Hero Guide to Actor-Critic & GAE</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 6 • Zero-to-Hero Guide to Actor-Critic & GAE";
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
  <span class="course-tag">CS285 Lecture 6 • Zero-to-Hero Field Manual</span>
  <h1>Actor-Critic Architectures &amp; Generalized Advantage Estimation (GAE)</h1>
  <div class="subtitle">A Comprehensive, Intuitive Textbook: Replacing Noisy Rollouts with Instant Critic Feedback, The Bias-Variance Dial, and Privileged Simulation</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Target Audience:</b> Complete Beginners to Advanced Robotics Practitioners</span>
  </div>
</div>

<!-- SECTION 1: CORE INTUITION -->
<h2>1. What is Actor-Critic? (The Theater Director Analogy)</h2>
<p>
  In Lecture 5, we studied REINFORCE (Monte Carlo policy gradients). 
  In REINFORCE, the robot runs a full 500-step episode to the end, sums up all rewards, and updates its policy. 
  While mathematically unbiased, it is agonizingly noisy. If one small contact wobble occurs at step 480, the entire trajectory return is ruined.
  Can we get immediate microsecond feedback at <i>every single step</i>? Yes! We introduce a second neural network: <b>The Critic</b>.
</p>

<div class="callout intuition">
  <div class="callout-title">🎭 The Stage Actor &amp; The Theater Director Analogy</div>
  <p>
    Imagine an actor rehearsing a 3-hour Shakespeare play:
  </p>
  <ul>
    <li><b>The Monte Carlo (REINFORCE) Way:</b> The actor performs the entire 3-hour play in an empty theater. At midnight, after the show ends, the newspaper publishes a review: <i>"2 out of 5 stars."</i> The actor has no idea which specific monologue was terrible and which was brilliant. Training takes years.</li>
    <li><b>The Actor-Critic Way:</b> The theater director sits in the front row during rehearsals. The instant the actor delivers a single line, the director whispers: 
      <br><i>"That line had great emotional resonance! (+Advantage)"</i> or <i>"You mumbled that phrase, speak louder! (-Advantage)"</i>.
      <br>The actor doesn't wait 3 hours to learn. They get <b>instant, microsecond feedback on every line</b>!
    </li>
  </ul>
  <p>
    In deep RL:
    <br>• <b>The Actor ($\pi_\theta$):</b> Proposes the continuous motor actions ($a_t$).
    <br>• <b>The Critic ($V_\phi$):</b> Evaluates how good the resulting state is, providing immediate advantage scores to guide the Actor!
  </p>
</div>

<!-- DIAGRAM 1: ACTOR-CRITIC ARCHITECTURE -->
<div class="diagram-container">
<svg width="600" height="120" viewBox="0 0 600 120">
  <rect x="20" y="35" width="130" height="50" rx="6" fill="#f8fafc" stroke="#475569" stroke-width="1.5"/>
  <text x="85" y="56" font-size="10" font-weight="700" fill="#0f172a" text-anchor="middle">Sensor State $s_t$</text>
  <text x="85" y="72" font-size="8" fill="#64748b" text-anchor="middle">33D Sensor Vector</text>

  <path d="M 150,50 L 210,25" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="210,25 201,23 206,31" fill="#2563eb"/>

  <path d="M 150,70 L 210,95" fill="none" stroke="#f59e0b" stroke-width="2"/>
  <polygon points="210,95 206,89 201,97" fill="#f59e0b"/>

  <rect x="210" y="5" width="200" height="45" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="310" y="24" font-size="10" font-weight="700" fill="#1e40af" text-anchor="middle">THE ACTOR $\pi_\theta(a \mid s)$</text>
  <text x="310" y="38" font-size="7.5" fill="#475569" text-anchor="middle">Outputs motor action $a_t \in \mathbb{R}^6$</text>

  <rect x="210" y="70" width="200" height="45" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
  <text x="310" y="89" font-size="10" font-weight="700" fill="#92400e" text-anchor="middle">THE CRITIC $V_\phi(s)$</text>
  <text x="310" y="103" font-size="7.5" fill="#475569" text-anchor="middle">Predicts expected future value $V(s) \in \mathbb{R}^1$</text>

  <line x1="410" y1="27" x2="480" y2="27" stroke="#2563eb" stroke-width="2"/>
  <polygon points="480,27 472,22 472,32" fill="#2563eb"/>
  <text x="535" y="31" font-size="9" font-weight="700" fill="#1e40af">Robot Motors</text>

  <line x1="410" y1="92" x2="480" y2="92" stroke="#f59e0b" stroke-width="2"/>
  <polygon points="480,92 472,87 472,97" fill="#f59e0b"/>
  <text x="535" y="96" font-size="9" font-weight="700" fill="#92400e">Advantage $\hat{A}_t$</text>
</svg>
</div>

<div class="page-break"></div>

<!-- SECTION 2: TEMPORAL DIFFERENCE LEARNING -->
<h2>2. Temporal Difference (TD) Learning: The Road Trip Traffic Jam</h2>
<div class="callout intuition">
  <div class="callout-title">🚗 The Road Trip Traffic Jam Analogy</div>
  <p>
    Suppose you embark on a 4-hour road trip. 
    One hour in, you encounter a colossal traffic jam. Your GPS announces that your remaining drive is now 5 hours (total trip: 6 hours).
    <br><br>
    Do you need to wait 5 more hours until you reach your destination to conclude that your original 4-hour estimate was wrong? 
    <b>Of course not!</b> You update your estimate <b>right now</b>. 
    You took 1 hour of cold, hard reality + your updated estimate of the rest of the trip.
  </p>
</div>

<h3>2.1 The 1-Step TD Residual Error $\delta_t$ (Parameter Anatomy)</h3>
<div class="formula">
  $$\delta_t = r(s_t, a_t) + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$$
</div>

<!-- PARAMETER ANATOMY TABLE 1 -->
<table>
  <thead>
    <tr>
      <th style="width: 18%;">Symbol</th>
      <th style="width: 22%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 25%;">Real-World Example Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\delta_t$</b></td>
      <td>TD Residual / Surprise Factor</td>
      <td>How much better or worse was this step than your Critic expected?</td>
      <td>$\delta_t = +1.45$ (Positive surprise!)</td>
    </tr>
    <tr>
      <td><b>$r(s_t, a_t)$</b></td>
      <td>Immediate Reality</td>
      <td>The actual physical reward points received on this step.</td>
      <td>$+2.5$ points (Sawing reward)</td>
    </tr>
    <tr>
      <td><b>$\gamma V_\phi(s_{t+1})$</b></td>
      <td>Discounted Future Forecast</td>
      <td>The Critic's estimate of remaining score from the next state onward.</td>
      <td>$0.99 \times 12.0 = 11.88$</td>
    </tr>
    <tr>
      <td><b>$V_\phi(s_t)$</b></td>
      <td>Prior Expectation</td>
      <td>What the Critic thought your situation was worth <i>before</i> you took the action.</td>
      <td>$12.93$ points</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the TD Error</div>
  <p>
    <b>"TD Error is the surprise factor: (Reality right now + What you predict for tomorrow) MINUS (What you predicted yesterday). If $\delta > 0$, things went better than expected. If $\delta < 0$, things went worse!"</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: FOUR MULTI-DOMAIN CASE STUDIES -->
<h2>3. Four Real-World Case Studies for Actor-Critic</h2>
<p>
  Let's observe how the Actor and Critic interact across four diverse engineering systems:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 16%;">Domain</th>
      <th style="width: 28%;">What Does the Actor ($\pi_\theta$) Do?</th>
      <th style="width: 28%;">What Does the Critic ($V_\phi$) Do?</th>
      <th style="width: 28%;">What the Advantage ($\hat{A}$) Tells the Actor</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Soft Fruit Slicing (Our Lab's Research)</b></td>
      <td>Outputs continuous feed velocity $\Delta v_z$ and lateral sawing shear $v_{\text{slice}}$.</td>
      <td>Predicts remaining cumulative score to complete cut without fruit crushing.</td>
      <td><i>"Increasing lateral sawing reduced normal force by 3N. That was +4.5 points better than average. DO IT MORE!"</i></td>
    </tr>
    <tr>
      <td><b>2. Autonomous Car (Highway Driving)</b></td>
      <td>Outputs continuous steering angle and pedal pressure.</td>
      <td>Predicts remaining travel safety margin and time-to-arrival.</td>
      <td><i>"Braking gently early prevented an emergency stop later. Advantage = +8.2."</i></td>
    </tr>
    <tr>
      <td><b>3. ChatGPT Alignment (RLHF / PPO)</b></td>
      <td>Samples the next word token from 50,000 vocabulary words.</td>
      <td>Predicts final human satisfaction rating of the completed paragraph.</td>
      <td><i>"Adding that clarification sentence boosted user satisfaction. Advantage = +1.8."</i></td>
    </tr>
    <tr>
      <td><b>4. Quadruped Robot (Locomotion)</b></td>
      <td>Outputs target joint angles for all 12 leg motors.</td>
      <td>Predicts remaining time the robot will stay upright over rocky terrain.</td>
      <td><i>"Extending the right front leg absorbed the step impact smoothly. Advantage = +5.0."</i></td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 4: THE BIAS-VARIANCE DILEMMA -->
<h2>4. The Bias-Variance Dilemma: The Core Trade-off in Machine Learning</h2>
<p>
  When training the Actor, we face a fundamental trade-off:
</p>
<ul>
  <li><b>Pure Monte Carlo (REINFORCE):</b> Wait until the end of the cut. 
    <br>• <b>Bias: ZERO.</b> The final score is true reality.
    <br>• <b>Variance: MASSIVE.</b> Over 500 steps, tiny contact vibrations make the final score swing wildly between $+50$ and $-30$.
  </li>
  <li><b>Pure 1-Step TD (Critic only):</b> Use only 1 step of reality + Critic's prediction.
    <br>• <b>Variance: MINIMAL.</b> You only look 1 step into the future, so random noise cannot accumulate.
    <br>• <b>Bias: HIGH.</b> Early in training, the Critic's neural network outputs nonsense guesses. If the Critic is wrong, the Actor learns bad habits.
  </li>
</ul>

<!-- DIAGRAM 2: BIAS-VARIANCE SPECTRUM -->
<div class="diagram-container">
<svg width="600" height="85" viewBox="0 0 600 85">
  <line x1="50" y1="40" x2="550" y2="40" stroke="#94a3b8" stroke-width="4" stroke-linecap="round"/>

  <circle cx="80" cy="40" r="10" fill="#3b82f6"/>
  <text x="80" y="22" font-size="8.5" font-weight="700" fill="#1d4ed8" text-anchor="middle">TD(0) [$\lambda = 0$]</text>
  <text x="80" y="62" font-size="7.5" fill="#475569" text-anchor="middle">Low Variance</text>
  <text x="80" y="74" font-size="7.5" font-weight="700" fill="#b91c1c" text-anchor="middle">HIGH BIAS</text>

  <circle cx="450" cy="40" r="12" fill="#10b981"/>
  <text x="450" y="20" font-size="9" font-weight="700" fill="#047857" text-anchor="middle">GAE [$\lambda = 0.95$] SWEET SPOT</text>
  <text x="450" y="62" font-size="7.5" font-weight="700" fill="#047857" text-anchor="middle">Optimal Variance-Bias Balance</text>

  <circle cx="520" cy="40" r="10" fill="#f59e0b"/>
  <text x="520" y="22" font-size="8.5" font-weight="700" fill="#b45309" text-anchor="middle">Monte Carlo [$\lambda = 1$]</text>
  <text x="520" y="62" font-size="7.5" fill="#475569" text-anchor="middle">Zero Bias</text>
  <text x="520" y="74" font-size="7.5" font-weight="700" fill="#b91c1c" text-anchor="middle">HIGH VARIANCE</text>
</svg>
</div>

<!-- SECTION 5: GAE-LAMBDA -->
<h2>5. Generalized Advantage Estimation (GAE-$\lambda$): The Blending Slider</h2>
<p>
  John Schulman et al. (2015) invented <b>GAE</b> to smoothly interpolate between TD(0) and Monte Carlo using a single tuning parameter <b>$\lambda \in [0, 1]$</b>:
</p>
<div class="formula">
  $$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}$$
</div>

<!-- PARAMETER ANATOMY TABLE 2 -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Parameter</th>
      <th style="width: 25%;">Formal Name</th>
      <th style="width: 35%;">Plain English Meaning</th>
      <th style="width: 25%;">Recommended Setting</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\lambda$</b></td>
      <td>GAE Decay Parameter</td>
      <td><b>The Trust Slider:</b> How much do you trust multi-step rollouts versus the Critic?</td>
      <td><b>$\lambda = 0.95$</b> (Standard across all robotics)</td>
    </tr>
    <tr>
      <td><b>$(\gamma \lambda)^l$</b></td>
      <td>Exponential Weighting</td>
      <td>Future TD errors $\delta_{t+l}$ are discounted exponentially so distant errors matter less.</td>
      <td>For $l=1$: $0.99 \times 0.95 = 0.9405$</td>
    </tr>
    <tr>
      <td><b>$\delta_{t+l}$</b></td>
      <td>Future TD Residuals</td>
      <td>The surprise factors encountered at future steps $t+1, t+2, \dots$.</td>
      <td>Calculated backward in time!</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of GAE</div>
  <p>
    <b>"GAE calculates your advantage by summing up the surprise factor today ($\delta_t$), plus 95% of tomorrow's surprise ($\delta_{t+1}$), plus 90% of the day after ($\delta_{t+2}$)... It blends long-term reality with short-term stability!"</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 6: PRIVILEGED ASYMMETRIC ACTOR-CRITIC -->
<h2>6. Privileged Simulation: The Asymmetric Actor-Critic Superpower</h2>
<p>
  One of the greatest breakthroughs in modern robot learning (used by Boston Dynamics, ETH Zurich, and our lab) is <b>Asymmetric Actor-Critic</b>:
</p>

<div class="callout robotics">
  <div class="callout-title">🤖 The Open-Book Exam Analogy</div>
  <p>
    When a student takes an exam, they must do it closed-book. 
    However, when the <b>professor grades the exam</b>, the professor has the complete teacher's answer key!
    <br><br>
    <b>In NVIDIA Isaac Sim:</b>
    <br>• <b>The Critic ($V_\phi$):</b> Trains with privileged, ground-truth physics information that is impossible to measure on a real robot: the exact internal pulp deformation mesh, true fruit center of mass, unobservable friction coefficients, and blade-skin contact stress.
    <br>• <b>The Actor ($\pi_\theta$):</b> Only receives sensor readings available on the physical robot: joint angles, 6-axis F/T load cell, and acoustic bursts.
    <br><br>
    Because the Critic is discarded after training, the Actor deploys to physical Franka robot arms with <b>zero sim-to-real transfer penalty</b>!
  </p>
</div>

<!-- SECTION 7: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>7. Concrete Numerical Walkthrough: Calculating GAE by Hand</h2>
<p>
  Let's calculate GAE for a 3-step sequence with <b>$\gamma = 0.99$</b> and <b>$\lambda = 0.95$</b> ($\gamma \lambda = \mathbf{0.9405}$):
</p>

<table>
  <thead>
    <tr>
      <th style="width: 10%;">Step $t$</th>
      <th style="width: 15%;">Reward $r_t$</th>
      <th style="width: 18%;">Critic $V(s_t)$</th>
      <th style="width: 27%;">TD Error $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$</th>
      <th style="width: 30%;">GAE Advantage $\hat{A}_t$</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$t=2$</b></td>
      <td>$r_2 = +5.0$</td>
      <td>$V(s_2) = 15.0$<br>$V(s_3) = 16.0$</td>
      <td>$\delta_2 = 5.0 + 0.99(16.0) - 15.0 = \mathbf{+5.84}$</td>
      <td>$\hat{A}_2 = \delta_2 = \mathbf{+5.84}$</td>
    </tr>
    <tr>
      <td><b>$t=1$</b></td>
      <td>$r_1 = +2.0$</td>
      <td>$V(s_1) = 12.0$<br>$V(s_2) = 15.0$</td>
      <td>$\delta_1 = 2.0 + 0.99(15.0) - 12.0 = \mathbf{+4.85}$</td>
      <td>$\hat{A}_1 = \delta_1 + (\gamma \lambda) \hat{A}_2 = 4.85 + 0.9405(5.84) = \mathbf{+10.34}$</td>
    </tr>
    <tr>
      <td><b>$t=0$</b></td>
      <td>$r_0 = +1.0$</td>
      <td>$V(s_0) = 10.0$<br>$V(s_1) = 12.0$</td>
      <td>$\delta_0 = 1.0 + 0.99(12.0) - 10.0 = \mathbf{+2.88}$</td>
      <td>$\hat{A}_0 = \delta_0 + (\gamma \lambda) \hat{A}_1 = 2.88 + 0.9405(10.34) = \mathbf{+12.60}$</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- SECTION 8: DIARY OF AN ACTOR-CRITIC TRAINING RUN -->
<h2>8. "Diary of a Training Run" (TensorBoard Diagnostics)</h2>
<table>
  <thead>
    <tr>
      <th style="width: 20%;">Diagnostic Metric</th>
      <th style="width: 35%;">Healthy Value Behavior</th>
      <th style="width: 45%;">What a Warning Sign Means</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Explained Variance</b></td>
      <td>Starts at $0.0$, steadily climbs to $0.80 - 0.95$.</td>
      <td>If negative ($<0.0$), the Critic is predicting <i>worse</i> than random chance. Increase Critic learning rate!</td>
    </tr>
    <tr>
      <td><b>Critic Value Loss</b></td>
      <td>Decreases steadily, stabilizes near residual task noise.</td>
      <td>If exploding toward $10^6$, check for unmasked terminal states or missing target network detach!</td>
    </tr>
    <tr>
      <td><b>Mean Advantage</b></td>
      <td>Strictly centered around $0.0 \pm 0.05$.</td>
      <td>If mean advantage drifts to $+10.0$, advantage normalization was omitted.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 9: PYTORCH IMPLEMENTATION -->
<h2>9. Vectorized GAE Implementation in PyTorch</h2>

<div class="callout code-box">
  <div class="callout-title">🐍 Vectorized PyTorch GAE Function (`gae.py`)</div>
<pre style="margin: 0; padding: 0;">
import torch

def compute_gae(rewards, values, next_values, dones, gamma=0.99, gae_lambda=0.95):
    # rewards, values, next_values, dones: Tensors of shape (T, B)
    T, B = rewards.shape
    advantages = torch.zeros_like(rewards)
    last_gae = torch.zeros(B, device=rewards.device)

    # Backward temporal recursion from T-1 down to 0
    for t in reversed(range(T)):
        non_terminal = 1.0 - dones[t].float()
        # 1-Step TD error: delta = r + gamma * V(s') * (1-done) - V(s)
        delta = rewards[t] + gamma * next_values[t] * non_terminal - values[t]
        # Recursive exponential accumulation
        last_gae = delta + gamma * gae_lambda * non_terminal * last_gae
        advantages[t] = last_gae

    # Target returns for Critic MSE training: Returns = Advantages + Values
    returns = advantages + values
    return advantages, returns
</pre>
</div>

<div class="page-break"></div>

<!-- SECTION 10: PRACTITIONER'S CHECKLIST -->
<h2>10. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Failure Mode</th>
      <th style="width: 35%;">The Hidden Symptom</th>
      <th style="width: 40%;">How to Fix It Immediately</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Learning Rate Mismatch</b></td>
      <td>Critic cannot track policy shifts fast enough. Advantage estimates lag reality.</td>
      <td>Train the Critic with <b>$\alpha_c = 1\times 10^{-3}$</b> while Actor uses $\alpha_a = 3\times 10^{-4}$.</td>
    </tr>
    <tr>
      <td><b>2. Forgetting Advantage Normalization</b></td>
      <td>Un-normalized advantages cause gradient norms to swing between $0.1$ and $1000$.</td>
      <td>Always normalize across batch: <code>adv = (adv - adv.mean()) / (adv.std() + 1e-8)</code>.</td>
    </tr>
    <tr>
      <td><b>3. Episode Boundary Bleed</b></td>
      <td>Failing to zero out <code>last_gae</code> at resets allows rewards from a finished tomato to bleed into a new tomato.</td>
      <td>Always multiply <code>last_gae</code> by <code>(1.0 - done.float())</code>.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>CS285 Lecture 6 Zero-to-Hero Guide • DEX-ROB Lab (Tianjin University) • Prof. Shan An</i>
</div>

</body>
</html>
"""

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Lecture6_Beginner_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture6_Beginner_Guide.pdf"

render_utils.build_pdf(html_content, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
