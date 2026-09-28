import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Policy Gradients: Definitive Guide to CS285 Lecture 5</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 5: Policy Gradients & Variance Reduction";
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
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 5 Masterclass Study Guide</span>
  <h1>Mastering Policy Gradients &amp; Variance Reduction</h1>
  <div class="subtitle">Complete Mathematical &amp; Algorithmic Foundations: The Likelihood Ratio Trick, The Log-Derivative Identity, Causality &amp; Reward-to-Go, The EGLP Lemma, Optimal Baselines, and Production PyTorch REINFORCE</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Curriculum:</b> Berkeley CS285 + Achiam (Spinning Up) + Sutton &amp; Barto</span>
    <span><b>Scope:</b> General Continuous Policy Optimization &amp; Robotics Slicing</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The Executive Mental Map: Why Does Lecture 5 Exist?</h2>
<p>
  In supervised deep learning, optimization is straightforward: compute loss $\mathcal{L}(\theta) = \|f_\theta(x) - y\|^2$ and backpropagate gradients $\nabla_\theta \mathcal{L}$ directly through network layers.
</p>
<p>
  <b>The Central Dilemma of Robotics:</b> In physical control, between the policy's motor outputs and the scalar reward lies <b>the physical universe</b>: contact mechanics, non-linear friction, fluid dynamics, and biological tissue fracture. You cannot compute $\frac{\partial \text{Tissue Fracture}}{\partial \text{Motor Current}}$ through analytical backpropagation! The real world is non-differentiable.
</p>
<p>
  <b>Lecture 5 introduces the Policy Gradient Theorem:</b> a mathematical framework that optimizes neural network policies directly via evaluative trial-and-error, without ever needing an analytical physics model of the environment.
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 5 -->
<div class="diagram-container">
<svg width="690" height="90" viewBox="0 0 690 90">
  <rect x="5" y="10" width="128" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="69" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. Likelihood Ratio</text>
  <text x="69" y="52" font-size="8.2" fill="#475569" text-anchor="middle">The Log-Derivative Trick</text>
  <text x="69" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Physics Vanishes!</text>

  <rect x="141" y="10" width="128" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="205" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">2. Gaussian Policies</text>
  <text x="205" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Continuous Action Math</text>
  <text x="205" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Pushing the Mean</text>

  <rect x="277" y="10" width="128" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="341" y="36" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">3. The Variance Trap</text>
  <text x="341" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Lucky vs Unlucky Runs</text>
  <text x="341" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Noisy Sample Gradients</text>

  <rect x="413" y="10" width="128" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="477" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">4. Causality Proof</text>
  <text x="477" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Reward-to-Go Formulation</text>
  <text x="477" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Discarding the Past</text>

  <rect x="549" y="10" width="136" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="617" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">5. Baselines &amp; EGLP</text>
  <text x="617" y="52" font-size="8.2" fill="#475569" text-anchor="middle">EGLP Lemma Zero Bias</text>
  <text x="617" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Optimal Baseline b*</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: The Policy Gradient Theorem &amp; The Log-Derivative Trick</h2>
<p>
  <b>(Slides 1–15)</b> Let a trajectory be $\tau = (s_0, a_0, s_1, a_1, \dots, s_T)$ with cumulative return $R(\tau) = \sum_{t=0}^T r(s_t, a_t)$. The expected return objective is:
  $$J(\theta) = \mathbb{E}_{\tau \sim p_\theta(\tau)} [R(\tau)] = \int p_\theta(\tau) R(\tau) \, d\tau$$
</p>

<h3>1.1 Step-by-Step Derivation of the Policy Gradient</h3>
<p>
  We wish to compute $\nabla_\theta J(\theta)$. Differentiating directly under the integral sign:
</p>

<div class="formula">
  $$\nabla_\theta J(\theta) = \nabla_\theta \int p_\theta(\tau) R(\tau) \, d\tau = \int \nabla_\theta p_\theta(\tau) R(\tau) \, d\tau$$
</div>

<p>
  <b>The Obstacle:</b> We cannot evaluate this integral as an expectation because it is weighted by $\nabla_\theta p_\theta(\tau)$, which is <i>not</i> a valid probability distribution (it does not integrate to 1 and can be negative!).
  <br><b>The Solution (The Log-Derivative / Likelihood Ratio Identity):</b>
  Using the elementary calculus identity $\frac{d}{dx} \log f(x) = \frac{f'(x)}{f(x)} \implies f'(x) = f(x) \frac{d}{dx} \log f(x)$:
</p>

<div class="formula">
  $$\nabla_\theta p_\theta(\tau) = p_\theta(\tau) \frac{\nabla_\theta p_\theta(\tau)}{p_\theta(\tau)} = p_\theta(\tau) \nabla_\theta \log p_\theta(\tau)$$
</div>

<p>
  Substitute this back into the gradient integral:
</p>

<div class="formula">
  $$\nabla_\theta J(\theta) = \int p_\theta(\tau) \big[ \nabla_\theta \log p_\theta(\tau) \big] R(\tau) \, d\tau = \mathbb{E}_{\tau \sim p_\theta(\tau)} \Big[ \nabla_\theta \log p_\theta(\tau) \, R(\tau) \Big]$$
</div>

<h3>1.2 Why the Unknown Physics Dynamics Vanish Identically</h3>
<p>
  Recall the Markov chain expansion of trajectory probability $p_\theta(\tau)$:
  $$p_\theta(\tau) = \rho_0(s_0) \prod_{t=0}^{T-1} \pi_\theta(a_t \mid s_t) \, \mathcal{P}(s_{t+1} \mid s_t, a_t)$$
  Taking the natural logarithm:
  $$\log p_\theta(\tau) = \log \rho_0(s_0) + \sum_{t=0}^{T-1} \log \pi_\theta(a_t \mid s_t) + \sum_{t=0}^{T-1} \log \mathcal{P}(s_{t+1} \mid s_t, a_t)$$
  Now take the gradient with respect to $\theta$. Because initial state distribution $\rho_0(s_0)$ and transition physics $\mathcal{P}(s_{t+1}|s_t, a_t)$ do not depend on neural network weights $\theta$:
  $$\nabla_\theta \log \rho_0(s_0) = 0, \qquad \nabla_\theta \log \mathcal{P}(s_{t+1} \mid s_t, a_t) = 0$$
</p>

<div class="formula" style="border: 2px solid #2563eb; background: #eff6ff;">
  <b>The REINFORCE Policy Gradient Estimator (Williams, 1992):</b><br>
  $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \left( \sum_{t=0}^{T-1} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \right) \left( \sum_{t=0}^{T-1} r(s_t, a_t) \right) \right]$$
</div>

<div class="intuition">
  <div class="callout-title">The Plain-English Intuition of REINFORCE</div>
  <p>
    $\nabla_\theta \log \pi_\theta(a_t|s_t)$ represents the direction in parameter space that increases the probability of taking action $a_t$. 
    Multiplying by scalar return $R(\tau)$ scales this push:
    <ul>
      <li>If $R(\tau) > 0$, the gradient steps to make all actions taken in that trajectory <b>more likely</b>.</li>
      <li>If $R(\tau) < 0$, the gradient steps to make all actions taken in that trajectory <b>less likely</b>.</li>
    </ul>
    This is mathematically formal trial-and-error discovery without knowing the laws of physics!
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 2 -->
<h2>Part 2: Continuous Actions &amp; Gaussian Policy Gradients</h2>
<p>
  <b>(Slides 16–22)</b> In robotic systems, actions are continuous joint torques or velocities $a \in \mathbb{R}^{d_a}$. We model the policy as a Gaussian $\pi_\theta(a|s) = \mathcal{N}(\mu_\theta(s), \Sigma_\theta(s))$ with diagonal covariance $\Sigma = \operatorname{diag}(\sigma_1^2, \dots, \sigma_{d_a}^2)$.
</p>

<h3>2.1 The Analytical Score Function of a Gaussian Policy</h3>
<p>
  For a 1D continuous action with mean $\mu_\theta(s)$ and standard deviation $\sigma$:
  $$\log \pi_\theta(a \mid s) = -\frac{1}{2} \left[ \frac{(a - \mu_\theta(s))^2}{\sigma^2} + 2 \log \sigma + \log(2\pi) \right]$$
  Differentiating with respect to network parameters $\theta$:
</p>

<div class="formula">
  $$\nabla_\theta \log \pi_\theta(a \mid s) = \frac{a - \mu_\theta(s)}{\sigma^2} \, \nabla_\theta \mu_\theta(s)$$
</div>

<div class="robotics">
  <div class="callout-title">Physical Robotics Meaning: Pushing the Mean</div>
  <p>
    Notice the error term $(a - \mu_\theta(s))$:
    <ul>
      <li>Suppose the policy network intended to push the knife downward at $\mu = 10\text{ mm/s}$.</li>
      <li>Exploratory Gaussian noise sampled $a = 15\text{ mm/s}$, so $(a - \mu) = +5\text{ mm/s}$.</li>
      <li>If this action successfully initiated a clean cut through the tissue cuticle without crushing ($R(\tau) = +50$), the gradient update pushes $\mu_\theta(s)$ toward $+5\text{ mm/s}$, permanently shifting future mean knife speed higher!</li>
    </ul>
  </p>
</div>

<div class="silent-bug">
  <div class="callout-title">Spinning Up Bug Alert: Clamping Log-Std</div>
  <p>
    Joshua Achiam warns: if you let `log_std` float unconstrained, gradients will cause $\sigma \to 0$ (freezing exploration prematurely) or $\sigma \to \infty$ (causing `NaN` in division by $\sigma^2$). In production robotics code, always clamp log standard deviations: `log_std = torch.clamp(log_std, min=-20, max=2)`.
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 3 -->
<h2>Part 3: The High Variance Nightmare</h2>
<p>
  <b>(Slides 23–28)</b> While raw REINFORCE is unbiased, it is notoriously impractical in complex environments due to <b>destructive sample variance</b>.
</p>

<h3>3.1 The Credit Assignment Flaw: Lucky vs. Unlucky Trajectories</h3>
<p>
  In raw REINFORCE, the sum of all log-probabilities $\sum_{t=0}^T \nabla \log \pi(a_t|s_t)$ is multiplied by the <b>entire episode return $R(\tau)$</b>.
</p>

<!-- SVG Diagram: Trajectory Variance -->
<div class="diagram-container">
<svg width="680" height="110" viewBox="0 0 680 110">
  <rect x="20" y="10" width="310" height="90" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="175" y="32" font-size="9.5" font-weight="700" fill="#991b1b" text-anchor="middle">Trajectory 1: Unlucky Slip at t=195</text>
  <text x="175" y="50" font-size="8.2" fill="#475569" text-anchor="middle">Steps 0–190: Flawless surgical incision</text>
  <text x="175" y="64" font-size="8.2" fill="#ef4444" text-anchor="middle">Step 195: Robot slips ➔ Negative total score!</text>
  <text x="175" y="82" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">REINFORCE PENALIZES ALL 195 STEPS!</text>

  <rect x="350" y="10" width="310" height="90" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="505" y="32" font-size="9.5" font-weight="700" fill="#065f46" text-anchor="middle">Trajectory 2: Lucky Bounce at t=195</text>
  <text x="505" y="50" font-size="8.2" fill="#475569" text-anchor="middle">Steps 0–190: Erroneous, shaky control</text>
  <text x="505" y="64" font-size="8.2" fill="#047857" text-anchor="middle">Step 195: Random bounce hits target ➔ High score!</text>
  <text x="505" y="82" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">REINFORCE REWARDS ALL ERRATIC STEPS!</text>
</svg>
</div>

<p>
  Because every step is credited with the total score of the entire trajectory, millions of rollouts are needed for the noise to cancel out. We require two fundamental variance reduction techniques: <b>Causality</b> and <b>Baselines</b>.
</p>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 4 -->
<h2>Part 4: Variance Reduction I — Causality &amp; Reward-to-Go</h2>
<p>
  <b>(Slides 29–35)</b> The physical universe obeys causality: <b>an action taken at time $t$ cannot retroactively cause or influence rewards received at earlier times $t' < t$.</b>
</p>

<div class="math-box">
  <div class="callout-title">Mathematical Proof: Past Rewards Have Zero Expected Gradient</div>
  <p>
    Consider the expectation of an action gradient at time $t$ multiplied by a prior reward $r_{t'}$ where $t' < t$:
    $$\mathbb{E}_{\tau} \big[ \nabla_\theta \log \pi_\theta(a_t \mid s_t) \, r(s_{t'}, a_{t'}) \big]$$
    Using the tower property of conditional expectation:
    $$= \mathbb{E}_{s_0, a_0, \dots, s_t} \left[ r(s_{t'}, a_{t'}) \, \mathbb{E}_{a_t \sim \pi_\theta(\cdot|s_t)} \big[ \nabla_\theta \log \pi_\theta(a_t \mid s_t) \mid s_t \big] \right]$$
    Evaluating the inner expectation over $a_t$:
    $$\mathbb{E}_{a_t} [\nabla_\theta \log \pi_\theta(a_t \mid s_t)] = \int \pi_\theta(a_t \mid s_t) \frac{\nabla_\theta \pi_\theta(a_t \mid s_t)}{\pi_\theta(a_t \mid s_t)} da_t = \nabla_\theta \int \pi_\theta(a_t \mid s_t) da_t = \nabla_\theta (1) = 0$$
    The inner expectation is identically zero!
  </p>
</div>

<p>
  Therefore, removing past rewards does not introduce any bias, but eliminates massive amounts of uncorrelated noise! This gives the <b>Reward-to-Go</b> formulation:
</p>

<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>Reward-to-Go Policy Gradient:</b><br>
  $$\nabla_\theta J(\theta) = \sum_{t=0}^T \mathbb{E}_{(s_t, a_t)} \left[ \nabla_\theta \log \pi_\theta(a_t \mid s_t) \left( \sum_{t'=t}^T r(s_{t'}, a_{t'}) \right) \right]$$
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 5 -->
<h2>Part 5: Variance Reduction II — Baselines, EGLP Lemma &amp; Optimal Baseline</h2>
<p>
  <b>(Slides 36–45 &amp; Spinning Up ch09)</b> Even with reward-to-go, if all rewards are positive ($r_t \in [100, 110]$), the gradient will push <i>all</i> sampled actions to become more probable! To differentiate good actions from merely average actions, we subtract a <b>baseline</b> $b(s_t)$.
</p>

<h3>5.1 The Expected Grad-Log-Prob (EGLP) Lemma</h3>
<div class="formula" style="border: 2px solid #3b82f6; background: #eff6ff;">
  <b>The Expected Grad-Log-Prob (EGLP) Lemma:</b><br>
  $$\mathbb{E}_{x \sim P_\theta} \left[ \nabla_\theta \log P_\theta(x) \right] = 0$$
</div>

<p>
  Because $\mathbb{E}_{a_t \sim \pi}[\nabla_\theta \log \pi_\theta(a_t|s_t)] = 0$, any baseline function $b(s_t)$ that does not depend on the current action $a_t$ leaves the expectation completely unchanged:
  $$\mathbb{E} \big[ \nabla_\theta \log \pi_\theta(a_t \mid s_t) \, b(s_t) \big] = \mathbb{E}_{s_t} \left[ b(s_t) \underbrace{\mathbb{E}_{a_t \sim \pi} [\nabla_\theta \log \pi_\theta(a_t \mid s_t)]}_{= 0} \right] = 0$$
</p>

<h3>5.2 The Optimal Baseline Minimizing Variance</h3>
<p>
  What choice of baseline $b(s)$ minimizes the variance of the gradient estimator $\operatorname{Var}(\hat{g})$?
  Taking the derivative of variance with respect to $b$ and setting it to zero yields:
</p>

<div class="formula">
  $$b^*(s) = \frac{\mathbb{E}_{a \sim \pi} \left[ \|\nabla_\theta \log \pi_\theta(a \mid s)\|^2 \, Q(s, a) \right]}{\mathbb{E}_{a \sim \pi} \left[ \|\nabla_\theta \log \pi_\theta(a \mid s)\|^2 \right]}$$
</div>

<p>
  This is an expected return weighted by gradient magnitude. In practice, the state value function $V^\pi(s) = \mathbb{E}[Q(s, a)]$ is very close to $b^*(s)$ and is far easier to train via a neural network critic!
</p>

<h3>5.3 Achiam's 5 Forms of $\Phi_t$ (Spinning Up Universal Formulation)</h3>
<p>
  Joshua Achiam showed that all policy gradient methods can be written as:
  $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau} \left[ \sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t \mid s_t) \, \Phi_t \right]$$
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Choice of $\Phi_t$</th>
      <th style="width: 35%;">Mathematical Expression</th>
      <th style="width: 40%;">Bias &amp; Variance Characterization</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Total Return</b></td>
      <td>$\Phi_t = R(\tau) = \sum_{t'=0}^T r_{t'}$</td>
      <td>Unbiased; <b>Maximum Variance</b> (Classic REINFORCE).</td>
    </tr>
    <tr>
      <td><b>2. Reward-to-Go</b></td>
      <td>$\Phi_t = \sum_{t'=t}^T r_{t'}$</td>
      <td>Unbiased; <b>Lower Variance</b> (Removes past uncorrelated noise).</td>
    </tr>
    <tr>
      <td><b>3. Return with Baseline</b></td>
      <td>$\Phi_t = \sum_{t'=t}^T r_{t'} - b(s_t)$</td>
      <td>Unbiased; <b>Significantly Lower Variance</b> (Centers returns around mean).</td>
    </tr>
    <tr>
      <td><b>4. Q-Function</b></td>
      <td>$\Phi_t = Q^\pi(s_t, a_t)$</td>
      <td>Biased (if approximated by neural network); <b>Very Low Variance</b>.</td>
    </tr>
    <tr>
      <td><b>5. Advantage Function</b></td>
      <td>$\Phi_t = A^\pi(s_t, a_t) = Q^\pi(s_t, a_t) - V^\pi(s_t)$</td>
      <td>Biased (if approximated); <b>Lowest Variance (PPO / Actor-Critic)</b>.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 6 -->
<h2>Part 6: Formal Algorithm Specification &amp; PyTorch Implementation</h2>

<div class="algorithm-box">
  <div class="algorithm-header">Algorithm 1: REINFORCE with Learned State-Value Baseline</div>
  <p><b>Initialize:</b> Policy network parameters $\theta$, Baseline value network parameters $\phi$, learning rates $\alpha_\theta, \alpha_\phi$.</p>
  <ol>
    <li><b>for</b> iteration $k = 1, 2, \dots$ <b>do</b></li>
    <li>&nbsp;&nbsp;Sample batch of trajectories $\mathcal{D} = \{\tau_i\}$ by running policy $\pi_\theta$ in environment.</li>
    <li>&nbsp;&nbsp;<b>for</b> each trajectory $\tau_i$ and each time step $t$ <b>do</b></li>
    <li>&nbsp;&nbsp;&nbsp;&nbsp;Compute reward-to-go: $\hat{R}_{i,t} = \sum_{t'=t}^T \gamma^{t'-t} r_{i,t'}$.</li>
    <li>&nbsp;&nbsp;&nbsp;&nbsp;Compute advantage estimate: $\hat{A}_{i,t} = \hat{R}_{i,t} - V_\phi(s_{i,t})$.</li>
    <li>&nbsp;&nbsp;<b>end for</b></li>
    <li>&nbsp;&nbsp;Normalize advantages across batch: $\hat{A} \leftarrow \frac{\hat{A} - \operatorname{mean}(\hat{A})}{\operatorname{std}(\hat{A}) + 10^{-8}}$.</li>
    <li>&nbsp;&nbsp;Update Baseline Critic by minimizing MSE loss:
      $$\phi \leftarrow \phi - \alpha_\phi \nabla_\phi \frac{1}{|\mathcal{D}|} \sum_{i, t} \big( V_\phi(s_{i,t}) - \hat{R}_{i,t} \big)^2$$
    </li>
    <li>&nbsp;&nbsp;Update Policy Actor via policy gradient ascent:
      $$\theta \leftarrow \theta + \alpha_\theta \frac{1}{|\mathcal{D}|} \sum_{i, t} \nabla_\theta \log \pi_\theta(a_{i,t} \mid s_{i,t}) \, \hat{A}_{i,t}$$
    </li>
    <li><b>end for</b></li>
  </ol>
</div>

<h3>6.1 Production PyTorch Implementation</h3>
<div class="code-container">
<pre><span class="code-keyword">import</span> torch
<span class="code-keyword">import</span> torch.nn <span class="code-keyword">as</span> nn
<span class="code-keyword">from</span> torch.distributions.normal <span class="code-keyword">import</span> Normal

<span class="code-keyword">class</span> <span class="code-func">ContinuousActorCritic</span>(nn.Module):
    <span class="code-keyword">def</span> <span class="code-func">__init__</span>(self, obs_dim: int, act_dim: int):
        <span class="code-func">super</span>().__init__()
        <span class="code-comment"># Policy network (Actor)</span>
        self.actor_backbone = nn.Sequential(
            nn.Linear(obs_dim, 128), nn.Tanh(),
            nn.Linear(128, 128), nn.Tanh()
        )
        self.mu_head = nn.Linear(128, act_dim)
        self.log_std = nn.Parameter(torch.zeros(act_dim))
        
        <span class="code-comment"># Value network (Baseline Critic)</span>
        self.critic = nn.Sequential(
            nn.Linear(obs_dim, 128), nn.Tanh(),
            nn.Linear(128, 128), nn.Tanh(),
            nn.Linear(128, 1)
        )

    <span class="code-keyword">def</span> <span class="code-func">get_action_and_value</span>(self, obs: torch.Tensor, action: torch.Tensor = None):
        features = self.actor_backbone(obs)
        mu = self.mu_head(features)
        std = torch.exp(torch.clamp(self.log_std, min=-20.0, max=2.0))
        dist = Normal(mu, std)
        
        <span class="code-keyword">if</span> action <span class="code-keyword">is</span> None:
            action = dist.sample()
            
        <span class="code-comment"># Sum log probabilities over action dimensions!</span>
        log_prob = dist.log_prob(action).sum(dim=-1, keepdim=True)
        entropy = dist.entropy().sum(dim=-1, keepdim=True)
        value = self.critic(obs)
        <span class="code-keyword">return</span> action, log_prob, entropy, value
</pre>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 7 -->
<h2>Part 7: Conceptual Mastery &amp; Exam Challenge</h2>

<div class="quiz-box">
  <div class="quiz-q">Question 1: If we multiply all environment rewards by 10 (scaling $r \to 10r$), does the policy gradient update change?</div>
  <div class="quiz-a">
    <b>Answer:</b> In raw REINFORCE without advantage normalization, YES: the gradient magnitude scales by 10, effectively increasing learning rate by 10x and potentially causing catastrophic optimization instability. 
    However, if <b>batch advantage normalization</b> is used ($\hat{A} \leftarrow (\hat{A} - \mu) / \sigma$), the constant factor 10 cancels out, rendering the policy gradient invariant to reward scaling!
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: Why must the baseline $V_\phi(s)$ be detached (`.detach()`) when computing the policy gradient loss in PyTorch?</div>
  <div class="quiz-a">
    <b>Answer:</b> The advantage is $\hat{A}_t = R_t - V_\phi(s_t)$. When we write `loss = -(log_prob * advantage).mean()`, if $V_\phi$ is not detached, backpropagation will compute $\nabla_\phi$ through the advantage term, trying to minimize advantage rather than maximize return! Detaching ensures the policy optimizer updates only the Actor parameters $\theta$.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: Why is policy gradient loss often negative and continuously decreasing, even if the robot's task performance is degrading?</div>
  <div class="quiz-a">
    <b>Answer:</b> The policy gradient loss $-\sum \log \pi_\theta(a|s) \hat{A}$ is a <i>surrogate loss</i> evaluated on non-stationary data collected by an older policy. It is not an upper bound on performance. If entropy decays and $\log \pi$ explodes, the numerical loss will decrease to $-\infty$ even as the policy collapses to a single catastrophic action.
  </div>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    pdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture5_Beginner_Guide.pdf"
    backup_path = "/home/omen/Downloads/CS285_Lecture5_Beginner_Guide.pdf"
    render_utils.build_pdf(html_content, pdf_path, backup_path)
