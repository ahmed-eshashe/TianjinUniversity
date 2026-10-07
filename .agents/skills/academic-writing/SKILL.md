---
name: academic-writing
description: "IEEE conference and journal manuscript drafting standards, LaTeX syntax, claim traceability, and rebuttal preparation."
---

# Academic Writing Skill

## When to Use
Use when:
- Drafting or revising sections of the paper in `paper/sections/`.
- Structuring mathematical formulations, algorithms, and pseudocode.
- Formulating captions for figures and tables.
- Preparing rebuttal responses for ICRA/IROS reviews.

## Writing Rules
1. **Traceable Claims**: Never write a performance claim (e.g. "outperforms by 25%") without verifying that an underlying experiment exists in `research_state/paper_claims.yaml`.
2. **Clear Passive/Active Balance**: State what the method does clearly ("Our framework decouples high-level trajectory planning from low-level compliance regulation").
3. **Notation Consistency**: Keep all vectors bold lowercase ($\mathbf{x}$), matrices bold uppercase ($\mathbf{K}$), and scalars regular font ($E, \nu$).
4. **Figure Captions**: Figure captions must be self-contained and explain: (1) what is depicted, (2) the key trend/takeaway, and (3) what the shaded error bands represent (e.g., "Shaded regions denote 95% bootstrap confidence intervals across 5 random seeds").
