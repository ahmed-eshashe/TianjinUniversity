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
