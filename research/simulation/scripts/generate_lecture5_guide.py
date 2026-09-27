import os
import weasyprint
import shutil

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Policy Gradients: Beginner's Guide to CS285 Lecture 5</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
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
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 5 Enhanced Study Guide</span>
  <h1>Mastering Policy Gradients &amp; Variance Reduction</h1>
  <div class="subtitle">Complete Beginner-Friendly Breakdown: The Log-Derivative Trick, EGLP Lemma, Achiam's 5 Forms of Phi_t, Gaussian Continuous Control &amp; Bi-Manual Slicing</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Companion:</b> DEX-ROB Lab, Tianjin University</span>
    <span><b>Frameworks:</b> Achiam (Spinning Up) + Goodfellow (Optimization)</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The "Mental Map": Why Does Lecture 5 Exist?</h2>
<p>
  In Lecture 4, we formulated the general goal of reinforcement learning: find a policy $\pi_\theta(a|s)$ that maximizes expected cumulative return $J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} [r(\tau)]$.
</p>
<p>
  <b>The Central Dilemma of Robotics:</b> In standard deep learning, you compute the gradient of your loss with respect to network weights via backpropagation ($\nabla_\theta \mathcal{L}$). But in robotics, between the robot's motors and the final reward lies <b>the physical universe</b>: non-linear friction, knife-tissue deformation, skin crack initiation, and fluid dynamics.
</p>
<p>
  You cannot backpropagate a gradient through a physical tomato! How can we optimize a neural network when the physical laws connecting our actions to the results are completely non-differentiable? <b>Lecture 5 introduces the Policy Gradient Theorem and the magical "Log-Derivative Trick" that solves this dilemma.</b>
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 5 -->
<div class="diagram-container">
<svg width="680" height="90" viewBox="0 0 680 90">
  <rect x="5" y="10" width="125" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="67" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. Log-Derivative</text>
  <text x="67" y="52" font-size="8.5" fill="#475569" text-anchor="middle">No Physics Model</text>
  <text x="67" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Needed!</text>

  <rect x="140" y="10" width="125" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="202" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">2. Gaussian Policy</text>
  <text x="202" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Continuous Actions:</text>
  <text x="202" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Mean μ and Noise σ</text>

  <rect x="275" y="10" width="125" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="337" y="36" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">3. The Variance Trap</text>
  <text x="337" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Lucky vs Unlucky</text>
  <text x="337" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Noisy Gradients</text>

  <rect x="410" y="10" width="125" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="472" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">4. Causality</text>
  <text x="472" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Reward-to-Go:</text>
  <text x="472" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Past != Future</text>

  <rect x="545" y="10" width="125" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="607" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">5. Baselines &amp; EGLP</text>
  <text x="607" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Subtracting b(s):</text>
  <text x="607" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Zero Bias, Low Var</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: REINFORCE &amp; The Log-Derivative Trick</h2>
<p>
  <b>(Slides 1–15, Spoken Transcript 02:40–16:50)</b> How do we compute $\nabla_\theta J(\theta)$ without differentiating through the environment transition dynamics $p(s_{t+1}|s_t, a_t)$?
</p>

<h3>1.1 The Mathematical Derivation (Step-by-Step for Beginners)</h3>
<p>
  A trajectory $\tau = (s_1, a_1, s_2, a_2, \dots, s_T)$ has probability:
</p>
<div class="formula">
  p_\theta(\tau) = p(s_1) \prod_{t=1}^T \pi_\theta(a_t | s_t) \, p(s_{t+1} | s_t, a_t)
</div>
<p>
  The expected return is:
  $J(\theta) = \int p_\theta(\tau) \, r(\tau) \, d\tau$.
  Taking the gradient directly:
  $\nabla_\theta J(\theta) = \int \nabla_\theta p_\theta(\tau) \, r(\tau) \, d\tau$.
  Using the Log-Derivative Identity $\nabla_\theta p_\theta(\tau) = p_\theta(\tau) \nabla_\theta \log p_\theta(\tau)$:
</p>
<div class="formula">
  \nabla_\theta J(\theta) = \int p_\theta(\tau) \, \nabla_\theta \log p_\theta(\tau) \, r(\tau) \, d\tau = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \nabla_\theta \log p_\theta(\tau) \, r(\tau) \right]
</div>

<h3>1.2 Why the Physics Vanishes!</h3>
<p>
  Now expand $\log p_\theta(\tau)$:
  $\log p_\theta(\tau) = \log p(s_1) + \sum_{t=1}^T \log \pi_\theta(a_t | s_t) + \sum_{t=1}^T \log p(s_{t+1} | s_t, a_t)$.
  Notice that $p(s_1)$ and the transition dynamics $p(s_{t+1}|s_t, a_t)$ do NOT depend on policy weights $\theta$! Their derivatives with respect to $\theta$ are identically zero!
</p>
<div class="formula" style="border: 2px solid #2563eb; background: #eff6ff;">
  <b>The Policy Gradient Theorem (REINFORCE):</b><br>
  $$\nabla_\theta J(\theta) \approx \frac{1}{N} \sum_{i=1}^N \left( \sum_{t=1}^T \nabla_\theta \log \pi_\theta(a_{i,t} | s_{i,t}) \right) \left( \sum_{t=1}^T r(s_{i,t}, a_{i,t}) \right)$$
</div>

<div class="callout intuition">
  <div class="callout-title">Plain-English Intuition: What Did We Just Do?</div>
  <p>
    We do NOT need an equation for the skin toughness of a tomato. We only need to run simulated cuts, record which trajectories scored high rewards, and increase the likelihood of the actions the network took during those successful runs. Good actions are pushed to happen more often; bad actions are pushed to happen less often. This is mathematically formalized trial-and-error!
  </p>
</div>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: Continuous Actions &amp; Gaussian Policies</h2>
<p>
  <b>(Slides 16–22, Spoken Transcript 17:00–28:30)</b> In robotic manipulation, actions are continuous variables: feed velocity $\Delta z \in [-2, 2]$ mm, sawing speed $v_{\text{saw}} \in [-50, 50]$ mm/s, stiffness $\Delta K_z \in [-200, 200]$ N/m.
</p>

<h3>2.1 The Gaussian Policy Network</h3>
<div class="formula">
  \pi_\theta(a_t | s_t) = \mathcal{N}\big(\mu_\theta(s_t),\, \Sigma_\theta(s_t)\big) = \frac{1}{\sqrt{2\pi \sigma^2}} \exp\left( -\frac{(a_t - \mu_\theta(s_t))^2}{2\sigma^2} \right)
</div>

<!-- SVG Diagram: Gaussian Policy Distribution -->
<div class="diagram-container">
<svg width="680" height="150" viewBox="0 0 680 150">
  <path d="M 140 120 C 240 120, 290 25, 340 25 C 390 25, 440 120, 540 120" fill="none" stroke="#2563eb" stroke-width="3"/>
  <line x1="80" y1="120" x2="600" y2="120" stroke="#94a3b8" stroke-width="1.5"/>

  <!-- Mean Center line -->
  <line x1="340" y1="25" x2="340" y2="120" stroke="#dc2626" stroke-width="2" stroke-dasharray="4"/>
  <text x="340" y="18" font-size="10.5" font-weight="700" fill="#dc2626" text-anchor="middle">Mean μ_θ(s) [Intended Sawing Speed]</text>

  <!-- Variance / Noise Width -->
  <line x1="280" y1="65" x2="400" y2="65" stroke="#059669" stroke-width="2" marker-start="url(#arr-left)" marker-end="url(#arr-right)"/>
  <text x="340" y="80" font-size="9" font-weight="700" fill="#059669" text-anchor="middle">Exploration Noise σ_θ (Blade Vibration)</text>

  <!-- Sampled action -->
  <circle cx="390" cy="55" r="5" fill="#f59e0b"/>
  <line x1="390" y1="55" x2="390" y2="120" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="2"/>
  <text x="390" y="135" font-size="9" font-weight="700" fill="#d97706" text-anchor="middle">Sampled Action a_t</text>

  <defs>
    <marker id="arr-left" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M 8 1 L 0 5 L 8 9 z" fill="#059669"/>
    </marker>
    <marker id="arr-right" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">
      <path d="M 2 1 L 10 5 L 2 9 z" fill="#059669"/>
    </marker>
  </defs>
</svg>
</div>

<h3>2.2 The Analytical Derivative of a Gaussian Policy</h3>
<div class="formula">
  \nabla_\theta \log \pi_\theta(a|s) = \frac{a - \mu_\theta(s)}{\sigma^2} \, \nabla_\theta \mu_\theta(s)
</div>

<div class="callout robotics">
  <div class="callout-title">Physical Robotics Meaning: Pushing the Mean</div>
  <p>
    Look closely at the term $(a - \mu_\theta(s))$:
    <ul>
      <li>Suppose the network intended to saw at $\mu = 15$ mm/s, but exploratory noise sampled $a = 22$ mm/s ($a - \mu = +7$).</li>
      <li>If this cut successfully sliced the tomato skin without crushing, return $r(\tau)$ is positive ($+10$).</li>
      <li>The gradient update pushes $\mu_\theta(s)$ in the direction of $+7$, shifting the mean sawing speed higher!</li>
    </ul>
  </p>
</div>

<div class="callout silent-bug">
  <div class="callout-title">Spinning Up Bug Alert: Clamping Log-Std</div>
  <p>
    Joshua Achiam warns: if you let `log_std` float unconstrained, gradients will cause $\sigma \to 0$ (destroying exploration prematurely) or $\sigma \to \infty$ (causing `NaN` in division by $\sigma^2$). In production robotics code, always clamp log standard deviations: `log_std = torch.clamp(log_std, min=-20, max=2)`.
  </p>
</div>

<div class="page-break"></div>

<!-- PART 3 -->
<h2>Part 3: The High Variance Nightmare</h2>
<p>
  <b>(Slides 23–28, Spoken Transcript 29:00–41:10)</b> While REINFORCE is mathematically elegant, Sergey Levine points out why raw REINFORCE is completely unusable in practical robotics without variance reduction.
</p>

<h3>3.1 The Chess Analogy (Levine's Example)</h3>
<p>
  In chess ($+1$ for win, $-1$ for loss):
  If the agent plays an extraordinary opening at move 5, but blunders at move 45 and loses, REINFORCE multiplies <i>every</i> move by $-1$, so the brilliant move 5 is penalized!
  Mathematically, these errors average out over infinite samples, but in practice, you might need <b>100 million trajectories</b> just to drown out the noise!
</p>

<!-- SVG Diagram: Variance in Cutting Trajectories -->
<div class="diagram-container">
<svg width="680" height="130" viewBox="0 0 680 130">
  <rect x="20" y="15" width="300" height="95" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="170" y="38" font-size="10.5" font-weight="700" fill="#991b1b" text-anchor="middle">Trajectory 1: Unlucky Contact Slip</text>
  <text x="170" y="58" font-size="8.5" fill="#475569" text-anchor="middle">Steps 1-170: Perfect adaptive sawing</text>
  <text x="170" y="73" font-size="8.5" fill="#ef4444" text-anchor="middle">Step 175: Gripper slip ➔ Total Collapse</text>
  <text x="170" y="92" font-size="9" font-weight="700" fill="#b91c1c" text-anchor="middle">Raw REINFORCE: Penalizes ALL 175 steps!</text>

  <rect x="360" y="15" width="300" height="95" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="510" y="38" font-size="10.5" font-weight="700" fill="#065f46" text-anchor="middle">Trajectory 2: Lucky Puncture</text>
  <text x="510" y="58" font-size="8.5" fill="#475569" text-anchor="middle">Steps 1-50: Terrible erratic stiffness</text>
  <text x="510" y="73" font-size="8.5" fill="#047857" text-anchor="middle">Step 52: Random puncture ➔ Fruit holds</text>
  <text x="510" y="92" font-size="9" font-weight="700" fill="#047857" text-anchor="middle">Raw REINFORCE: Rewards ALL erratic steps!</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 4 -->
<h2>Part 4: Variance Reduction: Causality &amp; Reward-to-Go</h2>
<p>
  <b>(Slides 29–35, Spoken Transcript 41:30–52:00)</b> Physical causality states: <b>actions taken in the present cannot affect rewards received in the past!</b>
</p>

<h3>4.1 The Causality Proof</h3>
<p>
  For any time step $t' < t$, $\mathbb{E} [ \nabla_\theta \log \pi_\theta(a_t | s_t) \cdot r(s_{t'}, a_{t'}) ] = 0$.
  Discarding past rewards yields the <b>Reward-to-Go</b> $\hat{Q}_{i,t}$:
</p>
<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>Reward-to-Go Policy Gradient:</b><br>
  $$\nabla_\theta J(\theta) \approx \frac{1}{N} \sum_{i=1}^N \sum_{t=1}^T \nabla_\theta \log \pi_\theta(a_{i,t} | s_{i,t}) \left( \sum_{t'=t}^T r(s_{i,t'}, a_{i,t'}) \right)$$
</div>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Baselines, EGLP Lemma &amp; The 5 Forms of Phi_t</h2>
<p>
  <b>(Slides 36–45 &amp; Spinning Up ch09)</b> In *Spinning Up in Deep RL*, Joshua Achiam unifies all policy gradient methods into a single universal template:
</p>
<div class="formula">
  $$\nabla_\theta J(\pi_\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t | s_t) \, \Phi_t \right]$$
</div>
<p>
  Achiam identifies the <b>5 valid choices of $\Phi_t$</b>, proving they all share the exact same mathematical expectation and differ only in variance:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Choice of $\Phi_t$</th>
      <th style="width: 35%;">Mathematical Expression</th>
      <th style="width: 40%;">Variance &amp; Bias Tradeoff</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Total Return</b></td>
      <td>$\Phi_t = R(\tau) = \sum_{t'=0}^T r_{t'}$</td>
      <td>Unbiased, <b>Highest Variance</b> (pure REINFORCE).</td>
    </tr>
    <tr>
      <td><b>2. Reward-to-Go</b></td>
      <td>$\Phi_t = \sum_{t'=t}^T r_{t'}$</td>
      <td>Unbiased, <b>Lower Variance</b> (removes past noise via causality).</td>
    </tr>
    <tr>
      <td><b>3. Return with Baseline</b></td>
      <td>$\Phi_t = \sum_{t'=t}^T r_{t'} - b(s_t)$</td>
      <td>Unbiased, <b>Significantly Lower Variance</b> (centers returns).</td>
    </tr>
    <tr>
      <td><b>4. State-Action Q</b></td>
      <td>$\Phi_t = Q^\pi(s_t, a_t)$</td>
      <td>Biased (if Q learned), <b>Very Low Variance</b>.</td>
    </tr>
    <tr>
      <td><b>5. Advantage Function</b></td>
      <td>$\Phi_t = A^\pi(s_t, a_t) = Q^\pi(s_t, a_t) - V^\pi(s_t)$</td>
      <td>Biased (if approximated), <b>Lowest Variance (Actor-Critic &amp; PPO)</b>.</td>
    </tr>
  </tbody>
</table>

<h3>5.1 The EGLP Lemma (Why Baselines are Unbiased)</h3>
<div class="formula" style="border: 2px solid #3b82f6; background: #eff6ff;">
  <b>The Expected Grad-Log-Prob (EGLP) Lemma:</b><br>
  $$\mathbb{E}_{x \sim P_\theta} \left[ \nabla_\theta \log P_\theta(x) \right] = 0$$
</div>
<p>
  Because $\mathbb{E}_{a \sim \pi}[\nabla \log \pi(a|s)] = 0$, any state baseline $b(s_t)$ factors out: $\mathbb{E}[\nabla \log \pi(a|s) b(s)] = b(s) \cdot 0 = 0$.
</p>

<div class="callout warning-box">
  <div class="callout-title">Achiam's Rule: The Policy Gradient Loss is NOT a Loss Function!</div>
  <p>
    In supervised learning, loss measures performance. In policy gradients, the objective is a surrogate whose distribution shifts with $\theta$. 
    <b>You can drive the policy gradient surrogate loss to negative infinity while the robot's real cutting performance craters!</b> 
    Never use policy gradient loss to evaluate convergence. Only average episode return ($\bar{R}$) and success rate are meaningful metrics.
  </p>
</div>

<div class="page-break"></div>

<!-- PART 6 -->
<h2>Part 6: Paper 1 PyTorch Implementation Blueprint</h2>

<div class="code-block">
import torch
import torch.nn as nn
from torch.distributions.normal import Normal

class TomatoCuttingPolicy(nn.Module):
    def __init__(self, state_dim=33, action_dim=6):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ELU(),
            nn.Linear(256, 128),
            nn.ELU()
        )
        self.mean_layer = nn.Linear(128, action_dim)
        # Learnable log standard deviation clamped for numerical safety
        self.log_std = nn.Parameter(torch.zeros(action_dim))

    def forward(self, state):
        features = self.backbone(state)
        mean = self.mean_layer(features)
        # Numerical stability clamp: prevents NaN or zero-variance freeze
        log_std = torch.clamp(self.log_std, min=-20.0, max=2.0)
        std = torch.exp(log_std)
        return Normal(mean, std)

def compute_policy_gradient_loss(policy, states, actions, rewards_to_go, baselines):
    dist = policy(states)
    log_probs = dist.log_prob(actions).sum(dim=-1, keepdim=True)
    
    # CRITICAL: detach baselines so value gradients do not corrupt policy
    advantages = rewards_to_go - baselines.detach()
    
    # Advantage normalization across batch
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
    
    # Negative surrogate loss for PyTorch optimizer minimization
    loss = -(log_probs * advantages).mean()
    return loss
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 7: SELF-TEST QUIZ -->
<h2>Part 7: Interactive Tablet Self-Test Quiz (Test Your Understanding)</h2>

<div class="quiz-box">
  <div class="quiz-q">Question 1: Why does the environmental physics model $p(s_{t+1}|s_t, a_t)$ vanish when we apply the log-derivative trick?</div>
  <div class="quiz-a">
    <b>Answer:</b> When expanding $\log p_\theta(\tau)$, the physics dynamics appear as an additive term $\sum \log p(s_{t+1}|s_t, a_t)$. Because the laws of physics do not depend on the neural network parameters $\theta$, taking the partial derivative $\nabla_\theta$ causes this term to differentiate to exactly zero ($\nabla_\theta \log p(s_{t+1}|s_t, a_t) = 0$).
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: According to the EGLP Lemma, why does subtracting a state baseline $b(s)$ not change the expectation of the policy gradient?</div>
  <div class="quiz-a">
    <b>Answer:</b> The Expected Grad-Log-Prob Lemma states that $\mathbb{E}_{a \sim \pi}[\nabla_\theta \log \pi_\theta(a|s)] = 0$ because probability densities integrate to 1. Since $b(s)$ is independent of action $a$, it factors out as $b(s) \cdot 0 = 0$.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: If you forget to call `.detach()` on the baseline $V(s)$ when computing advantages, what silent bug occurs?</div>
  <div class="quiz-a">
    <b>Answer:</b> The PyTorch autograd graph will backpropagate the policy loss backward through the baseline network. Instead of fitting $V(s)$ to predict returns via MSE, the value network will be distorted by policy gradients, destabilizing value estimation and destroying training.
  </div>
</div>

<div class="page-break"></div>

<!-- PART 8: THESIS DEFENSE -->
<h2>Part 8: Thesis Defense Master Cheatsheet (Lecture 5 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Q1: "Why can't you simply backpropagate gradients directly through the Isaac Lab physics engine?"</div>
  <p>
    <b>Answer:</b> "While differentiable simulators exist, soft contact mechanics—specifically fracture of the tomato skin cuticle, non-linear fluid outflow, and frictional stick-slip transitions—are fundamentally discontinuous and non-differentiable. Even if approximate gradients could be computed, they suffer from catastrophic gradient explosion across multi-step contact impacts. The Policy Gradient Theorem bypasses physical derivatives entirely by differentiating only the policy's log-action probabilities weighted by the scalar performance return."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q2: "What is the physical role of the policy's standard deviation $\sigma$ in robotic cutting?"</div>
  <p>
    <b>Answer:</b> "In our continuous Gaussian policy, $\sigma$ represents active motor exploration. Early in training, high $\sigma$ creates stochastic micro-vibrations and multi-axis sawing motions, enabling the robot to stumble upon skin puncture events. As training converges, $\sigma$ decays naturally, yielding a smooth, deterministic compliant trajectory that executes steady sawing without erratic force oscillations."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q3: "Why is Reward-to-Go mathematically superior to Total Trajectory Return?"</div>
  <p>
    <b>Answer:</b> "Total return multiplies the action at step $t$ by past rewards received prior to step $t$. By causality, the robot's current action cannot influence events that have already occurred ($\mathbb{E}[\nabla \log \pi_t \cdot r_{t'}] = 0$ for $t' < t$). Retaining past rewards adds pure noise to the gradient estimate. Reward-to-go discards past rewards, preserving the identical mathematical expectation while dramatically reducing gradient variance."
  </p>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
<div style="text-align: center; font-size: 8.5pt; color: #64748b;">
  CS 285 Lecture 5 Comprehensive Study Guide • Prepared for DEX-ROB Lab, Tianjin University
</div>

</body>
</html>
"""

output_path = "/home/omen/Downloads/CS285_Lecture5_Beginner_Guide.pdf"
backup_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture5_Beginner_Guide.pdf"

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_utils

render_utils.build_pdf(html_content, output_path, backup_path)

