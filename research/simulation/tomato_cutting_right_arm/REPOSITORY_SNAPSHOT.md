# Update — 14 November 2026

Code, plans, tests, reports, successful and failed experiment evidence are archived
in PUBLICATION_UPDATE_20261114.json. Later solver and vision-pickup experiments
are under experiments_external/; dashboard snapshots are under
docs/progress/outputs_20261114/.

This is an archival snapshot of ongoing research, not a completed evaluation or
portable training release. Some live progress files may describe incomplete runs.
Individual included files are SHA-256 verified; files across a running experiment
are not guaranteed to represent one atomic checkpoint. Read each experiment's
contracts and reports before using its results. No paper claims are promoted.

Large assets, model weights, arrays, recordings and other excluded files remain
local and are indexed by source path and size in the update manifest. Installed environments, builds, and selected third-party checkouts are excluded;
small vendored source snapshots may remain with experiment provenance.
The manifest records the actual inclusion policy. Historical Git revisions retain
previous snapshots; no source workspace or simulation was changed for publication.

---

# Update — 7 November 2026

The incremental update is indexed in `PUBLICATION_UPDATE_20261107.json`.
It adds the research material/contact implementation, mounted-robot cutting and
horizontal withdrawal, natural-grip and kitchen scene work, recovery and research
roadmaps, learning-interface preparation, tests, and compact experiment evidence.
The checklists in `docs/progress/` are static snapshots of the local dashboards.

**Full separation is not achieved.** The latest production run at snapshot time
is `work/single_slice_20261106/robot_cut18`, resumed from run17 checkpoint 6475.
This is an ongoing, scripted exploratory simulation with a disclosed fixed knife
mount. Experimental calibration, motor-work qualification, full-trajectory
numerical convergence, and training remain pending. No paper claim is promoted.

The local coupled timestep comparison passed: maximum tomato position difference
0.054 mm, knife position difference 0.014 mm, force difference 0.86%, with identical
separation and eligibility at all eight comparison points. See
`work/single_slice_20261106/coupled_timestep_comparison.json`. These are short-window
numerical comparisons, not successful-cut or experimental-validation results.
Native stepping and collision checks stay at 2400 Hz; candidate material updates
are 600 Hz, with the wrench reapplied every native substep. Adoption is restricted
to horizontal withdrawal, under the user's approved comparison limits.

Large arrays, checkpoints, recordings, caches and third-party source remain local.
The update manifest lists large text/asset exclusions and category counts. It
hashes the copied files, not a subsequently changing live workspace. It does not
replace the original publication manifest, which records the earlier snapshot.
Machine-specific paths and external assets still need restoration before running.
Do not interpret the snapshot's runtime status files as a live status service.

---

## Earlier snapshot (historical)

# Tomato cutting workspace snapshot

This directory preserves the code, plans and experiment evidence from the local
`tomato_cutting_right_arm` workspace. Files listed as included in
`PUBLICATION_MANIFEST.json` were copied byte-for-byte and verified with SHA-256.
The repository path prefix was added; historical paths inside evidence were not
rewritten, so their recorded hashes and provenance remain intact.

## Contents

- `rl/`, `scripts/`, `tools/`, launch scripts and ROS source: implementation and tests.
- `docs/rl/`: mechanics, slicing, resource safeguards and preparation plans.
- `runs/offline/`, `logs/`, `output/`: saved experiment results, failed attempts,
  source snapshots, audits, and quota/interruption records.
- Small assets and archived source are included where allowed by the snapshot
  policy. Large asset collections/files remain local; their paths, sizes and
  SHA-256 hashes are listed with `status: local_only` in the publication manifest.
- Virtual environments, generated builds/caches, scratch files, model checkpoints
  and process locks/PIDs are excluded. These exclusions are counted separately.

## Research status and limits

The preserved accepted forward checkpoint is
`runs/offline/tomato_curvature_search_01/insertion292_20261027_h1644/attempt005`
at **9.638916015625 mm**. It is not evidence of a complete cut or independent release.
Offline reference tests and static/source checks are not native simulator or
training validation. Native contact, implicit cohesion/softening integration,
complete reset/continuation, two-way robot coupling, frozen grasp under load,
and throughput remain unresolved gates.

The approved 15-hour preparation window ended on **2026-10-28 at 08:10:31 UTC**.
Historical `session.json` fields may still say `waiting_quota`, `ACTIVE`, or name
a next probe: they are retained as historical evidence, not current authorization.
The expired automation was deleted on October 30. No simulation, training, quota
recovery, or old insertion continuation was launched for this repository import.
The saved final integrity result still awaits its recorded after-quota disposition;
this snapshot neither clears nor reruns it. The source-bound 2132 configuration
was created but its final exact preview and final readiness handoff were unfinished.

## Using this snapshot

Treat this directory as the original project root when resolving historical
relative paths. Many scripts also contain original machine-specific paths;
inspect them before running anything. This import is an archival source/evidence
snapshot, not a portable ready-to-train distribution. A machine must restore
required large assets and its own dependencies separately. A 32 GB RAM upgrade
alone does not validate mechanics or authorize simulator/training execution.

The repository's existing research documents and other contributors' uncommitted
local edits were not overwritten by this import.
