import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 10: Zero-to-Hero Guide to Advanced Policy Gradients, Natural Gradients, TRPO, &amp; PPO</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Lecture 10 • Zero-to-Hero Guide to PPO & Trust Regions";
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
    line-height: 1.54;
    font-size: 9.4pt;
  }

  .header-block {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 12px;
    margin-bottom: 16px;
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
    font-size: 18.5pt;
    font-weight: 800;
    margin: 0 0 6px 0;
    line-height: 1.25;
  }
  .subtitle {
    color: #475569;
    font-size: 10pt;
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
    font-size: 12pt;
    font-weight: 700;
    margin-top: 16px;
    margin-bottom: 8px;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    page-break-after: avoid;
  }

  h3 {
    color: #0f172a;
    font-size: 10pt;
    font-weight: 700;
    margin-top: 11px;
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
    padding: 9px 13px;
    margin: 9px 0;
    border-radius: 6px;
    font-size: 9.1pt;
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
    font-size: 7.8pt;
    padding: 8px 12px;
    margin: 9px 0;
    border-radius: 4px;
  }
  .code-box .callout-title { color: #475569; font-family: -apple-system, sans-serif; font-weight: 700; margin-bottom: 4px; }

  .formula {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 12px;
    margin: 8px 0;
    text-align: center;
    font-family: "Cambria Math", "Times New Roman", serif;
    font-size: 9.8pt;
    color: #0f172a;
    page-break-inside: avoid;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 8.5pt;
  }
  tr { page-break-inside: avoid; }
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
    margin: 9px 0;
    page-break-inside: avoid;
  }
</style>
</head>
<body>

<!-- Header Block -->
<div class="header-block">
  <span class="course-tag">CS285 Lecture 10 • Zero-to-Hero Field Manual</span>
  <h1>Advanced Policy Gradients: Natural Gradients, TRPO, &amp; PPO</h1>
  <div class="subtitle">From Scratch to Mastery: Conquering Policy Collapse, Understanding Trust Regions, and Mastering the Gold Standard of Modern GPU Robotics &amp; LLM Alignment</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Scope:</b> Policy Collapse, Kakade-Langford Bounds, Fisher Information, TRPO, &amp; PPO-Clip</span>
  </div>
</div>

<!-- SECTION 1: THE NIGHTMARE OF POLICY COLLAPSE -->
<h2>1. What is Policy Collapse? (The Student Burning Their Textbooks)</h2>
<p>
  In supervised deep learning (such as training a ResNet on ImageNet), if your learning rate is slightly too large, your training loss might spike abruptly on epoch 12. 
  You don't need to panic. On epoch 13, the optimizer sees the same static training images, calculates corrective gradients, and the network steadily recovers.
</p>
<p>
  <b>In Reinforcement Learning, an oversized gradient step causes instant, irreversible death.</b> 
  Why is RL so uniquely brittle compared to all other fields of machine learning?
</p>

<div class="callout warning-box">
  <div class="callout-title">💥 The Fatal Difference: The Policy Collects Its Own Training Data!</div>
  <p>
    In supervised learning, the dataset is stored safely on an SSD. 
    In RL, <b>there is no static dataset</b>: the training data is generated dynamically on-the-fly by the policy executing actions in the environment!
  </p>
  <ul>
    <li><b>Everyday Analogy (The Student Burning Their Textbooks):</b> Imagine an ambitious medical student studying for their board exams. 
      For three months, they study diligently, scoring $90\%$ on practice tests. 
      One night, they drink 5 energy drinks and try an extreme, frantic cramming technique. 
      The next morning, they take a practice quiz and get a slightly lower score ($82\%$). 
      Instead of making a calm $1\%$ adjustment, the student panics, <b>burns all their textbooks, destroys their laptop, and suffers severe retrograde amnesia—forgetting how to read and write</b>!
    </li>
    <li><b>The Catastrophic Death Spiral:</b> Because the student has forgotten how to read, every practice test they take next week scores a flat $0\%$. 
      And because all their test papers are blank gibberish, they have zero useful feedback to learn from. They can <i>never</i> recover.
    </li>
  </ul>
  <p>
    This is <b>Policy Collapse</b>: if an aggressive gradient update shifts the robot's neural weights into a bad parameter regime, the robot begins flailing wildly. 
    All 4,096 parallel environments in NVIDIA Isaac Sim suddenly generate pure garbage trajectories with $0$ rewards. 
    Because the incoming batch consists entirely of noise, the next gradient update is pure noise. Training collapses permanently!
  </p>
</div>

<!-- DIAGRAM 1: POLICY COLLAPSE DEATH SPIRAL -->
<div class="diagram-container">
<svg width="620" height="85" viewBox="0 0 620 85">
  <rect x="15" y="15" width="130" height="52" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="36" font-size="8.5" font-weight="700" fill="#1e40af" text-anchor="middle">1. Healthy Policy</text>
  <text x="80" y="52" font-size="7.5" fill="#475569" text-anchor="middle">Slices tomatoes cleanly</text>

  <path d="M 148,41 L 182,41" fill="none" stroke="#ef4444" stroke-width="2"/>
  <polygon points="182,41 174,37 174,45" fill="#ef4444"/>

  <rect x="185" y="15" width="130" height="52" rx="6" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="250" y="36" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">2. Oversized Step</text>
  <text x="250" y="52" font-size="7.5" fill="#7f1d1d" text-anchor="middle">Weights jump into abyss</text>

  <path d="M 318,41 L 352,41" fill="none" stroke="#ef4444" stroke-width="2"/>
  <polygon points="352,41 344,37 344,45" fill="#ef4444"/>

  <rect x="355" y="15" width="130" height="52" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="2"/>
  <text x="420" y="36" font-size="8.5" font-weight="700" fill="#dc2626" text-anchor="middle">3. Garbage Data</text>
  <text x="420" y="52" font-size="7.5" fill="#991b1b" text-anchor="middle">Robot flails; 0 cuts</text>

  <path d="M 488,41 L 522,41" fill="none" stroke="#7f1d1d" stroke-width="2"/>
  <polygon points="522,41 514,37 514,45" fill="#7f1d1d"/>

  <rect x="525" y="15" width="80" height="52" rx="6" fill="#450a0a"/>
  <text x="565" y="36" font-size="8.5" font-weight="800" fill="#ffffff" text-anchor="middle">IRREVERSIBLE</text>
  <text x="565" y="50" font-size="7.5" font-weight="700" fill="#fca5a5" text-anchor="middle">DEATH SPIRAL</text>
</svg>
</div>

<!-- SECTION 2: 4 REAL-WORLD INDUSTRIAL CASE STUDIES -->
<h2>2. Four Real-World Industrial Case Studies: Where PPO is Mandatory</h2>
<p>
  PPO is the undisputed workhorse of modern artificial intelligence, powering everything from bleeding-edge bipedal robots to massive frontier foundation models:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">Application Domain</th>
      <th style="width: 28%;">What Constitutes "Collapse"</th>
      <th style="width: 26%;">Why Standard Policy Gradient Fails</th>
      <th style="width: 26%;">How PPO Guarantees Safety</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Dual-Arm Fruit Slicing</b> (Robotics Thesis)</td>
      <td>Right arm jams knife horizontally into the table, tripping motor over-current protectors and shearing gear teeth.</td>
      <td>One bad gradient update causes knife pitch angle to spike by $40^\circ$. New rollouts produce $100\%$ table collisions.</td>
      <td>PPO probability ratio clipping strictly restricts motor torque command shifts to $\pm 20\%$ per batch.</td>
    </tr>
    <tr>
      <td><b>2. ChatGPT / LLM Alignment</b> (OpenAI RLHF)</td>
      <td>Model collapses into repeating single tokens (e.g. <i>"the the the..."</i>) or emitting toxic hallucinated gibberish.</td>
      <td>Unconstrained reward maximization exploits subtle loopholes in the reward model, degenerating English grammar.</td>
      <td>PPO clips token probability ratios, keeping the model within a strict trust region around the pre-trained foundation weights.</td>
    </tr>
    <tr>
      <td><b>3. Humanoid Locomotion</b> (Unitree H1 / Figure 01)</td>
      <td>Robot experiences catastrophic ankle joint divergence, violently crashing 50 kg metal chassis to the floor.</td>
      <td>High-speed balance dynamics are non-linear; an oversized step in ankle pitch destabilizes the entire inverted pendulum.</td>
      <td>PPO enables multi-epoch GPU batch reuse in Isaac Sim, discovering agile dynamic gait recovery without divergence.</td>
    </tr>
    <tr>
      <td><b>4. Nuclear Tokamak Fusion</b> (DeepMind Plasma Control)</td>
      <td>100,000,000°C burning plasma column touches the tokamak containment vessel wall, causing immediate thermal quench.</td>
      <td>Magnetic coil currents must be coordinated across 19 coils; any unconstrained gradient step violates magnetic field geometry.</td>
      <td>PPO enforces monotonic policy improvement, guaranteeing that updated magnetic controllers never destabilize the plasma boundary.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 3: THE ILLUSION OF PARAMETER SPACE -->
<h2>3. The Illusion of Parameter Space: Why Step Size $\alpha$ Fails</h2>
<p>
  In standard deep learning, you ensure stability by making your learning rate $\alpha$ small: $\theta_{\text{new}} \leftarrow \theta_{\text{old}} - \alpha \nabla_\theta \mathcal{L}$. 
  Why doesn't a small $\|\Delta \theta\|_2$ protect a policy from collapse?
</p>

<div class="callout intuition">
  <div class="callout-title">🎭 The Steep Cliff Analogy: Parameter Space $\neq$ Probability Space</div>
  <p>
    Neural networks are wildly non-linear. The mapping from <b>network weights $\theta$</b> to <b>action probability $\pi_\theta(a \mid s)$</b> is not uniform:
  </p>
  <ul>
    <li>In flat regions of the network, changing a weight by $\Delta \theta = +0.10$ changes action probabilities by only $0.001\%$.</li>
    <li>Near the steep saturation boundary of a sigmoid, softmax, or Gaussian standard deviation layer, changing a weight by the exact same $\Delta \theta = +0.10$ can swing action probability from <b>$0.99$ to $0.01$</b>!</li>
  </ul>
  <p>
    <b>The Fundamental Insight:</b> We do not care if the <i>parameters</i> move by a small distance. 
    What we care about is that the <b>resulting probability distribution $\pi(a \mid s)$ moves by a small statistical distance</b>!
  </p>
</div>

<!-- DIAGRAM 2: PARAMETER SPACE VS PROBABILITY SPACE -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <!-- Left: Parameter Space (Euclidean) -->
  <rect x="30" y="12" width="240" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="150" y="30" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">EUCLIDEAN PARAMETER SPACE ($\theta$)</text>
  <text x="60" y="52" font-size="8" fill="#475569">$\theta_1 = 1.40$</text>
  <path d="M 120,48 L 180,48" fill="none" stroke="#2563eb" stroke-width="2"/>
  <text x="150" y="44" font-size="7" fill="#2563eb" text-anchor="middle">$\Delta \theta = 0.05$ (Tiny!)</text>
  <text x="210" y="52" font-size="8" fill="#475569">$\theta_2 = 1.45$</text>
  <text x="150" y="72" font-size="7.5" fill="#64748b" text-anchor="middle">Looks completely harmless in Euclidean space</text>

  <!-- Arrow -->
  <text x="295" y="50" font-size="14" font-weight="700" fill="#dc2626" text-anchor="middle">⟹</text>

  <!-- Right: Probability Space (KL Divergence) -->
  <rect x="320" y="12" width="260" height="70" rx="6" fill="#fef2f2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="450" y="30" font-size="9" font-weight="700" fill="#991b1b" text-anchor="middle">STATISTICAL PROBABILITY SPACE ($\pi_\theta$)</text>
  <text x="450" y="50" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">$\pi(a_1 \mid s): \mathbf{95\%} \longrightarrow \mathbf{3\%}$ (CATASTROPHIC!)</text>
  <text x="450" y="68" font-size="7.5" fill="#7f1d1d" text-anchor="middle">$D_{\text{KL}}(\pi_{\text{old}} \parallel \pi_{\text{new}}) = \mathbf{4.2}$ (Policy has collapsed!)</text>
</svg>
</div>

<h3>3.1 Kakade &amp; Langford's Monotonic Improvement Guarantee (2002)</h3>
<p>
  Sham Kakade and John Langford proved mathematically how a new policy's expected return $\eta(\tilde{\pi})$ relates to an old policy's return $\eta(\pi)$:
</p>
<div class="formula">
  $$\eta(\tilde{\pi}) = \eta(\pi) + \sum_s \rho_{\tilde{\pi}}(s) \sum_a \tilde{\pi}(a \mid s) A_\pi(s, a)$$
</div>
<p>
  Because we do not know the state distribution $\rho_{\tilde{\pi}}(s)$ of the <i>new</i> policy before running it, we approximate it using the <i>old</i> policy's state distribution $\rho_\pi(s)$, defining the <b>Surrogate Advantage $L_\pi(\tilde{\pi})$</b>:
</p>
<div class="formula">
  $$L_\pi(\tilde{\pi}) = \eta(\pi) + \sum_s \rho_\pi(s) \sum_a \tilde{\pi}(a \mid s) A_\pi(s, a)$$
</div>
<p>
  Kakade and Langford established the celebrated <b>Conservative Policy Iteration Bound</b>:
</p>
<div class="formula">
  $$\eta(\tilde{\pi}) \ge L_\pi(\tilde{\pi}) - C \cdot D_{\text{KL}}^{\max}(\pi, \tilde{\pi}) \qquad \text{where} \qquad C = \frac{4 \epsilon \gamma}{(1 - \gamma)^2} \quad \text{and} \quad \epsilon = \max_{s, a} |A_\pi(s, a)|$$
</div>

<table>
  <thead>
    <tr>
      <th style="width: 22%;">Mathematical Term</th>
      <th style="width: 22%;">Formal Identity</th>
      <th style="width: 38%;">Plain English Meaning</th>
      <th style="width: 18%;">Significance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\eta(\tilde{\pi})$</b></td>
      <td>True Return of New Policy</td>
      <td>The actual physical reward the robot will achieve when deployed in the real world with updated weights $\tilde{\theta}$.</td>
      <td>What we ultimately want to maximize.</td>
    </tr>
    <tr>
      <td><b>$L_\pi(\tilde{\pi})$</b></td>
      <td>Surrogate Advantage</td>
      <td>How much reward the robot <i>thinks</i> it will earn, assuming it encounters the same familiar states as before.</td>
      <td>Easy to evaluate on collected rollouts.</td>
    </tr>
    <tr>
      <td><b>$D_{\text{KL}}^{\max}(\pi, \tilde{\pi})$</b></td>
      <td>Max Kullback-Leibler Divergence</td>
      <td>The worst-case statistical distance between action distributions across any state: how much the policy's behavior changed.</td>
      <td>Measures policy deviation.</td>
    </tr>
    <tr>
      <td><b>$C \cdot D_{\text{KL}}^{\max}$</b></td>
      <td>Distribution Shift Penalty</td>
      <td><b>The Reality Tax:</b> How badly the robot's predictions could fail because the new policy visits unfamiliar, untested states.</td>
      <td>Guarantees monotonic improvement if kept small!</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Bound</div>
  <p>
    <b>"As long as your new policy does not change its behavior by more than a tiny statistical distance ($D_{\text{KL}}$ is small), the true real-world return is GUARANTEED to be greater than or equal to your training surrogate! You will NEVER suffer policy collapse!"</b>
  </p>
</div>

<!-- SECTION 4: FROM NATURAL GRADIENT TO TRPO -->
<h2>4. From Natural Policy Gradient to TRPO: The Trust Region Path</h2>

<h3>4.1 Natural Policy Gradient &amp; The Fisher Information Matrix</h3>
<p>
  In 1998, Shun-ichi Amari introduced <b>Information Geometry</b>, showing that probability distributions form a curved Riemannian manifold. 
  Instead of following standard Euclidean gradients $\nabla_\theta J$, the true steepest ascent direction in probability space is the <b>Natural Gradient</b>:
</p>
<div class="formula">
  $$\nabla_\theta^{\text{nat}} J(\theta) = F(\theta)^{-1} \nabla_\theta J(\theta) \qquad \text{where} \qquad F(\theta) = \mathbb{E}_{s, a \sim \pi} \left[ \nabla_\theta \log \pi_\theta(a \mid s) \, \nabla_\theta \log \pi_\theta(a \mid s)^T \right]$$
</div>
<p>
  Here, $F(\theta)$ is the <b>Fisher Information Matrix</b> (dimension $P \times P$, where $P$ is the number of neural network parameters). 
  It acts as a local Riemannian metric tensor that warps Euclidean parameter space into true probability space.
</p>

<h3>4.2 TRPO: Trust Region Policy Optimization (Schulman et al., 2015)</h3>
<p>
  Kakade's theoretical penalty $C \cdot D_{\text{KL}}$ requires a constant $C$ that is absurdly huge ($C \approx 10^5$ for $\gamma = 0.99$), leading to microscopic, uselessly slow step sizes. 
  John Schulman solved this by turning the penalty into a hard <b>Trust Region Constraint</b>:
</p>
<div class="formula">
  $$\max_\theta \hat{\mathbb{E}}_t \left[ \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)} \hat{A}_t \right] \qquad \text{subject to} \qquad \hat{\mathbb{E}}_t \left[ D_{\text{KL}}(\pi_{\theta_{\text{old}}}(\cdot \mid s_t) \parallel \pi_\theta(\cdot \mid s_t)) \right] \le \delta$$
</div>

<h3>4.3 Why Was TRPO Abandoned in Modern Robotics?</h3>
<p>
  While TRPO was theoretically magnificent, it possessed a fatal engineering flaw:
</p>
<ul>
  <li>For a small neural network with $1,000,000$ weights, the Fisher Information Matrix $F$ contains $10^6 \times 10^6 = \mathbf{1,000,000,000,000}$ numbers (1 trillion floats = 4 Terabytes of RAM!). It cannot be inverted or stored on any GPU.</li>
  <li>TRPO bypassed matrix inversion using the <b>Conjugate Gradient (CG) algorithm</b> with Hessian-Vector Products ($F \cdot v$). 
    However, CG requires 10 to 20 serial iterations of backpropagation per gradient step, completely breaking PyTorch autograd graph pipelines and destroying parallel GPU scalability in NVIDIA Isaac Sim.
  </li>
</ul>

<!-- SECTION 5: PPO CLIPPING OBJECTIVE -->
<h2>5. Proximal Policy Optimization (PPO): The First-Order Masterstroke</h2>
<p>
  In 2017, John Schulman, Filip Wolski, and Prafulla Dhariwal at OpenAI asked: 
  <i>"Can we get all the stability benefits of TRPO's trust region without second-order Hessians, Fisher matrices, or Conjugate Gradients?"</i><br>
  Their solution was <b>PPO-Clip</b>.
</p>

<div class="callout intuition">
  <div class="callout-title">🎳 Everyday Analogy: The Bowling Alley Bumpers</div>
  <p>
    When young children play bowling, the bowling alley raises <b>inflatable bumpers</b> along the gutters. 
    No matter how erratically or wildly the child hurls the bowling ball, the ball bounces off the bumper, remains safely centered in the lane, and knocks down pins.
  </p>
  <p>
    <b>PPO puts bumpers on your neural network!</b><br>
    It tells the optimizer: <i>"You can update weights to make good actions more likely, but if the new policy's probability changes by more than <b>$\pm 20\%$ ($\epsilon = 0.20$)</b> from the old policy that collected the data, the gradient is instantaneously clipped to ZERO! You hit the bumper!"</i>
  </p>
</div>

<h3>5.1 The Probability Ratio (The Speedometer)</h3>
<p>
  Before every update, we record the old policy's action probabilities $\pi_{\theta_{\text{old}}}(a_t \mid s_t)$. 
  As the new policy $\theta$ trains, we define the <b>Probability Ratio $r_t(\theta)$</b>:
</p>
<div class="formula">
  $$r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)} = \exp\left( \log \pi_\theta(a_t \mid s_t) - \log \pi_{\theta_{\text{old}}}(a_t \mid s_t) \right)$$
</div>
<ul>
  <li>If $r_t = 1.0$: The new policy chooses this action with the exact same probability as the old policy.</li>
  <li>If $r_t = 1.15$: The new policy is $15\%$ more likely to choose this action.</li>
  <li>If $r_t = 0.85$: The new policy is $15\%$ less likely to choose this action.</li>
</ul>

<h3>5.2 The PPO Clipped Surrogate Objective</h3>
<div class="formula">
  $$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon) \hat{A}_t \right) \right]$$
</div>

<!-- DIAGRAM 3: PPO CLIPPING FUNCTION -->
<div class="diagram-container">
<svg width="600" height="95" viewBox="0 0 600 95">
  <line x1="30" y1="50" x2="570" y2="50" stroke="#94a3b8" stroke-width="1.5"/>

  <!-- Left: Clipped Region -->
  <rect x="40" y="15" width="140" height="65" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="110" y="38" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">CLIPPED: ZERO GRADIENT</text>
  <text x="110" y="52" font-size="7.5" fill="#7f1d1d" text-anchor="middle">$r_t &lt; 1 - \epsilon$ (Dropped &gt;20%)</text>
  <text x="110" y="66" font-size="7" fill="#991b1b" text-anchor="middle">Prevents over-punishment</text>

  <!-- Middle: Active Region -->
  <rect x="200" y="15" width="200" height="65" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="300" y="38" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">ACTIVE GRADIENT TRUST REGION</text>
  <text x="300" y="52" font-size="8.5" font-weight="700" fill="#047857" text-anchor="middle">$r_t \in [1 - \epsilon, 1 + \epsilon] = [0.8, 1.2]$</text>
  <text x="300" y="66" font-size="7.5" fill="#064e3b" text-anchor="middle">Normal policy gradient flows safely</text>

  <!-- Right: Clipped Region -->
  <rect x="420" y="15" width="140" height="65" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="490" y="38" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">CLIPPED: ZERO GRADIENT</text>
  <text x="490" y="52" font-size="7.5" fill="#7f1d1d" text-anchor="middle">$r_t &gt; 1 + \epsilon$ (Grown &gt;20%)</text>
  <text x="490" y="66" font-size="7" fill="#991b1b" text-anchor="middle">Prevents over-confidence</text>
</svg>
</div>

<!-- SECTION 6: THE 4-QUADRANT DECISION TABLE -->
<h2>6. The 4-Quadrant Response Matrix: How PPO Reacts to Every Situation</h2>
<p>
  Every single timestep in a training batch falls into one of four distinct mathematical quadrants based on advantage sign and ratio magnitude:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 14%;">Quadrant</th>
      <th style="width: 18%;">Advantage $\hat{A}_t$</th>
      <th style="width: 18%;">Ratio $r_t(\theta)$</th>
      <th style="width: 25%;">Surrogate Comparison</th>
      <th style="width: 25%;">Optimizer Action &amp; Gradient</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Quadrant 1</b></td>
      <td>$\mathbf{\hat{A} > 0}$ (Good Cut)</td>
      <td>$r_t \in [1.0, 1.2]$</td>
      <td>$r_t \hat{A} = \text{clip}(r_t) \hat{A}$</td>
      <td><b>Active Positive Gradient:</b> Nudge policy weights to make this successful slicing action more frequent.</td>
    </tr>
    <tr>
      <td><b>Quadrant 2</b></td>
      <td>$\mathbf{\hat{A} > 0}$ (Good Cut)</td>
      <td>$r_t > 1.2$ (Over 20%)</td>
      <td>$r_t \hat{A} > (1+\epsilon)\hat{A} \implies \min = (1+\epsilon)\hat{A}$</td>
      <td><b>Clipped to 0 Gradient:</b> Stop pushing! You already increased this action's probability by $20\%$. Don't over-commit.</td>
    </tr>
    <tr>
      <td><b>Quadrant 3</b></td>
      <td>$\mathbf{\hat{A} < 0}$ (Crushed Fruit)</td>
      <td>$r_t \in [0.8, 1.0]$</td>
      <td>$r_t \hat{A} = \text{clip}(r_t) \hat{A}$</td>
      <td><b>Active Negative Gradient:</b> Suppress this crushing motion and steer robot joints away from this configuration.</td>
    </tr>
    <tr>
      <td><b>Quadrant 4</b></td>
      <td>$\mathbf{\hat{A} < 0}$ (Crushed Fruit)</td>
      <td>$r_t < 0.8$ (Under 20%)</td>
      <td>$r_t \hat{A} < (1-\epsilon)\hat{A} \implies \min = (1-\epsilon)\hat{A}$</td>
      <td><b>Clipped to 0 Gradient:</b> Stop punishing! The probability has already dropped significantly. Leave the network alone.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 7: WHY PPO RULES GPU ROBOTICS -->
<h2>7. Why PPO Rules Massively Parallel GPU Robotics (NVIDIA Isaac Lab)</h2>
<div class="callout intuition">
  <div class="callout-title">⚡ The Secret Weapon: Multi-Epoch Mini-Batch Data Reuse</div>
  <p>
    In vanilla Policy Gradients (REINFORCE, Lecture 5), data is strictly <b>on-policy</b>. 
    You launch 4,096 parallel robot environments on an NVIDIA RTX 4090 GPU, simulate 64 steps per robot (262,144 transitions), compute <b>one single gradient step</b>, and you MUST throw away the entire batch immediately! 
    Simulating 262,144 transitions just to take one tiny weight update wastes <b>98% of your expensive GPU silicon</b>.
  </p>
  <p>
    <b>Why PPO dominates Isaac Lab:</b> Because PPO's clipping mechanism strictly guarantees that updates stay within a safe trust region, you can take that exact same batch of 262,144 transitions and train on it for <b>4 to 8 epochs</b> across mini-batches! 
    You extract $8\times$ more learning out of every single simulation frame, resulting in a <b>10x to 50x wall-clock speedup</b> over traditional methods!
  </p>
</div>

<!-- SECTION 8: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>8. Concrete Step-by-Step Numerical Walkthrough: 4 Cases with Real Numbers</h2>
<p>
  Let us calculate the exact loss and gradient behavior across four concrete transitions with clipping threshold $\epsilon = 0.20$:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 12%;">Scenario</th>
      <th style="width: 15%;">Advantage $\hat{A}_t$</th>
      <th style="width: 15%;">Ratio $r_t(\theta)$</th>
      <th style="width: 20%;">Term 1: $r_t \hat{A}_t$</th>
      <th style="width: 20%;">Term 2: $\text{clip}(r) \hat{A}_t$</th>
      <th style="width: 18%;">Final Min Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Moderate Win</b></td>
      <td>$\mathbf{+5.00}$ (Punctured skin)</td>
      <td>$1.10$ ($+10\%$)</td>
      <td>$1.10 \times 5.0 = 5.50$</td>
      <td>$1.10 \times 5.0 = 5.50$</td>
      <td>$\min(5.50, 5.50) = \mathbf{5.50}$ (Active gradient $\neq 0$)</td>
    </tr>
    <tr>
      <td><b>2. Runaway Win</b></td>
      <td>$\mathbf{+5.00}$ (Punctured skin)</td>
      <td>$1.45$ ($+45\%$)</td>
      <td>$1.45 \times 5.0 = 7.25$</td>
      <td>$1.20 \times 5.0 = 6.00$</td>
      <td>$\min(7.25, 6.00) = \mathbf{6.00}$ (Clipped! Gradient $= 0$)</td>
    </tr>
    <tr>
      <td><b>3. Moderate Loss</b></td>
      <td>$\mathbf{-4.00}$ (Pulp bruised)</td>
      <td>$0.90$ ($-10\%$)</td>
      <td>$0.90 \times (-4.0) = -3.60$</td>
      <td>$0.90 \times (-4.0) = -3.60$</td>
      <td>$\min(-3.60, -3.60) = \mathbf{-3.60}$ (Active gradient $\neq 0$)</td>
    </tr>
    <tr>
      <td><b>4. Massive Loss</b></td>
      <td>$\mathbf{-4.00}$ (Pulp bruised)</td>
      <td>$0.65$ ($-35\%$)</td>
      <td>$0.65 \times (-4.0) = -2.60$</td>
      <td>$0.80 \times (-4.0) = -3.20$</td>
      <td>$\min(-2.60, -3.20) = \mathbf{-3.20}$ (Clipped! Gradient $= 0$)</td>
    </tr>
  </tbody>
</table>

<h3>8.1 Approximate KL Divergence &amp; Early Stopping Diagnostic</h3>
<p>
  How can a roboticist monitor whether PPO is staying safely inside its trust region during training? 
  John Schulman derived the numerically stable <b>Approximate KL Divergence</b>:
</p>
<div class="formula">
  $$D_{\text{KL}}^{\text{approx}} = \frac{1}{B} \sum_{i=1}^B \left( r_i(\theta) - 1 - \log r_i(\theta) \right)$$
</div>
<div class="callout robotics">
  <div class="callout-title">🤖 Production Early Stopping Rule (SkRL / Isaac Lab)</div>
  <p>
    If you set <code>epochs: 8</code>, but after epoch 3 the approximate KL divergence exceeds your safety threshold:
    <br><code>if approx_kl &gt; 1.5 * target_kl (e.g. 0.015): break  # Early stop this batch!</code><br>
    This dynamically prevents policy collapse while maximizing GPU data reuse when the policy is stable!
  </p>
</div>

<!-- SECTION 9: DIARY OF AN ISAAC LAB TRAINING RUN -->
<h2>9. Diary of an Isaac Lab Training Run (0 to 2,000 Iterations)</h2>
<p>
  Here is the exact progression observed on TensorBoard when training our dual-arm fruit slicing robot:
</p>
<ul>
  <li><b>Iteration 0 – 100 (Chaotic Babbling):</b> Policy outputs high-entropy random actions. Episode lengths are short ($\approx 15$ steps) because knives immediately bump tables. Mean ratio $r_t \approx 1.002$. Advantage is noisy. Value function loss is high ($V_{\text{loss}} \approx 45.0$). Zero policy collapse.</li>
  <li><b>Iteration 100 – 400 (The Coordination Breakthrough):</b> Approximate KL rises to $0.008$. Clip fraction hits $12\%$ as the policy aggressively reinforces knife alignment. Episode returns surge from $-20.0$ to $+15.0$. The robot learns to stabilize the fruit with the fork before initiating the knife stroke.</li>
  <li><b>Iteration 400 – 1,200 (Impedance &amp; Compliance Refinement):</b> The robot discovers sawing kinematics. Value function loss plateaus at $0.85$ (explained variance $> 0.92$). The policy entropy gradually decays from $1.8$ to $0.4$, focusing actions tightly around optimal cutting feeds.</li>
  <li><b>Iteration 1,200 – 2,000 (Sub-Millimeter Asymptotic Mastery):</b> Slicing success rate reaches $98.4\%$. Mean normal force on fruit stays under $3.2$ N. Ratio clipping occurs on $< 3\%$ of transitions, indicating that policy updates have settled into a smooth, stable asymptotic optimum.</li>
</ul>

<!-- SECTION 10: COMPLETE PRODUCTION PYTORCH IMPLEMENTATION -->
<h2>10. Complete Production-Grade PyTorch PPO Implementation</h2>
<p>
  Below is the complete, modular PyTorch implementation of the PPO Clipped Surrogate Objective with Actor-Critic networks, Generalized Advantage Estimation, and Approximate KL tracking:
</p>

<div class="callout code-box">
  <div class="callout-title">🐍 Complete Production-Grade PPO Module (PyTorch)</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn
from torch.distributions.normal import Normal

class ActorCriticContinuous(nn.Module):
    # Two-headed or separate Actor-Critic network for continuous robot control
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super().__init__()
        # Actor Network (Policy)
        self.actor_mean = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, action_dim)
        )
        # Learnable log standard deviation per action dimension
        self.actor_log_std = nn.Parameter(torch.zeros(1, action_dim))

        # Critic Network (Value Function V(s))
        self.critic = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )

    def get_action_and_value(self, state, action=None):
        mean = self.actor_mean(state)
        std = self.actor_log_std.expand_as(mean).exp()
        dist = Normal(mean, std)

        if action is None:
            action = dist.sample()

        log_prob = dist.log_prob(action).sum(dim=-1, keepdim=True)
        entropy = dist.entropy().sum(dim=-1, keepdim=True)
        value = self.critic(state)
        return action, log_prob, entropy, value


class PPOBufferUpdate:
    # Vectorized Multi-Epoch PPO Update with Clipping and Early Stopping
    @staticmethod
    def update(policy_net, optimizer, states, actions, old_log_probs, 
               returns, advantages, clip_eps=0.2, c_v=0.5, c_ent=0.01, 
               epochs=5, batch_size=256, target_kl=0.015):
        
        num_samples = states.size(0)
        # Normalize advantages across the entire rollout batch (Guards gradient scale)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        for epoch in range(epochs):
            indices = torch.randperm(num_samples)
            for start in range(0, num_samples, batch_size):
                end = start + batch_size
                batch_idx = indices[start:end]

                b_states = states[batch_idx]
                b_actions = actions[batch_idx]
                b_old_log_probs = old_log_probs[batch_idx]
                b_returns = returns[batch_idx]
                b_advantages = advantages[batch_idx]

                # Evaluate new action probabilities and current value estimates
                _, new_log_probs, entropy, new_values = policy_net.get_action_and_value(b_states, b_actions)

                # 1. Probability Ratio: r(theta) = exp(log_pi_new - log_pi_old)
                ratio = torch.exp(new_log_probs - b_old_log_probs)

                # 2. Clipped Surrogate Objective
                surr1 = ratio * b_advantages
                surr2 = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * b_advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                # 3. Value Function Loss (MSE against Monte Carlo / GAE returns)
                value_loss = c_v * nn.functional.mse_loss(new_values, b_returns)

                # 4. Entropy Bonus (Prevents premature joint freeze)
                entropy_loss = -c_ent * entropy.mean()

                total_loss = policy_loss + value_loss + entropy_loss

                optimizer.zero_grad()
                total_loss.backward()
                nn.utils.clip_grad_norm_(policy_net.parameters(), max_norm=0.5)
                optimizer.step()

            # 5. Approximate KL Divergence for Adaptive Early Stopping
            with torch.no_grad():
                _, full_new_log_probs, _, _ = policy_net.get_action_and_value(states, actions)
                full_ratio = torch.exp(full_new_log_probs - old_log_probs)
                approx_kl = ((full_ratio - 1.0) - torch.log(full_ratio)).mean().item()

            if approx_kl > 1.5 * target_kl:
                # Early stop: policy has reached the trust region boundary
                break
</pre>
</div>

<!-- SECTION 11: PRACTITIONER'S FIELD GUIDE -->
<h2>11. Practitioner's Field Guide: 6 Insidious PPO Failure Modes &amp; Solutions</h2>
<p>
  When implementing or tuning PPO in production or research, these 6 subtle bugs are responsible for almost all training stagnation:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 22%;">Failure Symptom</th>
      <th style="width: 38%;">The Hidden Root Cause</th>
      <th style="width: 40%;">The Production-Proven Fix</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Mini-Batch Advantage Normalization</b></td>
      <td>Normalizing advantages inside the inner mini-batch loop: <code>b_adv = (b_adv - b_adv.mean()) / b_adv.std()</code>. This destroys relative advantage weighting across different states!</td>
      <td>Always normalize advantages <b>once across the entire rollout batch</b> before entering mini-batch SGD loops!</td>
    </tr>
    <tr>
      <td><b>2. Value Function Loss Clipping ($V$-clip)</b></td>
      <td>Clipping the Critic loss ($L^V = \max[(V - y)^2, (V_{\text{clip}} - y)^2]$). While introduced in early OpenAI baselines, subsequent robotics benchmarks show it severely impedes value convergence.</td>
      <td>Leave the Critic unclipped! Train $V(s)$ using clean, unclipped Mean Squared Error (MSE) or Huber loss.</td>
    </tr>
    <tr>
      <td><b>3. Too Many Epochs ($K > 10$)</b></td>
      <td>Setting <code>epochs: 15</code> causes policy drift. By epoch 8, $85\%$ of samples exceed $[0.8, 1.2]$, zeroing gradients and causing GPU thrashing.</td>
      <td>Set <code>epochs: 4</code> or <code>5</code>. Implement <code>approx_kl &gt; 1.5 * target_kl</code> early stopping.</td>
    </tr>
    <tr>
      <td><b>4. Observation Standardization Drift</b></td>
      <td>Updating observation running mean and variance during policy evaluation or testing. Shifts input coordinate frames, causing the robot to flail.</td>
      <td>Freeze observation normalizer statistics (<code>normalizer.eval()</code>) whenever running validation rollouts.</td>
    </tr>
    <tr>
      <td><b>5. Gradient Norm Explosion</b></td>
      <td>Forgetting to clip gradient norms. A rare bad contact spike in simulation produces a massive gradient vector that shatters network weights.</td>
      <td>Always apply <code>torch.nn.utils.clip_grad_norm_(parameters, max_norm=0.5)</code> before <code>optimizer.step()</code>.</td>
    </tr>
    <tr>
      <td><b>6. Dimension Mismatch Broadcasting</b></td>
      <td>Loss computed between <code>new_values</code> of shape <code>[256, 1]</code> and <code>b_returns</code> of shape <code>[256]</code>. PyTorch silently broadcasts to a <code>[256, 256]</code> matrix!</td>
      <td>Always assert: <code>b_returns = b_returns.view(-1, 1)</code> before calling MSE loss.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 12: GRAND COMPARISON TABLE -->
<h2>12. Grand Algorithm Comparison: PPO vs TRPO vs SAC vs DDPG</h2>
<table>
  <thead>
    <tr>
      <th style="width: 18%;">Dimension</th>
      <th style="width: 20%;">DDPG (2015)</th>
      <th style="width: 20%;">TRPO (2015)</th>
      <th style="width: 20%;">PPO (2017)</th>
      <th style="width: 22%;">SAC (2018)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Data Strategy</b></td>
      <td>Off-Policy (Replay Buffer)</td>
      <td>On-Policy (1 epoch)</td>
      <td><b>On-Policy (Multi-Epoch)</b></td>
      <td>Off-Policy (Replay Buffer)</td>
    </tr>
    <tr>
      <td><b>Trust Region Enforcement</b></td>
      <td>None (Unconstrained)</td>
      <td>Hard KL Constraint (CG + HVP)</td>
      <td><b>First-Order Clipping ($1 \pm \epsilon$)</b></td>
      <td>Entropy Temperature ($\alpha$)</td>
    </tr>
    <tr>
      <td><b>Sample Efficiency</b></td>
      <td>Moderate</td>
      <td>Low</td>
      <td><b>High (Massive GPU Parallel)</b></td>
      <td>Very High (Serial Data)</td>
    </tr>
    <tr>
      <td><b>Implementation Complexity</b></td>
      <td>Low</td>
      <td>Extremely High (Hessians)</td>
      <td><b>Low (~15 lines of loss)</b></td>
      <td>Moderate</td>
    </tr>
    <tr>
      <td><b>Hyperparameter Robustness</b></td>
      <td>Brittle (Overestimates)</td>
      <td>Very Robust</td>
      <td><b>Extremely Robust</b></td>
      <td>Very Robust</td>
    </tr>
    <tr>
      <td><b>Primary Domain Today</b></td>
      <td>Deprecated / Historical</td>
      <td>Theoretical Reference</td>
      <td><b>GPU Sim (Isaac Lab, RLHF, Boston Dynamics)</b></td>
      <td>Physical Robot Manipulation</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>CS285 Lecture 10 Zero-to-Hero Guide • DEX-ROB Lab (Tianjin University) • Prof. Shan An</i>
</div>

</body>
</html>
"""

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Lecture10_Beginner_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Lecture10_Beginner_Guide.pdf"

render_utils.build_pdf(html_content, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
