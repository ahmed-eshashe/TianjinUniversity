# Taxonomy of Robotic Cutting & Deformable Object Manipulation (DOM)

This document organizes the literature into a structured scientific matrix to identify state-of-the-art baselines and research gaps.

---

## 1. Material Mechanics & Modeling

| Class | Mechanics Model | Solvers | Key Literature | Advantages & Pitfalls |
| :--- | :--- | :--- | :--- | :--- |
| **Rigid Approximation** | Rigid Body Dynamics | ODE, PhysX Rigid, Bullet | Early assembly literature | Fails completely for soft food slicing; induces instant force spikes. |
| **Mass-Spring-Damper** | Discrete point-mass network | Custom, Isaac Sim PBD | General games / graphics | Fast computation, but lacks volume conservation and true shear stress. |
| **Continuum FEM** | Tetrahedral Neo-Hookean / Mooney-Rivlin | PhysX 5 FEM, SOFA, Abaqus | Sanchez et al. (RA-L 2021) | High physical fidelity, true hydrostatic pressure; computationally demanding. |
| **Material Point Method (MPM)** | Continuum particles on Eulerian background grid | Taichi, Genesis, Warp | Genesis (2024), MLS-MPM | Handles extreme topological tearing naturally; high GPU memory footprint. |

---

## 2. Slicing Control Strategies

| Control Strategy | Trajectory Generation | Force Feedback | Limitations |
| :--- | :--- | :--- | :--- |
| **Kinematic Sawing (Open-Loop)** | Pre-planned Cartesian sinusoids | None | Crushes soft overripe tomatoes; stalls on tough skins. |
| **Classical Impedance Control** | Task-space compliance $(M, D, K)$ | 6-axis F/T wrench | Fixed stiffness cannot dynamically balance sawing vs pressing phases. |
| **End-to-End Deep RL** | Monolithic MLP / Transformer | F/T + joint states | High sample complexity ($> 20\text{M}$ steps); unsafe real-world exploration. |
| **Residual RL (Proposed)** | Nominal sawing primitive + RL delta | F/T + fingertip tactile array | Safe exploration; fast sample convergence ($< 3\text{M}$ steps); high sim-to-real transfer. |

---

## 3. Sensor Modalities & Hardware Embodiment

- **Vision Only**: RGB-D camera (Intel RealSense D435i / ZED 2i). Excellent for global object localization and bounding box, but blind to micro-fracture contact states and internal strain.
- **Wrist F/T Sensing**: 6-axis wrench ($F_x, F_y, F_z, M_x, M_y, M_z$) at $1\,\text{kHz}$. Detects macro cutting resistance and normal force peaks.
- **Tactile Skin / Fingertip Arrays**: LinkerHand O6 tactile arrays. Detects tangential micro-slip and local deformation at holding contacts.
- **Vision-Tactile Fusion**: Hierarchical decoupling—Vision at $30\,\text{Hz}$ for global trajectory; Tactile at $1\,\text{kHz}$ for contact compliance.
