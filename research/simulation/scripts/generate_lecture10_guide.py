import os
import shutil
import render_utils

html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Lecture 10: Zero-to-Hero Guide to Advanced Policy Gradients & PPO</title>
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
    line-height: 1.56;
    font-size: 9.6pt;
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
  <span class="course-tag">CS285 Lecture 10 • Zero-to-Hero Field Manual</span>
  <h1>Proximal Policy Optimization (PPO) &amp; Trust Regions</h1>
  <div class="subtitle">From Scratch to Mastery: Understanding Why Reinforcement Learning Collapses, How Clipping Saves It, and Why PPO Rules Modern Robotics</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Focus:</b> Policy Collapse, Kakade-Langford Bounds, TRPO, &amp; The PPO Clipped Objective</span>
  </div>
</div>

<!-- SECTION 1: THE NIGHTMARE OF POLICY COLLAPSE -->
<h2>1. What is Policy Collapse? (The Student Burning Their Books)</h2>
<p>
  In supervised machine learning (like image classification), if you choose a learning rate that is too high, the loss spikes on epoch 12. 
  You don't panic. On epoch 13, the network sees more normal images, and the loss recovers.
  <b>In Reinforcement Learning, an oversized learning rate causes instant, permanent death.</b> Why?
</p>

<div class="callout warning-box">
  <div class="callout-title">💥 The Catastrophic RL Death Spiral</div>
  <p>
    In RL, <b>the policy collects its own training data</b>!
  </p>
  <ul>
    <li>Imagine a student studying for an important medical exam.</li>
    <li>On Friday, the student tries a slightly unusual study method. They take a practice test on Saturday and get a mediocre score.</li>
    <li>Instead of making a minor 2% adjustment, the student panics, <b>burns all their textbooks, deletes their memory, and forgets how to read</b>!</li>
    <li>Because they forgot how to read, every practice test they take next week scores a zero. Because every test is a zero, they can never learn anything new.</li>
  </ul>
  <p>
    This is <b>Policy Collapse</b>: if an aggressive gradient update moves network weights into an unstable region, the robot starts flailing wildly. 
    All 1,024 parallel environments in Isaac Sim generate pure garbage trajectories. 
    Because the new data is 100% garbage, the next gradient update makes the policy even worse. Training dies permanently!
  </p>
</div>

<!-- DIAGRAM 1: POLICY COLLAPSE DEATH SPIRAL -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <rect x="20" y="20" width="130" height="50" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="85" y="42" font-size="9" font-weight="700" fill="#1e40af" text-anchor="middle">1. Healthy Policy</text>
  <text x="85" y="58" font-size="7.5" fill="#475569" text-anchor="middle">Slices tomatoes well</text>

  <path d="M 150,45 L 190,45" fill="none" stroke="#ef4444" stroke-width="2"/>
  <polygon points="190,45 182,40 182,50" fill="#ef4444"/>

  <rect x="190" y="20" width="130" height="50" rx="6" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
  <text x="255" y="42" font-size="9" font-weight="700" fill="#b91c1c" text-anchor="middle">2. Oversized Step</text>
  <text x="255" y="58" font-size="7.5" fill="#7f1d1d" text-anchor="middle">Weights jump into bad zone</text>

  <path d="M 320,45 L 360,45" fill="none" stroke="#ef4444" stroke-width="2"/>
  <polygon points="360,45 352,40 352,50" fill="#ef4444"/>

  <rect x="360" y="20" width="130" height="50" rx="6" fill="#fef2f2" stroke="#dc2626" stroke-width="2"/>
  <text x="425" y="42" font-size="9" font-weight="700" fill="#dc2626" text-anchor="middle">3. Garbage Rollouts</text>
  <text x="425" y="58" font-size="7.5" fill="#991b1b" text-anchor="middle">Robot flails; 0 cuts</text>

  <path d="M 490,45 L 530,45" fill="none" stroke="#7f1d1d" stroke-width="2"/>
  <polygon points="530,45 522,40 522,50" fill="#7f1d1d"/>

  <rect x="530" y="20" width="60" height="50" rx="6" fill="#450a0a"/>
  <text x="560" y="42" font-size="8.5" font-weight="700" fill="#ffffff" text-anchor="middle">DEATH</text>
  <text x="560" y="56" font-size="7" fill="#fca5a5" text-anchor="middle">SPIRAL</text>
</svg>
</div>

<!-- SECTION 2: THE PPO SOLUTION & BOWLING BUMPERS -->
<h2>2. The Solution: PPO &amp; The Bowling Bumpers</h2>
<div class="callout intuition">
  <div class="callout-title">🎳 The Bowling Alley Bumpers Analogy</div>
  <p>
    When children play bowling, the alley puts up <b>inflatable bumpers</b> along the gutters. 
    No matter how wildly the child throws the ball, the ball bounces off the bumper, stays in the lane, and hits pins.
    <br><br>
    <b>Proximal Policy Optimization (PPO)</b> puts bumpers on neural network updates! 
    It says: <i>"No matter how enthusiastic the gradient is about an action, the new policy is NEVER allowed to deviate by more than <b>20% ($\epsilon = 0.2$)</b> from the old policy that collected the data."</i>
  </p>
</div>

<h3>2.1 The PPO Clipped Surrogate Objective (Parameter Anatomy)</h3>
<p>
  First, define the <b>Probability Ratio (The Speedometer)</b>:
</p>
<div class="formula">
  $$r_t(\theta) = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_{\text{old}}}(a_t \mid s_t)}$$
</div>
<p>
  Then, the <b>PPO Clipped Objective (The Bumpers)</b>:
</p>
<div class="formula">
  $$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon) \hat{A}_t \right) \right]$$
</div>

<!-- PARAMETER ANATOMY TABLE 1 -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Parameter</th>
      <th style="width: 22%;">Formal Name</th>
      <th style="width: 38%;">Plain English Meaning</th>
      <th style="width: 25%;">Recommended Value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$r_t(\theta)$</b></td>
      <td>Probability Ratio</td>
      <td><b>The Speedometer:</b> How much more or less likely is action $a_t$ under the new policy compared to the old policy?</td>
      <td>$r=1.0$ at start of batch; rises or falls during training.</td>
    </tr>
    <tr>
      <td><b>$\epsilon$</b></td>
      <td>Clipping Threshold</td>
      <td><b>The Speed Limit:</b> The maximum allowed percentage change in action probability.</td>
      <td><b>$\epsilon = 0.2$</b> (Allows $\pm 20\%$ change: $[0.8, 1.2]$).</td>
    </tr>
    <tr>
      <td><b>$\hat{A}_t$</b></td>
      <td>Advantage Score</td>
      <td>Was this robot motion better ($\hat{A} > 0$) or worse ($\hat{A} < 0$) than average?</td>
      <td>Computed via GAE($\lambda = 0.95$).</td>
    </tr>
    <tr>
      <td><b>$\min(\dots)$</b></td>
      <td>Pessimistic Bound</td>
      <td>Forces the algorithm to take the more conservative, pessimistic estimate so it never over-promises.</td>
      <td>Guarantees monotonic policy improvement.</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the PPO Loss</div>
  <p>
    <b>"If an action was good ($\hat{A} > 0$), make it more likely—but once you have increased its probability by 20% ($r > 1.2$), STOP pushing and ignore further gradients! If an action was bad ($\hat{A} < 0$), decrease it—but once it dropped by 20% ($r < 0.8$), STOP punishing it!"</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: THE 4-QUADRANT MATRIX -->
<h2>3. The 4-Quadrant Matrix: How PPO Responds to Every Situation</h2>
<p>
  Every single timestep in an Isaac Lab batch falls into one of four clear quadrants:
</p>

<!-- DIAGRAM 2: PPO CLIPPING ZONES -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <line x1="40" y1="50" x2="560" y2="50" stroke="#94a3b8" stroke-width="2"/>

  <!-- Left: Clipped zone -->
  <rect x="50" y="15" width="140" height="65" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="120" y="42" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">CLIPPED TO ZERO</text>
  <text x="120" y="58" font-size="7.5" fill="#7f1d1d" text-anchor="middle">$r_t(\theta) &lt; 0.8$ (Dropped &gt;20%)</text>

  <!-- Middle: Active update zone -->
  <rect x="210" y="15" width="180" height="65" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="300" y="38" font-size="9.5" font-weight="700" fill="#047857" text-anchor="middle">ACTIVE GRADIENT ZONE</text>
  <text x="300" y="54" font-size="8.5" font-weight="700" fill="#065f46" text-anchor="middle">$r_t(\theta) \in [0.8, 1.2]$</text>
  <text x="300" y="68" font-size="7.5" fill="#64748b" text-anchor="middle">Normal learning occurs safely</text>

  <!-- Right: Clipped zone -->
  <rect x="410" y="15" width="140" height="65" rx="4" fill="#fee2e2" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="3,3"/>
  <text x="480" y="42" font-size="8.5" font-weight="700" fill="#b91c1c" text-anchor="middle">CLIPPED TO ZERO</text>
  <text x="480" y="58" font-size="7.5" fill="#7f1d1d" text-anchor="middle">$r_t(\theta) &gt; 1.2$ (Grown &gt;20%)</text>
</svg>
</div>

<!-- 4 QUADRANT TABLE -->
<table>
  <thead>
    <tr>
      <th style="width: 15%;">Scenario</th>
      <th style="width: 20%;">Advantage ($\hat{A}$)</th>
      <th style="width: 25%;">Ratio Condition ($r_t$)</th>
      <th style="width: 40%;">What PPO Does (Plain English)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Quadrant 1</b></td>
      <td><b>$\hat{A} > 0$</b> (Good cut)</td>
      <td>$r_t \in [1.0, 1.2]$ (Safe increase)</td>
      <td><b>Normal Positive Gradient:</b> Robot keeps increasing the probability of this successful motion.</td>
    </tr>
    <tr>
      <td><b>Quadrant 2</b></td>
      <td><b>$\hat{A} > 0$</b> (Good cut)</td>
      <td>$r_t > 1.2$ (Exceeded 20%)</td>
      <td><b>Clipped to 0 Gradient:</b> Stop pushing! You already made this action 20% more likely. Don't over-commit.</td>
    </tr>
    <tr>
      <td><b>Quadrant 3</b></td>
      <td><b>$\hat{A} < 0$</b> (Crushed fruit)</td>
      <td>$r_t \in [0.8, 1.0]$ (Safe decrease)</td>
      <td><b>Normal Negative Gradient:</b> Suppresses the probability of this crushing mistake.</td>
    </tr>
    <tr>
      <td><b>Quadrant 4</b></td>
      <td><b>$\hat{A} < 0$</b> (Crushed fruit)</td>
      <td>$r_t < 0.8$ (Dropped &gt;20%)</td>
      <td><b>Clipped to 0 Gradient:</b> Stop punishing! The probability has already dropped significantly. Leave it alone.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 4: WHY PPO RULES GPU ROBOTICS -->
<h2>4. Why PPO Rules GPU Robotics (NVIDIA Isaac Lab)</h2>
<div class="callout intuition">
  <div class="callout-title">⚡ The 10x Speedup Secret: Multi-Epoch Data Reuse</div>
  <p>
    In vanilla policy gradients (Lecture 5), you simulate 1,024 parallel robots on GPU, take <b>ONE single gradient step</b>, and you MUST throw away all data immediately. Why? Because the data is now off-policy! Generating 10 million transitions to take 1,000 steps wastes 99% of your GPU power.
    <br><br>
    <b>Why PPO dominates Isaac Lab:</b> Because PPO's clipping mechanism guarantees safety, you can take the exact same batch of GPU simulation data and train on it for <b>4 to 8 epochs</b> across mini-batches! You extract $8\times$ more learning out of every single simulation frame.
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 5: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>5. Concrete Numerical Walkthrough: 4 Cases with Real Numbers</h2>
<p>
  Let's calculate PPO's objective value across four concrete actions with clipping threshold <b>$\epsilon = 0.20$</b>:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 10%;">Case</th>
      <th style="width: 18%;">Advantage $\hat{A}$</th>
      <th style="width: 18%;">Ratio $r_t(\theta)$</th>
      <th style="width: 27%;">Unclipped Term $r_t \hat{A}_t$</th>
      <th style="width: 27%;">Clipped Term $\text{clip}(r) \hat{A}_t$</th>
      <th style="width: 15%;">Final Loss</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Moderate Win</b></td>
      <td>$\mathbf{+5.0}$ (Good)</td>
      <td>$1.10$ ($+10\%$)</td>
      <td>$1.10 \times 5.0 = 5.50$</td>
      <td>$1.10 \times 5.0 = 5.50$</td>
      <td>$\min(5.5, 5.5) = \mathbf{5.50}$</td>
    </tr>
    <tr>
      <td><b>2. Runaway Win</b></td>
      <td>$\mathbf{+5.0}$ (Good)</td>
      <td>$1.45$ ($+45\%$)</td>
      <td>$1.45 \times 5.0 = 7.25$</td>
      <td>$1.20 \times 5.0 = 6.00$</td>
      <td>$\min(7.25, 6.0) = \mathbf{6.00}$ (Clipped!)</td>
    </tr>
    <tr>
      <td><b>3. Moderate Loss</b></td>
      <td>$\mathbf{-4.0}$ (Bad)</td>
      <td>$0.90$ ($-10\%$)</td>
      <td>$0.90 \times (-4.0) = -3.60$</td>
      <td>$0.90 \times (-4.0) = -3.60$</td>
      <td>$\min(-3.6, -3.6) = \mathbf{-3.60}$</td>
    </tr>
    <tr>
      <td><b>4. Massive Loss</b></td>
      <td>$\mathbf{-4.0}$ (Bad)</td>
      <td>$0.65$ ($-35\%$)</td>
      <td>$0.65 \times (-4.0) = -2.60$</td>
      <td>$0.80 \times (-4.0) = -3.20$</td>
      <td>$\min(-2.6, -3.2) = \mathbf{-3.20}$ (Clipped!)</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 6: PYTORCH IMPLEMENTATION -->
<h2>6. Complete PyTorch PPO Loss Implementation</h2>

<div class="callout code-box">
  <div class="callout-title">🐍 Complete PyTorch PPO Clipped Loss with Entropy Bonus</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn

def compute_ppo_loss(log_probs, old_log_probs, advantages, entropy, clip_eps=0.2, c_entropy=0.01):
    # 1. Compute Probability Ratio: r(theta) = exp(log_prob - old_log_prob)
    ratio = torch.exp(log_probs - old_log_probs)

    # 2. Unclipped and Clipped Surrogate Objectives
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1.0 - clip_eps, 1.0 + clip_eps) * advantages

    # 3. PPO Policy Loss: Take minimum (pessimistic bound) and negate for optimizer
    policy_loss = -torch.min(surr1, surr2).mean()

    # 4. Entropy Bonus: Encourages exploration of dynamic impedance values
    entropy_loss = -c_entropy * entropy.mean()

    total_loss = policy_loss + entropy_loss
    return total_loss, policy_loss.item(), ratio.mean().item()
</pre>
</div>

<!-- SECTION 7: PRACTITIONER'S CHECKLIST -->
<h2>7. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Failure Mode</th>
      <th style="width: 35%;">The Hidden Symptom</th>
      <th style="width: 40%;">How to Fix It</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. KL Divergence Explosion</b></td>
      <td>Policy changes too rapidly despite clipping. Approximate KL divergence $\text{KL} \approx \text{mean}((\text{ratio} - 1) - \log(\text{ratio}))$ spikes above $0.05$.</td>
      <td>Use an <b>Adaptive Learning Rate Scheduler</b> (like <code>KLAdaptiveLR</code> in SkRL): if KL $>0.02$, lower learning rate; if KL $<0.005$, increase it.</td>
    </tr>
    <tr>
      <td><b>2. Too Many Epochs Per Batch</b></td>
      <td>Setting <code>epochs: 20</code> causes the policy to overfit to the batch. The ratio blows past $[0.8, 1.2]$ and 90% of transitions get clipped to zero gradients.</td>
      <td>In Isaac Lab, set <b><code>epochs: 4</code> or <code>5</code></b>. More epochs provide diminishing returns.</td>
    </tr>
    <tr>
      <td><b>3. Clipping the Critic Target</b></td>
      <td>Clipping the Value function loss ($V$-clip) was popular in 2018, but recent ablation studies show it actively harms performance in continuous robotics.</td>
      <td>Leave the Critic unclipped: train $V(s)$ with standard MSE loss.</td>
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
