import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Actor-Critic & GAE: Definitive Guide to CS285 Lecture 6</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
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
    line-height: 1.56;
    font-size: 9.8pt;
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
    font-size: 20pt;
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
    margin-top: 20px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    page-break-after: avoid;
  }

  h3 {
    color: #0f172a;
    font-size: 10.5pt;
    font-weight: 700;
    margin-top: 14px;
    margin-bottom: 5px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 8px 0;
    text-align: justify;
  }

  .callout {
    padding: 10px 14px;
    margin: 10px 0;
    border-radius: 6px;
    font-size: 9.3pt;
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

  .silent-bug {
    background: #fdf2f8;
    border-left: 4px solid #db2777;
    color: #831843;
  }
  .silent-bug .callout-title { color: #be185d; }

  .code-container {
    background: #0f172a;
    color: #e2e8f0;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0;
    font-family: "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace;
    font-size: 8.4pt;
    line-height: 1.45;
    page-break-inside: avoid;
    overflow-x: auto;
  }
  .code-container pre { margin: 0; }
  .code-comment { color: #94a3b8; font-style: italic; }
  .code-keyword { color: #38bdf8; font-weight: bold; }
  .code-func { color: #a78bfa; }
  .code-string { color: #4ade80; }

  .algorithm-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #475569;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
    page-break-inside: avoid;
  }
  .algorithm-header {
    font-weight: 800;
    font-size: 9.5pt;
    color: #0f172a;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 6px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .formula {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 10px 0;
    text-align: center;
    font-size: 10.5pt;
    color: #0f172a;
    page-break-inside: avoid;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 8.8pt;
    page-break-inside: avoid;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 7px 9px;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 6px 9px;
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
    padding: 10px 14px;
    margin: 12px 0;
    page-break-inside: avoid;
  }
  .quiz-q { font-weight: 700; color: #0f172a; margin-bottom: 5px; }
  .quiz-a { color: #334155; font-size: 9pt; margin-top: 4px; border-top: 1px dashed #cbd5e1; padding-top: 4px; }

  .page-break { page-break-before: always; }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 6 Masterclass Study Guide</span>
  <h1>Mastering Actor-Critic Architectures &amp; GAE</h1>
  <div class="subtitle">Complete Mathematical &amp; Algorithmic Foundations: Policy Evaluation, Temporal Difference Bootstrapping, Generalized Advantage Estimation Telescoping Derivation, Squashed Continuous Control, Asymmetric Actor-Critic, and PyTorch Vectorized Implementations</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Curriculum:</b> Berkeley CS285 + Schulman et al. (GAE) + Achiam (Spinning Up)</span>
    <span><b>Scope:</b> General Continuous Actor-Critic Theory &amp; Robotics Slicing</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The Executive Mental Map: Why Does Lecture 6 Exist?</h2>
<p>
  In Lecture 5, we saw that subtracting a state-dependent baseline $b(s_t) = V(s_t)$ reduces policy gradient variance without introducing bias. However, in standard REINFORCE with a baseline, we still compute advantage using <b>full Monte Carlo rollouts</b> to the end of the episode:
  $$\hat{A}_t = \sum_{t'=t}^T \gamma^{t'-t} r_{t'} - V_\phi(s_t)$$
</p>
<p>
  <b>The Critical Vulnerability:</b> In long-horizon continuous robotics tasks (such as delicate surgical dissection or contact manipulation), relying on full episode rollouts means a single unpredictable disturbance at step $t=195$ corrupts the learning signal for all preceding 194 steps.
</p>
<p>
  <b>Lecture 6 introduces the Actor-Critic paradigm:</b> Instead of waiting for the future to happen, the agent trains a dedicated <b>Critic neural network</b> to predict the future via <b>bootstrapping and Temporal Difference (TD) learning</b>. The <b>Actor</b> can then update policy parameters at every single time-step, eliminating Monte Carlo variance.
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 6 -->
<div class="diagram-container">
<svg width="690" height="90" viewBox="0 0 690 90">
  <rect x="5" y="10" width="128" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="69" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. Actor-Critic</text>
  <text x="69" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Actor (Student) +</text>
  <text x="69" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Critic (Coach)</text>

  <rect x="141" y="10" width="128" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="205" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">2. TD Bootstrapping</text>
  <text x="205" y="52" font-size="8.2" fill="#475569" text-anchor="middle">1-Step Error δ_t</text>
  <text x="205" y="66" font-size="8.2" fill="#475569" text-anchor="middle">r + γ V(s') - V(s)</text>

  <rect x="277" y="10" width="128" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="341" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">3. Bias-Variance</text>
  <text x="341" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Monte Carlo (Noise) vs</text>
  <text x="341" y="66" font-size="8.2" fill="#475569" text-anchor="middle">1-Step TD (Bias)</text>

  <rect x="413" y="10" width="128" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="477" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">4. GAE-λ Telescoping</text>
  <text x="477" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Exponential Horizon</text>
  <text x="477" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Optimal λ = 0.95</text>

  <rect x="549" y="10" width="136" height="70" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>
  <text x="617" y="36" font-size="9" font-weight="700" fill="#334155" text-anchor="middle">5. Asymmetric AC</text>
  <text x="617" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Privileged Critic Training</text>
  <text x="617" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Deployable Real Actor</text>
</svg>
</div>

<div class="page-break"></div>

<!-- PART 1 -->
<h2>Part 1: The Core Architecture — Actor (Student) &amp; Critic (Coach)</h2>
<p>
  <b>(Slides 1–15)</b> An Actor-Critic algorithm decouples the decision-making policy from the value prediction network into two specialized systems operating in closed-loop synergy:
</p>

<!-- SVG Diagram: Detailed Actor Critic Architecture -->
<div class="diagram-container">
<svg width="680" height="190" viewBox="0 0 680 190">
  <rect x="250" y="10" width="180" height="32" rx="5" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>
  <text x="340" y="31" font-size="10" font-weight="700" fill="#1e293b" text-anchor="middle">State s_t (Sensor Observation)</text>

  <line x1="280" y1="42" x2="160" y2="70" stroke="#3b82f6" stroke-width="2"/>
  <rect x="70" y="70" width="180" height="60" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="160" y="92" font-size="10.5" font-weight="800" fill="#1e40af" text-anchor="middle">ACTOR π_θ(a|s)</text>
  <text x="160" y="108" font-size="8.2" fill="#3b82f6" text-anchor="middle">"The Student / Executer"</text>
  <text x="160" y="120" font-size="8.2" fill="#475569" text-anchor="middle">Outputs Continuous Action a_t</text>

  <line x1="400" y1="42" x2="520" y2="70" stroke="#10b981" stroke-width="2"/>
  <rect x="430" y="70" width="180" height="60" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="520" y="92" font-size="10.5" font-weight="800" fill="#065f46" text-anchor="middle">CRITIC V_ϕ(s)</text>
  <text x="520" y="108" font-size="8.2" fill="#047857" text-anchor="middle">"The Coach / Evaluator"</text>
  <text x="520" y="120" font-size="8.2" fill="#475569" text-anchor="middle">Predicts Expected Value V_ϕ(s_t)</text>

  <rect x="230" y="145" width="220" height="35" rx="5" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="340" y="162" font-size="9.5" font-weight="700" fill="#92400e" text-anchor="middle">Advantage TD Evaluation</text>
  <text x="340" y="174" font-size="8" fill="#b45309" text-anchor="middle">δ_t = r_t + γ V_ϕ(s_{t+1}) - V_ϕ(s_t)</text>

  <line x1="160" y1="130" x2="230" y2="155" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3"/>
  <line x1="520" y1="130" x2="450" y2="155" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3"/>
</svg>
</div>

<h3>1.1 Mathematical Definitions of the Value Triad</h3>
<table>
  <thead>
    <tr>
      <th style="width: 22%;">Function</th>
      <th style="width: 32%;">Mathematical Formula</th>
      <th style="width: 46%;">Physical Role in Robotic Manipulation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>State Value $V^\pi(s)$</b></td>
      <td>$$\mathbb{E}_{\tau \sim \pi} \left[ \sum_{t=0}^\infty \gamma^t r_t \;\middle|\; s_0 = s \right]$$</td>
      <td>Evaluates state promise: <i>"Blade is aligned with zero shear strain; expected cumulative return is $+65$."</i></td>
    </tr>
    <tr>
      <td><b>Action Value $Q^\pi(s, a)$</b></td>
      <td>$$\mathbb{E}_{\tau \sim \pi} \left[ \sum_{t=0}^\infty \gamma^t r_t \;\middle|\; s_0 = s, a_0 = a \right]$$</td>
      <td>Evaluates action consequence: <i>"Taking downward feed velocity $v_z = 2\text{ mm/s}$ right now yields $+80$."</i></td>
    </tr>
    <tr>
      <td><b>Advantage Function $A^\pi(s, a)$</b></td>
      <td>$$A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$$</td>
      <td>Relative superiority of action: $A = 80 - 65 = \mathbf{+15}$. The action was substantially better than average!</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: Value Function Fitting &amp; Temporal Difference Bootstrapping</h2>
<p>
  <b>(Slides 16–35)</b> How does the Critic learn to predict $V(s)$ accurately?
</p>

<h3>2.1 Monte Carlo vs. Temporal Difference (TD) Targets</h3>
<ol>
  <li>
    <b>Monte Carlo Target:</b> Wait for full episode completion to observe true total return $y_t^{\text{MC}} = \sum_{t'=t}^T \gamma^{t'-t} r_{t'}$.
    $$\mathcal{L}_{\text{Critic}}(\phi) = \frac{1}{2} \mathbb{E} \left[ \big( V_\phi(s_t) - y_t^{\text{MC}} \big)^2 \right]$$
    <i>Tradeoff:</i> Strictly unbiased, but massive variance because $y_t^{\text{MC}}$ sums hundreds of random future state transitions.
  </li>
  <li>
    <b>1-Step Temporal Difference (TD) Bootstrapping Target:</b> Step forward just <b>1 single time-step</b>, observe immediate reward $r_t$, and bootstrap from the Critic's own prediction at the next state $s_{t+1}$:
    $$y_t^{\text{TD}} = r_t + \gamma V_\phi(s_{t+1})$$
    $$\mathcal{L}_{\text{Critic}}(\phi) = \frac{1}{2} \mathbb{E} \left[ \big( V_\phi(s_t) - [r_t + \gamma V_\phi(s_{t+1})] \big)^2 \right]$$
    <i>Tradeoff:</i> Near-zero variance, but biased early in training when $V_\phi$ is poorly fitted.
  </li>
</ol>

<h3>2.2 The 1-Step TD Error ($\delta_t^V$) as an Advantage Estimator</h3>
<div class="formula" style="border: 2px solid #3b82f6; background: #eff6ff;">
  $$\delta_t^V = r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t)$$
</div>
<p>
  Notice that $\delta_t^V$ is an unbiased 1-step sample estimator of the true Advantage function:
  $$\mathbb{E}[\delta_t^V \mid s_t, a_t] = \mathbb{E}[r_t + \gamma V(s_{t+1}) \mid s_t, a_t] - V(s_t) = Q(s_t, a_t) - V(s_t) = A(s_t, a_t)$$
</p>

<div class="callout silent-bug">
  <div class="callout-title">The Semi-Gradient Detach Trap</div>
  <p>
    In TD learning, the target $y = r + \gamma V_\phi(s_{t+1})$ is treated as a <b>fixed regression target</b> derived from the Bellman operator. 
    In PyTorch, you must write:
    <br><code>target = (reward + gamma * critic(next_state).detach())</code><br>
    If you omit `.detach()`, PyTorch computes gradients through both $V(s_t)$ and $V(s_{t+1})$, transforming TD regression into a broken optimization problem where the network chases its own tail, resulting in eigenvalue explosion and divergence.
  </p>
</div>

<div class="page-break"></div>

<!-- PART 3 -->
<h2>Part 3: The Bias-Variance Dilemma &amp; N-Step Returns</h2>
<p>
  <b>(Slides 36–48)</b> Neither pure Monte Carlo nor 1-step TD is fully satisfactory across all robotics tasks:
</p>
<ul>
  <li><b>Monte Carlo ($\infty$-step):</b> Zero bias, but extreme variance. Soft tissue contact noise compounds endlessly across hundreds of steps.</li>
  <li><b>1-Step TD:</b> Minimal variance, but biased if the Critic's prediction is imperfect early in training.</li>
  <li><b>N-Step Return:</b> Looks $n$ steps ahead before bootstrapping:
    <div class="formula">$$G_t^{(n)} = \sum_{k=0}^{n-1} \gamma^k r_{t+k} + \gamma^n V(s_{t+n})$$</div>
  </li>
</ul>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 4 -->
<h2>Part 4: Generalized Advantage Estimation (GAE-$\lambda$)</h2>
<p>
  <b>(Slides 49–65)</b> In their landmark paper <i>High-Dimensional Continuous Control Using Generalized Advantage Estimation</i>, John Schulman, Sergey Levine et al. (2016) proposed a mathematically unified method that smoothly interpolates between 1-step TD and full Monte Carlo.
</p>

<h3>4.1 Mathematical Derivation of the Telescoping GAE Sum</h3>
<p>
  Define the $k$-step advantage estimator $\hat{A}_t^{(k)}$:
</p>
<div class="formula">
  $$\hat{A}_t^{(1)} = \delta_t^V = r_t + \gamma V(s_{t+1}) - V(s_t)$$
  $$\hat{A}_t^{(2)} = \delta_t^V + \gamma \delta_{t+1}^V = r_t + \gamma r_{t+1} + \gamma^2 V(s_{t+2}) - V(s_t)$$
  $$\hat{A}_t^{(k)} = \sum_{l=0}^{k-1} \gamma^l \delta_{t+l}^V = \sum_{l=0}^{k-1} \gamma^l r_{t+l} + \gamma^k V(s_{t+k}) - V(s_t)$$
</div>

<p>
  Notice how all intermediate value predictions telescope and cancel out identically!
  Schulman et al. define the **Generalized Advantage Estimator** as the exponentially weighted average of all $k$-step estimators, parameterized by $\lambda \in [0, 1]$:
</p>

<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>The GAE Telescoping Identity:</b><br>
  $$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = (1 - \lambda) \sum_{k=1}^\infty \lambda^{k-1} \hat{A}_t^{(k)} = \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}^V$$
</div>

<!-- SVG Diagram: Exponential Falloff of GAE -->
<div class="diagram-container">
<svg width="680" height="120" viewBox="0 0 680 120">
  <line x1="40" y1="90" x2="640" y2="90" stroke="#94a3b8" stroke-width="2"/>
  
  <rect x="60" y="20" width="70" height="70" fill="#3b82f6"/>
  <text x="95" y="50" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle">δ_t</text>
  <text x="95" y="68" font-size="8" fill="#ffffff" text-anchor="middle">Weight: 1.0</text>
  <text x="95" y="105" font-size="8" fill="#475569" text-anchor="middle">t (Now)</text>

  <rect x="170" y="35" width="70" height="55" fill="#60a5fa"/>
  <text x="205" y="58" font-size="10" font-weight="700" fill="#ffffff" text-anchor="middle">δ_t+1</text>
  <text x="205" y="74" font-size="8" fill="#ffffff" text-anchor="middle">Weight: γλ</text>
  <text x="205" y="105" font-size="8" fill="#475569" text-anchor="middle">t + 1</text>

  <rect x="280" y="50" width="70" height="40" fill="#93c5fd"/>
  <text x="315" y="68" font-size="9" font-weight="700" fill="#1e3a8a" text-anchor="middle">δ_t+2</text>
  <text x="315" y="80" font-size="7.5" fill="#1e3a8a" text-anchor="middle">(γλ)²</text>
  <text x="315" y="105" font-size="8" fill="#475569" text-anchor="middle">t + 2</text>

  <rect x="390" y="65" width="70" height="25" fill="#bfdbfe"/>
  <text x="425" y="80" font-size="8" font-weight="700" fill="#1e3a8a" text-anchor="middle">δ_t+3</text>
  <text x="425" y="105" font-size="8" fill="#475569" text-anchor="middle">t + 3</text>

  <text x="540" y="55" font-size="10.5" font-weight="700" fill="#2563eb" text-anchor="middle">Exponential Falloff (γλ)^l</text>
  <text x="540" y="72" font-size="8.5" fill="#64748b" text-anchor="middle">Dampens long-term noise</text>
</svg>
</div>

<h3>4.2 Geometric Decay and the $\lambda$ Tuning Spectrum</h3>
<ul>
  <li><b>$\lambda = 0$:</b> $\hat{A}_t^{\text{GAE}} = \delta_t^V$. Strictly 1-step TD. Lowest variance, highest bias.</li>
  <li><b>$\lambda = 1$:</b> $\hat{A}_t^{\text{GAE}} = \sum_{l=0}^\infty \gamma^l \delta_{t+l}^V = \sum_{l=0}^\infty \gamma^l r_{t+l} - V(s_t)$. Full Monte Carlo return minus baseline. Zero bias, highest variance.</li>
  <li><b>The Universal Gold Standard: $\lambda = 0.95, \gamma = 0.99$.</b> Setting $\lambda = 0.95$ provides the optimal bias-variance Pareto frontier for robotics, allowing credit assignment over roughly $1 / (1 - \lambda) \approx 20$ to $40$ steps while dampening distant contact noise.</li>
</ul>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Continuous Control &amp; Squashed Gaussian Policies</h2>
<p>
  <b>(Slides 66–78 &amp; Spinning Up ch19)</b> In continuous robotics, actions are physically bounded (e.g., motor velocities cannot exceed physical limits). How do we bound continuous Gaussian policies?
</p>

<h3>5.1 The Tanh Squashing Transformation &amp; Jacobian Correction</h3>
<p>
  Instead of clipping actions (which destroys gradients outside the boundary), we apply a smooth hyperbolic tangent squashing function:
  $a = \tanh(u)$, where $u \sim \mathcal{N}(\mu_\theta(s), \sigma_\theta(s))$.
  Because $\tanh$ is a non-linear change of variables, the probability density transforms according to the Jacobian determinant:
</p>

<div class="formula">
  $$P(a \mid s) = P(u \mid s) \cdot \left| \det \left( \frac{da}{du} \right) \right|^{-1}$$
</div>
<p>
  Taking the logarithm:
</p>
<div class="formula" style="border: 2px solid #c084fc; background: #fdf4ff;">
  $$\log \pi(a \mid s) = \log \mu(u \mid s) - \sum_{i=1}^d \log \big( 1 - \tanh^2(u_i) + \epsilon \big)$$
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 6 -->
<h2>Part 6: Asymmetric Actor-Critic for Modern Robotics</h2>
<div class="robotics">
  <div class="callout-title">The Asymmetric Information Principle (Isaac Gym / Isaac Lab)</div>
  <p>
    During deployment on a physical robot, the Actor policy must act solely on realistic, noisy sensor inputs: joint encoders, tactile pressure arrays, and camera RGB-D images ($o_t \in \Omega$).<br><br>
    However, <b>during simulation training, the Critic is never deployed on the physical robot!</b> The Critic is purely an offline coach used to evaluate states. Therefore, we can feed the Critic <b>privileged ground-truth simulator states</b> $s_t$: exact tissue friction coefficients, internal stress tensor fields, cutting board reaction torques, and true blade penetration depth!
    <br><br>
    <b>The Benefit:</b> The Critic learns a near-perfect value landscape without sensory ambiguity, providing ultra-clean advantage signals that guide the sensory-restricted Actor to master delicate cutting!
  </p>
</div>

<div class="page-break"></div>

<!-- PART 7 -->
<h2>Part 7: Formal Algorithm Specification &amp; PyTorch Implementation</h2>

<div class="algorithm-box">
  <div class="algorithm-header">Algorithm 2: Synchronous Advantage Actor-Critic (A2C) with GAE</div>
  <p><b>Initialize:</b> Policy parameters $\theta$, Critic parameters $\phi$, hyperparams $\gamma = 0.99, \lambda = 0.95, c_1 = 0.5, c_2 = 0.01$.</p>
  <ol>
    <li><b>for</b> iteration $k = 1, 2, \dots$ <b>do</b></li>
    <li>&nbsp;&nbsp;Collect $T$ transitions across $M$ parallel GPU environments using current policy $\pi_\theta$.</li>
    <li>&nbsp;&nbsp;Evaluate Critic values $V_\phi(s_t)$ and terminal bootstrap value $V_\phi(s_{T+1})$.</li>
    <li>&nbsp;&nbsp;Compute 1-step TD errors: $\delta_t^V = r_t + \gamma (1 - d_t) V_\phi(s_{t+1}) - V_\phi(s_t)$.</li>
    <li>&nbsp;&nbsp;Compute GAE advantages recursively backwards from $t = T$ down to $1$:
      $$\hat{A}_t = \delta_t^V + \gamma \lambda (1 - d_t) \hat{A}_{t+1}$$
    </li>
    <li>&nbsp;&nbsp;Compute value targets: $\hat{R}_t = \hat{A}_t + V_\phi(s_t)$.</li>
    <li>&nbsp;&nbsp;Normalize advantages across batch: $\hat{A} \leftarrow \frac{\hat{A} - \operatorname{mean}(\hat{A})}{\operatorname{std}(\hat{A}) + 10^{-8}}$.</li>
    <li>&nbsp;&nbsp;Compute composite loss:
      $$\mathcal{L}(\theta, \phi) = -\frac{1}{M \cdot T} \sum \left[ \log \pi_\theta(a_t \mid s_t) \hat{A}_t - c_1 (V_\phi(s_t) - \hat{R}_t)^2 + c_2 \mathcal{H}(\pi_\theta(\cdot \mid s_t)) \right]$$
    </li>
    <li>&nbsp;&nbsp;Update $(\theta, \phi)$ via Adam optimizer.</li>
    <li><b>end for</b></li>
  </ol>
</div>

<h3>7.1 Production Vectorized PyTorch GAE Computation</h3>
<div class="code-container">
<pre><span class="code-keyword">import</span> torch

<span class="code-keyword">def</span> <span class="code-func">compute_gae_vectorized</span>(rewards, values, next_values, dones, gamma=0.99, lam=0.95):
    <span class="code-comment"># rewards, values, next_values, dones: Shape [T, N]</span>
    T = rewards.size(0)
    advantages = torch.zeros_like(rewards)
    last_gae = 0.0
    
    <span class="code-keyword">for</span> t <span class="code-keyword">in</span> <span class="code-func">reversed</span>(<span class="code-func">range</span>(T)):
        non_terminal = 1.0 - dones[t]
        delta = rewards[t] + gamma * next_values[t] * non_terminal - values[t]
        advantages[t] = last_gae = delta + gamma * lam * non_terminal * last_gae
        
    returns = advantages + values
    <span class="code-comment"># Normalize advantage across batch</span>
    norm_adv = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
    <span class="code-keyword">return</span> norm_adv, returns
</pre>
</div>

<div class="page-break"></div>

<!-- PART 8 -->
<h2>Part 8: Interactive Tablet Self-Test Quiz</h2>

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

<!-- PART 9: THESIS DEFENSE MASTER CHEATSHEET -->
<h2>Part 9: Thesis Defense Master Cheatsheet (Lecture 6 Focus)</h2>

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

</body>
</html>
"""

if __name__ == "__main__":
    pdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture6_Beginner_Guide.pdf"
    backup_path = "/home/omen/Downloads/CS285_Lecture6_Beginner_Guide.pdf"
    render_utils.build_pdf(html_content, pdf_path, backup_path)
