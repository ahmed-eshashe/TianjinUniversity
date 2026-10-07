# Workflow 01: Literature Survey to Falsifiable Hypothesis

## Objective
Identify a validated scientific gap in the robotic cutting / DOM literature and formalize it into a falsifiable hypothesis in `research_state/hypotheses.yaml`.

```mermaid
sequenceDiagram
    participant Lead as Research Lead
    participant Lit as Literature Agent
    participant Human as Human Researcher
    participant State as research_state/

    Lead->>Lit: Request SOTA survey on cutting gap
    Lit->>Lit: Survey ICRA/IROS/RSS/CoRL literature
    Lit->>State: Record paper entries & update taxonomy.md
    Lit->>Lead: Synthesize open gap & proposed hypothesis
    Lead->>Human: Present candidate hypothesis & rationale
    Human-->>Lead: Approve / Refine hypothesis
    Lead->>State: Append ratified hypothesis to hypotheses.yaml
```

## Step-by-Step Procedure
1. **Trigger**: Research Lead identifies an unverified domain assumption or new literature release.
2. **Execution**: `literature_agent` performs taxonomy lookup, notes limitations in existing papers, and flags potential novelty.
3. **Synthesis**: Draft hypothesis stating exact independent variables, dependent metrics, and falsification condition.
4. **Approval Gate**: Human researcher reviews and approves before hypothesis is logged as active.
