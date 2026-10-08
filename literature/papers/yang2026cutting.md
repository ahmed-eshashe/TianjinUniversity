---
title: "BladeMaster: Real-Time Robotic Cutting Simulation with Online-Generated Persistent Discontinuities"
authors: "Zhanyu Yang, Yunuo Chen, Yanjia Huang, Joseph Masterjohn, Yin Yang, Chenfanfu Jiang"
year: 2026
venue: "arXiv"
---

# Summary
Cutting changes both the shape and topology of deformable objects, making accurate simulation challenging for robotic manipulation. A simulator must track the cutting tool as a cut develops, preserve the resulting discontinuities after tool withdrawal, and enable newly exposed surfaces to interact with the tool and with each other. Existing formulations often prescribe cut surfaces in advance or couple material separation to auxiliary geometric fields. We introduce BladeMaster, a GPU-accelerated cutting framework based on the total Lagrangian material point method (TLMPM). Our key idea is to encode the cutting history directly on material points through persistent side labels generated online from the blade geometry. These labels govern particle-grid coupling, preserving connectivity within intact material while preventing spurious coupling across cut faces after tool withdrawal. Our formulation supports progressive and intersecting cuts without predefined cut surfaces or particle duplication. Material-material contact enables cut surfaces to recontact and slide against each other without reconnecting, while two-way tool-material coupling allows material reaction forces to influence tool motion. Experiments demonstrate tool-driven cutting followed by manipulation, with faster-than-real-time performance on representative tasks. Project page: https://jango6324.github.io/blademaster/.
