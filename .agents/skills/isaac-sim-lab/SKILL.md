---
name: isaac-sim-lab
description: "Expert guidance for NVIDIA Isaac Sim 6.1.0, Isaac Lab, PhysX 5 FEM deformable bodies, USD asset pipelines, and domain randomization."
---

# Isaac Sim & Isaac Lab Skill

## When to Use
Use when:
- Creating or editing USD robot scenes (`.usd` / `.usda`).
- Configuring PhysX 5 FEM deformable meshes, hyperelastic materials, and contact collision properties.
- Setting up parallel vectorized environments in Isaac Lab.
- Tuning GPU solver parameters (`solver_position_iterations`, `solver_velocity_iterations`).
- Designing domain randomization distributions for sim-to-real transfer.

## Best Practices
1. **Headless Execution**: Always run training with `--headless` to save GPU memory on the RTX 5060 (8GB VRAM).
2. **Mesh Optimization**: For FEM deformable bodies, keep tetrahedral mesh element counts moderate ($< 1,500$ tetrahedra per tomato) to avoid memory saturation across 128+ parallel instances.
3. **Contact Stability**:
   - Set contact offset and rest offset carefully ($\approx 1\text{ mm}$ for knife contact).
   - Use high solver position iteration counts ($\ge 8$) to avoid knife tunneling through thin deformable membranes.
