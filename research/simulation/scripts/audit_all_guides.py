import os
import subprocess
import re

DOWNLOADS_DIR = "/home/omen/Downloads"
REPO_DIR = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/simulation"

PDF_FILES = [
    "CS285_Lecture1_Beginner_Guide.pdf",
    "CS285_Lecture4_Beginner_Guide.pdf",
    "CS285_Lecture5_Beginner_Guide.pdf",
    "CS285_Lecture6_Beginner_Guide.pdf",
    "CS285_Lecture8_Beginner_Guide.pdf",
    "CS285_Lecture10_Beginner_Guide.pdf",
    "CS285_Priority1_Master_Robotics_Guide.pdf"
]

def check_pdf(filename):
    dl_path = os.path.join(DOWNLOADS_DIR, filename)
    repo_path = os.path.join(REPO_DIR, filename)

    if not os.path.exists(dl_path):
        return {"file": filename, "error": f"Missing in Downloads: {dl_path}"}
    if not os.path.exists(repo_path):
        return {"file": filename, "error": f"Missing in Repo: {repo_path}"}

    dl_size = os.path.getsize(dl_path)
    repo_size = os.path.getsize(repo_path)
    if dl_size != repo_size:
        return {"file": filename, "error": f"Size mismatch: dl={dl_size} vs repo={repo_size}"}

    # Pages
    info = subprocess.check_output(["pdfinfo", dl_path]).decode()
    pages = 0
    for line in info.splitlines():
        if "Pages:" in line:
            pages = int(line.split(":")[1].strip())

    # Math purity
    txt = subprocess.check_output(["pdftotext", dl_path, "-"]).decode()
    bad_math = re.findall(r'(\\\\[a-zA-Z]+|\$[^$\n]+\$)', txt)

    return {
        "file": filename,
        "pages": pages,
        "size_kb": round(dl_size / 1024, 1),
        "unrendered_math": len(bad_math),
        "bad_samples": bad_math[:5]
    }

def main():
    print("=" * 80)
    print("       CS285 PRIORITY 1 ZERO-TO-HERO LIBRARY AUDIT REPORT")
    print("=" * 80)
    
    total_pages = 0
    total_unrendered = 0
    all_ok = True

    print(f"{'PDF File Name':<45} | {'Pages':<6} | {'Size (KB)':<10} | {'Bad Math':<8}")
    print("-" * 80)

    for pdf in PDF_FILES:
        res = check_pdf(pdf)
        if "error" in res:
            print(f"{pdf:<45} | ERROR: {res['error']}")
            all_ok = False
            continue

        pages = res["pages"]
        total_pages += pages
        total_unrendered += res["unrendered_math"]

        status_str = f"{res['unrendered_math']}"
        if res["unrendered_math"] > 0:
            status_str += f" (FAIL: {res['bad_samples']})"
            all_ok = False

        print(f"{pdf:<45} | {pages:<6} | {res['size_kb']:<10} | {status_str:<8}")

    print("=" * 80)
    print(f"TOTAL PAGES ACROSS 7 GUIDES: {total_pages}")
    print(f"TOTAL UNRENDERED MATH TOKENS: {total_unrendered}")
    print(f"100+ PAGES TARGET ACHIEVED:   {'YES! PASS' if total_pages >= 100 else 'NO (LESS THAN 100)'}")
    print(f"ALL MATH FULLY RENDERED:      {'YES! PASS' if total_unrendered == 0 else 'NO (FAIL)'}")
    print("=" * 80)

if __name__ == "__main__":
    main()
