---
name: scientific-analysis
description: "Statistical rigor, hypothesis testing, bootstrap confidence intervals, and IEEE publication-quality plotting."
---

# Scientific Analysis & Statistical Rigor Skill

## When to Use
Use when:
- Aggregating multi-seed experimental runs.
- Computing hypothesis test statistics ($p$-values, effect sizes).
- Generating publication figures and LaTeX tables.
- Verifying whether paper claims in `research_state/paper_claims.yaml` meet required thresholds.

## Statistical Protocols
1. **Multi-Seed Rule**:
   - $N \ge 5$ seeds for simulation benchmarks; $N \ge 15$ trials for physical robot slicing.
2. **Normality Testing**:
   - Run Shapiro-Wilk test to assess distribution normality before choosing parametric ($t$-test) vs non-parametric (Mann-Whitney $U$) tests.
3. **Confidence Bounds**:
   - Compute non-parametric bootstrap confidence intervals ($B = 10,000$ resamples) with 95% confidence level.
4. **Plotting**:
   - Use colorblind-friendly palettes (e.g. `seaborn.color_palette("colorblind")`).
   - Export both vector (`.pdf` / `.svg`) and high-res raster (`.png`, 300+ DPI).
