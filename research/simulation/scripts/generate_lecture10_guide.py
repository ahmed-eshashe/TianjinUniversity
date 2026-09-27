import os
import weasyprint
import shutil

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mastering Advanced Policy Gradients & PPO: Beginner's Guide to CS285 Lecture 10</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @top-right {
      content: "CS285 Lecture 10: Advanced Policy Gradients & PPO";
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
  <span class="course-tag">UC Berkeley CS 185/285 • Lecture 10 Enhanced Study Guide</span>
  <h1>Mastering Advanced Policy Gradients &amp; PPO</h1>
  <div class="subtitle">Complete Beginner-Friendly Breakdown: Policy Collapse, Kakade-Langford Bounds, Natural Gradients, TRPO, PPO-Clip &amp; Massively Parallel Isaac Lab Simulation</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley)</span>
    <span><b>Companion:</b> DEX-ROB Lab, Tianjin University</span>
    <span><b>Frameworks:</b> Achiam (Spinning Up ch16) + Schulman &amp; Levine TRPO/PPO</span>
  </div>
</div>

<!-- SECTION 0 -->
<h2>0. The "Mental Map": Why Does Lecture 10 Exist?</h2>
<p>
  In Lecture 5 and Lecture 6, we derived the Policy Gradient Theorem and learned how to calculate policy updates. However, in standard gradient descent, taking a step that is even slightly too large can trigger a lethal disaster known as <b>Policy Collapse</b>.
</p>
<p>
  In computer vision, taking a bad gradient step just means your loss temporarily increases on the current batch; the next batch re-centers the network. <b>In reinforcement learning, the policy generates its own future training data.</b> If one oversized gradient step makes the robot slam the knife violently, every rollout in the next iteration will result in crushed tomatoes and zero reward. The policy enters an unrecoverable death spiral.
</p>
<p>
  <b>Lecture 10 introduces Trust Region Policy Optimization (TRPO) and Proximal Policy Optimization (PPO):</b> the algorithms that put a mathematical "safety leash" on policy updates, ensuring monotonic improvement and making deep RL robust enough to train complex robots in Isaac Lab.
</p>

<!-- SVG Diagram: The 5 Themes of Lecture 10 -->
<div class="diagram-container">
<svg width="680" height="90" viewBox="0 0 680 90">
  <rect x="5" y="10" width="125" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="67" y="36" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">1. Policy Collapse</text>
  <text x="67" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Why Bad Steps</text>
  <text x="67" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Permanently Crash RL</text>

  <rect x="140" y="10" width="125" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="202" y="36" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">2. State Shift</text>
  <text x="202" y="52" font-size="8.5" fill="#475569" text-anchor="middle">d^π(s) vs d^π_old(s):</text>
  <text x="202" y="66" font-size="8.5" fill="#475569" text-anchor="middle">The Distribution Gap</text>

  <rect x="275" y="10" width="125" height="70" rx="6" fill="#fdf4ff" stroke="#c084fc" stroke-width="1.5"/>
  <text x="337" y="36" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">3. TRPO &amp; KL</text>
  <text x="337" y="52" font-size="8.5" fill="#475569" text-anchor="middle">Fisher Matrix &amp;</text>
  <text x="337" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Conjugate Gradients</text>

  <rect x="410" y="10" width="125" height="70" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="1.5"/>
  <text x="472" y="36" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">4. PPO Clipping</text>
  <text x="472" y="52" font-size="8.5" fill="#475569" text-anchor="middle">min(rA, clip(r)A):</text>
  <text x="472" y="66" font-size="8.5" fill="#475569" text-anchor="middle">The Elegant Leash</text>

  <rect x="545" y="10" width="125" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="607" y="36" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">5. Isaac Lab Speed</text>
  <text x="607" y="52" font-size="8.5" fill="#475569" text-anchor="middle">4096 Envs Parallel</text>
  <text x="607" y="66" font-size="8.5" fill="#475569" text-anchor="middle">Epoch Reuse</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 1 -->
<h2>Part 1: The Catastrophe of Policy Collapse</h2>
<p>
  <b>(Slides 1–15, Spoken Transcript 02:10–16:40)</b> Sergey Levine explains why policy optimization is uniquely fragile compared to standard supervised learning.
</p>

<!-- SVG Diagram: Supervised vs RL Error Recovery -->
<div class="diagram-container">
<svg width="680" height="150" viewBox="0 0 680 150">
  <rect x="30" y="15" width="280" height="115" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="170" y="38" font-size="10.5" font-weight="700" fill="#1e40af" text-anchor="middle">Supervised Learning (Stable)</text>
  <text x="170" y="58" font-size="8.5" fill="#475569" text-anchor="middle">Fixed Dataset (ImageNet / COCO)</text>
  <text x="170" y="74" font-size="8.5" fill="#dc2626" text-anchor="middle">Oversized Step ➔ High Batch Loss</text>
  <text x="170" y="90" font-size="8.5" fill="#059669" text-anchor="middle">Next Batch: Recovers easily</text>
  <text x="170" y="108" font-size="8" fill="#3b82f6" text-anchor="middle">Data distribution never changes!</text>

  <rect x="370" y="15" width="280" height="115" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="510" y="38" font-size="10.5" font-weight="700" fill="#991b1b" text-anchor="middle">Reinforcement Learning (FRAGILE)</text>
  <text x="510" y="58" font-size="8.5" fill="#475569" text-anchor="middle">Policy generates its own future data!</text>
  <text x="510" y="74" font-size="8.5" fill="#dc2626" text-anchor="middle">Oversized Step ➔ Destructive Actions</text>
  <text x="510" y="90" font-size="8.5" fill="#b91c1c" font-weight="700" text-anchor="middle">Next Batch: 100% Crushed Tomatoes</text>
  <text x="510" y="108" font-size="8.5" font-weight="700" fill="#ef4444" text-anchor="middle">CATASTROPHIC COLLAPSE (No Recovery)</text>
</svg>
</div>

<h3>1.1 The State Distribution Mismatch</h3>
<p>
  When updating from $\pi_{\theta_{\text{old}}}$ to $\pi_\theta$, we want to optimize:
</p>
<div class="formula">
  J(\theta) = \mathbb{E}_{s \sim d^{\pi_\theta}(s)} \left[ \mathbb{E}_{a \sim \pi_\theta(a|s)} \left[ Q^{\pi_{\theta_{\text{old}}}}(s, a) \right] \right]
</div>
<p>
  In standard policy gradients, we sampled states from the <i>old</i> distribution $d^{\pi_{\theta_{\text{old}}}}(s)$, pretending that changing the policy would not change which states the robot visits.
  Levine asks: <i>"When is it mathematically permissible to ignore this distribution change?"</i>
  <b>Answer: Only when the new policy $\pi_\theta$ stays strictly within a bounded 'trust region' around $\pi_{\theta_{\text{old}}}$!</b>
</p>

<div class="page-break"></div>

<!-- PART 2 -->
<h2>Part 2: Bounding Policy Shift: Trust Regions &amp; KL Divergence</h2>
<p>
  <b>(Slides 16–35, Spoken Transcript 16:50–34:10)</b> In their 2015 paper, Schulman, Levine et al. derived the fundamental theoretical bound for policy optimization:
</p>

<h3>2.1 The Kakade-Langford / TRPO Bound</h3>
<div class="formula" style="border: 2px solid #2563eb; background: #eff6ff;">
  J(\pi') \ge J(\pi) + \sum_s d^\pi(s) \sum_a \pi'(a|s) A^\pi(s, a) - C \cdot D_{\text{KL}}^{\max}(\pi, \pi')
</div>
<p>
  Where $C = \frac{4 \epsilon \gamma}{(1-\gamma)^2}$ is a constant depending on discount factor and maximum advantage, and $D_{\text{KL}}^{\max}$ is the maximum Kullback-Leibler (KL) divergence between policies across all states.
</p>

<!-- SVG Diagram: Trust Region Sphere -->
<div class="diagram-container">
<svg width="680" height="150" viewBox="0 0 680 150">
  <rect x="80" y="10" width="520" height="130" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.5"/>
  <circle cx="340" cy="75" r="55" fill="#eff6ff" stroke="#3b82f6" stroke-width="2" stroke-dasharray="4"/>
  <text x="340" y="35" font-size="9.5" font-weight="700" fill="#1e40af" text-anchor="middle">Trust Region: D_KL(π_old || π) &lt;= ε</text>

  <circle cx="340" cy="75" r="6" fill="#1e293b"/>
  <text x="340" y="95" font-size="9" font-weight="700" fill="#1e293b" text-anchor="middle">Old Policy θ_old</text>

  <circle cx="375" cy="65" r="5" fill="#10b981"/>
  <line x1="340" y1="75" x2="375" y2="65" stroke="#10b981" stroke-width="2"/>
  <text x="400" y="65" font-size="8.5" font-weight="700" fill="#047857" text-anchor="start">Safe PPO Step</text>

  <circle cx="510" cy="40" r="5" fill="#ef4444"/>
  <line x1="340" y1="75" x2="510" y2="40" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="2"/>
  <text x="525" y="42" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="start">Unconstrained SGD (Collapse!)</text>
</svg>
</div>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 3 -->
<h2>Part 3: From Natural Policy Gradients &amp; TRPO to PPO</h2>
<p>
  <b>(Slides 36–52, Spoken Transcript 34:25–51:00)</b> How did researchers originally enforce this KL constraint?
</p>

<h3>3.1 Natural Policy Gradient &amp; TRPO</h3>
<p>
  Natural Gradients measure distance in distribution space rather than parameter Euclidean space, using the <b>Fisher Information Matrix $F$</b>:
  $\Delta \theta \propto F^{-1} \nabla_\theta J(\theta)$.
  TRPO solves this via <b>Conjugate Gradient (CG)</b>. While mathematically principled, inverting $F$ across 4,096 parallel environments is computationally prohibitive on GPU clusters.
</p>

<div class="page-break"></div>

<!-- PART 4 -->
<h2>Part 4: Proximal Policy Optimization (PPO) Deconstructed</h2>
<p>
  <b>(Slides 53–70 &amp; Spinning Up ch16)</b> In 2017, John Schulman, Sergey Levine et al. developed PPO to achieve TRPO's stability using first-order gradient descent.
</p>

<h3>4.1 The Clipped Surrogate Objective</h3>
<div class="formula">
  r_t(\theta) = \frac{\pi_\theta(a_t | s_t)}{\pi_{\theta_{\text{old}}}(a_t | s_t)}
</div>
<div class="formula" style="border: 2px solid #10b981; background: #ecfdf5;">
  <b>The PPO Clipped Objective:</b><br>
  L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min \left( r_t(\theta) \hat{A}_t,\; \text{clip}\big(r_t(\theta),\, 1-\epsilon,\, 1+\epsilon\big) \hat{A}_t \right) \right]
</div>

<!-- SVG Diagram: The 2 PPO Curves -->
<div class="diagram-container">
<svg width="680" height="170" viewBox="0 0 680 170">
  <rect x="30" y="15" width="290" height="140" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
  <text x="175" y="38" font-size="10.5" font-weight="700" fill="#15803d" text-anchor="middle">Case 1: Advantage A &gt; 0 (Good Action)</text>
  
  <line x1="60" y1="130" x2="290" y2="130" stroke="#64748b" stroke-width="1.5"/>
  <line x1="60" y1="130" x2="60" y2="50" stroke="#64748b" stroke-width="1.5"/>
  
  <line x1="60" y1="120" x2="180" y2="70" stroke="#16a34a" stroke-width="2"/>
  <line x1="180" y1="70" x2="280" y2="70" stroke="#16a34a" stroke-width="2.5" stroke-dasharray="3"/>
  
  <circle cx="180" cy="70" r="4" fill="#dc2626"/>
  <text x="180" y="60" font-size="8" font-weight="700" fill="#dc2626" text-anchor="middle">Clip: 1 + ε (1.2)</text>
  <text x="175" y="145" font-size="8" fill="#475569" text-anchor="middle">No extra reward for pushing r &gt; 1.2</text>

  <rect x="360" y="15" width="290" height="140" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="505" y="38" font-size="10.5" font-weight="700" fill="#b91c1c" text-anchor="middle">Case 2: Advantage A &lt; 0 (Bad Action)</text>
  
  <line x1="390" y1="70" x2="620" y2="70" stroke="#64748b" stroke-width="1.5"/>
  <line x1="390" y1="130" x2="390" y2="50" stroke="#64748b" stroke-width="1.5"/>

  <line x1="390" y1="70" x2="480" y2="70" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="3"/>
  <line x1="480" y1="70" x2="590" y2="120" stroke="#dc2626" stroke-width="2"/>

  <circle cx="480" cy="70" r="4" fill="#2563eb"/>
  <text x="480" y="60" font-size="8" font-weight="700" fill="#2563eb" text-anchor="middle">Clip: 1 - ε (0.8)</text>
  <text x="505" y="145" font-size="8" fill="#475569" text-anchor="middle">No penalty reduction below 0.8</text>
</svg>
</div>

<h3>4.2 KL Early Stopping Heuristic (Achiam ch16)</h3>
<p>
  Even with ratio clipping, running 5 to 8 epochs over a batch can cause the policy to drift excessively. 
  In *Spinning Up in Deep RL*, Joshua Achiam documents the canonical early-stopping rule:
</p>
<div class="formula">
  \text{If } \bar{D}_{\text{KL}}(\pi_{\text{old}} || \pi_\theta) > 1.5 \times d_{\text{target}} \implies \text{Terminate Epoch Loop Immediately!}
</div>
<p>
  In your SkRL configuration, setting `kl_threshold: 0.015` enforces this exact safety brake.
</p>

<div class="callout silent-bug">
  <div class="callout-title">Spinning Up Bug Alert: Premature Batch Flattening</div>
  <p>
    In parallel environments, observations arrive as `[T, num_envs, 33]`. 
    <b>Never flatten the temporal dimension before computing GAE!</b> 
    Advantages and returns must be calculated backwards through the temporal structure. If you flatten `[T, num_envs]` into `[T * num_envs]` before running GAE, the terminal step of environment 0 will erroneously bootstrap into the initial step of environment 1, corrupting credit assignment!
  </p>
</div>

<div class="page-break"></div>

<!-- PART 5 -->
<h2>Part 5: Why Isaac Lab &amp; Robotics Simulation Are Built for PPO</h2>
<p>
  <b>(Slides 71–85, Spoken Transcript 1:12:45–1:24:00)</b> Why is PPO the undisputed default algorithm across modern GPU-accelerated robotics frameworks (NVIDIA Isaac Lab, Isaac Gym, Orbit)?
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Feature</th>
      <th style="width: 35%;">Standard RL (e.g., REINFORCE / SAC)</th>
      <th style="width: 40%;">Isaac Lab + PPO Synergy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Data Reuse</b></td>
      <td>On-policy REINFORCE must discard all rollouts after <i>one</i> gradient step.</td>
      <td><b>4 to 8 Epochs per Rollout:</b> Because clipping prevents policy collapse, PPO safely loops over the same simulation batch multiple times!</td>
    </tr>
    <tr>
      <td><b>Parallel Scalability</b></td>
      <td>Off-policy SAC struggles with 4,096 parallel streams because maintaining a 10M transition replay buffer exhausts GPU VRAM.</td>
      <td><b>Direct On-Policy Streaming:</b> Collect 64 steps across 4,096 parallel environments ($262,144$ transitions in 50 ms), optimize PPO, and flush buffer.</td>
    </tr>
    <tr>
      <td><b>Optimizer Stability</b></td>
      <td>TRPO requires complex second-order Conjugate Gradient solvers.</td>
      <td>Standard first-order <b>Adam optimizer</b> with gradient clipping ($1.0$). Zero matrix inversions.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">

<!-- PART 6 -->
<h2>Part 6: Paper 1 Production Configuration: SkRL `ppo_cfg.yaml`</h2>

<div class="code-block">
# Production PPO Configuration for Dual-Arm Compliant Tomato Slicing
agent:
  class: PPO
  rollouts: 64                 # Steps collected per environment per iteration
  learning_epochs: 5           # Passes over rollout buffer (safe due to clipping)
  mini_batches: 8              # Sub-batches per epoch (32,768 transitions per mini-batch)
  discount_factor: 0.99        # γ: Value horizon (~200 steps at 60 Hz)
  lambda: 0.95                 # GAE-λ: Optimal contact bias/variance tradeoff
  learning_rate: 3.0e-4        # Adam initial learning rate
  learning_rate_scheduler: AdaptiveKL
  learning_rate_scheduler_kwargs:
    kl_threshold: 0.015        # Dynamic safety brake: drops LR if policy drifts
  ratio_clip: 0.2              # PPO trust region parameter ε = 0.2
  value_clip: 0.2              # Prevents Critic value predictions from exploding
  clip_predicted_values: True
  entropy_loss_scale: 0.005    # Light entropy bonus to maintain exploratory sawing
  value_loss_scale: 1.0        # Critic loss weight
  grad_norm_clip: 1.0          # Max gradient norm to guard against contact force spikes

models:
  separate: True               # Separate Actor and Critic (prevents gradient competition)
  policy:
    class: GaussianMixin
    clip_actions: True
    network:
      - name: net
        type: linear
        layers: [256, 128, 64]
        activations: [elu, elu, elu]
  value:
    class: DeterministicMixin
    network:
      - name: net
        type: linear
        layers: [256, 128, 64]
        activations: [elu, elu, elu]
</div>

<div class="page-break"></div>

<!-- PART 7: SELF-TEST QUIZ -->
<h2>Part 7: Interactive Tablet Self-Test Quiz (Test Your Understanding)</h2>

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

<!-- PART 8: THESIS DEFENSE -->
<h2>Part 8: Thesis Defense Master Cheatsheet (Lecture 10 Focus)</h2>

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

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
<div style="text-align: center; font-size: 8.5pt; color: #64748b;">
  CS 285 Lecture 10 Comprehensive Study Guide • Prepared for DEX-ROB Lab, Tianjin University
</div>

</body>
</html>
"""

output_path = "/home/omen/Downloads/CS285_Lecture10_Beginner_Guide.pdf"
backup_path = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture10_Beginner_Guide.pdf"

print("Compiling Enhanced Lecture 10 PDF with WeasyPrint...")
html = weasyprint.HTML(string=html_content)
html.write_pdf(output_path)
print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

shutil.copyfile(output_path, backup_path)
print(f"Copied to: {backup_path}")
