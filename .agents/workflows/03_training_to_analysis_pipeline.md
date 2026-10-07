# Workflow 03: Training Execution to Statistical Analysis Pipeline

## Objective
Safely launch and monitor Isaac Lab headless training runs on GPU, collect telemetry, and produce statistical analyses and plots.

```mermaid
sequenceDiagram
    participant Human as Human Researcher
    participant Lead as Research Lead
    participant Train as Training Agent
    participant Ana as Analysis Agent
    participant State as research_state/

    Lead->>Human: Present experiment run request (seeds, GPU budget)
    Human-->>Lead: Approve execution
    Lead->>Train: Launch Isaac Lab headless training
    Train->>Train: Run multi-seed vectorized training
    Train->>Train: Save runs/<exp_id>/metrics.csv & checkpoints
    Train->>Ana: Notify run completion
    Ana->>Ana: Compute bootstrap CI & hypothesis test p-values
    Ana->>Ana: Generate IEEE-format plots & tables
    Ana->>State: Update experiment_matrix.yaml (status=COMPLETED)
```

## Step-by-Step Procedure
1. **Safety Approval**: Training Agent presents resource requirements (VRAM budget, estimated run time) for Human Researcher sign-off.
2. **Headless Execution**: Execute run using Isaac Lab python wrapper (`./isaaclab.sh -p ... --headless`).
3. **Artifact Isolation**: Store full telemetry (`metrics.csv`, `config.yaml`, `git_commit.txt`) in isolated directory `experiments/runs/<exp_id>/`.
4. **Statistical Evaluation**: `analysis_agent` loads all seed runs, performs significance testing against baselines, and generates figures in `experiments/results/plots/`.
