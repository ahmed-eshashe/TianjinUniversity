#!/usr/bin/env python3
"""
Publication-Grade Academic Research Proposal for Prof. Shan An (安山):
Autonomous Agent-in-the-Loop Reinforcement Learning in NVIDIA Isaac Lab
Project: Bimanual Deformable Object Manipulation (DOM) - Soft-Body Slicing with ARX AR5-L6 Dual Arms
Laboratory: DEX-ROB Lab, School of Electrical & Automation Engineering, Tianjin University (天津大学)
Authors: Ahmed & Shahd (M.S. Control Science & Engineering)
"""

import os
import weasyprint

OUTPUT_HTML = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/reports/autonomous_rl_agent_research_proposal.html"
OUTPUT_PDF = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/reports/autonomous_rl_agent_research_proposal.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Research Proposal: Autonomous Agent-in-the-Loop Reinforcement Learning for Bimanual Deformable Slicing in NVIDIA Isaac Lab</title>
<style>
  @page {
    size: A4;
    margin: 15mm 15mm 16mm 15mm;
    @top-left {
      content: "TIANJIN UNIVERSITY (天津大学) | DEX-ROB Lab · SEAE";
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 7.2pt;
      color: #64748b;
      font-weight: 600;
      border-bottom: 0.5pt solid #cbd5e1;
      padding-bottom: 4px;
      margin-bottom: 5px;
    }
    @top-right {
      content: "M.S. Research Proposal: Autonomous RL in Isaac Lab";
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 7.2pt;
      color: #64748b;
      font-weight: 500;
      border-bottom: 0.5pt solid #cbd5e1;
      padding-bottom: 4px;
      margin-bottom: 5px;
    }
    @bottom-left {
      content: "Bimanual DOM: Dual ARX AR5-L6 Arms · PhysX 5 FEM Slicing · LLM-Guided Reward Tuning";
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 7.2pt;
      color: #94a3b8;
      border-top: 0.5pt solid #cbd5e1;
      padding-top: 4px;
    }
    @bottom-right {
      content: "Page " counter(page) " of " counter(pages);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 7.2pt;
      font-weight: 700;
      color: #334155;
      border-top: 0.5pt solid #cbd5e1;
      padding-top: 4px;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    font-size: 8.4pt;
    line-height: 1.42;
    text-rendering: optimizeLegibility;
  }

  .page-start {
    page-break-before: always;
    break-before: page;
  }

  /* Header Section */
  .header-card {
    background: linear-gradient(135deg, #091e42 0%, #1e3a8a 50%, #0369a1 100%);
    color: #ffffff;
    padding: 15px 18px;
    border-radius: 6px;
    margin-bottom: 10px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
  .header-badge {
    display: inline-block;
    background: rgba(59, 130, 246, 0.35);
    border: 1px solid rgba(147, 197, 253, 0.4);
    color: #bfdbfe;
    font-size: 6.8pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 2px 6px;
    border-radius: 3px;
    margin-bottom: 5px;
  }
  .header-title {
    font-size: 14pt;
    font-weight: 800;
    line-height: 1.2;
    margin: 0 0 5px 0;
    letter-spacing: -0.3px;
    color: #ffffff;
  }
  .header-subtitle {
    font-size: 8.6pt;
    font-weight: 400;
    color: #93c5fd;
    margin: 0 0 8px 0;
    line-height: 1.32;
  }
  .header-meta-grid {
    display: grid;
    grid-template-columns: 1.3fr 1.3fr 1.3fr 1.5fr;
    gap: 7px;
    border-top: 1px solid rgba(255, 255, 255, 0.18);
    padding-top: 6px;
    font-size: 7.2pt;
  }
  .meta-item strong {
    color: #93c5fd;
    font-weight: 600;
  }

  /* Section Headings */
  h1 {
    font-size: 10.4pt;
    font-weight: 800;
    color: #0f172a;
    border-left: 4px solid #2563eb;
    padding-left: 6px;
    margin-top: 10px;
    margin-bottom: 5px;
    letter-spacing: -0.2px;
    text-transform: uppercase;
    page-break-after: avoid;
    break-after: avoid;
  }
  h2 {
    font-size: 8.8pt;
    font-weight: 700;
    color: #1e3a8a;
    margin-top: 7px;
    margin-bottom: 3px;
    page-break-after: avoid;
    break-after: avoid;
  }
  p {
    margin: 0 0 5.5px 0;
    text-align: justify;
  }

  /* Callout Box */
  .callout {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #0284c7;
    border-radius: 4px;
    padding: 7px 11px;
    margin: 6px 0 8px 0;
  }
  .callout-title {
    font-size: 7.4pt;
    font-weight: 800;
    color: #0369a1;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 2.5px;
  }
  .callout p {
    margin: 0;
    font-size: 8.1pt;
    color: #334155;
    line-height: 1.38;
  }

  /* Highlight Box */
  .highlight-box {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 4px;
    padding: 7px 10px;
    margin: 6px 0;
  }
  .highlight-title {
    font-weight: 800;
    color: #1d4ed8;
    margin-bottom: 2.5px;
    font-size: 8.1pt;
  }

  /* Math Block */
  .math-block {
    background-color: #f1f5f9;
    border-left: 3px solid #64748b;
    padding: 4px 10px;
    margin: 5px 0;
    font-family: 'Cambria Math', 'Times New Roman', serif;
    font-size: 8.6pt;
    color: #0f172a;
    text-align: center;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0 8px 0;
    font-size: 7.4pt;
  }
  th {
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 4px 6px;
    border: 1px solid #0f172a;
    font-size: 7.1pt;
    letter-spacing: 0.2px;
  }
  td {
    padding: 4px 6px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
    line-height: 1.32;
  }
  tr:nth-child(even) {
    background-color: #f8fafc;
  }

  /* Code Block */
  pre {
    background-color: #0f172a;
    color: #e2e8f0;
    padding: 6px 8px;
    border-radius: 4px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 6.9pt;
    line-height: 1.32;
    margin: 5px 0;
    overflow: hidden;
    border: 1px solid #1e293b;
  }
  code {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 7.3pt;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1px 3px;
    border-radius: 3px;
    border: 0.5px solid #cbd5e1;
  }
  pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
    border: none;
  }

  /* Citation tags */
  .citation-tag {
    display: inline-block;
    background-color: #dbeafe;
    color: #1e40af;
    font-weight: 700;
    font-size: 6.5pt;
    padding: 1px 3.5px;
    border-radius: 2px;
    margin-right: 2px;
  }

  /* Grid Layouts */
  .two-col {
    display: flex;
    gap: 8px;
    margin: 4px 0;
  }
  .col {
    flex: 1;
  }

  /* Diagram Container */
  .diagram-container {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 5px;
    margin: 6px 0;
    text-align: center;
  }
  .diagram-caption {
    font-size: 7.0pt;
    font-weight: 600;
    color: #475569;
    margin-top: 3px;
    text-align: center;
  }

  .avoid-break {
    page-break-inside: avoid;
    break-inside: avoid;
  }

  /* References */
  .ref-item {
    font-size: 7.0pt;
    margin-bottom: 3px;
    padding-left: 16px;
    text-indent: -16px;
    line-height: 1.32;
    color: #334155;
  }
  .ref-num {
    font-weight: 700;
    color: #1e3a8a;
  }
</style>
</head>
<body>

<!-- =================================================================== -->
<!-- PAGE 1: Header, Abstract, and Problem Formulation                   -->
<!-- =================================================================== -->
<div>
  <!-- Header Card -->
  <div class="header-card">
    <div class="header-badge">DEX-ROB Lab · Graduate Research Proposal &amp; Methodological Plan</div>
    <h1 class="header-title">Autonomous Agent-in-the-Loop Reinforcement Learning:<br>LLM-Guided Reward Synthesis &amp; Policy Optimization in Isaac Lab</h1>
    <div class="header-subtitle">Methodological Framework for Bimanual Deformable Slicing (DOM) on Dual ARX AR5-L6 Arms with PhysX 5 FEM</div>
    <div class="header-meta-grid">
      <div class="meta-item"><strong>Advisor:</strong> Prof. Shan An (安山)</div>
      <div class="meta-item"><strong>Authors:</strong> Ahmed &amp; Shahd (M.S. Candidates)</div>
      <div class="meta-item"><strong>Lab &amp; Dept:</strong> DEX-ROB Lab · SEAE, TJU</div>
      <div class="meta-item"><strong>Target Platform:</strong> ARX AR5-L6 (7-DoF) &amp; Isaac Lab</div>
    </div>
  </div>

  <!-- Executive Summary -->
  <div class="callout">
    <div class="callout-title">Proposal Abstract &amp; Research Motivation for DEX-ROB Lab</div>
    <p>
      Autonomous robotic manipulation of deformable culinary produce (e.g., tomatoes and soft agricultural products) represents a critical frontier in intelligent kitchen automation (directly aligning with DEX-ROB Lab's cooking robotics initiatives and Meishanshi / 美膳狮 collaboration). Continuum slicing exhibits severe mechanical discontinuities: knife puncture through the outer peel induces an abrupt reduction in penetration resistance, while coordinated dual arms face a coupled <strong>"Tear-versus-Slip" trade-off</strong> (holding normal force must remain strictly bounded to prevent slippage under sawing shear drag without causing localized crush damage). In this proposal, we investigate the fundamental scientific question: <em>Can an autonomous LLM reward-synthesis agent discover physically consistent, non-linear reward structures for contact-rich bimanual deformable manipulation, where manually designed linear scalar rewards fail?</em> Introducing an autonomous reasoning agent (grounded in the <strong>Eureka [ICLR 2024 Oral]</strong> and <strong>DrEureka [2024]</strong> paradigms) directly into <strong>NVIDIA Isaac Lab</strong>, the agent programmatically synthesizes non-linear barrier reward code and domain randomization distributions for our dual <strong>ARX AR5-L6 7-DoF arms</strong> with LinkerHand O6 dexterous hands. This framework eliminates weeks of empirical trial-and-error, establishing a rigorous foundation for our planned <strong>IEEE RA-L / IROS</strong> manuscript.
    </p>
  </div>

  <!-- Section 1 -->
  <h1>1. Problem Formulation: The Bimanual Reward Engineering Bottleneck</h1>
  <p>
    In the canonical continuous-action Markov Decision Process &lang;<i>S</i>, <i>A</i>, <i>P</i>, <i>R</i>, &gamma;&rang;, the policy optimization objective is to discover policy parameters &theta;* maximizing expected discounted return:
  </p>
  <div class="math-block">
    <i>J</i>(&theta;) = <b>E</b><sub>&tau; ~ &pi;<sub>&theta;</sub></sub> [ &sum;<sub><i>t</i>=0</sub><sup><i>T</i></sup> &gamma;<sup><i>t</i></sup> <i>R</i>(<i>s</i><sub><i>t</i></sub>, <i>a</i><sub><i>t</i></sub>) ]
  </div>
  <p>
    In our two-person research workflow (Subsystem A: Shahd's Slicing Arm; Subsystem B: Ahmed's Compliant Holding Arm), human researchers typically attempt to hand-craft multi-objective dense reward functions:
  </p>
  <div class="math-block">
    <i>R</i><sub>dense</sub>(<i>s</i>, <i>a</i>) = <i>w</i><sub>pen</sub> <i>R</i><sub>pen</sub> + <i>w</i><sub>saw</sub> <i>R</i><sub>saw</sub> &minus; <i>w</i><sub>slam</sub> <i>P</i><sub>slam</sub> &minus; <i>w</i><sub>damage</sub> <i>P</i><sub>damage</sub> &minus; <i>w</i><sub>slip</sub> <i>P</i><sub>slip</sub> &minus; <i>w</i><sub>reg</sub> ||<i>a</i>||<sup>2</sup>
  </div>
  <p>
    When simulating continuum deformation via <strong>PhysX 5 FEM</strong> tetrahedral meshes, this manual scalar trial-and-error approach breaks down due to three fundamental bottlenecks:
  </p>
  <ul style="margin-top: 3px; padding-left: 17px; margin-bottom: 0;">
    <li style="margin-bottom: 4px;"><strong>Post-Puncture Force Discontinuity:</strong> Empirical puncture tests across soft produce literature demonstrate that puncturing the outer peel into the flesh induces an abrupt reduction in cutting resistance (frequently dropping by 50%–75% within milliseconds, depending on blade geometry, approach velocity, ripeness, and cultivar). Linear penalty approximations fail to arrest downward knife momentum, causing the blade to slam into the interior and crush the food.</li>
    <li style="margin-bottom: 4px;"><strong>The Bimanual Pareto Conflict:</strong> Ahmed's holding arm must maintain normal force strictly inside an experimentally calibrated compliance window (<i>F</i><sub>min, slip</sub> &lt; <i>F</i><sub>hold</sub> &lt; <i>F</i><sub>max, damage</sub>) to resist Shahd's sawing shear force (<i>F</i><sub><i>x</i></sub>) without inducing localized tissue bruising. Manually balancing multiple coupled scalar weights across two 7-DoF arms requires weeks of iterative retuning.</li>
    <li><strong>Proprioceptive Torque Sensing Constraint (Lab Hardware Confirmed):</strong> As confirmed with Prof. Shan An, the physical laboratory setup operates with native joint torque sensing (&tau;<sub>ext</sub> &rarr; <i>F</i><sub>ext</sub> via Jacobian transpose) and camera vision, rather than specialized dense tactile skin arrays. Reward formulations must therefore operate robustly over proprioceptive torque signals and FEM state variables.</li>
  </ul>
</div>

<!-- =================================================================== -->
<!-- PAGE 2: Literature Review and System Architecture                   -->
<!-- =================================================================== -->
<div class="page-start">
  <!-- Section 2 -->
  <h1>2. Literature Review: SOTA Precedents &amp; Foundation Benchmarks</h1>
  <p>
    The proposed methodology synthesizes breakthroughs in LLM programmatic synthesis and GPU-parallel robot learning, establishing our project on top-tier validated literature:
  </p>

  <table class="avoid-break">
    <thead>
      <tr>
        <th style="width: 15%;">Framework / Paper</th>
        <th style="width: 21%;">Authors &amp; Institution</th>
        <th style="width: 32%;">Core Algorithmic Innovation</th>
        <th style="width: 32%;">Demonstrated Experimental Results</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Eureka</strong> <span class="citation-tag">[1]</span></td>
        <td>Y. J. Ma et al.<br><em>NVIDIA, Stanford, Penn</em><br>ICLR 2024 (Oral)</td>
        <td>Zero-shot LLM reward code generation via evolutionary search with in-context reflection over raw Isaac Gym simulation logs.</td>
        <td>Outperformed human expert rewards on <strong>83%</strong> of 29 benchmarks across 10 robot embodiments; achieved <strong>52% average normalized improvement</strong> across the suite.</td>
      </tr>
      <tr>
        <td><strong>DrEureka</strong> <span class="citation-tag">[2]</span></td>
        <td>Y. J. Ma et al.<br><em>NVIDIA &amp; Penn</em><br>arXiv 2024</td>
        <td>Extends Eureka to sim-to-real transfer. Simultaneously discovers reward code and domain randomization (DR) ranges (friction, damping, latency).</td>
        <td>First zero-shot sim-to-real transfer of quadruped locomotion atop rolling yoga balls and varied physical terrain without real-world tuning.</td>
      </tr>
      <tr>
        <td><strong>IsaacLabEureka</strong> <span class="citation-tag">[3]</span></td>
        <td>NVIDIA Corporation<br><em>Official Framework</em><br>GitHub 2024</td>
        <td>Isaac Lab implementation of Eureka. Public implementation is based on <code>DirectRLEnv</code> with RSL-RL and RL-Games backends, with OpenAI/Azure API support.</td>
        <td>Adapting the framework to our custom bimanual deformable task and alternative LLM backends (Anthropic Claude, local models) represents a key engineering contribution.</td>
      </tr>
      <tr>
        <td><strong>Text2Reward</strong> <span class="citation-tag">[4]</span></td>
        <td>T. Xie, S. Zhao, C. H. Wu et al.<br><em>ICLR 2024</em></td>
        <td>Generates dense reward code from natural language instructions with compiler verification and user preference feedback.</td>
        <td>Demonstrated zero-shot generation across 17 manipulation tasks on ManiSkill2 and MetaWorld, and 4 MuJoCo locomotion environments.</td>
      </tr>
      <tr>
        <td><strong>DexCatch &amp; Open TeleDex</strong> <span class="citation-tag">[5, 6]</span></td>
        <td>F. Lan et al. [5];<br>S. An et al. [6]<br><em>CoRL 2024; DEX-ROB Lab</em></td>
        <td>[5] Dynamic dexterous catching baseline. [6] Lab-developed teleoperation platform establishing dual-arm kinodynamics and teleoperation infrastructure.</td>
        <td>Provides laboratory-validated kinodynamic baseline and trajectory data for dual-arm robotic manipulation at Tianjin University.</td>
      </tr>
      <tr>
        <td><strong>AutoRL &amp; Orbit</strong> <span class="citation-tag">[7, 9]</span></td>
        <td>Chiang et al. [7];<br>Mittal et al. [9]<br><em>IEEE RA-L 2019, 2023</em></td>
        <td>[7] Evolutionary reward search in continuous control. [9] Unified simulation framework for robot learning in Omniverse, foundation of Isaac Lab.</td>
        <td>Demonstrates the superiority of automated reward optimization and GPU-accelerated parallel simulation for complex manipulation.</td>
      </tr>
    </tbody>
  </table>

  <!-- Section 3 -->
  <h1>3. Proposed Closed-Loop System Architecture for Isaac Lab</h1>
  <p>
    We propose deploying an autonomous orchestrator script (<code>agent_tuner.py</code>) running locally that interfaces directly with Isaac Lab. The closed-loop architecture coordinates four tightly coupled modules:
  </p>

  <!-- Vector Architecture Diagram -->
  <div class="diagram-container avoid-break">
    <svg viewBox="0 0 760 190" width="100%" height="190" xmlns="http://www.w3.org/2000/svg">
      <!-- Box 1: Task Input -->
      <rect x="10" y="45" width="125" height="92" rx="6" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
      <text x="72" y="64" fill="#93c5fd" font-size="8.0" font-weight="700" text-anchor="middle">1. BIMANUAL SPEC</text>
      <text x="72" y="78" fill="#f8fafc" font-size="6.7" text-anchor="middle">• Dual AR5-L6 (7-DoF Arms)</text>
      <text x="72" y="90" fill="#f8fafc" font-size="6.7" text-anchor="middle">• LinkerHand O6 End-Effectors</text>
      <text x="72" y="102" fill="#f8fafc" font-size="6.7" text-anchor="middle">• Proprioceptive Torque F_ext</text>
      <text x="72" y="114" fill="#f8fafc" font-size="6.7" text-anchor="middle">• PhysX 5 FEM Mesh State</text>
      <text x="72" y="126" fill="#cbd5e1" font-size="6.4" text-anchor="middle">• Calibrated Hold Bounds</text>

      <!-- Arrow 1 -> 2 -->
      <path d="M 135 91 L 170 91" stroke="#2563eb" stroke-width="2"/>
      <polygon points="170,91 163,87 163,95" fill="#2563eb"/>

      <!-- Box 2: LLM Synthesizer -->
      <rect x="175" y="32" width="165" height="122" rx="6" fill="#1e3a8a" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="257" y="52" fill="#ffffff" font-size="8.6" font-weight="800" text-anchor="middle">2. AI REASONING AGENT</text>
      <text x="257" y="66" fill="#bfdbfe" font-size="6.9" font-weight="600" text-anchor="middle">Code Synthesis &amp; Mechanics Reasoner</text>
      <rect x="187" y="75" width="141" height="68" rx="4" fill="#0f172a" fill-opacity="0.6"/>
      <text x="257" y="89" fill="#e2e8f0" font-size="6.6" text-anchor="middle">• Fracture Discontinuity Logic</text>
      <text x="257" y="101" fill="#e2e8f0" font-size="6.6" text-anchor="middle">• Non-Linear Barrier Potentials</text>
      <text x="257" y="113" fill="#e2e8f0" font-size="6.6" text-anchor="middle">• Bimanual Hold-Cut Coupling</text>
      <text x="257" y="125" fill="#e2e8f0" font-size="6.6" text-anchor="middle">• DrEureka DR Range Tuning</text>
      <text x="257" y="137" fill="#67e8f9" font-size="6.6" font-weight="600" text-anchor="middle">Writes: RewardsCfg.py</text>

      <!-- Arrow 2 -> 3 -->
      <path d="M 340 91 L 375 91" stroke="#2563eb" stroke-width="2"/>
      <polygon points="375,91 368,87 368,95" fill="#2563eb"/>

      <!-- Box 3: Isaac Lab Simulator -->
      <rect x="380" y="40" width="165" height="106" rx="6" fill="#0f172a" stroke="#0284c7" stroke-width="1.5"/>
      <text x="462" y="60" fill="#38bdf8" font-size="8.4" font-weight="700" text-anchor="middle">3. ISAAC LAB SIMULATOR</text>
      <text x="462" y="74" fill="#ffffff" font-size="6.9" text-anchor="middle">Massively Parallel GPU Rollouts</text>
      <text x="462" y="87" fill="#94a3b8" font-size="6.7" text-anchor="middle">PhysX 5 FEM + SAC/PPO</text>
      <rect x="393" y="94" width="139" height="42" rx="3" fill="#1e293b"/>
      <text x="462" y="107" fill="#f8fafc" font-size="6.6" text-anchor="middle">Dual ARX AR5-L6 (Left &amp; Right)</text>
      <text x="462" y="119" fill="#f8fafc" font-size="6.6" text-anchor="middle">16–64 Local Envs (Proto) / 512 Cluster</text>
      <text x="462" y="130" fill="#34d399" font-size="6.6" font-weight="600" text-anchor="middle">Hardware: RTX 5060 &amp; Lab Cluster</text>

      <!-- Arrow 3 -> 4 -->
      <path d="M 545 91 L 580 91" stroke="#2563eb" stroke-width="2"/>
      <polygon points="580,91 573,87 573,95" fill="#2563eb"/>

      <!-- Box 4: Reflection & Archive -->
      <rect x="585" y="32" width="165" height="122" rx="6" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
      <text x="667" y="52" fill="#ffffff" font-size="8.6" font-weight="800" text-anchor="middle">4. IN-CONTEXT REFLECTION</text>
      <text x="667" y="66" fill="#a7f3d0" font-size="6.9" font-weight="600" text-anchor="middle">Telemetry &amp; Failure Diagnostician</text>
      <rect x="597" y="75" width="141" height="68" rx="4" fill="#022c22" fill-opacity="0.6"/>
      <text x="667" y="89" fill="#ffffff" font-size="6.6" text-anchor="middle">• Clean Cut Completion Rate (%)</text>
      <text x="667" y="101" fill="#ffffff" font-size="6.6" text-anchor="middle">• Post-Puncture Slam Acceleration</text>
      <text x="667" y="113" fill="#ffffff" font-size="6.6" text-anchor="middle">• Holding Slip &amp; Bruise Violations</text>
      <text x="667" y="125" fill="#ffffff" font-size="6.6" text-anchor="middle">• Stress-Thresholded Tearing Metric</text>
      <text x="667" y="137" fill="#fde047" font-size="6.6" font-weight="600" text-anchor="middle">Pareto Archive &amp; Code Mutation</text>

      <!-- Feedback Arrow: 4 -> 2 -->
      <path d="M 667 32 L 667 14 L 257 14 L 257 32" fill="none" stroke="#e11d48" stroke-width="2" stroke-dasharray="4,3"/>
      <polygon points="257,32 253,25 261,25" fill="#e11d48"/>
      <rect x="390" y="6" width="190" height="15" rx="3" fill="#ffffff" stroke="#e11d48" stroke-width="1"/>
      <text x="485" y="16.5" fill="#e11d48" font-size="6.6" font-weight="700" text-anchor="middle">ITERATIVE REFLECTION &amp; REWARD MUTATION</text>
    </svg>
    <div class="diagram-caption"><strong>Figure 1:</strong> Closed-Loop Autonomous Reward Synthesis &amp; Policy Tuning Engine for Dual ARX AR5-L6 Arms in NVIDIA Isaac Lab.</div>
  </div>

  <h2>3.1 The 4-Stage Iterative Optimization Cycle</h2>
  <ol style="margin-top: 2px; padding-left: 17px; margin-bottom: 0;">
    <li style="margin-bottom: 2px;"><strong>Bimanual Environment Serialization:</strong> The agent ingests the robot interface: dual ARX AR5-L6 7-DoF joint limits, LinkerHand O6 actuator states, Franka/ARX torque-reconstructed contact wrench, and PhysX FEM tetrahedral mesh nodal states.</li>
    <li style="margin-bottom: 2px;"><strong>Evolutionary Code Synthesis:</strong> The LLM authors <i>K</i> candidate reward function classes in native Python using Isaac Lab's <code>RewTerm</code> decorators, implementing non-linear barrier potential mathematics.</li>
    <li style="margin-bottom: 2px;"><strong>Vectorized GPU Rollout:</strong> Isaac Lab executes headless vectorized training (16–64 environments on local prototyping testbed; scaling to 256–512 environments on lab compute cluster) for 1,000 policy iterations.</li>
    <li><strong>Automated Reflection &amp; Mutation:</strong> The log parser analyzes policy telemetry (cut completion, slam acceleration, slip count, nodal stress distribution) and prompts the reasoning engine to mutate and refine candidate reward structures for subsequent generations.</li>
  </ol>
</div>

<!-- =================================================================== -->
<!-- PAGE 3: Deformable Slicing Application and Methodological Rigor     -->
<!-- =================================================================== -->
<div class="page-start">
  <!-- Section 4 -->
  <h1>4. Application: Dual ARX AR5-L6 Deformable Slicing (DOM)</h1>
  <p>
    In our laboratory research setup, two collaborative <strong>ARX AR5-L6 7-DoF arms</strong> (actuated joints 1 to 7, equipped with <strong>LinkerHand O6</strong> 5-finger dexterous hands, defined in our stack via <code>AR5_L6_left.usda</code>, <code>AR5_L6_right.usda</code>, and <code>ar5_o6_left_combined.usda</code>) execute coordinated holding, tensioning, and slicing of soft culinary bodies modeled with <strong>PhysX 5 FEM</strong> continuum mechanics.
  </p>

  <div class="highlight-box">
    <div class="highlight-title">Resolving the Non-Linear "Tear-versus-Slip" Trade-Off in Deformable Slicing</div>
    <p>
      Biological soft tissue exhibits non-linear, strain-rate dependent mechanics. Insufficient grasp force causes tissue slippage under lateral sawing drag (<i>F</i><sub>hold</sub> &lt; <i>F</i><sub>min, slip</sub>); conversely, excessive clamping or cutting velocity generates localized Cauchy shear stress exceeding critical yield limits (&sigma; &gt; &sigma;<sub>crit</sub>), inducing premature mesh tearing and crushing.
    </p>
    <p style="margin-top: 2.5px;">
      <strong>The Agent Synthesis Advantage:</strong> Where human engineering relies on linear scalar penalties that destabilize training, the LLM agent synthesizes <em>non-linear soft barrier potentials</em> that remain near zero during compliant contact and spike exponentially toward &minus;&infin; as the FEM stress tensor approaches rupture limits.
    </p>
  </div>

  <pre><code># Synthesized Isaac Lab Reward Configuration for Bimanual ARX AR5-L6 Slicing
@configclass
class BimanualTomatoCuttingRewardsCfg:
    # 1. Primary Task: Continuous downward blade penetration along planned cutting trajectory
    cutting_progress = RewTerm(func=mdp.cutting_path_progress, weight=6.0)

    # 2. Sawing Motion Reward: Longitudinal velocity reduces normal penetration resistance
    sawing_efficiency = RewTerm(
        func=custom_sawing_shear_reward,
        weight=3.0,
        params={"min_sawing_vel_m_s": 0.02, "contact_force_threshold_N": 0.5}
    )

    # 3. Post-Puncture Slam Arrest: Exponential penalty on vertical blade acceleration
    post_puncture_slam_barrier = RewTerm(
        func=mdp.exponential_acceleration_barrier,
        weight=-10.0,
        params={"acceleration_threshold_m_s2": 1.5, "force_drop_ratio": 0.5}
    )

    # 4. Holding Arm Normal Force Compliance: Calibrated safe holding window
    holding_force_window = RewTerm(
        func=custom_holding_compliance_barrier,
        weight=-8.0,
        params={"f_min_slip_N": 1.5, "f_max_damage_N": 5.0}  # Calibrated experimentally per cultivar
    )

    # 5. Action Regularization: Suppresses motor torque chatter on delicate tissue
    action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=-0.005)</code></pre>

  <!-- Section 5 -->
  <div style="margin-top: 8px;">
    <h1>5. Methodological Rigor &amp; Technical Safeguards</h1>
    <p>
      To ensure theoretical validity, numerical stability, and robust execution within our laboratory's software stack, the architecture incorporates three formal design safeguards:
    </p>
    <table style="margin-top: 4px;">
      <thead>
        <tr>
          <th style="width: 25%;">Safeguard Dimension</th>
          <th style="width: 37%;">Methodological Principle</th>
          <th style="width: 38%;">Implementation Mechanism in DEX-ROB Pipeline</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Timescale Decoupling</strong></td>
          <td>Strict separation between high-frequency policy control and meta-level reasoning.</td>
          <td>The RL policy executes continuous torque control at <strong>60 Hz</strong> natively on CUDA tensors. The LLM operates solely at the <strong>meta-level</strong>, executing once every 1,000 training iterations to analyze logs and refine objective code.</td>
        </tr>
        <tr>
          <td><strong>Symbolic Formulation vs. Black-Box Tuning</strong></td>
          <td>Overcoming the expressive limitations of classical parameter optimization.</td>
          <td>Traditional black-box optimization (BO, Hyperband) optimizes scalar weights within a predefined parametric family. The LLM agent authors symbolic mathematical expressions, creating barrier potentials (e.g., exp(<i>k</i>(&sigma; &minus; &sigma;<sub>crit</sub>))) and geometric invariants.</td>
        </tr>
        <tr>
          <td><strong>Compiler &amp; Runtime Safety Sandbox</strong></td>
          <td>Zero-shot execution safety preventing simulation crashes or CUDA memory faults.</td>
          <td>Prior to deployment, synthesized code passes an Abstract Syntax Tree (AST) validation check followed by a 10-step dry-run rollout. If an exception arises, the stack trace is reflected back to the LLM for immediate autonomous correction.</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<!-- =================================================================== -->
<!-- PAGE 4: Computational Budget, Roadmap, and Advisory Decisions        -->
<!-- =================================================================== -->
<div class="page-start">
  <!-- Section 6 -->
  <h1>6. Computational Budget &amp; Workstation Feasibility Analysis</h1>
  <p>
    Isaac Sim officially specifies a minimum requirement of 32 GB RAM and 16 GB VRAM for standard simulation workloads. To ensure operational feasibility within DEX-ROB Lab, we implement a <strong>two-tier execution strategy</strong> that leverages our local prototyping workstation alongside the laboratory GPU compute cluster:
  </p>

  <table class="avoid-break">
    <thead>
      <tr>
        <th style="width: 20%;">Hardware Dimension</th>
        <th style="width: 25%;">Tier 1: Local Prototyping Testbed</th>
        <th style="width: 25%;">Tier 2: Lab Cluster Scaling</th>
        <th style="width: 30%;">Operational Role &amp; Benchmarking Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>GPU VRAM</strong></td>
        <td>NVIDIA RTX 5060 Laptop (8,151 MB GDDR7)</td>
        <td>NVIDIA RTX 4090 / A6000 (24–48 GB VRAM)</td>
        <td>Local: 16–64 envs for syntax verification and short rollouts. Cluster: 256–512 envs for full training.</td>
      </tr>
      <tr>
        <td><strong>Host System RAM</strong></td>
        <td>16 GB DDR5 5600 MHz</td>
        <td>64 GB–128 GB Server DDR5</td>
        <td>Headless execution minimizes memory footprint. High-env FEM rollouts scale to lab server.</td>
      </tr>
      <tr>
        <td><strong>Compute Cores</strong></td>
        <td>Intel Core i7-14650HX (16C / 24T)</td>
        <td>AMD EPYC / Intel Xeon 32+ Cores</td>
        <td>Enables fast compilation, log parsing, and local policy testing (~3–4 min per 1,000 steps).</td>
      </tr>
      <tr>
        <td><strong>LLM API Budget</strong></td>
        <td>API (Claude 3.5 Sonnet / GPT-4o)</td>
        <td>API / Local DeepSeek-Coder</td>
        <td>~1,500 tokens / generation; <strong>&lt;$2.00 total API cost</strong> for a 30-generation evolutionary run.</td>
      </tr>
    </tbody>
  </table>

  <div class="callout avoid-break">
    <div class="callout-title">Research Time Efficiency: Accelerating DEX-ROB Lab Publication Timelines</div>
    <p>
      In conventional robotics research, graduate researchers spend <strong>3 to 5 weeks</strong> iteratively guessing scalar reward weights to circumvent policy failures. Under the autonomous agent framework, writing the initial environment specification requires less than 2 hours; the agent subsequently conducts 25–30 evolutionary iterations unattended overnight. This shifts laboratory effort from tedious trial-and-error tweaking toward high-impact scientific contributions: constitutive material modeling, ablation analysis, and manuscript preparation.
    </p>
  </div>

  <!-- Section 7 -->
  <h1 style="margin-top: 8px;">7. Proposed Implementation Roadmap &amp; Advisory Guidance Requested</h1>
  <p style="font-size: 7.5pt; color: #475569; margin-bottom: 4px;">
    <strong>Estimated Target Implementation Schedule</strong> (subject to experimental FEM solver stability and hardware scaling):
  </p>
  <div class="two-col avoid-break">
    <div class="col" style="border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; background-color: #f8fafc;">
      <h2 style="margin-top: 0; color: #1e3a8a; font-size: 8.3pt;">Phase 1: Single-Arm Baselines (W1–W2)</h2>
      <p style="font-size: 7.3pt; margin: 0;">
        Construct isolated Isaac Lab stages: Shahd builds clamped cutting stage; Ahmed builds holding compliance using ARX AR5-L6 kinematics and torque force reconstruction.
      </p>
    </div>
    <div class="col" style="border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; background-color: #f8fafc;">
      <h2 style="margin-top: 0; color: #1e3a8a; font-size: 8.3pt;">Phase 2: Agent Harness Setup (W3–W4)</h2>
      <p style="font-size: 7.3pt; margin: 0;">
        Deploy lightweight Python orchestrator (<code>agent_tuner.py</code>). Connect LLM API to author candidate <code>RewardsCfg</code> files, run AST checks, and parse event metrics.
      </p>
    </div>
  </div>

  <div class="two-col avoid-break">
    <div class="col" style="border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; background-color: #f8fafc;">
      <h2 style="margin-top: 0; color: #1e3a8a; font-size: 8.3pt;">Phase 3: Bimanual Integration (W5–W6)</h2>
      <p style="font-size: 7.3pt; margin: 0;">
        Merge subsystems into full dual-arm <code>BimanualTomatoCuttingEnv</code>. Execute autonomous 20-generation evolutionary tuning runs to co-optimize holding and cutting feed.
      </p>
    </div>
    <div class="col" style="border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; background-color: #f8fafc;">
      <h2 style="margin-top: 0; color: #1e3a8a; font-size: 8.3pt;">Phase 4: Paper Finalization (W7–W8)</h2>
      <p style="font-size: 7.3pt; margin: 0;">
        Synthesize comparative ablation studies (Human baseline vs. Agent-synthesized reward vs. DrEureka domain randomization). Finalize manuscript for submission to IEEE RA-L / IROS.
      </p>
    </div>
  </div>

  <div class="highlight-box avoid-break" style="margin-top: 5px;">
    <div class="highlight-title">Advisory Guidance &amp; Decisions Requested from Prof. Shan An</div>
    <ol style="margin: 0; padding-left: 17px; font-size: 7.4pt; color: #1e293b;">
      <li><strong>Target Publication Venue:</strong> Advice on positioning the manuscript primarily for <em>IEEE Robotics and Automation Letters (RA-L) with IROS/ICRA option</em> focusing on continuum contact manipulation, or as an autonomous robotics learning framework.</li>
      <li><strong>Hardware Validation Scope:</strong> Guidance on whether physical dual-arm ARX AR5-L6 validation in the laboratory is requested for the initial submission, or if high-fidelity PhysX 5 FEM continuum simulation with comprehensive DrEureka domain randomization provides sufficient empirical validation.</li>
      <li><strong>Baseline Comparison Portfolio:</strong> Approval of the proposed comparative benchmarks: (a) human-expert hand-crafted reward, (b) classical MoveIt 2 impedance trajectory control, and (c) autonomous LLM-synthesized barrier policies.</li>
    </ol>
  </div>
</div>

<!-- =================================================================== -->
<!-- PAGE 5: References and Experimental Ablation Protocol                -->
<!-- =================================================================== -->
<div class="page-start">
  <!-- References Section -->
  <h1>8. Academic References (IEEE Format)</h1>
  <div class="avoid-break">
    <div class="ref-item"><span class="ref-num">[1]</span> Y. J. Ma, W. Liang, G. Wang, D.-A. Huang, O. Bastani, D. Jayaraman, Y. Zhu, L. Fan, and A. Anandkumar, "Eureka: Human-Level Reward Design via Coding Large Language Models," in <em>Proc. Int. Conf. Learn. Represent. (ICLR)</em>, 2024 (Oral).</div>
    <div class="ref-item"><span class="ref-num">[2]</span> Y. J. Ma, W. Liang, H. Wang, G. Wang, Y. Zhu, L. Fan, O. Bastani, and D. Jayaraman, "DrEureka: Language Model Guided Sim-to-Real Transfer," <em>arXiv preprint arXiv:2406.01967</em>, 2024.</div>
    <div class="ref-item"><span class="ref-num">[3]</span> NVIDIA Corporation, "IsaacLabEureka: Automated LLM-Driven Reward Design for Isaac Lab Environments," <em>Official GitHub Repository: isaac-sim/IsaacLabEureka</em>, 2024.</div>
    <div class="ref-item"><span class="ref-num">[4]</span> T. Xie, S. Zhao, C. H. Wu, Y. Liu, Q. Luo, V. Zhong, Y. Yang, and T. Yu, "Text2Reward: Automated Dense Reward Function Generation for Reinforcement Learning," in <em>Proc. Int. Conf. Learn. Represent. (ICLR)</em>, 2024.</div>
    <div class="ref-item"><span class="ref-num">[5]</span> F. Lan, S. Wang, Y. Zhang, H. Xu, O. O. Oseni, Z. Zhang, Y. Gao, and T. Zhang, "DexCatch: Learning to Catch Arbitrary Dynamic Objects with a Dexterous Hand," in <em>Proc. Conf. Robot Learn. (CoRL)</em>, 2024.</div>
    <div class="ref-item"><span class="ref-num">[6]</span> S. An, et al., "Open TeleDex: A General Dexterous Teleoperation Platform," <em>arXiv preprint arXiv:2510.xxxxx</em>, Oct. 2025.</div>
    <div class="ref-item"><span class="ref-num">[7]</span> H. T. L. Chiang, A. Faust, M. Fiser, and A. Francis, "Learning Navigation Behaviors End-to-End with AutoRL," <em>IEEE Robot. Autom. Lett.</em>, vol. 4, no. 2, pp. 2007–2014, 2019.</div>
    <div class="ref-item"><span class="ref-num">[8]</span> J. Liang, W. Huang, F. Xia, P. Peng, K. Dresner, Q. Vuong, D. Xu, M. Lu, A. Toshev, and K. Hausman, "Code as Policies: Language Model Programs for Embodied Control," in <em>Proc. IEEE Int. Conf. Robot. Autom. (ICRA)</em>, 2023.</div>
    <div class="ref-item"><span class="ref-num">[9]</span> M. Mittal, C. Yu, Q. Yu, J. Liu, N. Rudin, D. Hoeller, J. Yuan, R. Singh, Y. Guo, H. Mazhar, A. Mandlekar, B. Babich, M. State, M. Hutter, and A. Garg, "Orbit: A Unified Simulation Framework for Interactive Robot Learning via NVIDIA Omniverse," <em>IEEE Robot. Autom. Lett.</em>, vol. 8, no. 6, pp. 3740–3747, 2023.</div>
    <div class="ref-item"><span class="ref-num">[10]</span> NVIDIA Corporation, "PhysX 5 Finite Element Method (FEM) Simulation for Deformable Solids and Cloth," <em>NVIDIA Omniverse Technical Documentation</em>, 2024.</div>
  </div>

  <!-- Section 9: Planned Experimental Ablations & Evaluation Protocol -->
  <div class="avoid-break" style="margin-top: 10px;">
    <h1>9. Planned Experimental Ablations &amp; Evaluation Protocol</h1>
    <p>
      To establish rigorous scientific validation for publication, the experimental protocol benchmarks the autonomous agent against three baseline manipulation architectures across five quantitative metrics:
    </p>
    <table style="margin-top: 4px;">
      <thead>
        <tr>
          <th style="width: 25%;">Ablation Condition</th>
          <th style="width: 37%;">Control &amp; Reward Formulation</th>
          <th style="width: 38%;">Core Scientific Hypothesis Under Evaluation</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Baseline 1: Classical Impedance</strong></td>
          <td>Cartesian impedance control with fixed stiffness matrices via MoveIt 2.</td>
          <td>Evaluates trajectory tracking accuracy without dynamic adaptation to tearing force drops.</td>
        </tr>
        <tr>
          <td><strong>Baseline 2: Human-Crafted RL</strong></td>
          <td>Standard SAC with manually tuned weighted linear reward terms (<i>R</i><sub>dense</sub>).</td>
          <td>Quantifies performance degradation and failure modes (chatter, premature mesh rupture) induced by linear penalty approximations.</td>
        </tr>
        <tr>
          <td><strong>Proposed: Eureka Agent RL</strong></td>
          <td>LLM-synthesized non-linear soft barrier potentials with evolutionary mutation.</td>
          <td>Hypothesizes superior trade-off resolution (higher cut completion rate with lower peak tearing stress).</td>
        </tr>
        <tr>
          <td><strong>Proposed + DrEureka DR</strong></td>
          <td>Simultaneous reward synthesis and automated domain randomization bounds.</td>
          <td>Validates policy robustness against non-linear material stiffness variations and contact friction uncertainty.</td>
        </tr>
      </tbody>
    </table>

    <table style="margin-top: 6px;">
      <thead>
        <tr>
          <th style="width: 22%;">Target Evaluation Metric</th>
          <th style="width: 38%;">Physical Definition &amp; Sensor Source</th>
          <th style="width: 40%;">Hypothesized Performance Threshold</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Clean Cut Completion (%)</strong></td>
          <td>Blade reaches planned terminal cutting depth without inducing premature topological rupture.</td>
          <td>&gt;85% completion rate across randomized initial poses and mesh dimensions.</td>
        </tr>
        <tr>
          <td><strong>Peak Slam Acceleration</strong></td>
          <td>Maximum downward acceleration |<i>a</i><sub><i>z</i></sub>| of the blade immediately post-puncture.</td>
          <td>Reduced by &gt;60% relative to linear reward baselines via synthesized barrier.</td>
        </tr>
        <tr>
          <td><strong>Hold Compliance Violations</strong></td>
          <td>Cumulative episode timesteps where <i>F</i><sub>hold</sub> falls outside safe compliance bounds.</td>
          <td>Maintained strictly within <i>F</i><sub>min, slip</sub> and <i>F</i><sub>max, damage</sub> for &gt;90% of cutting cycle.</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Compiling Professor Proposal PDF with WeasyPrint...")
html = weasyprint.HTML(OUTPUT_HTML)
html.write_pdf(OUTPUT_PDF)

print(f"Publication-grade Professor Proposal PDF successfully compiled: {OUTPUT_PDF}")
print(f"File size: {os.path.getsize(OUTPUT_PDF) / 1024:.1f} KB")
