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
  <span class="course-tag">CS285 Lecture 5 • Zero-to-Hero Field Manual</span>
  <h1>Policy Gradients: Trial-and-Error Learning</h1>
  <div class="subtitle">From Scratch to Mastery: How AI Learns by Reinforcing Good Actions and Suppressing Mistakes Without Differentiating Physics</div>
  <div class="meta-bar">
    <span><b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)</span>
    <span><b>Focus:</b> The Policy Gradient Theorem, Gaussian Policies, &amp; Baseline Variance Reduction</span>
  </div>
</div>

<!-- SECTION 1: CORE INTUITION & THE PUPPY ANALOGY -->
<h2>1. What is Policy Gradient? (The Puppy Training Analogy)</h2>
<p>
  In supervised deep learning (like classifying cat photos), we compute gradients by backpropagating through known mathematical layers. 
  But in robotics, the robot acts on the physical world. If a knife cuts a tomato, the physical tearing of the tomato skin is <b>not a differentiable mathematical function</b>! You cannot backpropagate through skin rupture.
  How can we train a neural network policy $\pi_\theta(a|s)$ when physics is non-differentiable?
</p>

<div class="callout intuition">
  <div class="callout-title">🐶 The Puppy Training Analogy</div>
  <p>
    Imagine you are teaching a puppy to sit on command:
  </p>
  <ul>
    <li>You cannot open the puppy's skull with a screwdriver and rewire its neurons.</li>
    <li>Instead, you say <i>"Sit!"</i>. The puppy doesn't know what that means. It wiggles, barks, spins in circles, and scratches its ear.</li>
    <li>Eventually, purely by random chance, the puppy sits down on the carpet.</li>
    <li><b>The Instant Reinforcement:</b> You immediately shout <i>"GOOD BOY!"</i> and give it a piece of bacon (<b>Reward</b>).</li>
    <li>The puppy's brain automatically adjusts: <i>"Whatever I just did with my hind legs when the human made that sound, DO IT MORE OFTEN!"</i></li>
  </ul>
  <p>
    <b>Policy Gradient is literally the exact mathematical equation for "GOOD BOY!"</b> 
    We let the robot try random actions. When an action leads to a high reward, we push the neural network weights to make that action more likely in the future!
  </p>
</div>

<!-- DIAGRAM 1: PUPPY REINFORCEMENT LOOP -->
<div class="diagram-container">
<svg width="600" height="90" viewBox="0 0 600 90">
  <!-- Action Box -->
  <rect x="20" y="20" width="150" height="50" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="2"/>
  <text x="95" y="42" font-size="9.5" font-weight="700" fill="#1e40af" text-anchor="middle">TRIAL ACTION $a_t$</text>
  <text x="95" y="58" font-size="8" fill="#475569" text-anchor="middle">Sampled from $\pi_\theta(a|s)$</text>

  <!-- Arrow to Outcome -->
  <path d="M 170,45 L 230,45" fill="none" stroke="#2563eb" stroke-width="2"/>
  <polygon points="230,45 220,40 220,50" fill="#2563eb"/>

  <!-- Outcome Box -->
  <rect x="230" y="20" width="140" height="50" rx="6" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
  <text x="300" y="42" font-size="9.5" font-weight="700" fill="#065f46" text-anchor="middle">OUTCOME / SCORE</text>
  <text x="300" y="58" font-size="8" fill="#047857" text-anchor="middle">Advantage $\hat{A}_t$</text>

  <!-- Arrow to Adjustment -->
  <path d="M 370,45 L 430,45" fill="none" stroke="#10b981" stroke-width="2"/>
  <polygon points="430,45 420,40 420,50" fill="#10b981"/>

  <!-- Adjustment Box -->
  <rect x="430" y="15" width="150" height="60" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="2"/>
  <text x="505" y="38" font-size="9" font-weight="700" fill="#92400e" text-anchor="middle">WEIGHT ADJUSTMENT</text>
  <text x="505" y="52" font-size="7.5" fill="#78350f" text-anchor="middle">$\hat{A} &gt; 0 \implies$ Boost Action</text>
  <text x="505" y="65" font-size="7.5" fill="#78350f" text-anchor="middle">$\hat{A} &lt; 0 \implies$ Suppress Action</text>
</svg>
</div>

<!-- SECTION 2: THE POLICY GRADIENT EQUATION -->
<h2>2. The Policy Gradient Theorem (Parameter Anatomy)</h2>
<p>
  Here is the foundational equation derived by Ronald Williams in 1992 (the REINFORCE algorithm):
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
      <td>Policy Gradient</td>
      <td>The compass direction in neural network weight space that increases expected total reward.</td>
      <td>Nudges network weights $\theta \leftarrow \theta + \alpha \nabla_\theta J$.</td>
    </tr>
    <tr>
      <td><b>$\pi_\theta(a_t \mid s_t)$</b></td>
      <td>Action Probability</td>
      <td>The probability that the policy chooses action $a_t$ in state $s_t$.</td>
      <td>Robot motor torque or feed velocity output.</td>
    </tr>
    <tr>
      <td><b>$\nabla_\theta \log \pi_\theta$</b></td>
      <td>Score Function</td>
      <td><b>The Steering Wheel:</b> <i>"Which direction in weight space makes action $a_t$ more probable?"</i></td>
      <td>Points directly toward increasing the likelihood of the chosen action.</td>
    </tr>
    <tr>
      <td><b>$\hat{Q}_t$</b></td>
      <td>Return / Advantage Multiplier</td>
      <td><b>The Gas Pedal &amp; Reverse Gear:</b> <i>"Was this action a triumph or a disaster?"</i></td>
      <td>If $\hat{Q} > 0$, press gas pedal forward. If $\hat{Q} < 0$, put in reverse!</td>
    </tr>
  </tbody>
</table>

<div class="callout math-box">
  <div class="callout-title">📝 Plain English Translation of the Policy Gradient Equation</div>
  <p>
    <b>"For every action the robot took, calculate the direction in neural network weights that would make that action MORE likely. Then multiply that direction by the action's score ($\hat{Q}$). If the action was great, nudge the weights to do it more. If the action crushed the tomato, nudge the weights in the exact opposite direction!"</b>
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 3: CONTINUOUS GAUSSIAN POLICIES -->
<h2>3. Continuous Gaussian Policies: Controlling Real Robot Motors</h2>
<p>
  In video games, actions are discrete buttons (Left, Right, Jump). But in your dual-arm robotic slicing task, the robot outputs continuous real numbers (e.g. downward feed velocity $v_z = 2.45$ mm/s).
</p>
<p>
  How does a neural network output continuous numbers while still exploring? It outputs the parameters of a <b>Normal (Gaussian) Distribution</b>:
</p>

<!-- DIAGRAM 2: GAUSSIAN CURVE SHIFTING -->
<div class="diagram-container">
<svg width="600" height="110" viewBox="0 0 600 110">
  <!-- Original Gaussian Curve -->
  <path d="M 50,90 Q 150,90 200,60 Q 250,15 300,15 Q 350,15 400,60 Q 450,90 550,90" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,4"/>
  <line x1="300" y1="15" x2="300" y2="90" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="2,2"/>
  <text x="300" y="102" font-size="8" fill="#64748b" text-anchor="middle">Initial Mean $\mu = 2.0$</text>

  <!-- Sampled action to the right -->
  <circle cx="380" cy="50" r="5" fill="#10b981"/>
  <text x="380" y="42" font-size="8" font-weight="700" fill="#047857" text-anchor="middle">Sampled Action $a = 2.8$</text>
  <text x="380" y="65" font-size="7.5" fill="#065f46" text-anchor="middle">(Clean Cut! Score $+10$)</text>

  <!-- Green Shifted Curve -->
  <path d="M 110,90 Q 210,90 260,60 Q 310,15 360,15 Q 410,15 460,60 Q 510,90 590,90" fill="none" stroke="#10b981" stroke-width="2.5"/>
  <line x1="360" y1="15" x2="360" y2="90" stroke="#10b981" stroke-width="1.5"/>
  <text x="360" y="102" font-size="8" font-weight="700" fill="#047857" text-anchor="middle">New Mean $\mu' = 2.4$ (PULLED RIGHT!)</text>
</svg>
</div>

<h3>3.1 Score Function of a Gaussian Policy</h3>
<p>
  When the policy is Gaussian $\pi_\theta(a|s) \sim \mathcal{N}(\mu_\theta(s), \sigma_\theta(s))$, the score function has a remarkably clean analytical form:
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
      <th style="width: 25%;">Tomato Slicing Example</th>
      <th style="width: 25%;">Physical Intuition</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>$\mu_\theta(s)$</b></td>
      <td>The Robot's Intended Action (Mean)</td>
      <td>$\mu = 2.0$ mm/s downward feed</td>
      <td>What the robot thinks is best.</td>
    </tr>
    <tr>
      <td><b>$\sigma$</b></td>
      <td>Exploration Noise (Standard Dev)</td>
      <td>$\sigma = 0.5$ mm/s wiggle room</td>
      <td>How much the robot experiments.</td>
    </tr>
    <tr>
      <td><b>$a - \mu$</b></td>
      <td>The Exploration Deviation</td>
      <td>$2.8 - 2.0 = +0.8$ mm/s</td>
      <td>Did the robot push harder ($>0$) or softer ($<0$)?</td>
    </tr>
    <tr>
      <td><b>$\frac{a - \mu}{\sigma^2} \cdot \hat{Q}$</b></td>
      <td>Gradient Pull Force</td>
      <td>$\frac{+0.8}{0.25} \times (+10) = +32.0$</td>
      <td>Pulls $\mu$ directly toward successful actions!</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 4: THE BASELINE & GRADING ON A CURVE -->
<h2>4. The Baseline: Why We Must Grade on a Curve</h2>
<div class="callout intuition">
  <div class="callout-title">🎓 The College Exam Analogy (Why Raw Scores Deceive)</div>
  <p>
    Imagine you take an exam where every student scores between 90 and 100 points because the test was too easy. 
    If you score 91, did you do well? <b>No, you were in the bottom 5% of the class!</b>
    <br><br>
    In RL, if all rewards are positive (e.g. $+100, +105, +95$), raw policy gradients will <b>push UP every action</b>, even the terrible ones that only scored $+95$.
    <br><br>
    <b>The Fix (The Baseline):</b> We subtract the average expected score $b(s) = V(s)$:
    <br>$$\hat{A}_t = Q(s_t, a_t) - V(s_t)$$
    Now, an action that scores $+95$ when the average was $+100$ gets an advantage of <b>$-5.0$</b>! It gets suppressed, while an action that scores $+105$ gets <b>$+5.0$</b> and gets reinforced.
  </p>
</div>

<div class="page-break"></div>

<!-- SECTION 5: CONCRETE NUMERICAL WALKTHROUGH -->
<h2>5. Concrete Numerical Walkthrough: Updating a Robot Cutting Policy</h2>
<p>
  Let's walk through an exact numerical calculation of one policy gradient step:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 10%;">Step</th>
      <th style="width: 25%;">Variable / Calculation</th>
      <th style="width: 25%;">Value</th>
      <th style="width: 40%;">Physical Interpretation</th>
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
      <td>Stochastic variance $\sigma^2 = 0.25$.</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Sampled Action $a$</td>
      <td><b>$2.6$ mm/s</b></td>
      <td>Gaussian noise sampled $\epsilon = +1.2$: $a = 2.0 + 0.5(1.2) = 2.6$.</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Observed Return $G$</td>
      <td><b>$+18.0$</b></td>
      <td>The blade sliced cleanly through skin into pulp!</td>
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
      <td>Action outperformed expectations by $+6.0$ points!</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Gaussian Score $\frac{a - \mu}{\sigma^2}$</td>
      <td>$\frac{2.6 - 2.0}{0.25} = \mathbf{+2.4}$</td>
      <td>Gradient direction pointing toward higher feed rates.</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Gradient Step (Learning rate $\alpha = 0.01$)</td>
      <td>$\Delta \mu = 0.01 \times (2.4) \times (6.0) = \mathbf{+0.144}$</td>
      <td>Mean feed rate increases from <b>$2.0 \to 2.144$ mm/s</b>!</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 6: PYTORCH IMPLEMENTATION -->
<h2>6. PyTorch Policy Gradient Implementation with Baseline</h2>

<div class="callout code-box">
  <div class="callout-title">🐍 PyTorch REINFORCE with Continuous Gaussian Policy &amp; Baseline</div>
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
        std = torch.exp(torch.clamp(self.log_std, min=-2.0, max=1.0))
        dist = Normal(mean, std)
        return dist

def compute_policy_loss(dist, actions, advantages):
    # 1. Compute log-probability of taken actions: log pi(a|s)
    log_probs = dist.log_prob(actions).sum(dim=-1)  # Sum across action dimensions

    # 2. Policy Gradient Objective: -E[ log pi(a|s) * Advantage ]
    # We negate because PyTorch optimizers minimize loss
    policy_loss = -(log_probs * advantages.detach()).mean()
    return policy_loss
</pre>
</div>

<!-- SECTION 7: PRACTITIONER'S CHECKLIST -->
<h2>7. Practitioner's Failure Modes &amp; Debugging Checklist</h2>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Failure Mode</th>
      <th style="width: 35%;">Why It Destroys Training</th>
      <th style="width: 40%;">How to Fix It</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Standard Deviation Collapse</b></td>
      <td>The network figures out that setting $\sigma \to 0$ eliminates penalty risk. The policy freezes into a deterministic rut and stops exploring completely.</td>
      <td>Clamp $\log \sigma$ with a minimum floor: <code>torch.clamp(log_std, min=-2.0)</code> or add an <b>Entropy Bonus</b>.</td>
    </tr>
    <tr>
      <td><b>2. Forgetting to Detach Advantages</b></td>
      <td>If you don't call <code>advantages.detach()</code>, gradients flow backward through the Critic network into the policy loss, distorting Critic weights.</td>
      <td>Always call <code>advantages.detach()</code> before multiplying by <code>log_probs</code>.</td>
    </tr>
    <tr>
      <td><b>3. High Batch Variance</b></td>
      <td>Policy gradients on small batches (e.g. 32 steps) are mostly random noise. The policy takes erratic steps and diverges.</td>
      <td>Collect at least <b>2,048 to 4,096 parallel environment steps</b> before each policy gradient update.</td>
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
