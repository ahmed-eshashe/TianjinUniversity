#!/usr/bin/env python3
"""
Research State Management & Multi-Agent CLI
DEX-ROB Lab | Tianjin University
"""

import sys
import argparse
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT_DIR / "research_state"

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

from validate_state import validate_all_states


def cmd_status(args):
    """Show the live project research dashboard."""
    status_file = STATE_DIR / "project_status.yaml"
    hyp_file = STATE_DIR / "hypotheses.yaml"
    exp_file = STATE_DIR / "experiment_matrix.yaml"
    claims_file = STATE_DIR / "paper_claims.yaml"

    if not status_file.exists():
        print(f"Error: {status_file} not found.")
        return

    with open(status_file, "r", encoding="utf-8") as f:
        status_data = yaml.safe_load(f)

    with open(hyp_file, "r", encoding="utf-8") as f:
        hyp_data = yaml.safe_load(f)

    with open(exp_file, "r", encoding="utf-8") as f:
        exp_data = yaml.safe_load(f)

    with open(claims_file, "r", encoding="utf-8") as f:
        claims_data = yaml.safe_load(f)

    overview = status_data.get("project_overview", {})

    if USE_RICH:
        console.print(Panel(
            f"[bold cyan]{overview.get('institution', 'Tianjin University')}[/] | "
            f"[bold yellow]{overview.get('laboratory', 'DEX-ROB Lab')}[/]\n"
            f"[bold white]Project:[/] {status_data.get('project')}\n"
            f"[bold white]Current Phase:[/] [green]{overview.get('current_phase')}[/] | "
            f"[bold white]Target Venue:[/] [magenta]{overview.get('target_venue')}[/]",
            title="[bold green]Robotics Research Lab Dashboard[/]",
            border_style="blue"
        ))

        # Milestones Table
        m_table = Table(title="Project Milestones & Timeline", border_style="cyan")
        m_table.add_column("ID", style="bold")
        m_table.add_column("Milestone Title")
        m_table.add_column("Assigned Agent", style="yellow")
        m_table.add_column("Target Date")
        m_table.add_column("Status")
        m_table.add_column("Progress", justify="right")

        for m in status_data.get("milestones", []):
            st_style = "green" if m["status"] == "COMPLETED" else ("yellow" if m["status"] == "IN_PROGRESS" else "dim")
            m_table.add_row(
                m["id"],
                m["title"],
                m["assigned_agent"],
                m["target_date"],
                f"[{st_style}]{m['status']}[/]",
                f"{m['progress_percent']}%"
            )
        console.print(m_table)

        # Hypotheses Table
        h_table = Table(title="Scientific Hypotheses", border_style="magenta")
        h_table.add_column("ID", style="bold")
        h_table.add_column("Hypothesis Title")
        h_table.add_column("Status")
        h_table.add_column("Associated Experiments")

        for h in hyp_data.get("hypotheses", []):
            st_style = "green" if h["status"] == "SUPPORTED" else ("yellow" if h["status"] == "UNDER_EVALUATION" else "cyan")
            h_table.add_row(
                h["id"],
                h["title"],
                f"[{st_style}]{h['status']}[/]",
                ", ".join(h.get("associated_experiments", []))
            )
        console.print(h_table)

        # Experiment Matrix Summary
        e_table = Table(title="Registered Experiment Matrix", border_style="blue")
        e_table.add_column("ID", style="bold")
        e_table.add_column("Name")
        e_table.add_column("Category", style="cyan")
        e_table.add_column("Algorithm")
        e_table.add_column("Seeds")
        e_table.add_column("Status")

        for e in exp_data.get("experiments", []):
            st_style = "green" if e["status"] == "COMPLETED" else ("red" if e["status"] == "FAILED" else "dim")
            e_table.add_row(
                e["id"],
                e["name"],
                e["category"],
                e["algorithm"],
                str(len(e.get("seeds", []))),
                f"[{st_style}]{e['status']}[/]"
            )
        console.print(e_table)

        # Claims Table
        c_table = Table(title="Paper Claims Traceability Audit", border_style="yellow")
        c_table.add_column("ID", style="bold")
        c_table.add_column("Section")
        c_table.add_column("Required Experiments")
        c_table.add_column("Status")

        for c in claims_data.get("claims", []):
            st_style = "green" if c["status"] == "VERIFIED" else ("red" if c["status"] == "REFUTED" else "bold yellow")
            c_table.add_row(
                c["id"],
                c["paper_section"],
                ", ".join(c.get("required_experiments", [])),
                f"[{st_style}]{c['status']}[/]"
            )
        console.print(c_table)

    else:
        print("=== ROBOTICS RESEARCH DASHBOARD ===")
        print(f"Project: {status_data.get('project')}")
        print(f"Phase: {overview.get('current_phase')} | Venue: {overview.get('target_venue')}")
        print("\n--- Milestones ---")
        for m in status_data.get("milestones", []):
            print(f"[{m['status']}] {m['id']}: {m['title']} ({m['assigned_agent']}) - {m['progress_percent']}%")
        print("\n--- Hypotheses ---")
        for h in hyp_data.get("hypotheses", []):
            print(f"[{h['status']}] {h['id']}: {h['title']}")
        print("\n--- Experiments ---")
        for e in exp_data.get("experiments", []):
            print(f"[{e['status']}] {e['id']}: {e['name']} ({e['category']})")


def cmd_validate(args):
    """Validate all state files against Pydantic schemas."""
    passed, results = validate_all_states()
    if USE_RICH:
        t = Table(title="Research State Pydantic Validation", border_style="green" if passed else "red")
        t.add_column("State File")
        t.add_column("Validation Result")
        t.add_column("Errors / Details")
        for fname, (ok, errs) in results.items():
            t.add_row(
                fname,
                "[green]PASSED[/]" if ok else "[red]FAILED[/]",
                "\n".join(errs) if errs else "[dim]None[/]"
            )
        console.print(t)
    else:
        for fname, (ok, errs) in results.items():
            print(f"{fname}: {'PASSED' if ok else 'FAILED'}")
            for e in errs:
                print(f"  -> {e}")

    sys.exit(0 if passed else 1)


def cmd_verify_claims(args):
    """Audit all paper claims against registered experiments and run data."""
    claims_file = STATE_DIR / "paper_claims.yaml"
    exp_file = STATE_DIR / "experiment_matrix.yaml"

    with open(claims_file, "r", encoding="utf-8") as f:
        claims_data = yaml.safe_load(f)
    with open(exp_file, "r", encoding="utf-8") as f:
        exp_data = yaml.safe_load(f)

    registered_exp_ids = {e["id"]: e for e in exp_data.get("experiments", [])}

    all_backed = True
    audit_rows = []

    for c in claims_data.get("claims", []):
        req_exps = c.get("required_experiments", [])
        missing = [exp_id for exp_id in req_exps if exp_id not in registered_exp_ids]
        incomplete = [exp_id for exp_id in req_exps if exp_id in registered_exp_ids and registered_exp_ids[exp_id]["status"] != "COMPLETED"]

        if missing:
            all_backed = False
            audit_rows.append((c["id"], c["paper_section"], "[red]MISSING EXPERIMENT REGISTRATION[/]", f"Missing: {missing}"))
        elif incomplete:
            audit_rows.append((c["id"], c["paper_section"], "[yellow]PENDING EXECUTION[/]", f"Incomplete: {incomplete}"))
        else:
            audit_rows.append((c["id"], c["paper_section"], "[green]FULLY BACKED[/]", "All experiments completed"))

    if USE_RICH:
        t = Table(title="Scientific Integrity Claim Audit", border_style="cyan")
        t.add_column("Claim ID", style="bold")
        t.add_column("Paper Section")
        t.add_column("Audit Result")
        t.add_column("Details")
        for r in audit_rows:
            t.add_row(*r)
        console.print(t)
    else:
        for r in audit_rows:
            print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")


def cmd_add_exp(args):
    """Add a new experiment entry to experiment_matrix.yaml."""
    exp_file = STATE_DIR / "experiment_matrix.yaml"
    with open(exp_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    existing_ids = {e["id"] for e in data.get("experiments", [])}
    if args.id in existing_ids:
        print(f"Error: Experiment ID '{args.id}' already exists!")
        sys.exit(1)

    new_entry = {
        "id": args.id,
        "hypothesis_id": args.hypothesis,
        "name": args.name,
        "description": args.desc or "Experiment description",
        "status": "PLANNED",
        "category": args.category,
        "algorithm": args.algo,
        "environment": args.env or "IsaacLab-TomatoSlicing-v0",
        "num_envs": args.num_envs,
        "seeds": [42, 100, 2026, 777, 999],
        "config_path": f"experiments/configs/{args.id.lower()}.yaml",
        "primary_metric": args.metric or "slice_success_rate",
        "target_metric_value": float(args.target_val or 0.85),
        "failure_criteria": args.failure or "Pulp burst > 15%"
    }

    data["experiments"].append(new_entry)
    with open(exp_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, indent=2)

    print(f"✓ Successfully registered experiment '{args.id}' linked to {args.hypothesis}!")


def main():
    parser = argparse.ArgumentParser(description="Research State Multi-Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = subparsers.add_parser("status", help="Show research project dashboard")
    p_status.set_defaults(func=cmd_status)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate state YAML files")
    p_val.set_defaults(func=cmd_validate)

    # verify-claims
    p_vc = subparsers.add_parser("verify-claims", help="Audit paper claims against experiment results")
    p_vc.set_defaults(func=cmd_verify_claims)

    # add-exp
    p_add = subparsers.add_parser("add-exp", help="Register a new experiment")
    p_add.add_argument("--id", required=True, help="Unique ID (e.g. EXP-009-TEST)")
    p_add.add_argument("--hypothesis", required=True, help="Hypothesis ID (e.g. H1)")
    p_add.add_argument("--name", required=True, help="Experiment name")
    p_add.add_argument("--category", choices=["BASELINE", "PROPOSED", "ABLATION"], default="PROPOSED")
    p_add.add_argument("--algo", required=True, help="Algorithm name (e.g. RESIDUAL_PPO)")
    p_add.add_argument("--desc", default="", help="Description")
    p_add.add_argument("--env", default="IsaacLab-TomatoSlicing-v0", help="Isaac Lab env name")
    p_add.add_argument("--num-envs", type=int, default=256, help="Number of vectorized parallel envs")
    p_add.add_argument("--metric", default="slice_success_rate", help="Primary metric")
    p_add.add_argument("--target-val", type=float, default=0.85, help="Target value")
    p_add.add_argument("--failure", default="Pulp burst > 15%", help="Failure condition")
    p_add.set_defaults(func=cmd_add_exp)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
