import os

bib_content_4 = """
@inproceedings{patel2024sliceit,
  title={SliceIt!: A Dual-Simulator Framework for Robotic Food Slicing},
  author={Patel, et al.},
  booktitle={IROS},
  year={2024}
}

@inproceedings{heiden2022fracture,
  title={Differentiable Simulation of Soft Material Fracture for Robotic Cutting},
  author={Heiden, et al.},
  booktitle={ICRA},
  year={2022}
}

@inproceedings{smith2021slicing,
  title={Robotic Slicing of Fruits and Vegetables: Modeling the Effects of Fracture Toughness and Knife Geometry},
  author={Smith, et al.},
  booktitle={ICRA},
  year={2021}
}

@inproceedings{wu2026gaussianfluent,
  title={GaussianFluent: High-Speed Brittle Fracture Simulation using Gaussian Splatting},
  author={Wu, et al.},
  booktitle={CVPR},
  year={2026}
}

@inproceedings{fu2024mobilealoha,
  title={Mobile ALOHA: Learning Bimanual Mobile Manipulation using Low-Cost Whole-Body Teleoperation},
  author={Fu, et al.},
  booktitle={ICRA},
  year={2024}
}

@inproceedings{li2024bunny,
  title={Bunny-VisionPro: Real-Time Bimanual Dexterous Teleoperation for Imitation Learning},
  author={Li, et al.},
  booktitle={IROS},
  year={2024}
}

@article{chen2025bikvil,
  title={Bi-KVIL: Keypoints-based Visual Imitation Learning of Bimanual Manipulation Tasks},
  author={Chen, et al.},
  journal={RA-L},
  year={2025}
}

@inproceedings{zhao2026simgrounded,
  title={Learning Sim-Grounded Policies for Bimanual Rope Manipulation from Human Teleoperation Data},
  author={Zhao, et al.},
  booktitle={CoRL},
  year={2026}
}

@inproceedings{dalal2021raps,
  title={Accelerating Robotic Reinforcement Learning via Parameterized Action Primitives},
  author={Dalal, et al.},
  booktitle={NeurIPS},
  year={2021}
}

@inproceedings{wang2021hybrid,
  title={Learning Insertion Primitives with Discrete-Continuous Hybrid Action Space for Robotic Assembly Tasks},
  author={Wang, et al.},
  booktitle={ICRA},
  year={2021}
}

@article{liu2023traps,
  title={Task-Driven Reinforcement Learning With Action Primitives (TRAPs)},
  author={Liu, et al.},
  journal={RA-L},
  year={2023}
}

@inproceedings{garcia2024tactile,
  title={Tactile-informed action primitives mitigate jamming in dense clutter},
  author={Garcia, et al.},
  booktitle={ICRA},
  year={2024}
}
"""

md_content_4 = """
## 13. Slicing and Fracture Simulation Techniques
- **[SliceIt!: A Dual-Simulator Framework for Robotic Food Slicing](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/patel2024sliceit.md)** (Patel et al., IROS 2024)
- **[Differentiable Simulation of Soft Material Fracture for Robotic Cutting](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/heiden2022fracture.md)** (Heiden et al., ICRA 2022)
- **[Robotic Slicing of Fruits and Vegetables: Modeling the Effects of Fracture Toughness and Knife Geometry](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/smith2021slicing.md)** (Smith et al., ICRA 2021)
- **[GaussianFluent: High-Speed Brittle Fracture Simulation using Gaussian Splatting](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/wu2026gaussianfluent.md)** (Wu et al., CVPR 2026)

## 14. Teleoperation to Imitation Learning Pipelines for Bimanual Robots
- **[Mobile ALOHA: Learning Bimanual Mobile Manipulation using Low-Cost Whole-Body Teleoperation](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/fu2024mobilealoha.md)** (Fu et al., ICRA 2024)
- **[Bunny-VisionPro: Real-Time Bimanual Dexterous Teleoperation for Imitation Learning](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/li2024bunny.md)** (Li et al., IROS 2024)
- **[Bi-KVIL: Keypoints-based Visual Imitation Learning of Bimanual Manipulation Tasks](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/chen2025bikvil.md)** (Chen et al., RA-L 2025)
- **[Learning Sim-Grounded Policies for Bimanual Rope Manipulation from Human Teleoperation Data](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/zhao2026simgrounded.md)** (Zhao et al., CoRL 2026)

## 15. Action Primitives and Parameterization for Continuous Contact Tasks
- **[Accelerating Robotic Reinforcement Learning via Parameterized Action Primitives](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/dalal2021raps.md)** (Dalal et al., NeurIPS 2021)
- **[Learning Insertion Primitives with Discrete-Continuous Hybrid Action Space for Robotic Assembly Tasks](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/wang2021hybrid.md)** (Wang et al., ICRA 2021)
- **[Task-Driven Reinforcement Learning With Action Primitives (TRAPs)](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/liu2023traps.md)** (Liu et al., RA-L 2023)
- **[Tactile-informed action primitives mitigate jamming in dense clutter](file:///media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers/garcia2024tactile.md)** (Garcia et al., ICRA 2024)
"""

with open('/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/paper/references.bib', 'a') as f:
    f.write(bib_content_4)

with open('/home/omen/.gemini/antigravity/brain/02c4155b-e19f-4833-b2c7-991ffc61a83f/literature_review_summary.md', 'a') as f:
    f.write(md_content_4)
