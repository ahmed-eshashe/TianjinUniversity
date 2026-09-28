import os
import sys
import re
import render_utils

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Priority1_Master_Robotics_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Priority1_Master_Robotics_Guide.pdf"

def extract_body(script_path):
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    if m:
        b = m.group(1).strip()
        # Remove top header-block
        b = re.sub(r'<div class="header-block">.*?</div>', '', b, count=1, flags=re.DOTALL)
        # Remove bottom footer
        b = re.sub(r'<hr[^>]*>\s*<div style="font-size: 8\.5pt;[^>]*>.*?</div>\s*$', '', b, flags=re.DOTALL)
        return b
    return ''

# 1. Base CSS and Header
html_head = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CS285 Priority 1 Master Compendium: Zero-to-Hero Robotics Reinforcement Learning</title>
<style>
  @page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @top-right {
      content: "CS285 Priority 1 Master Compendium • Zero-to-Hero Robotics RL Blueprint";
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
    font-size: 9.3pt;
  }

  .cover-header {
    border-bottom: 3px solid #2563eb;
    padding-bottom: 14px;
    margin-bottom: 16px;
  }
  .series-tag {
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    font-weight: 700;
    font-size: 8.5pt;
    padding: 3px 10px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
  }
  h1 {
    color: #0f172a;
    font-size: 19pt;
    font-weight: 800;
    margin: 0 0 6px 0;
    line-height: 1.22;
  }
  .subtitle {
    color: #334155;
    font-size: 10.2pt;
    margin: 0 0 10px 0;
    font-weight: 500;
  }
  .meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    font-size: 8.5pt;
    color: #475569;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 8px 12px;
    border-radius: 6px;
  }

  h2 {
    color: #1e3a8a;
    font-size: 12.2pt;
    font-weight: 700;
    margin-top: 16px;
    margin-bottom: 7px;
    border-left: 4px solid #2563eb;
    padding-left: 9px;
    page-break-after: avoid;
  }
  .module-header {
    page-break-before: always;
    margin-top: 0;
    padding-top: 4px;
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
    font-size: 8.7pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
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
    font-size: 7.7pt;
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
    font-size: 8.4pt;
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

<!-- Cover Block -->
<div class="cover-header">
  <span class="series-tag">UC Berkeley CS 185/285 • Priority 1 Complete Master Compendium</span>
  <h1>Robotics Reinforcement Learning Foundations: Zero to Hero</h1>
  <div class="subtitle">An Intuitive, Parameter-Explained, Visual Field Manual for Dual-Arm Soft Object Slicing (Paper 1: Adaptive Tomato Slicing with PPO / SAC in NVIDIA Isaac Lab via SkRL)</div>
  <div class="meta-grid">
    <div>
      <b>Lectures Unified:</b> CS285 L01, L04, L05, L06, L08, L10<br>
      <b>Instructor:</b> Prof. Sergey Levine (UC Berkeley RAIL Lab)
    </div>
    <div>
      <b>Research Lab:</b> DEX-ROB Lab, Tianjin University (Prof. Shan An)<br>
      <b>Environment &amp; Stack:</b> NVIDIA Isaac Lab / PhysX 5 • SkRL Framework • PyTorch
    </div>
  </div>
</div>

<!-- EXECUTIVE ROADMAP -->
<div class="callout intuition">
  <div class="callout-title">🧭 The Zero-to-Hero Learning Journey: How the 6 Lectures Connect</div>
  <p>
    This master compendium takes an absolute beginner with zero prior knowledge of Reinforcement Learning and guides them to true conceptual, mathematical, and practical mastery. 
    Rather than getting lost in dry algebraic derivations, every core equation is accompanied by an exhaustive <b>Parameter Anatomy Table</b> explaining what every symbol means in plain English, paired with vivid real-world analogies, rich visual schemas, and concrete numerical examples.
  </p>
  <ul>
    <li><b>Lecture 1 (Foundations &amp; Closed Loop):</b> Why open-loop copying fails ($\mathcal{O}(\epsilon T^2)$), how closed-loop feedback stabilizes robots ($\mathcal{O}(\epsilon T)$), and how the MDP 6-tuple formalizes physical reality.</li>
    <li><b>Lecture 4 (Value Functions &amp; Bellman Equations):</b> Why predicting the future is essential, how the Bellman Expectation and Optimality equations break infinite time into two steps, and how the Advantage function reveals smart actions.</li>
    <li><b>Lecture 5 (Policy Gradients &amp; REINFORCE):</b> Why physical contact cannot be differentiated with standard calculus, how the "Good Boy!" Theorem optimizes black-box physics, and how Gaussian policies output continuous motor torques.</li>
    <li><b>Lecture 6 (Actor-Critic &amp; GAE):</b> Why waiting for the end of the episode is too noisy, how the Critic acts as a theater director whispering immediate guidance, and how GAE-$\lambda$ strikes the perfect bias-variance balance.</li>
    <li><b>Lecture 8 (Continuous Q-Learning &amp; Soft Actor-Critic):</b> Why finding continuous $\max Q$ on 14 robot joints is an impossible infinite beach search, how the Actor Maximizer solves it, and how Maximum Entropy RL cures timid policy freeze.</li>
    <li><b>Lecture 10 (Trust Regions &amp; PPO):</b> Why oversized updates cause catastrophic policy collapse (the student burning textbooks), how PPO's clipping mechanism acts as bowling alley bumpers, and why PPO unlocks 10x-50x speedups in GPU simulators.</li>
  </ul>
</div>

<!-- GRAND ARCHITECTURE DIAGRAM -->
<div class="diagram-container">
<svg width="620" height="95" viewBox="0 0 620 95">
  <rect x="10" y="10" width="90" height="75" rx="5" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="55" y="28" font-size="8.5" font-weight="700" fill="#1e40af" text-anchor="middle">LEC 01</text>
  <text x="55" y="44" font-size="7.5" fill="#1e3a8a" text-anchor="middle">MDP &amp; Closed</text>
  <text x="55" y="56" font-size="7.5" fill="#1e3a8a" text-anchor="middle">Loop Control</text>
  <text x="55" y="74" font-size="7" fill="#64748b" text-anchor="middle">$\mathcal{O}(\epsilon T)$ Bound</text>

  <path d="M 100,47 L 115,47" fill="none" stroke="#64748b" stroke-width="1.5"/>
  <polygon points="115,47 109,43 109,51" fill="#64748b"/>

  <rect x="115" y="10" width="90" height="75" rx="5" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="160" y="28" font-size="8.5" font-weight="700" fill="#334155" text-anchor="middle">LEC 04</text>
  <text x="160" y="44" font-size="7.5" fill="#334155" text-anchor="middle">Bellman &amp;</text>
  <text x="160" y="56" font-size="7.5" fill="#334155" text-anchor="middle">Value Functions</text>
  <text x="160" y="74" font-size="7" fill="#64748b" text-anchor="middle">$V^\pi, Q^\pi, A^\pi$</text>

  <path d="M 205,47 L 220,47" fill="none" stroke="#64748b" stroke-width="1.5"/>
  <polygon points="220,47 214,43 214,51" fill="#64748b"/>

  <rect x="220" y="10" width="90" height="75" rx="5" fill="#fefce8" stroke="#eab308" stroke-width="1.5"/>
  <text x="265" y="28" font-size="8.5" font-weight="700" fill="#854d0e" text-anchor="middle">LEC 05</text>
  <text x="265" y="44" font-size="7.5" fill="#854d0e" text-anchor="middle">Policy Gradients</text>
  <text x="265" y="56" font-size="7.5" fill="#854d0e" text-anchor="middle">&amp; REINFORCE</text>
  <text x="265" y="74" font-size="7" fill="#64748b" text-anchor="middle">$\nabla \log \pi \cdot Q$</text>

  <path d="M 310,47 L 325,47" fill="none" stroke="#64748b" stroke-width="1.5"/>
  <polygon points="325,47 319,43 319,51" fill="#64748b"/>

  <rect x="325" y="10" width="90" height="75" rx="5" fill="#f0fdf4" stroke="#22c55e" stroke-width="1.5"/>
  <text x="370" y="28" font-size="8.5" font-weight="700" fill="#166534" text-anchor="middle">LEC 06</text>
  <text x="370" y="44" font-size="7.5" fill="#166534" text-anchor="middle">Actor-Critic</text>
  <text x="370" y="56" font-size="7.5" fill="#166534" text-anchor="middle">&amp; GAE</text>
  <text x="370" y="74" font-size="7" fill="#64748b" text-anchor="middle">$\lambda = 0.95$ Blend</text>

  <path d="M 415,47 L 430,47" fill="none" stroke="#64748b" stroke-width="1.5"/>
  <polygon points="430,47 424,43 424,51" fill="#64748b"/>

  <rect x="430" y="10" width="85" height="75" rx="5" fill="#fff7ed" stroke="#f97316" stroke-width="1.5"/>
  <text x="472" y="28" font-size="8.5" font-weight="700" fill="#9a3412" text-anchor="middle">LEC 08</text>
  <text x="472" y="44" font-size="7.5" fill="#9a3412" text-anchor="middle">Continuous</text>
  <text x="472" y="56" font-size="7.5" fill="#9a3412" text-anchor="middle">SAC &amp; MaxEnt</text>
  <text x="472" y="74" font-size="7" fill="#64748b" text-anchor="middle">Twin-Q + $\alpha \mathcal{H}$</text>

  <path d="M 515,47 L 530,47" fill="none" stroke="#64748b" stroke-width="1.5"/>
  <polygon points="530,47 524,43 524,51" fill="#64748b"/>

  <rect x="530" y="10" width="80" height="75" rx="5" fill="#fdf2f8" stroke="#ec4899" stroke-width="1.5"/>
  <text x="570" y="28" font-size="8.5" font-weight="700" fill="#9d174d" text-anchor="middle">LEC 10</text>
  <text x="570" y="44" font-size="7.5" fill="#9d174d" text-anchor="middle">PPO &amp; Trust</text>
  <text x="570" y="56" font-size="7.5" fill="#9d174d" text-anchor="middle">Regions</text>
  <text x="570" y="74" font-size="7" fill="#64748b" text-anchor="middle">Clipped $r_t \hat{A}$</text>
</svg>
</div>
"""

# Extract each lecture's body
script_dir = "research/simulation/scripts"
l1_body = extract_body(f"{script_dir}/generate_lecture1_guide.py")
l4_body = extract_body(f"{script_dir}/generate_lecture4_guide.py")
l5_body = extract_body(f"{script_dir}/generate_lecture5_guide.py")
l6_body = extract_body(f"{script_dir}/generate_lecture6_guide.py")
l8_body = extract_body(f"{script_dir}/generate_lecture8_guide.py")
l10_body = extract_body(f"{script_dir}/generate_lecture10_guide.py")

# Format modules with clean module-header breaks
mod1 = f'<h2 class="module-header">Grand Module 1: The Foundations of Decision-Making &amp; Closed-Loop Control (Lecture 1)</h2>\n' + l1_body
mod2 = f'<h2 class="module-header">Grand Module 2: The Core Mathematics of Value &amp; Policy Evaluation (Lecture 4)</h2>\n' + l4_body
mod3 = f'<h2 class="module-header">Grand Module 3: Direct Policy Optimization &amp; Policy Gradients (Lecture 5)</h2>\n' + l5_body
mod4 = f'<h2 class="module-header">Grand Module 4: Actor-Critic Architectures &amp; Generalized Advantage Estimation (Lecture 6)</h2>\n' + l6_body
mod5 = f'<h2 class="module-header">Grand Module 5: Continuous Action Spaces, DDPG, TD3, &amp; Soft Actor-Critic (Lecture 8)</h2>\n' + l8_body
mod6 = f'<h2 class="module-header">Grand Module 6: Advanced Policy Gradients, Trust Regions, &amp; PPO (Lecture 10)</h2>\n' + l10_body

# Unique Master Synthesis Modules: 7, 8, 9, 10, 11
mod_synthesis = r"""
<!-- ========================================== -->
<!-- GRAND MODULE 7: 12-DIMENSION COMPARISON MATRIX -->
<!-- ========================================== -->
<h2 class="module-header">Grand Module 7: Master 12-Dimension Algorithm Grand Comparison Matrix</h2>
<p>
  The authoritative reference comparison across all six foundational reinforcement learning algorithms:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 15%;">Dimension</th>
      <th style="width: 14%;">REINFORCE (L5)</th>
      <th style="width: 14%;">A2C / GAE (L6)</th>
      <th style="width: 14%;">DQN (L4)</th>
      <th style="width: 15%;">SAC (L8)</th>
      <th style="width: 14%;">TRPO (L10)</th>
      <th style="width: 14%;">PPO (L10)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. Paradigm</b></td>
      <td>On-Policy PG</td>
      <td>On-Policy Actor-Critic</td>
      <td>Off-Policy TD</td>
      <td>Off-Policy MaxEnt AC</td>
      <td>On-Policy Trust Region</td>
      <td>On-Policy Clipped AC</td>
    </tr>
    <tr>
      <td><b>2. Policy Type</b></td>
      <td>Stochastic $\pi_\theta$</td>
      <td>Stochastic $\pi_\theta$</td>
      <td>Implicit $\arg\max Q$</td>
      <td>Stochastic Gaussian</td>
      <td>Stochastic Gaussian</td>
      <td>Stochastic Gaussian</td>
    </tr>
    <tr>
      <td><b>3. Action Space</b></td>
      <td>Discrete / Cont.</td>
      <td>Discrete / Cont.</td>
      <td>Discrete only</td>
      <td>Continuous only</td>
      <td>Discrete / Cont.</td>
      <td>Discrete / Cont.</td>
    </tr>
    <tr>
      <td><b>4. Sample Efficiency</b></td>
      <td>Very Low ($10^7$)</td>
      <td>Low ($10^7$)</td>
      <td>High ($10^5$)</td>
      <td><b>Very High ($10^5$)</b></td>
      <td>Moderate ($10^6$)</td>
      <td>Moderate ($10^6$)</td>
    </tr>
    <tr>
      <td><b>5. Wall-Clock Speed</b></td>
      <td>Slow</td>
      <td>Fast</td>
      <td>Moderate</td>
      <td>Moderate (Replay RAM)</td>
      <td>Slow (Fisher Hessian)</td>
      <td><b>Fastest on GPU</b></td>
    </tr>
    <tr>
      <td><b>6. Objective Function</b></td>
      <td>$\mathbb{E}[\nabla \log \pi G_t]$</td>
      <td>$\mathbb{E}[\nabla \log \pi \hat{A}^{\text{GAE}}]$</td>
      <td>$\mathbb{E}[(r + \gamma \max Q - Q)^2]$</td>
      <td>$\mathbb{E}[r + \alpha \mathcal{H}(\pi)]$</td>
      <td>$\max L_\pi \text{ s.t. } D_{\text{KL}} \le \delta$</td>
      <td>$\mathbb{E}[\min(r \hat{A}, \text{clip} \hat{A})]$</td>
    </tr>
    <tr>
      <td><b>7. Stability</b></td>
      <td>Extremely Low</td>
      <td>Moderate</td>
      <td>Moderate</td>
      <td><b>High (Twin-Q + Polyak)</b></td>
      <td>Very High</td>
      <td><b>Very High</b></td>
    </tr>
    <tr>
      <td><b>8. Replay Buffer</b></td>
      <td>No</td>
      <td>No</td>
      <td>Yes</td>
      <td><b>Yes ($10^6$ transitions)</b></td>
      <td>No</td>
      <td>No</td>
    </tr>
    <tr>
      <td><b>9. Exploration</b></td>
      <td>Stochastic policy</td>
      <td>Entropy bonus</td>
      <td>$\epsilon$-greedy</td>
      <td><b>MaxEnt ($\alpha \mathcal{H}$)</b></td>
      <td>Stochastic policy</td>
      <td>Entropy loss scale</td>
    </tr>
    <tr>
      <td><b>10. Sim-to-Real</b></td>
      <td>Poor</td>
      <td>Moderate</td>
      <td>Poor (Continuous)</td>
      <td><b>High</b></td>
      <td>High</td>
      <td><b>Highest (Dominant)</b></td>
    </tr>
    <tr>
      <td><b>11. Parallel Sim</b></td>
      <td>Poor</td>
      <td>Good</td>
      <td>Poor (Async buffer)</td>
      <td>Moderate</td>
      <td>Poor (CG overhead)</td>
      <td><b>Optimal (Linear)</b></td>
    </tr>
    <tr>
      <td><b>12. Canonical Use</b></td>
      <td>Toy CartPole</td>
      <td>Atari 2600</td>
      <td>Video Games</td>
      <td><b>Physical Robotics</b></td>
      <td>Robotics Locomotion</td>
      <td><b>Isaac Lab / RLHF</b></td>
    </tr>
  </tbody>
</table>

<div class="callout robotics">
  <div class="callout-title">🌲 The Robotics Algorithm Selection Decision Tree</div>
  <p>
    When starting a new physical robotics or simulation project, follow this exact rule:
  </p>
  <ul>
    <li><b>Are actions discrete (e.g. navigation grid, tool picking)?</b> $\longrightarrow$ Use <b>DQN</b> or Double-DQN.</li>
    <li><b>Are you training directly on physical hardware where robot hours are scarce ($&lt; 50$ hours)?</b> $\longrightarrow$ Use <b>SAC</b> (Maximum Entropy Off-Policy). Its replay buffer achieves unmatched sample efficiency.</li>
    <li><b>Are you training inside a massively parallel GPU simulator (NVIDIA Isaac Lab / Omniverse) with 1,024+ envs?</b> $\longrightarrow$ Use <b>PPO</b> with GAE($\lambda = 0.95$). It scales linearly with GPU threads, trains in 40 minutes, and has zero replay buffer memory overhead.</li>
  </ul>
</div>

<!-- ========================================== -->
<!-- GRAND MODULE 8: PAPER 1 BLUEPRINT -->
<!-- ========================================== -->
<h2 class="module-header">Grand Module 8: Master Paper 1 Implementation Blueprint (Dual-Arm Slicing)</h2>
<p>
  Here is the complete operational blueprint connecting CS285 Priority 1 directly to your Master's thesis methodology: 
  <b>Adaptive Dual-Arm Soft Object Slicing with PPO / SAC in NVIDIA Isaac Lab via SkRL</b>.
</p>

<h3>8.1 Multi-Modal State Space Mapping ($\mathbb{R}^{33}$)</h3>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Subsystem</th>
      <th style="width: 15%;">Dimension</th>
      <th style="width: 35%;">Sensor / Physical Origin</th>
      <th style="width: 25%;">Normalization Range</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Arm Kinematics</b></td>
      <td>$\mathbb{R}^{14}$</td>
      <td>Dual-arm joint angles $q$ (7) and velocities $\dot{q}$ (7).</td>
      <td>Normalized by physical joint limits.</td>
    </tr>
    <tr>
      <td><b>Blade Kinematics</b></td>
      <td>$\mathbb{R}^9$</td>
      <td>Blade tip 3D position $p$, linear velocity $v$, angular velocity $\omega$.</td>
      <td>Relative to cutting board coordinate frame.</td>
    </tr>
    <tr>
      <td><b>Tomato Geometry</b></td>
      <td>$\mathbb{R}^7$</td>
      <td>3D center of mass $p$ and orientation quaternion $q$.</td>
      <td>USD pose in sim; YOLO/RGB-D in real.</td>
    </tr>
    <tr>
      <td><b>TacBlade F/T</b></td>
      <td>$\mathbb{R}^6$</td>
      <td>3-axis force ($F_x, F_y, F_z$) and torque ($T_x, T_y, T_z$).</td>
      <td>Filtered 50 Hz; $F_z \in [0, 25]$ N.</td>
    </tr>
    <tr>
      <td><b>Acoustic Burst</b></td>
      <td>$\mathbb{R}^1$</td>
      <td>RMS acoustic energy envelope ($100 \text{ Hz} - 5 \text{ kHz}$).</td>
      <td>Detects exact millisecond of skin puncture.</td>
    </tr>
    <tr style="background: #eff6ff;">
      <td><b>Total State $\mathcal{S}$</b></td>
      <td><b>$\mathbb{R}^{33}$</b></td>
      <td><b>Full Markovian observation vector fed to Actor &amp; Critic.</b></td>
      <td><b>Standardized via running mean and variance.</b></td>
    </tr>
  </tbody>
</table>

<h3>8.2 Continuous Action Parameterization ($\mathbb{R}^6$)</h3>
<table>
  <thead>
    <tr>
      <th style="width: 14%;">Channel</th>
      <th style="width: 24%;">Physical Parameter</th>
      <th style="width: 20%;">Operational Range</th>
      <th style="width: 42%;">Robotic Function</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>$a_0$</td>
      <td>Downward Feed $\Delta v_z$</td>
      <td>$[-5.0, +5.0]$ mm/s</td>
      <td>Modulates vertical penetration rate based on contact resistance.</td>
    </tr>
    <tr>
      <td>$a_1$</td>
      <td>Sawing Velocity $v_{\text{slice}}$</td>
      <td>$[-30.0, +30.0]$ mm/s</td>
      <td>Lateral sawing motion reducing normal puncture force.</td>
    </tr>
    <tr>
      <td>$a_2$</td>
      <td>Vertical Stiffness $\Delta K_z$</td>
      <td>$[-500, +500]$ N/m</td>
      <td>Impedance modulation: softens blade upon contact to avoid crushing.</td>
    </tr>
    <tr>
      <td>$a_3$</td>
      <td>Vertical Damping $\Delta D_z$</td>
      <td>$[-20, +20]$ Ns/m</td>
      <td>Damps out high-frequency contact vibrations.</td>
    </tr>
    <tr>
      <td>$a_4$</td>
      <td>Grasp Normal Force $F_{\text{hold}}$</td>
      <td>$[1.0, 6.0]$ N</td>
      <td>Holding arm normal contact force preventing tomato slip.</td>
    </tr>
    <tr>
      <td>$a_5$</td>
      <td>Holding Compliance $\Delta K_{\text{hold}}$</td>
      <td>$[-300, +300]$ N/m</td>
      <td>Maintains adaptive grip on soft, deforming fruit pulp.</td>
    </tr>
  </tbody>
</table>

<h3>8.3 Domain Randomization (DR) Master Table (Sim-to-Real Transfer)</h3>
<p>
  To guarantee that policies trained in NVIDIA Isaac Lab transfer seamlessly to the physical Franka Emika Panda arms without fine-tuning, 10 parameters are randomized across every episode:
</p>
<table>
  <thead>
    <tr>
      <th style="width: 25%;">Physical Parameter</th>
      <th style="width: 25%;">Nominal Value</th>
      <th style="width: 25%;">Randomization Range</th>
      <th style="width: 25%;">Sim-to-Real Protection</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Skin Puncture Force ($F_{\text{punc}}$)</b></td>
      <td>$3.2$ N</td>
      <td>$[1.8, 5.5]$ N (Uniform)</td>
      <td>Fruit ripeness &amp; skin thickness variance.</td>
    </tr>
    <tr>
      <td><b>Pulp Elastic Modulus ($E$)</b></td>
      <td>$45$ kPa</td>
      <td>$[20, 80]$ kPa (Log-Uniform)</td>
      <td>Soft flesh vs firm over-ripe fruit flesh.</td>
    </tr>
    <tr>
      <td><b>Blade-Skin Friction ($\mu$)</b></td>
      <td>$0.35$</td>
      <td>$[0.15, 0.60]$ (Uniform)</td>
      <td>Wetness, juices, and surface lubrication.</td>
    </tr>
    <tr>
      <td><b>Knife Sharpness Factor</b></td>
      <td>$1.0$ (New)</td>
      <td>$[0.6, 1.2]$ (Uniform)</td>
      <td>Dull vs sharp blade contact mechanics.</td>
    </tr>
    <tr>
      <td><b>Fruit Mass ($m$)</b></td>
      <td>$140$ g</td>
      <td>$[90, 220]$ g (Normal)</td>
      <td>Fruit size and inertial variation.</td>
    </tr>
    <tr>
      <td><b>Knife Initial Pitch Tilt</b></td>
      <td>$0^\circ$</td>
      <td>$[-4^\circ, +4^\circ]$ (Normal)</td>
      <td>Mounting calibration and fixture error.</td>
    </tr>
    <tr>
      <td><b>Actuator Latency ($\tau_{\text{delay}}$)</b></td>
      <td>$20$ ms</td>
      <td>$[10, 45]$ ms (Discrete)</td>
      <td>EtherCAT bus communication jitter.</td>
    </tr>
    <tr>
      <td><b>F/T Sensor Zero Drift</b></td>
      <td>$0.0$ N</td>
      <td>$[-0.3, +0.3]$ N (Normal)</td>
      <td>Thermal sensor drift and tare offset.</td>
    </tr>
    <tr>
      <td><b>Acoustic Burst Noise Floor</b></td>
      <td>$35$ dB</td>
      <td>$[30, 48]$ dB (Uniform)</td>
      <td>Kitchen environment background noise.</td>
    </tr>
    <tr>
      <td><b>Holding Gripper Friction</b></td>
      <td>$0.70$</td>
      <td>$[0.40, 0.95]$ (Uniform)</td>
      <td>Silicone gripper pad wear and fruit moisture.</td>
    </tr>
  </tbody>
</table>

<!-- ========================================== -->
<!-- GRAND MODULE 9: PRODUCTION SKRL CODE -->
<!-- ========================================== -->
<h2 class="module-header">Grand Module 9: Production SkRL &amp; PyTorch Architecture</h2>
<p>
  Below is the complete, modular PyTorch implementation of our dual-head Actor-Critic network and environment reward function:
</p>

<div class="callout code-box">
  <div class="callout-title">🐍 PyTorch Dual-Head Actor-Critic Model (`models.py`)</div>
<pre style="margin: 0; padding: 0;">
import torch
import torch.nn as nn
from skrl.models.torch import GaussianMixin, DeterministicMixin, Model

class SlicingActorCritic(GaussianMixin, DeterministicMixin, Model):
    def __init__(self, observation_space, action_space, device, clip_actions=False):
        Model.__init__(self, observation_space, action_space, device)
        GaussianMixin.__init__(self, clip_actions=clip_actions)
        DeterministicMixin.__init__(self)

        in_dim = observation_space.shape[0]   # 33 inputs
        out_dim = action_space.shape[0]       # 6 continuous actions

        # Shared representation backbone
        self.backbone = nn.Sequential(
            nn.Linear(in_dim, 256), nn.ELU(),
            nn.Linear(256, 256), nn.ELU()
        )
        self.actor_mean = nn.Linear(256, out_dim)
        self.log_std_parameter = nn.Parameter(torch.zeros(out_dim))
        self.critic_head = nn.Linear(256, 1)

    def act(self, inputs, role):
        features = self.backbone(inputs["states"])
        if role == "policy":
            mean = self.actor_mean(features)
            log_std = torch.clamp(self.log_std_parameter, min=-20.0, max=2.0)
            return mean, log_std, {}
        elif role == "value":
            value = self.critic_head(features)
            return value, {}
</pre>
</div>

<h3>9.1 Master SkRL Configuration (`ppo_cfg.yaml`)</h3>
<div class="callout code-box">
  <div class="callout-title">⚙️ Production ppo_cfg.yaml Reference</div>
<pre style="margin: 0; padding: 0;">
algorithm:
  class: PPO
  clip_range: 0.2            # Lecture 10: Bowling bumpers preventing policy collapse
  gae_lambda: 0.95           # Lecture 6: Optimal exponential blend of TD(0) and MC
  discount_factor: 0.99      # Lecture 4: gamma = 0.99 ensures planning across 300+ steps
  learning_rate: 3e-4        # Standard Adam step size
  learning_rate_scheduler: KLAdaptiveLR  # Scales LR based on policy KL divergence
  entropy_loss_scale: 0.01   # Lecture 8: Encourages exploration of impedance parameters
  value_loss_scale: 1.0      # Weight of Critic MSE regression loss
  epochs: 5                  # Lecture 10: Safely re-uses parallel GPU rollout batches
  mini_batches: 4            # Subdivides 1,024 parallel envs into mini-batches
</pre>
</div>

<!-- ========================================== -->
<!-- GRAND MODULE 10: TENSORBOARD DIAGNOSTIC FIELD GUIDE -->
<!-- ========================================== -->
<h2 class="module-header">Grand Module 10: TensorBoard Diagnostic Field Guide: Reading the Vital Signs of RL</h2>
<p>
  When training reinforcement learning policies, watching raw terminal printouts is useless. 
  An expert roboticist reads TensorBoard curves like a doctor reads an electrocardiogram (ECG):
</p>

<table>
  <thead>
    <tr>
      <th style="width: 20%;">TensorBoard Curve</th>
      <th style="width: 25%;">Healthy Behavior</th>
      <th style="width: 27%;">Pathological Warning Sign</th>
      <th style="width: 28%;">Diagnostic &amp; Immediate Remedy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1. <code>approx_kl</code></b><br>(Approximate KL)</td>
      <td>Stays smoothly between $0.005$ and $0.015$. Gentle sawtooth pattern during epochs.</td>
      <td>Spikes violently above $0.040$, followed by immediate collapse in episode return.</td>
      <td><b>Trust region rupture!</b> Learning rate is too high. Lower LR from <code>3e-4</code> to <code>1e-4</code>, or enable <code>KLAdaptiveLR</code>.</td>
    </tr>
    <tr>
      <td><b>2. <code>clip_fraction</code></b><br>(PPO Clip Ratio)</td>
      <td>Hovers around $0.08$ to $0.18$ ($8\%$ to $18\%$ of transitions active on bumpers).</td>
      <td>Exceeds $0.50$ ($50\%$ clipped) or collapses to $0.00$ ($0\%$ clipped).</td>
      <td>If $>0.50$: Batch size too small or too many epochs; If $0.00$: Policy is not learning at all.</td>
    </tr>
    <tr>
      <td><b>3. <code>explained_variance</code></b><br>(Critic Accuracy)</td>
      <td>Rises steadily from $0.0$ to $0.85$–$0.95$ ($1 - \frac{\text{Var}(y-V)}{\text{Var}(y)}$).</td>
      <td>Stays negative ($&lt; 0.0$) or hovers near zero for 500,000 steps.</td>
      <td><b>Critic is worse than predicting the mean!</b> Check reward scaling (multiply rewards by $0.1$). Ensure $V(s)$ network has sufficient capacity.</td>
    </tr>
    <tr>
      <td><b>4. <code>entropy</code></b><br>(Action Distribution)</td>
      <td>Starts high ($\approx 2.5$), smoothly decays over 1M steps to $\approx 0.5$ as policy masters task.</td>
      <td>Collapses abruptly to $-15.0$ in first 20,000 steps (premature convergence).</td>
      <td><b>Entropy collapse!</b> Policy locked into a rigid bad habit. Increase <code>entropy_loss_scale</code> from <code>0.001</code> to <code>0.02</code>.</td>
    </tr>
    <tr>
      <td><b>5. <code>mean_reward</code></b><br>(Episode Return)</td>
      <td>Monotonic upward climb: negative early score $\to 0 \to +50 \to +140$ plateau.</td>
      <td>Rises to $+60$, then drops off a cliff to $-40$ and stays flat forever.</td>
      <td><b>Policy collapse death spiral!</b> Revert to previous checkpoint; decrease PPO clip range to $\epsilon = 0.15$.</td>
    </tr>
  </tbody>
</table>

<!-- ========================================== -->
<!-- GRAND MODULE 11: THESIS DEFENSE MASTER CHEATSHEET -->
<!-- ========================================== -->
<h2 class="module-header">Grand Module 11: Thesis Defense Master Cheatsheet (Top 15 Reviewer Q&amp;A)</h2>
<p>
  These 15 questions represent the most demanding, technical inquiries posed by academic examination committees and journal reviewers:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 5%;">#</th>
      <th style="width: 42%;">Reviewer / Committee Question</th>
      <th style="width: 53%;">Your Bulletproof Academic Answer</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>1</b></td>
      <td>Why use Reinforcement Learning instead of standard Classical Impedance Control?</td>
      <td>Classical impedance control requires hand-tuning constant stiffness ($K$) and damping ($D$). Soft fruits exhibit non-linear viscoplastic fracture transitions where contact stiffness drops by over 80% within milliseconds upon skin puncture. RL dynamically modulates compliance parameters in response to real-time high-frequency tactile and acoustic signals.</td>
    </tr>
    <tr>
      <td><b>2</b></td>
      <td>Why is your task formulated as a Markov Decision Process (MDP)?</td>
      <td>Our 33-dimensional state vector contains both kinematics (joint and blade positions/velocities) and contact forces ($F/T$), meaning the transition to $s_{t+1}$ depends solely on the current state $s_t$ and action $a_t$, strictly satisfying the Markov conditional independence property.</td>
    </tr>
    <tr>
      <td><b>3</b></td>
      <td>Why did you choose PPO over Model-Based RL?</td>
      <td>Deformable viscoplastic fracture mechanics are notoriously difficult to model analytically. Model-based RL compounds model bias across extended horizons, causing sim-to-real transfer failure. PPO is model-free, highly robust, and directly optimizes the true multi-objective reward.</td>
    </tr>
    <tr>
      <td><b>4</b></td>
      <td>How do you address PPO's low sample efficiency?</td>
      <td>Through GPU-vectorized parallel physics simulation in NVIDIA Isaac Lab. By simulating 1,024 environments simultaneously on an RTX GPU, we collect over 10 million simulation transitions in under 45 minutes, rendering on-policy sample efficiency irrelevant.</td>
    </tr>
    <tr>
      <td><b>5</b></td>
      <td>What is the exact role of the Critic network?</td>
      <td>The Critic approximates the State-Value function $V(s)$ using Temporal Difference learning. It is used to compute the Advantage function $\hat{A}(s, a) = Q(s, a) - V(s)$, which dramatically reduces policy gradient variance compared to raw Monte Carlo rollouts.</td>
    </tr>
    <tr>
      <td><b>6</b></td>
      <td>Why is Generalized Advantage Estimation (GAE) with $\lambda = 0.95$ used?</td>
      <td>Pure TD learning ($\lambda = 0$) has minimal variance but introduces bias if the Critic is inaccurate. Pure rollouts ($\lambda = 1$) have zero bias but massive variance. GAE with $\lambda = 0.95$ achieves an optimal exponential blend of multi-step returns.</td>
    </tr>
    <tr>
      <td><b>7</b></td>
      <td>Why did you configure continuous action spaces instead of discrete?</td>
      <td>Robot joint motor torques, feed velocities, and compliance deltas ($\Delta K, \Delta D$) are continuous physical quantities. Discretizing them creates coarse, jerky motions that damage soft object skins.</td>
    </tr>
    <tr>
      <td><b>8</b></td>
      <td>What is the purpose of PPO's clipping mechanism?</td>
      <td>It bounds the probability ratio $r_t(\theta)$ between $[1-\epsilon, 1+\epsilon]$ (typically $\epsilon = 0.2$). This prevents policy collapse by discarding gradient steps that deviate too far from the policy that generated the trajectory data.</td>
    </tr>
    <tr>
      <td><b>9</b></td>
      <td>Why is lateral sawing velocity rewarded?</td>
      <td>Under fracture mechanics shear-stress coupling, lateral slicing motion significantly reduces the required normal downward force ($F_z$) to achieve fracture toughness ($K_{\text{Ic}}$), preventing fruit crushing.</td>
    </tr>
    <tr>
      <td><b>10</b></td>
      <td>How does Soft Actor-Critic (SAC) prevent local minima?</td>
      <td>By optimizing Maximum Entropy RL ($\text{Reward} + \alpha \cdot \text{Entropy}$). The entropy term encourages broad, stochastic exploration, preventing the robot from adopting timid policies that freeze above the tomato skin to avoid crushing penalties.</td>
    </tr>
    <tr>
      <td><b>11</b></td>
      <td>Why do you use Asymmetric Actor-Critic in simulation?</td>
      <td>During simulation training, the Critic is fed privileged state information (e.g. true ground-truth internal tomato stress, exact blade friction coefficient) which is unavailable on the physical robot. The Actor is only fed realistic sensor observations (joint encoders, F/T sensor, acoustic RMS). Because the Critic is discarded during deployment, the policy executes flawlessly with zero sim-to-real observation mismatch!</td>
    </tr>
    <tr>
      <td><b>12</b></td>
      <td>How does Domain Randomization bridge the Sim-to-Real gap?</td>
      <td>By randomizing 10 physical parameters (friction, stiffness, puncture force, actuator delays) during training, the simulation covers an envelope of physical realities. The policy learns a robust, invariant control strategy that treats real-world dynamics as just another sample from its training distribution.</td>
    </tr>
    <tr>
      <td><b>13</b></td>
      <td>What prevents the policy from learning high-frequency motor chatter?</td>
      <td>Our reward function includes an explicit action smoothness penalty: $p_{\text{smooth}} = -0.05 \sum_i (a_t^i - a_{t-1}^i)^2$. Furthermore, low-pass filtering on torque commands dampens jerk above 10 Hz, protecting robot gearboxes.</td>
    </tr>
    <tr>
      <td><b>14</b></td>
      <td>Why is the discount factor set to $\gamma = 0.99$ instead of $0.90$?</td>
      <td>With an effective planning horizon $H_{\text{eff}} = \frac{1}{1-\gamma}$, $\gamma = 0.90$ only plans $10$ steps ahead ($0.2$ seconds at 50 Hz). A slicing stroke requires 300 steps ($6.0$ seconds). $\gamma = 0.99$ yields $H_{\text{eff}} = 100$ steps, giving the robot sufficient foresight to plan multi-stroke sawing without stalling.</td>
    </tr>
    <tr>
      <td><b>15</b></td>
      <td>How do you guarantee physical safety on real hardware?</td>
      <td>Hardware safety is guaranteed by: (1) strict joint velocity and torque limit clamping at the low-level FOC motor driver layer; (2) automatic emergency stop triggers if normal force $F_z$ exceeds 15 N; and (3) running the RL policy in impedance-offset mode rather than raw unconstrained direct torque mode.</td>
    </tr>
  </tbody>
</table>

<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0 10px 0;">
<div style="font-size: 8.5pt; color: #64748b; text-align: center;">
  <i>DEX-ROB Lab (Tianjin University) Master's Research Program • Prof. Shan An • Created with Antigravity AI</i>
</div>

</body>
</html>
"""

full_html = html_head + "\n" + mod1 + "\n" + mod2 + "\n" + mod3 + "\n" + mod4 + "\n" + mod5 + "\n" + mod6 + "\n" + mod_synthesis

print(f"Total Master HTML length: {len(full_html)} chars, {len(full_html.splitlines())} lines.")

with open(f"{script_dir}/generate_priority1_master_guide.py", "w", encoding="utf-8") as f:
    f.write(r'''import os
import sys
import shutil
import render_utils

PDF_OUT_DOWNLOADS = "/home/omen/Downloads/CS285_Priority1_Master_Robotics_Guide.pdf"
PDF_OUT_REPO = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation/CS285_Priority1_Master_Robotics_Guide.pdf"

html_doc = r"""''' + full_html + r'''"""

render_utils.build_pdf(html_doc, PDF_OUT_DOWNLOADS, PDF_OUT_REPO)
''')

print("-> Successfully updated generate_priority1_master_guide.py!")
