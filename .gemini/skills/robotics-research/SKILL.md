---
name: robotics-research
description: "Methodology, gap identification, baseline fairness, and research governance for top-tier robotics publications (ICRA/IROS/T-RO)."
---

# Robotics Research Skill

## When to Use
Use when:
- Defining or refining the primary research question.
- Framing defensible research contributions for ICRA / IROS / T-RO.
- Formulating falsifiable hypotheses and ensuring baseline fairness.
- Evaluating whether an experiment constitutes a legitimate scientific contribution or merely engineering effort.

## Core Principles
1. **Contribution vs Engineering**: A new robot CAD model or working code is engineering. A scientific contribution is a validated, generalizable insight (e.g., explaining why residual impedance decoupling stabilizes contact-rich fracture while end-to-end RL fails).
2. **Fair Baseline Comparison**:
   - Give baselines fair hyperparameter tuning; do not handicap the baseline to make your method look good.
   - Always compare against the best traditional method (e.g. impedance control with force-limiting) in addition to RL baselines.
3. **Reproducibility Standards**:
   - Fix and record random seeds.
   - Keep dataset / rollout distributions documented.
   - Report negative results and failure modes openly.
