# Workflow 02: Hypothesis to Experiment Configuration

## Objective
Convert an approved hypothesis into a fully specified experimental design, baseline comparisons, ablation studies, and runnable YAML configuration.

```mermaid
sequenceDiagram
    participant Lead as Research Lead
    participant Exp as Experiment Agent
    participant RL as RL Agent
    participant Sim as Simulation Agent
    participant State as research_state/

    Lead->>Exp: Direct hypothesis operationalization
    Exp->>RL: Request MDP observation/action parameterization
    RL-->>Exp: Specify reward terms & action bounds
    Exp->>Sim: Request scene & physics parameter requirements
    Sim-->>Exp: Confirm FEM mesh & solver parameters
    Exp->>State: Register experiment in experiment_matrix.yaml
    Exp->>Exp: Generate experiments/configs/<exp_id>.yaml
```

## Step-by-Step Procedure
1. **Trigger**: New hypothesis ratified in `research_state/hypotheses.yaml`.
2. **Design**: `experiment_agent` establishes:
   - Control vs treatment conditions.
   - 4 required baselines (open-loop kinematic, fixed impedance, no-tactile, no-residual).
   - Seed schedule ($N = 5$ random seeds).
3. **Configuration**: Save runnable Hydra config in `experiments/configs/<exp_id>.yaml`.
4. **Registration**: Append unique `exp_id` to `research_state/experiment_matrix.yaml` with status `PLANNED`.
