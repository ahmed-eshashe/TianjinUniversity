---
name: masterclass-documentation
description: "Generate publication-grade, beginner-accessible Masterclass PDFs and Markdown documentation for robotics milestones, with strict concept/action duality, real-world analogies, timestamps, and dual-location PDF compilation."
---

# Masterclass Documentation Skill

## When to Use
Use when:
- A milestone is cleared, a complex bug is solved, or progress needs to be permanently documented.
- Creating onboarding and replication material for Ahmed, Shahd, Prof. Shan An, or new lab members.
- Generating timestamped PDF masterclasses and updating the master documentation archive.
- Compiling weekly progress reports for Prof. Shan An.

## Core Directives
1. **The Concept ("The Why"):** Always lead with intuitive theory, parameter meanings in plain English, and vivid real-world analogies (e.g. Tungsten & Cardboard, Fainting Noodle, Piano Player vs Light Switch, Bones vs Spine).
2. **Step-by-Step Action ("The How"):** Immediately follow with literal, click-by-click UI sequences and copy-pasteable code diffs.
3. **Capture Silent Traps (⚠️):** Explicitly highlight C++ strict types, colcon build install cache, conda PATH collisions, and race conditions.
4. **Automated Dual-Delivery:**
   - Save Markdown to `docs/milestones/<filename>.md`.
   - Compile PDF with WeasyPrint via `scripts/generate_masterclass_doc.py`.
   - Include creation timestamp on page header/footer.
   - Automatically mirror PDF to `/home/omen/Downloads/<filename>.pdf`.
   - Append to `docs/DOCUMENTATION_INDEX.md`.
