---
title: "TopoCut: Learning Multi-Step Cutting with Spectral Rewards and Discrete Diffusion Policies"
authors: "Liquan Wang, Jiangjie Bian, Eric Heiden, Animesh Garg"
year: 2025
venue: "arXiv"
---

# Summary
Robotic manipulation tasks involving cutting deformable objects remain challenging due to complex topological behaviors, difficulties in perceiving dense object states, and the lack of efficient evaluation methods for cutting outcomes. In this paper, we introduce TopoCut, a comprehensive benchmark for multi-step robotic cutting tasks that integrates a cutting environment and generalized policy learning. TopoCut is built upon three core components: (1) We introduce a high-fidelity simulation environment based on a particle-based elastoplastic solver with compliant von Mises constitutive models, augmented by a novel damage-driven topology discovery mechanism that enables accurate tracking of multiple cutting pieces. (2) We develop a comprehensive reward design that integrates the topology discovery with a pose-invariant spectral reward model based on Laplace-Beltrami eigenanalysis, facilitating consistent and robust assessment of cutting quality. (3) We propose an integrated policy learning pipeline, where a dynamics-informed perception module predicts topological evolution and produces particle-wise, topology-aware embeddings to support PDDP (Particle-based Score-Entropy Discrete Diffusion Policy) for goal-conditioned policy learning. Extensive experiments demonstrate that TopoCut supports trajectory generation, scalable learning, precise evaluation, and strong generalization across diverse object geometries, scales, poses, and cutting goals.
