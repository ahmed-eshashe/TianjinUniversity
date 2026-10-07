#!/usr/bin/env python3
"""
Research State Pydantic Schema Validator
Ensures single-source-of-truth integrity across research_state/*.yaml
"""

import sys
from pathlib import Path
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT_DIR / "research_state"

class HypothesisModel(BaseModel):
    id: str
    title: str
    statement: str
    rationale: str
    independent_variables: List[str]
    dependent_variables: List[str]
    falsification_condition: str
    status: Literal["PLANNED", "UNDER_EVALUATION", "SUPPORTED", "REJECTED"]
    associated_experiments: List[str]

class HypothesesFileModel(BaseModel):
    version: str
    project: str
    last_updated: str
    hypotheses: List[HypothesisModel]

class ExperimentModel(BaseModel):
    id: str
    hypothesis_id: str
    name: str
    description: str
    status: Literal["PLANNED", "RUNNING", "COMPLETED", "FAILED"]
    category: Literal["BASELINE", "PROPOSED", "ABLATION"]
    algorithm: str
    environment: str
    num_envs: int = Field(gt=0)
    seeds: List[int]
    config_path: str
    primary_metric: str
    target_metric_value: float
    failure_criteria: str

class ExperimentMatrixFileModel(BaseModel):
    version: str
    project: str
    last_updated: str
    experiments: List[ExperimentModel]

class PaperClaimModel(BaseModel):
    id: str
    paper_section: str
    statement: str
    hypothesis_id: str
    required_experiments: List[str]
    metric_threshold: str
    statistical_test: str
    status: Literal["UNVERIFIED", "VERIFIED", "REFUTED"]
    target_figure: Optional[str] = None
    target_table: Optional[str] = None

class PaperClaimsFileModel(BaseModel):
    version: str
    project: str
    last_updated: str
    claims: List[PaperClaimModel]

class MilestoneModel(BaseModel):
    id: str
    title: str
    target_date: str
    status: Literal["PLANNED", "IN_PROGRESS", "COMPLETED", "BLOCKED"]
    assigned_agent: str
    progress_percent: int = Field(ge=0, le=100)

class ProjectStatusFileModel(BaseModel):
    version: str
    project: str
    last_updated: str
    project_overview: dict
    milestones: List[MilestoneModel]
    active_blockers: List[str]
    recent_activities: List[dict]


def validate_file(file_path: Path, model_cls):
    if not file_path.exists():
        return False, [f"File missing: {file_path.name}"]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        model_cls.model_validate(data)
        return True, []
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return False, errors
    except Exception as e:
        return False, [str(e)]


def validate_all_states():
    files_to_validate = [
        (STATE_DIR / "hypotheses.yaml", HypothesesFileModel),
        (STATE_DIR / "experiment_matrix.yaml", ExperimentMatrixFileModel),
        (STATE_DIR / "paper_claims.yaml", PaperClaimsFileModel),
        (STATE_DIR / "project_status.yaml", ProjectStatusFileModel),
    ]

    all_passed = True
    results = {}
    for fpath, model in files_to_validate:
        ok, errs = validate_file(fpath, model)
        results[fpath.name] = (ok, errs)
        if not ok:
            all_passed = False

    return all_passed, results


if __name__ == "__main__":
    passed, res = validate_all_states()
    for fname, (ok, errs) in res.items():
        if ok:
            print(f"✓ {fname}: VALID")
        else:
            print(f"✗ {fname}: INVALID")
            for e in errs:
                print(f"   -> {e}")

    sys.exit(0 if passed else 1)
