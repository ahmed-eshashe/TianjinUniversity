import os
import glob

LITERATURE_DIR = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/literature/papers"
OUTPUT_MD = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/docs/milestones/consolidated_literature_review.md"

def extract_title_and_content(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Basic extraction, you can refine this
    title = os.path.basename(filepath).replace(".md", "")
    for line in content.split("\n"):
        if line.startswith("title:"):
            title = line.replace("title:", "").strip().strip('"').strip("'")
            break
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break
    return title, content

def main():
    md_files = glob.glob(os.path.join(LITERATURE_DIR, "*.md"))
    
    # We can group by some heuristic or simply sort alphabetically by filename for now
    # Since we want to sort by phase, we can try to categorize based on keywords in content
    categories = {
        "Phase 1: FEM Simulation & Soft Bodies": ["isaac", "physx", "fem", "simulation", "deformable"],
        "Phase 2: Tactile & Impedance Control": ["tactile", "impedance", "force", "haptic"],
        "Phase 3: Bimanual Manipulation": ["bimanual", "dual-arm", "teleoperation"],
        "Phase 4: RL & Cutting Policies": ["rl", "reinforcement learning", "cutting", "slicing", "fracture", "food"]
    }
    
    categorized_papers = {cat: [] for cat in categories}
    categorized_papers["Other Relevant Papers"] = []

    for fpath in md_files:
        title, content = extract_title_and_content(fpath)
        content_lower = content.lower()
        
        placed = False
        for cat, keywords in categories.items():
            if any(kw in content_lower for kw in keywords):
                categorized_papers[cat].append((title, content))
                placed = True
                break
                
        if not placed:
            categorized_papers["Other Relevant Papers"].append((title, content))
            
    # Compile markdown
    compiled_md = []
    
    for cat, papers in categorized_papers.items():
        if not papers: continue
        compiled_md.append(f"## {cat}\n")
        for title, content in papers:
            # Add a separator and the content
            compiled_md.append(f"### {title}\n")
            # Filter out yaml frontmatter for cleaner pdf
            lines = content.split("\n")
            in_yaml = False
            clean_lines = []
            for i, line in enumerate(lines):
                if line.strip() == "---":
                    if i == 0 or in_yaml:
                        in_yaml = not in_yaml
                        continue
                if not in_yaml:
                    # Upgrade heading levels so they don't conflict
                    if line.startswith("# "):
                        clean_lines.append("#### " + line[2:])
                    elif line.startswith("## "):
                        clean_lines.append("##### " + line[3:])
                    else:
                        clean_lines.append(line)
            
            compiled_md.append("\n".join(clean_lines) + "\n\n---\n\n")

    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(compiled_md))

    print(f"Consolidated markdown created at {OUTPUT_MD}")

if __name__ == "__main__":
    main()
