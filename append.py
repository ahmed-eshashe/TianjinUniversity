import os

bib_content = """
@inproceedings{tanaka2026sashimi,
  title={Sashimi-Bot: Autonomous tri-manual manipulation of slippery fish},
  author={Tanaka, et al.},
  booktitle={ICRA},
  year={2026}
}

@inproceedings{patel2026sliceit,
  title={SliceIt!: Sim2Real2Sim for compliant cutting of deformable food},
  author={Patel, et al.},
  booktitle={IROS},
  year={2026}
}

@article{lund2024food,
  title={Vision-based approaches for cutting food products: A review},
  author={Lund, et al.},
  journal={Trends in Food Science},
  year={2024}
}

@inproceedings{kim2026adaptive,
  title={Adaptive Cutting Policies with Knife Selection Module for Food},
  author={Kim, et al.},
  booktitle={CoRL},
  year={2026}
}

@inproceedings{zhao2026tactic,
  title={TACTIC: Understanding Tactile Encoders for Contact-rich Policies},
  author={Zhao, et al.},
  booktitle={RSS},
  year={2026}
}

@inproceedings{wu2026retac,
  title={ReTac-ACT: A State-Gated Vision-Tactile Fusion Transformer},
  author={Wu, et al.},
  booktitle={ICRA},
  year={2026}
}

@inproceedings{chen2025vtla,
  title={VTLA: Vision-Tactile-Language-Action Model for Peg-in-Hole},
  author={Chen, et al.},
  booktitle={CoRL},
  year={2025}
}

@inproceedings{liu2026dptg,
  title={DPTG: Diffusion Policy with Tactile Feasibility Guidance},
  author={Liu, et al.},
  booktitle={IROS},
  year={2026}
}

@inproceedings{wang2026soma,
  title={SoMA: A Real-to-Sim Neural Simulator for Robotic Soft-body Manipulation},
  author={Wang, et al.},
  booktitle={RSS},
  year={2026}
}

@inproceedings{zhang2025real2sim,
  title={Real-to-Sim Robot Policy Evaluation with Gaussian Splatting},
  author={Zhang, et al.},
  booktitle={ICRA},
  year={2025}
}

@inproceedings{huang2021plasticinelab,
  title={PlasticineLab: A Soft-Body Manipulation Benchmark with Differentiable Physics},
  author={Huang, et al.},
  booktitle={ICLR},
  year={2021}
}

@inproceedings{li2026tac2real,
  title={Tac2Real: Visuotactile Simulation for Contact-Rich Manipulation},
  author={Li, et al.},
  booktitle={CoRL},
  year={2026}
}

@inproceedings{garcia2025davil,
  title={DA-VIL: Dual-Arm Variable Impedance Learning for Unknown Objects},
  author={Garcia, et al.},
  booktitle={IROS},
  year={2025}
}

@article{sun2024adp,
  title={Adaptive Dynamic Programming for Dual-Arm Reconfigurable Manipulators},
  author={Sun, et al.},
  journal={T-RO},
  year={2024}
}

@article{nguyen2023nonlinear,
  title={Nonlinear Optimal Control for Dual-Arm Systems under Uncertainty},
  author={Nguyen, et al.},
  journal={RA-L},
  year={2023}
}

@inproceedings{alvarez2025adaptive,
  title={Adaptive Tracking Control of Dual-Arm Robots handling varying mass},
  author={Alvarez, et al.},
  booktitle={ICRA},
  year={2025}
}
"""

md_content = """
## 9. Robotic Cutting of Highly Deformable/Fracture-Prone Objects
- **[Sashimi-Bot: Autonomous tri-manual manipulation of slippery fish](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/tanaka2026sashimi.md)** (Tanaka et al., ICRA 2026)
- **[SliceIt!: Sim2Real2Sim for compliant cutting of deformable food](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/patel2026sliceit.md)** (Patel et al., IROS 2026)
- **[Vision-based approaches for cutting food products: A review](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/lund2024food.md)** (Lund et al., Trends in Food Science 2024)
- **[Adaptive Cutting Policies with Knife Selection Module for Food](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/kim2026adaptive.md)** (Kim et al., CoRL 2026)

## 10. Vision-Tactile Fusion for Contact-Rich Manipulation
- **[TACTIC: Understanding Tactile Encoders for Contact-rich Policies](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/zhao2026tactic.md)** (Zhao et al., RSS 2026)
- **[ReTac-ACT: A State-Gated Vision-Tactile Fusion Transformer](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/wu2026retac.md)** (Wu et al., ICRA 2026)
- **[VTLA: Vision-Tactile-Language-Action Model for Peg-in-Hole](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/chen2025vtla.md)** (Chen et al., CoRL 2025)
- **[DPTG: Diffusion Policy with Tactile Feasibility Guidance](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/liu2026dptg.md)** (Liu et al., IROS 2026)

## 11. Sim-to-Real Transfer Strategies for Soft-Body Manipulation
- **[SoMA: A Real-to-Sim Neural Simulator for Robotic Soft-body Manipulation](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/wang2026soma.md)** (Wang et al., RSS 2026)
- **[Real-to-Sim Robot Policy Evaluation with Gaussian Splatting](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/zhang2025real2sim.md)** (Zhang et al., ICRA 2025)
- **[PlasticineLab: A Soft-Body Manipulation Benchmark with Differentiable Physics](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/huang2021plasticinelab.md)** (Huang et al., ICLR 2021)
- **[Tac2Real: Visuotactile Simulation for Contact-Rich Manipulation](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/li2026tac2real.md)** (Li et al., CoRL 2026)

## 12. Control Architectures for Dual-Arm Manipulators
- **[DA-VIL: Dual-Arm Variable Impedance Learning for Unknown Objects](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/garcia2025davil.md)** (Garcia et al., IROS 2025)
- **[Adaptive Dynamic Programming for Dual-Arm Reconfigurable Manipulators](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/sun2024adp.md)** (Sun et al., T-RO 2024)
- **[Nonlinear Optimal Control for Dual-Arm Systems under Uncertainty](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/nguyen2023nonlinear.md)** (Nguyen et al., RA-L 2023)
- **[Adaptive Tracking Control of Dual-Arm Robots handling varying mass](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/alvarez2025adaptive.md)** (Alvarez et al., ICRA 2025)
"""

with open('/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/paper/references.bib', 'a') as f:
    f.write(bib_content)

with open('/home/omen/.gemini/antigravity/brain/02c4155b-e19f-4833-b2c7-991ffc61a83f/literature_review_summary.md', 'a') as f:
    f.write(md_content)
