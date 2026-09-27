import os
import weasyprint
import shutil

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Actor-Critic & Generalized Advantage Estimation: Beginner's Guide to CS285 Lecture 6</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {
      content: "CS285 Lecture 6: Actor-Critic Architectures & GAE";
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

  .code-block {
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 14px;
    border-radius: 6px;
    font-family: Consolas, Monaco, "Courier New", monospace;
    font-size: 8.6pt;
    line-height: 1.45;
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
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 6 Enhanced Study Guide</span>
  <h1>Mastering Actor-Critic &amp; GAE</h1>
  <div class="subtitle">Complete Beginner-Friendly Breakdown: Value Bootstrapping, Temporal Difference Errors, GAE Telescoping Derivation, Squashed Gaussians &amp; Compliant Slicing</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Companion:</b> DEX-ROB Lab, Tianjin University</span>
    <span><b>Frameworks:</b> Achiam (Spinning Up) + Schulman &amp; Levine GAE</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The "Mental Map": Why Does Lecture 6 Exist?</h2>
<p>
  In Lecture 5, we discovered the Policy Gradient Theorem and learned that we can reduce variance by subtracting a baseline $b(s) = V(s)$. However, in REINFORCE, we still had to wait until the robot completed an entire 200-step cutting trajectory to calculate empirical reward-to-go $\hat{Q}_{i,t} = \sum_{t'=t}^T r_{t'}$.
</p>
<p>
  In continuous physical robotics, relying on full trajectory rollouts is dangerous: a single unexpected contact slip or numerical perturbation at step 195 corrupts the return for all previous 194 steps.
</p>
<p>
  <b>Lecture 6 solves this by introducing Actor-Critic architectures.</b> Instead of waiting for the future to happen, the robot trains a second neural network—<b>the Critic</b>—to predict the future. The Actor can then update its actions at every individual time-step using <i>bootstrapping</i> and <i>Temporal Difference (TD) learning</i>.
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 6 -->
<div class="diagram-container">
<svg width="680" height="90" viewBox="0 0 680 90">
  <rect x="5" y="10" width="125" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="67" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. Actor-Critic</text>
  <text x="67" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Student (Policy) +</text>
  <text x="67" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Coach (Critic)</text>

  <rect x="140" y="10" width="125" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="202" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">2. TD Learning</text>
  <text x="202" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Bootstrapping:</text>
  <text x="202" y="66" font-size="8.5" fill="#475569" text-anchor="middle">δ_t = r + γV' - V</text>

  <rect x="275" y="10" width="125" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="337" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">3. Bias vs. Variance</text>
  <text x="337" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Monte Carlo (Noise)</text>
  <text x="337" y="66" font-size="8.5" fill="#475569" text-anchor="middle">vs. TD (Bias)</text>

  <rect x="410" y="10" width="125" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="472" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">4. GAE-λ</text>
  <text x="472" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Blending n-Steps:</text>
  <text x="472" y="66" font-size="8.5" fill="#475569" text-anchor="middle">λ = 0.95 in SkRL</text>

  <rect x="545" y="10" width="125" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="607" y="36" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">5. Squashed Gaussian</text>
  <text x="607" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Tanh Bounds &amp;</text>
  <text x="607" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Jacobian Correction</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: The Core Architecture: Actor (Student) &amp; Critic (Coach)</h2>
<p>
  <b>(Slides 1–15, Spoken Transcript 03:10–18:25)</b> An Actor-Critic algorithm divides the learning agent into two distinct neural networks that work in symbiosis:
</p>

<!-- SVG Diagram: Detailed Actor Critic Architecture -->
<div class="diagram-container">
<svg width="680" height="200" viewBox="0 0 680 200">
  <rect x="250" y="10" width="180" height="35" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>
  <text x="340" y="32" font-size="10.5" font-weight="700" fill="#1e293b" text-anchor="middle">State s_t (33-dim Vector)</text>

  <!-- Actor -->
  <line x1="280" y1="45" x2="160" y2="75" stroke="#3b82f6" stroke-width="2" marker-end="url(#arr-b)"/>
  <rect x="70" y="75" width="180" height="65" rx="8" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="160" y="98" font-size="11" font-weight="700" fill="#1e40af" text-anchor="middle">ACTOR π_θ(a|s)</text>
  <text x="160" y="115" font-size="8.5" fill="#3b82f6" text-anchor="middle">"The Student / Executer"</text>
  <text x="160" y="128" font-size="8.5" fill="#475569" text-anchor="middle">Outputs Action a_t (6-dim)</text>

  <!-- Critic -->
  <line x1="400" y1="45" x2="520" y2="75" stroke="#10b981" stroke-width="2" marker-end="url(#arr-g)"/>
  <rect x="430" y="75" width="180" height="65" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="520" y="98" font-size="11" font-weight="700" fill="#065f46" text-anchor="middle">CRITIC V_ϕ(s)</text>
  <text x="520" y="115" font-size="8.5" fill="#047857" text-anchor="middle">"The Coach / Evaluator"</text>
  <text x="520" y="128" font-size="8.5" fill="#475569" text-anchor="middle">Predicts Expected Return V_ϕ</text>

  <!-- Feedback -->
  <rect x="250" y="150" width="180" height="40" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="340" y="167" font-size="10" font-weight="700" fill="#92400e" text-anchor="middle">Advantage Evaluation</text>
  <text x="340" y="181" font-size="8.5" fill="#b45309" text-anchor="middle">δ_t = r_t + γ V_ϕ(s_t+1) - V_ϕ(s_t)</text>

  <line x1="160" y1="140" x2="250" y2="165" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3"/>
  <line x1="520" y1="140" x2="430" y2="165" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3"/>

  <defs>
    <marker id="arr-b" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#3b82f6"/>
    </marker>
    <marker id="arr-g" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981"/>
    </marker>
  </defs>
</svg>
</div>

<h3>1.1 Dissecting the 3 Core Value Notations</h3>
<table>
  <thead>
    <tr>
      <th style="width: 20%;">Function</th>
      <th style="width: 25%;">Notation &amp; Formula</th>
      <th style="width: 55%;">Physical Meaning in Tomato Slicing</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>State Value</b></td>
      <td>$V^\pi(s) = \mathbb{E}\left[\sum_{t=0}^\infty \gamma^t r_t \,\Big|\, s_0 = s\right]$</td>
      <td>How promising is the current situation? E.g., <i>"The knife is resting flush on the cuticle with zero tilt error. Expected return is $+35$."</i></td>
    </tr>
    <tr>
      <td><b>State-Action Value</b></td>
      <td>$Q^\pi(s, a) = \mathbb{E}\left[\sum_{t=0}^\infty \gamma^t r_t \,\Big|\, s_0=s, a_0=a\right]$</td>
      <td>How good is taking a specific action in this state? E.g., <i>"In this state, if I choose action $a_1$ (saw at 25 mm/s), expected return is $+42$."</i></td>
    </tr>
    <tr>
      <td><b>Advantage Function</b></td>
      <td>$A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$</td>
      <td>How much better was this action compared to the average policy action? $A = 42 - 35 = \mathbf{+7}$ (Better than expected!).</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: Value Function Fitting &amp; Temporal Difference Bootstrapping</h2>
<p>
  <b>(Slides 16–35, Spoken Transcript 18:30–36:00)</b> How does the Critic learn to predict $V(s)$?
</p>

<h3>2.1 Monte Carlo vs. Temporal Difference (TD)</h3>
<ol>
  <li>
    <b>Monte Carlo Target:</b> Run full episode until $t=T$, sum all observed rewards $y_t^{\text{MC}} = \sum_{t'=t}^T \gamma^{t'-t} r_{t'}$.
    <div class="formula">\min_\phi \frac{1}{2} \sum_t \big( V_\phi(s_t) - y_t^{\text{MC}} \big)^2</div>
    <i>Flaw:</i> Unbiased, but monstrous variance because $y_t^{\text{MC}}$ depends on hundreds of stochastic future steps.
  </li>
  <li>
    <b>Temporal Difference (TD) Bootstrapping Target:</b> Observe just <i>one</i> step: get immediate reward $r_t$ and bootstrap from $V(s_{t+1})$:
    <div class="formula">y_t^{\text{TD}} = r_t + \gamma V_\phi(s_{t+1})</div>
    The regression loss minimizes the <b>Bellman error</b>:
    <div class="formula">\min_\phi \frac{1}{2} \sum_t \big( V_\phi(s_t) - [r_t + \gamma V_\phi(s_{t+1})] \big)^2</div>
  </li>
</ol>

<h3>2.2 The Temporal Difference Error ($\delta_t$)</h3>
<div class="formula" style="border: 2px solid #3b82f6; background: #eff6ff;">
  \delta_t^V = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)
</div>
<p>
  Notice that $\delta_t^V$ is a 1-step sample estimate of the Advantage function:
  $Q(s_t, a_t) \approx r_t + \gamma V(s_{t+1}) \implies A(s_t, a_t) \approx \delta_t^V$.
</p>

<div class="callout silent-bug">
  <div class="callout-title">Spinning Up Bug Alert: Semi-Gradient Detach Trap</div>
  <p>
    Joshua Achiam warns: Bellman updates are <b>semi-gradient methods</b>. 
    When computing MSE loss for the Critic:
    <code>loss = (V(s) - (r + gamma * V(s_next).detach()))**2</code>
    If you omit <code>.detach()</code> on <code>V(s_next)</code>, PyTorch will compute gradients with respect to both terms. This is mathematically broken and leads to runaway gradient divergence.
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 3 -->
<h2>Part 3: The Bias-Variance Dilemma &amp; N-Step Returns</h2>
<p>
  <b>(Slides 36–48, Spoken Transcript 36:15–48:40)</b> Neither pure Monte Carlo nor 1-step TD is fully satisfactory:
</p>
<ul>
  <li><b>Monte Carlo ($\infty$-step):</b> Zero bias, but extreme variance. Soft tissue contact noise compounds endlessly.</li>
  <li><b>1-Step TD:</b> Minimal variance, but biased if the Critic's prediction is imperfect early in training.</li>
  <li><b>N-Step Return:</b> Looks $n$ steps ahead before bootstrapping:
    <div class="formula">G_t^{(n)} = \sum_{k=0}^{n-1} \gamma^k r_{t+k} + \gamma^n V(s_{t+n})</div>
  </li>
</ul>

<div class="page-break"></div>

<!-- PART 4 -->
<h2>Part 4: Generalized Advantage Estimation (GAE-$\lambda$)</h2>
<p>
  <b>(Slides 49–65, Spoken Transcript 48:50–1:05:20)</b> Schulman, Levine et al. (2016) proposed taking an exponentially weighted average of all $k$-step advantage estimators:
</p>

<h3>4.1 The Telescoping Sum Derivation</h3>
<p>
  Define the $k$-step advantage: $\hat{A}_t^{(k)} = \sum_{l=0}^{k-1} \gamma^l r_{t+l} + \gamma^k V(s_{t+k}) - V(s_t) = \sum_{l=0}^{k-1} \gamma^l \delta_{t+l}^V$.
  Notice how intermediate value terms telescope and cancel!
  GAE takes an exponentially weighted sum across all horizons using parameter $\lambda \in [0, 1]$:
</p>
<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>The GAE Advantage Formula:</b><br>
  \hat{A}_t^{\text{GAE}(\gamma, \lambda)} = (1 - \lambda) \sum_{k=1}^\infty \lambda^{k-1} \hat{A}_t^{(k)} = \sum_{l=0}^{\infty} (\gamma \lambda)^l \delta_{t+l}^V
</div>

<!-- SVG Diagram: Exponential Falloff of GAE -->
<div class="diagram-container">
<svg width="680" height="130" viewBox="0 0 680 130">
  <line x1="40" y1="100" x2="640" y2="100" stroke="#94a3b8" stroke-width="2"/>
  
  <rect x="60" y="20" width="70" height="80" fill="#3b82f6"/>
  <text x="95" y="55" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle">δ_t</text>
  <text x="95" y="75" font-size="8.5" fill="#ffffff" text-anchor="middle">Weight: 1.0</text>
  <text x="95" y="115" font-size="8.5" fill="#475569" text-anchor="middle">t (Now)</text>

  <rect x="170" y="40" width="70" height="60" fill="#60a5fa"/>
  <text x="205" y="65" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle">δ_t+1</text>
  <text x="205" y="80" font-size="8.5" fill="#ffffff" text-anchor="middle">Weight: γλ</text>
  <text x="205" y="115" font-size="8.5" fill="#475569" text-anchor="middle">t + 1</text>

  <rect x="280" y="60" width="70" height="40" fill="#93c5fd"/>
  <text x="315" y="80" font-size="9" font-weight="700" fill="#1e3a8a" text-anchor="middle">δ_t+2</text>
  <text x="315" y="93" font-size="7.5" fill="#1e3a8a" text-anchor="middle">(γλ)²</text>
  <text x="315" y="115" font-size="8.5" fill="#475569" text-anchor="middle">t + 2</text>

  <rect x="390" y="75" width="70" height="25" fill="#bfdbfe"/>
  <text x="425" y="91" font-size="8" font-weight="700" fill="#1e3a8a" text-anchor="middle">δ_t+3</text>
  <text x="425" y="115" font-size="8.5" fill="#475569" text-anchor="middle">t + 3</text>

  <text x="540" y="65" font-size="11" font-weight="700" fill="#2563eb" text-anchor="middle">Exponential Falloff (γλ)^l</text>
  <text x="540" y="85" font-size="9" fill="#64748b" text-anchor="middle">Prioritizes near-term TD accuracy</text>
</svg>
</div>

<h3>4.2 The Magic Parameter Tuning for Robotics</h3>
<ul>
  <li><b>$\lambda = 0$:</b> $\hat{A}_t = \delta_t^V$. Pure 1-step TD. Minimal variance, highest bias.</li>
  <li><b>$\lambda = 1$:</b> $\hat{A}_t = \sum \gamma^l r_{t+l} - V(s_t)$. Pure Monte Carlo. Zero bias, highest variance.</li>
  <li><b>The Universal Gold Standard: $\lambda = 0.95, \gamma = 0.99$.</b> In Isaac Lab and SkRL, setting $\lambda = 0.95$ provides the sweet spot: it allows the policy to look roughly 20–40 steps ahead while aggressively damping out long-term contact noise.</li>
</ul>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Continuous Control &amp; Squashed Gaussian Policies</h2>
<p>
  <b>(Slides 66–78 &amp; Spinning Up ch19)</b> In continuous robotics, actions are physically bounded (e.g., motor velocities cannot exceed physical limits). How do we bound continuous Gaussian policies?
</p>

<h3>5.1 The Tanh Squashing Transformation</h3>
<p>
  Instead of clipping actions (which destroys gradients outside the boundary), we apply a smooth hyperbolic tangent squashing function:
  $a = \tanh(u)$, where $u \sim \mathcal{N}(\mu_\theta(s), \sigma_\theta(s))$.
</p>

<h3>5.2 The Jacobian Determinant Correction</h3>
<p>
  Because $\tanh$ is a non-linear change of variables, the probability density changes! By the change of variables formula:
</p>
<div class="formula">
  P(a|s) = P(u|s) \cdot \left| \det \left( \frac{da}{du} \right) \right|^{-1}
</div>
<p>
  Taking the logarithm:
</p>
<div class="formula" style="border: 2px solid #c084fc; background: #fdf4ff;">
  \log \pi(a|s) = \log \mu(u|s) - \sum_{i=1}^d \log \big( 1 - \tanh^2(u_i) + \epsilon \big)
</div>
<p>
  Omitting this Jacobian correction term is a classic silent failure that distorts entropy calculations and policy gradient updates!
</p>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 6 -->
<h2>Part 6: Paper 1 PyTorch Implementation of GAE</h2>

<div class="code-block">
import torch

def compute_gae(rewards, values, next_values, dones, gamma=0.99, lam=0.95):
    \"\"\"
    Vectorized computation of Generalized Advantage Estimation (GAE-λ).
    rewards:     [T, num_envs]
    values:      [T, num_envs] - Critic predictions V(s_t)
    next_values: [T, num_envs] - Critic predictions V(s_{t+1})
    dones:       [T, num_envs] - Episode termination flags
    \"\"\"
    num_steps = rewards.size(0)
    advantages = torch.zeros_like(rewards)
    last_gae = 0.0

    # Iterate backwards in time (from T-1 down to 0)
    for t in reversed(range(num_steps)):
        non_terminal = 1.0 - dones[t]
        
        # 1-Step TD Error: δ_t = r_t + γ V(s_{t+1}) - V(s_t)
        delta = rewards[t] + gamma * next_values[t] * non_terminal - values[t]
        
        # Recursive GAE accumulation: A_t = δ_t + (γ λ) A_{t+1}
        advantages[t] = last_gae = delta + gamma * lam * non_terminal * last_gae

    # Target values for training the Critic: Returns = Advantage + V(s)
    returns = advantages + values
    
    # Normalize advantages across the parallel environment batch
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
    return advantages, returns
</div>

<div class="page-break"></div>

<!-- PART 7: SELF-TEST QUIZ -->
<h2>Part 7: Interactive Tablet Self-Test Quiz (Test Your Understanding)</h2>

<div class="quiz-box">
  <div class="quiz-q">Question 1: What happens to GAE when you set $\lambda = 0$, and what happens when you set $\lambda = 1$?</div>
  <div class="quiz-a">
    <b>Answer:</b> When $\lambda = 0$, GAE reduces strictly to 1-step TD error ($\delta_t = r_t + \gamma V(s') - V(s)$), giving lowest variance but highest bias. When $\lambda = 1$, GAE telescopes into the full empirical Monte Carlo return minus baseline ($\sum \gamma^l r_{t+l} - V(s)$), giving zero bias but maximum variance.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: Why must the Critic network be trained with semi-gradients (detaching the target)?</div>
  <div class="quiz-a">
    <b>Answer:</b> The Bellman target $y = r + \gamma V(s')$ is derived from dynamic programming, where $V(s')$ serves as a fixed reference value. If we backpropagate gradients into $V(s')$, the network will try to move both its current prediction and future target simultaneously, causing eigenvalues to drift and resulting in mathematical instability.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: Why does setting $\lambda = 0.95$ prevent the robot from misinterpreting a skin puncture reward?</div>
  <div class="quiz-a">
    <b>Answer:</b> Skin puncture is an abrupt transition that yields a high localized reward. Setting $\lambda = 0.95$ focuses the advantage assignment on the 20–40 steps directly surrounding the rupture event, rewarding the preparatory deceleration and sawing actions without smearing noise across the subsequent 160 steps of pulp slicing.
  </div>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 8: THESIS DEFENSE -->
<h2>Part 8: Thesis Defense Master Cheatsheet (Lecture 6 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Q1: "What is the primary advantage of Actor-Critic over pure Policy Gradients (REINFORCE)?"</div>
  <p>
    <b>Answer:</b> "REINFORCE relies on empirical Monte Carlo returns, requiring complete trajectory rollouts. This introduces immense variance, as a single disturbance late in the episode pollutes credit assignment for all earlier steps. Actor-Critic introduces a learned Critic $V_\phi(s)$ that evaluates states via 1-step Temporal Difference bootstrapping ($r + \gamma V(s')$), drastically reducing variance and enabling stable, sample-efficient learning in contact-rich tasks."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q2: "Explain the Bias-Variance tradeoff between Monte Carlo evaluation and 1-Step TD learning."</div>
  <p>
    <b>Answer:</b> "Monte Carlo evaluation has zero bias because it measures true realized rewards, but suffers from extreme variance due to compounding stochastic transitions. 1-step TD learning has minimal variance because it only looks one step ahead, but introduces bias because it relies on the Critic's own function approximation $\hat{V}(s_{t+1})$, which may be inaccurate early in training."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q3: "Why is GAE-λ universally preferred for continuous robotic manipulation like tomato slicing?"</div>
  <p>
    <b>Answer:</b> "Robotic cutting involves abrupt physical regime shifts (e.g., non-contact approach $\to$ elastic skin indentation $\to$ rupture $\to$ flesh slicing). Pure 1-step TD is too myopic to anticipate delayed fruit deformation, while pure Monte Carlo is overwhelmed by contact noise. GAE-$\lambda$ exponentially weights multi-step returns with parameter $\lambda = 0.95$, providing the optimal balance: it reacts quickly to localized rupture events while maintaining a sufficient temporal horizon to optimize smooth compliant trajectories."
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
<div style="text-align: center; font-size: 8.5pt; color: #64748b;">
  CS 285 Lecture 6 Comprehensive Study Guide • Prepared for DEX-ROB Lab, Tianjin University
</div>

</body>
</html>
"""

output_path = "/home/omen/Downloads/CS285_Lecture6_Beginner_Guide.pdf"
backup_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture6_Beginner_Guide.pdf"

print("Compiling Enhanced Lecture 6 PDF with WeasyPrint...")
html = weasyprint.HTML(string=html_content)
html.write_pdf(output_path)
print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

shutil.copyfile(output_path, backup_path)
print(f"Copied to: {backup_path}")
