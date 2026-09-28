import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Advanced Policy Gradients & PPO: Definitive Guide to CS285 Lecture 10</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 10: Advanced Policy Gradients, TRPO & PPO";
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
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 10 Masterclass Study Guide</span>
  <h1>Mastering Advanced Policy Gradients &amp; PPO</h1>
  <div class="subtitle">Complete Mathematical &amp; Algorithmic Foundations: Policy Collapse, Kakade-Langford Monotonic Improvement Guarantee, Natural Policy Gradients, Fisher Information Matrix, TRPO, Clipped Surrogate PPO, and Isaac Lab Scaling</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Curriculum:</b> Berkeley CS285 + Schulman et al. (TRPO/PPO) + Achiam (Spinning Up)</span>
    <span><b>Scope:</b> General Trust Region Optimization &amp; Robotics Slicing</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The Executive Mental Map: Why Does Lecture 10 Exist?</h2>
<p>
  In Lecture 5 and Lecture 6, we derived the Policy Gradient Theorem and learned how to calculate policy updates via gradient ascent: $\theta \leftarrow \theta + \alpha \nabla_\theta J(\theta)$.
</p>
<p>
  <b>The Fatal Flaw of Standard Gradient Steps:</b> In supervised learning, taking a step with a learning rate that is slightly too large causes a temporary bump in test error; the next mini-batch corrects it. <b>In reinforcement learning, the policy generates its own future training data.</b>
</p>
<p>
  If a single oversized gradient step pushes the policy into a destructive regime (e.g., slamming the knife into the cutting table or pitching a drone upside down), <b>every rollout collected in the next iteration will fail completely</b>. The neural network receives zero reward across the entire batch, variance explodes, and the policy enters an unrecoverable catastrophic collapse.
</p>
<p>
  <b>Lecture 10 introduces Trust Region Policy Optimization (TRPO) and Proximal Policy Optimization (PPO):</b> the algorithms that place a rigorous mathematical "safety leash" on policy updates, guaranteeing monotonic policy improvement and enabling reliable robot learning in massively parallel simulators.
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 10 -->
<div class="diagram-container">
<svg width="690" height="90" viewBox="0 0 690 90">
  <rect x="5" y="10" width="128" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="69" y="36" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">1. Policy Collapse</text>
  <text x="69" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Why Bad Steps</text>
  <text x="69" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Cause Death Spirals</text>

  <rect x="141" y="10" width="128" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="205" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">2. Monotonic Bounds</text>
  <text x="205" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Kakade &amp; Langford Proof</text>
  <text x="205" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Surrogate Lower Bound</text>

  <rect x="277" y="10" width="128" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="341" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">3. Natural Gradient</text>
  <text x="341" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Fisher Matrix F</text>
  <text x="341" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Conjugate Gradients</text>

  <rect x="413" y="10" width="128" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="477" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">4. PPO-Clip Engine</text>
  <text x="477" y="52" font-size="8.2" fill="#475569" text-anchor="middle">min(rA, clip(r)A)</text>
  <text x="477" y="66" font-size="8.2" fill="#475569" text-anchor="middle">The 4-Quadrant Analysis</text>

  <rect x="549" y="10" width="136" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="617" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">5. Parallel Scaling</text>
  <text x="617" y="52" font-size="8.2" fill="#475569" text-anchor="middle">Isaac Lab 4096 Envs</text>
  <text x="617" y="66" font-size="8.2" fill="#475569" text-anchor="middle">Epoch Reuse Paradigm</text>
</svg>
</div>

<div class="page-break"></div>

<!-- PART 1 -->
<h2>Part 1: The Catastrophe of Policy Collapse</h2>
<p>
  <b>(Slides 1–15)</b> To understand why standard gradient descent fails in RL, we compare how error recovery functions in Supervised Learning vs. Reinforcement Learning:
</p>

<!-- SVG Diagram: Supervised vs RL Error Recovery -->
<div class="diagram-container">
<svg width="680" height="140" viewBox="0 0 680 140">
  <rect x="30" y="15" width="290" height="110" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="175" y="38" font-size="10.5" font-weight="700" fill="#1e40af" text-anchor="middle">Supervised Learning (Stable)</text>
  <text x="175" y="56" font-size="8.2" fill="#475569" text-anchor="middle">Fixed offline dataset (ImageNet)</text>
  <text x="175" y="72" font-size="8.2" fill="#dc2626" text-anchor="middle">Oversized Step ➔ Bad batch loss</text>
  <text x="175" y="88" font-size="8.2" fill="#059669" text-anchor="middle">Next Batch: Recovers easily</text>
  <text x="175" y="104" font-size="8" fill="#3b82f6" text-anchor="middle">Data distribution remains static!</text>

  <rect x="360" y="15" width="290" height="110" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="505" y="38" font-size="10.5" font-weight="700" fill="#991b1b" text-anchor="middle">Reinforcement Learning (FRAGILE)</text>
  <text x="505" y="56" font-size="8.2" fill="#475569" text-anchor="middle">Policy collects its own training data!</text>
  <text x="505" y="72" font-size="8.2" fill="#dc2626" text-anchor="middle">Oversized Step ➔ Destructive Actions</text>
  <text x="505" y="88" font-size="8.2" fill="#b91c1c" font-weight="700" text-anchor="middle">Next Batch: 100% Failed Trajectories</text>
  <text x="505" y="104" font-size="8.2" font-weight="700" fill="#ef4444" text-anchor="middle">CATASTROPHIC COLLAPSE (Irrecoverable)</text>
</svg>
</div>

<h3>1.1 The State Distribution Shift Dilemma</h3>
<p>
  When updating policy parameters from $\theta_{\text{old}}$ to $\theta$, the true expected performance of the new policy is:
  $$J(\pi_\theta) = \mathbb{E}_{s \sim d^{\pi_\theta}(s)} \left[ \mathbb{E}_{a \sim \pi_\theta(a|s)} [Q^{\pi_{\text{old}}}(s, a)] \right]$$
  In practice, we evaluate actions using states sampled from the <b>old policy</b>: $s \sim d^{\pi_{\text{old}}}(s)$. 
  We are ignoring the fact that changing the policy alters the state visitation distribution!
  <br><b>Sergey Levine's Core Question:</b> <i>"When is it mathematically valid to approximate $d^{\pi_\theta}(s)$ with $d^{\pi_{\text{old}}}(s)$?"</i>
  <br><b>The Answer:</b> Only when the probability distributions $\pi_\theta(a|s)$ and $\pi_{\text{old}}(a|s)$ remain extremely close in distribution space, bounded by a <b>Trust Region</b>!
</p>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: The Kakade-Langford Monotonic Improvement Guarantee</h2>
<p>
  <b>(Slides 16–35)</b> In their 2002 paper, Sham Kakade and John Langford proved the fundamental theorem underpinning all modern trust region methods:
</p>

<div class="math-box">
  <div class="callout-title">The Exact Policy Value Identity</div>
  <p>
    For any two arbitrary policies $\pi$ and $\tilde{\pi}$:
    $$J(\tilde{\pi}) = J(\pi) + \mathbb{E}_{\tau \sim \tilde{\pi}} \left[ \sum_{t=0}^\infty \gamma^t A^\pi(s_t, a_t) \right] = J(\pi) + \sum_{s} d^{\tilde{\pi}}(s) \sum_{a} \tilde{\pi}(a \mid s) A^\pi(s, a)$$
    <b>Proof:</b> Express advantage as $A^\pi(s_t, a_t) = r_t + \gamma V^\pi(s_{t+1}) - V^\pi(s_t)$. The infinite sum telescopes:
    $$\sum_{t=0}^\infty \gamma^t \big( r_t + \gamma V^\pi(s_{t+1}) - V^\pi(s_t) \big) = \sum_{t=0}^\infty \gamma^t r_t - V^\pi(s_0)$$
    Taking expectations with respect to $\tilde{\pi}$:
    $$\mathbb{E}_{\tilde{\pi}} \left[ \sum_{t=0}^\infty \gamma^t A^\pi(s_t, a_t) \right] = J(\tilde{\pi}) - \mathbb{E}_{s_0}[V^\pi(s_0)] = J(\tilde{\pi}) - J(\pi)$$
  </p>
</div>

<h3>2.1 The Surrogate Lower Bound</h3>
<p>
  Because the true state distribution $d^{\tilde{\pi}}(s)$ is unknown, we define the <b>Surrogate Objective</b> using the old state distribution:
  $$L_\pi(\tilde{\pi}) = J(\pi) + \sum_{s} d^\pi(s) \sum_{a} \tilde{\pi}(a \mid s) A^\pi(s, a)$$
</p>

<div class="formula" style="border: 2px solid #2563eb; background: #eff6ff;">
  <b>The TRPO Monotonic Lower Bound (Schulman et al., 2015):</b><br>
  $$J(\tilde{\pi}) \ge L_\pi(\tilde{\pi}) - C \cdot D_{\text{KL}}^{\max}(\pi, \tilde{\pi})$$
  $$\text{where } C = \frac{4\epsilon\gamma}{(1-\gamma)^2} \quad \text{and} \quad D_{\text{KL}}^{\max}(\pi, \tilde{\pi}) = \max_s D_{\text{KL}}\big(\pi(\cdot|s) \,\|\, \tilde{\pi}(\cdot|s)\big)$$
</div>

<p>
  <b>The Monotonic Improvement Guarantee:</b> If we maximize the right-hand side, we are guaranteed that true performance $J(\tilde{\pi})$ will monotonically increase at every iteration!
</p>

<div class="page-break"></div>

<!-- PART 3 -->
<h2>Part 3: From Natural Policy Gradients &amp; TRPO to PPO</h2>
<p>
  <b>(Slides 36–52)</b> How do we optimize within a trust region in practice?
</p>

<h3>3.1 Natural Policy Gradient &amp; The Fisher Information Matrix</h3>
<p>
  Standard gradient descent steps in parameter Euclidean space: $\|\Delta \theta\|^2 \le \epsilon$. But in neural networks, a tiny shift in one layer's weight can cause a massive shift in output probabilities, while a large shift in another weight causes zero change!
  <b>Natural Policy Gradients</b> measure distance directly in probability distribution space using the <b>Fisher Information Matrix (FIM)</b> $F$:
</p>

<div class="formula">
  $$F(\theta) = \mathbb{E}_{s \sim d^\pi,\, a \sim \pi} \left[ \nabla_\theta \log \pi_\theta(a \mid s) \, \nabla_\theta \log \pi_\theta(a \mid s)^T \right]$$
  $$\Delta \theta_{\text{Natural}} \propto F^{-1} \nabla_\theta J(\theta)$$
</div>

<h3>3.2 TRPO: Trust Region Policy Optimization</h3>
<p>
  TRPO solves the constrained optimization problem:
  $$\max_\theta L_{\theta_{\text{old}}}(\theta) \quad \text{subject to} \quad \bar{D}_{\text{KL}}(\pi_{\theta_{\text{old}}} \,\|\, \pi_\theta) \le \delta$$
  Using second-order Taylor expansion on the constraint and first-order on the objective, TRPO solves:
  $$\Delta \theta = \sqrt{\frac{2\delta}{g^T F^{-1} g}} F^{-1} g$$
  where $g = \nabla_\theta L$. 
  To avoid inverting the massive $P \times P$ matrix $F$ directly, TRPO uses the <b>Conjugate Gradient (CG)</b> algorithm and <b>Fisher-Vector Products ($F v$)</b>.
</p>

<div class="warning-box">
  <div class="callout-title">The Downside of TRPO: Why Robotics Moved to PPO</div>
  <p>
    While TRPO is theoretically elegant, Conjugate Gradient requires multiple backpropagation passes per step to compute Fisher-vector products. It cannot be combined with first-order optimizers like Adam, struggles with recurrent networks, and is computationally prohibitive when scaling to 4,096 parallel GPU simulation environments in Isaac Lab.
  </p>
</div>

<div class="page-break"></div>

<!-- PART 4 -->
<h2>Part 4: Proximal Policy Optimization (PPO-Clip) Deconstructed</h2>
<p>
  <b>(Slides 53–70 &amp; Spinning Up ch16)</b> In 2017, John Schulman, Sergey Levine et al. introduced PPO to retain TRPO's monotonic stability while using simple, first-order gradient descent.
</p>

<h3>4.1 The Clipped Surrogate Objective</h3>
<p>
  Define the probability ratio:
  $$r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)}$$
</p>

<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>The PPO Clipped Surrogate Objective:</b><br>
  $$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min \left( r_t(\theta) \hat{A}_t,\; \operatorname{clip}\big(r_t(\theta),\, 1-\epsilon,\, 1+\epsilon\big) \hat{A}_t \right) \right]$$
</div>

<h3>4.2 The 4-Quadrant Analysis of PPO Clipping</h3>

<!-- SVG Diagram: The 2 PPO Curves -->
<div class="diagram-container">
<svg width="680" height="160" viewBox="0 0 680 160">
  <rect x="30" y="10" width="290" height="140" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
  <text x="175" y="32" font-size="10" font-weight="700" fill="#15803d" text-anchor="middle">Case 1: Advantage A &gt; 0 (Good Action)</text>
  
  <line x1="60" y1="120" x2="290" y2="120" stroke="#64748b" stroke-width="1.5"/>
  <line x1="60" y1="120" x2="60" y2="45" stroke="#64748b" stroke-width="1.5"/>
  
  <line x1="60" y1="110" x2="180" y2="65" stroke="#16a34a" stroke-width="2"/>
  <line x1="180" y1="65" x2="280" y2="65" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="3"/>
  
  <circle cx="180" cy="65" r="4" fill="#dc2626"/>
  <text x="180" y="55" font-size="8" font-weight="700" fill="#dc2626" text-anchor="middle">Clip: 1 + ε (1.2)</text>
  <text x="175" y="138" font-size="8" fill="#475569" text-anchor="middle">No extra reward for pushing r &gt; 1.2</text>

  <rect x="360" y="10" width="290" height="140" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="505" y="32" font-size="10" font-weight="700" fill="#b91c1c" text-anchor="middle">Case 2: Advantage A &lt; 0 (Bad Action)</text>
  
  <line x1="390" y1="65" x2="620" y2="65" stroke="#64748b" stroke-width="1.5"/>
  <line x1="390" y1="120" x2="390" y2="45" stroke="#64748b" stroke-width="1.5"/>

  <line x1="390" y1="65" x2="480" y2="65" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="3"/>
  <line x1="480" y1="65" x2="590" y2="110" stroke="#dc2626" stroke-width="2"/>

  <circle cx="480" cy="65" r="4" fill="#2563eb"/>
  <text x="480" y="55" font-size="8" font-weight="700" fill="#2563eb" text-anchor="middle">Clip: 1 - ε (0.8)</text>
  <text x="505" y="138" font-size="8" fill="#475569" text-anchor="middle">No penalty reduction below 0.8</text>
</svg>
</div>

<ol>
  <li><b>Positive Advantage ($A > 0$), Ratio $r \le 1+\epsilon$:</b> Normal policy gradient. The action was good, so we increase its probability.</li>
  <li><b>Positive Advantage ($A > 0$), Ratio $r > 1+\epsilon$:</b> The objective is <b>clipped</b> to $(1+\epsilon)A$. Gradient $\frac{\partial}{\partial \theta} = 0$. The optimizer is prevented from excessively over-committing to this move!</li>
  <li><b>Negative Advantage ($A < 0$), Ratio $r \ge 1-\epsilon$:</b> Normal policy gradient. The action was bad, so we decrease its probability.</li>
  <li><b>Negative Advantage ($A < 0$), Ratio $r < 1-\epsilon$:</b> The objective is <b>clipped</b> to $(1-\epsilon)A$. Gradient $\frac{\partial}{\partial \theta} = 0$. The optimizer is prevented from over-penalizing an already suppressed action!</li>
</ol>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Production Engineering with Isaac Lab &amp; SkRL</h2>

<div class="code-container">
<pre><span class="code-comment"># Complete Vectorized PPO Loss Function in PyTorch</span>
<span class="code-keyword">import</span> torch
<span class="code-keyword">import</span> torch.nn.functional <span class="code-keyword">as</span> F

<span class="code-keyword">def</span> <span class="code-func">compute_ppo_loss</span>(actor, critic, obs, actions, log_prob_old, returns, advantages, clip_eps=0.2, c_v=0.5, c_ent=0.01):
    <span class="code-comment"># 1. Evaluate current policy on historical batch</span>
    dist = actor(obs)
    log_prob_new = dist.log_prob(actions).sum(dim=-1, keepdim=True)
    entropy = dist.entropy().sum(dim=-1, keepdim=True).mean()
    
    <span class="code-comment"># 2. Probability Ratio r_t(theta)</span>
    ratio = torch.exp(log_prob_new - log_prob_old)
    
    <span class="code-comment"># 3. Clipped Surrogate Policy Loss</span>
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * advantages
    actor_loss = -torch.min(surr1, surr2).mean()
    
    <span class="code-comment"># 4. Value Loss (MSE with optional clipping)</span>
    values = critic(obs)
    critic_loss = c_v * F.mse_loss(values, returns)
    
    <span class="code-comment"># 5. Composite Loss</span>
    total_loss = actor_loss + critic_loss - c_ent * entropy
    <span class="code-keyword">return</span> total_loss, actor_loss, critic_loss, entropy
</pre>
</div>

<div class="silent-bug">
  <div class="callout-title">The Log-Prob Subtraction vs Ratio Trap</div>
  <p>
    Never compute the probability ratio via division: `ratio = pi_new / pi_old`. 
    Probabilities in continuous spaces or high-dimensional token spaces evaluate to microscopic values like $10^{-45}$, causing immediate division by zero and `NaN`. 
    Always compute log probabilities and exponentiate their difference:
    <br><code>ratio = torch.exp(log_prob_new - log_prob_old)</code>
  </p>
</div>

<div class="page-break"></div>

<!-- PART 6 -->
<h2>Part 6: Interactive Tablet Self-Test Quiz</h2>

<div class="quiz-box">
  <div class="quiz-q">Question 1: In PPO, what happens when an action yields a positive advantage ($A > 0$) and its probability ratio reaches $r_t(\theta) = 1.35$ (with $\epsilon = 0.2$)?</div>
  <div class="quiz-a">
    <b>Answer:</b> The ratio $1.35$ exceeds the upper clip boundary $1 + \epsilon = 1.2$. The objective term is clipped to $1.2 \times A$, causing the gradient with respect to policy weights $\theta$ to drop to exactly zero. This prevents the optimizer from aggressively over-committing to this single action.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 2: Why did OpenAI abandon PPO-Penalty (adaptive KL penalty) in favor of PPO-Clip?</div>
  <div class="quiz-a">
    <b>Answer:</b> PPO-Penalty requires continuous manual heuristics to scale the penalty coefficient $\beta$. If $\beta$ is tuned incorrectly, updates become either too conservative (freezing learning) or too aggressive (causing collapse). PPO-Clip enforces the trust region boundary directly in the objective with a fixed scalar $\epsilon = 0.2$, requiring zero hyperparameter tuning.
  </div>
</div>

<div class="quiz-box">
  <div class="quiz-q">Question 3: Why does `value_clip: 0.2` matter when the knife breaks through the tomato skin?</div>
  <div class="quiz-a">
    <b>Answer:</b> Cuticle rupture causes an abrupt drop in contact forces and a surge in rewards. Without value clipping, the Critic's loss would spike, causing a massive gradient update that distorts value predictions for all non-contact states. Value clipping restricts $V(s)$ updates to within $\pm 0.2$ of previous estimates, preserving value stability.
  </div>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 7: THESIS DEFENSE MASTER CHEATSHEET -->
<h2>Part 7: Thesis Defense Master Cheatsheet (Lecture 10 Focus)</h2>

<div class="callout intuition">
  <div class="callout-title">Q1: "What is Policy Collapse, and how does PPO prevent it during training?"</div>
  <p>
    <b>Answer:</b> "Policy collapse occurs in reinforcement learning when an oversized gradient step alters policy behavior such that all future rollouts result in failure. Because the policy collects its own training data, the replay buffer is corrupted with catastrophic trajectories, making recovery impossible. PPO prevents this by clipping the probability ratio $r_t(\theta) = \pi_\theta / \pi_{\text{old}}$ within $[1-\epsilon, 1+\epsilon]$ ($\epsilon=0.2$). This bounds the policy update to a local trust region, mathematically preventing destructive updates."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q2: "Why can PPO perform multiple training epochs on the same rollout batch, while REINFORCE cannot?"</div>
  <p>
    <b>Answer:</b> "REINFORCE assumes on-policy data sampled strictly from the current policy distribution. As soon as a single gradient step is taken, the policy changes, rendering the old rollout data off-policy and invalid. PPO incorporates an importance-sampling ratio $r_t(\theta)$ combined with surrogate clipping. This enables the algorithm to safely execute 4 to 8 gradient epochs on the same rollout buffer without causing policy divergence, dramatically increasing sample efficiency."
  </p>
</div>

<div class="callout intuition">
  <div class="callout-title">Q3: "Why choose PPO over TRPO for training in Isaac Lab?"</div>
  <p>
    <b>Answer:</b> "TRPO strictly enforces the trust region via a hard KL constraint ($\mathbb{E}[D_{\text{KL}}] \le \delta$), which requires computing the Fisher Information Matrix and solving a quadratic program using Conjugate Gradients. This is computationally expensive and difficult to parallelize on GPUs. PPO achieves equivalent empirical stability through a simple first-order clipped surrogate objective that integrates seamlessly with standard GPU optimizers like Adam."
  </p>
</div>

</body>
</html>
"""

if __name__ == "__main__":
    pdf_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture10_Beginner_Guide.pdf"
    backup_path = "/home/omen/Downloads/CS285_Lecture10_Beginner_Guide.pdf"
    render_utils.build_pdf(html_content, pdf_path, backup_path)
