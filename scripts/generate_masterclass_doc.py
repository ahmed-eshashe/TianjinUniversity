#!/usr/bin/env python3
"""
==============================================================================
Masterclass Documentation & PDF Generator
DEX-ROB Lab | Tianjin University
==============================================================================
Generates publication-grade, beginner-accessible Masterclass PDFs and Markdown
records for robotics milestones, bug fixes, and lab progress tracking.
Includes timestamps, dual-location saving (Repo + Downloads), and semantic styling.
==============================================================================
"""

import os
import sys
import re
import shutil
import argparse
from datetime import datetime
import weasyprint

try:
    # Optional vector math rendering if available
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../research/simulation/scripts")))
    import render_utils
    HAS_MATH_RENDERER = True
except ImportError:
    HAS_MATH_RENDERER = False

CSS_TEMPLATE = """
@page {
  size: A4;
  margin: 16mm 14mm 18mm 14mm;
  @top-left {
    content: "DEX-ROB Lab • Tianjin University";
    font-size: 8pt;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #64748b;
  }
  @top-right {
    content: "__RUNNING_TITLE__";
    font-size: 8pt;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #64748b;
  }
  @bottom-left {
    content: "Generated: __TIMESTAMP__";
    font-size: 7.5pt;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #94a3b8;
  }
  @bottom-center {
    content: "Page " counter(page) " of " counter(pages);
    font-size: 8.5pt;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #64748b;
  }
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #1e293b;
  line-height: 1.56;
  font-size: 9.5pt;
}

.header-block {
  border-bottom: 2px solid #2563eb;
  padding-bottom: 14px;
  margin-bottom: 18px;
}

.course-tag {
  display: inline-block;
  background: #dbeafe;
  color: #1d4ed8;
  font-weight: 700;
  font-size: 8pt;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.timestamp-badge {
  display: inline-block;
  background: #f1f5f9;
  color: #475569;
  font-weight: 600;
  font-size: 8pt;
  padding: 3px 8px;
  border-radius: 4px;
  margin-left: 8px;
  margin-bottom: 6px;
}

h1 {
  color: #0f172a;
  font-size: 19pt;
  font-weight: 800;
  margin: 0 0 6px 0;
  line-height: 1.25;
}

.subtitle {
  color: #475569;
  font-size: 10.2pt;
  margin: 0 0 10px 0;
  font-weight: 500;
}

.meta-grid {
  display: flex;
  font-size: 8.5pt;
  color: #64748b;
  margin-top: 6px;
}

h2 {
  color: #1e3a8a;
  font-size: 14pt;
  font-weight: 700;
  margin-top: 20px;
  margin-bottom: 10px;
  border-left: 4px solid #2563eb;
  padding: 8px 10px;
  background-color: #f8fafc;
  page-break-after: avoid;
}

h3 {
  color: #0f172a;
  font-size: 11.5pt;
  font-weight: 700;
  margin-top: 14px;
  margin-bottom: 6px;
  page-break-after: avoid;
}

p {
  margin: 0 0 8px 0;
  text-align: justify;
}

ul, ol {
  margin: 0 0 8px 0;
  padding-left: 20px;
}

li {
  margin-bottom: 5px;
}

.callout {
  padding: 12px 16px;
  margin: 12px 0;
  border-radius: 6px;
  font-size: 9.2pt;
  page-break-inside: avoid;
}

.callout-title {
  font-weight: 800;
  font-size: 9pt;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.callout p {
  margin: 0;
}

.intuition {
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
  color: #1e3a8a;
}
.intuition .callout-title { color: #1d4ed8; }

.action-box {
  background: #f5f3ff;
  border-left: 4px solid #8b5cf6;
  color: #4c1d95;
}
.action-box .callout-title { color: #6d28d9; }

.warning-box {
  background: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #7f1d1d;
}
.warning-box .callout-title { color: #b91c1c; }

.robotics {
  background: #ecfdf5;
  border-left: 4px solid #10b981;
  color: #064e3b;
}
.robotics .callout-title { color: #047857; }

.code-box {
  background: #1e1e1e;
  border-left: 4px solid #64748b;
  color: #d4d4d4;
  font-family: "SFMono-Regular", Consolas, Menlo, monospace;
  font-size: 8.5pt;
  padding: 10px 14px;
  border-radius: 5px;
  page-break-inside: avoid;
  white-space: pre-wrap;
  margin: 8px 0;
}

code {
  font-family: "SFMono-Regular", Consolas, Menlo, monospace;
  background-color: #f1f5f9;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 8.8pt;
  color: #0f172a;
}

.page-break {
  page-break-before: always;
}
"""

def markdown_to_html_body(md_text: str) -> str:
    """Converts structured markdown into semantic HTML for WeasyPrint."""
    # Convert code blocks ```
    def replace_code_block(match):
        code = match.group(1).strip()
        return f'<div class="code-box">{code}</div>'
    
    html = re.sub(r'```(?:[a-zA-Z0-9_\-]+)?\n([\s\S]*?)```', replace_code_block, md_text)

    # Convert callout blocks like > [!NOTE], > [!TIP], > [!WARNING]
    lines = html.split('\n')
    new_lines = []
    in_callout = False
    callout_type = "intuition"
    callout_title = "NOTE"
    callout_content = []

    for line in lines:
        if line.startswith('> [!NOTE]') or line.startswith('> [!CONCEPT]') or '💡' in line and line.startswith('>'):
            in_callout = True
            callout_type = "intuition"
            callout_title = "💡 Concept: The Why & Intuition"
            callout_content = []
        elif line.startswith('> [!TIP]') or line.startswith('> [!ACTION]') or '🛠️' in line and line.startswith('>'):
            in_callout = True
            callout_type = "action-box"
            callout_title = "🛠️ Step-by-Step Action: The How"
            callout_content = []
        elif line.startswith('> [!WARNING]') or line.startswith('> [!CAUTION]') or '⚠️' in line and line.startswith('>'):
            in_callout = True
            callout_type = "warning-box"
            callout_title = "⚠️ Trap & Silent Failure"
            callout_content = []
        elif in_callout and line.startswith('>'):
            cleaned = line.lstrip('>').strip()
            if cleaned:
                callout_content.append(cleaned)
        elif in_callout and not line.startswith('>'):
            body_p = "<br>".join(callout_content)
            new_lines.append(f'<div class="callout {callout_type}"><div class="callout-title">{callout_title}</div><p>{body_p}</p></div>')
            in_callout = False
            new_lines.append(line)
        else:
            new_lines.append(line)
            
    if in_callout:
        body_p = "<br>".join(callout_content)
        new_lines.append(f'<div class="callout {callout_type}"><div class="callout-title">{callout_title}</div><p>{body_p}</p></div>')

    html = "\n".join(new_lines)

    # Basic markdown header substitutions
    html = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^\*\*(.*?)\*\*$', r'<p><b>\1</b></p>', html, flags=re.MULTILINE)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = html.replace('<!-- page-break -->', '<div class="page-break"></div>')

    return html

def build_masterclass_doc(
    title: str,
    subtitle: str,
    tag: str,
    content_html_or_md: str,
    filename_base: str,
    is_markdown: bool = False,
    downloads_dir: str = "/home/omen/Downloads",
    repo_docs_dir: str = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/docs/milestones"
):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    running_title = f"{tag} • {title}"

    css = CSS_TEMPLATE.replace("__RUNNING_TITLE__", running_title).replace("__TIMESTAMP__", now_str)

    if is_markdown:
        body_content = markdown_to_html_body(content_html_or_md)
    else:
        body_content = content_html_or_md

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>

<div class="header-block">
  <span class="course-tag">{tag}</span>
  <span class="timestamp-badge">📅 Created: {now_str}</span>
  <h1>{title}</h1>
  <div class="subtitle">{subtitle}</div>
  <div class="meta-grid">
    <span><b>Researchers:</b> Ahmed & Shahd &nbsp;|&nbsp; <b>Advisor:</b> Prof. Shan An &nbsp;|&nbsp; <b>Lab:</b> DEX-ROB Lab (Tianjin University)</span>
  </div>
</div>

{body_content}

</body>
</html>
"""

    os.makedirs(repo_docs_dir, exist_ok=True)
    os.makedirs(downloads_dir, exist_ok=True)

    pdf_repo_path = os.path.join(repo_docs_dir, f"{filename_base}.pdf")
    pdf_downloads_path = os.path.join(downloads_dir, f"{filename_base}.pdf")
    html_repo_path = os.path.join(repo_docs_dir, f"{filename_base}.html")

    # Save HTML source
    with open(html_repo_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    # Compile PDF
    print(f"-> Compiling Masterclass PDF with WeasyPrint: {pdf_repo_path}...")
    if HAS_MATH_RENDERER and "<div class=\"formula\"" in full_html:
        rendered_html = render_utils.render_mathjax_html(full_html)
        weasyprint.HTML(string=rendered_html).write_pdf(pdf_repo_path)
    else:
        weasyprint.HTML(string=full_html).write_pdf(pdf_repo_path)

    # Copy to Downloads
    shutil.copyfile(pdf_repo_path, pdf_downloads_path)

    # Update Documentation Index
    index_path = os.path.abspath(os.path.join(repo_docs_dir, "../DOCUMENTATION_INDEX.md"))
    index_entry = f"| {now_str} | **{tag}** | [{title}](./milestones/{filename_base}.pdf) | `docs/milestones/{filename_base}.md` | [PDF Link](file://{pdf_downloads_path}) |\n"
    
    if not os.path.exists(index_path):
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("# DEX-ROB Lab Masterclass & Progress Archive\n\n")
            f.write("Master repository of all milestone completions, technical replication guides, and lab progress reports.\n\n")
            f.write("| Timestamp | Milestone / Tag | Document Title | Markdown Path | Downloads Mirror |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- |\n")
            f.write(index_entry)
    else:
        with open(index_path, "a", encoding="utf-8") as f:
            f.write(index_entry)

    print(f"✓ Masterclass PDF generated:")
    print(f"  • Repo Copy: {pdf_repo_path}")
    print(f"  • Downloads Copy: {pdf_downloads_path}")
    print(f"  • Timestamp: {now_str}")
    print(f"  • Index updated: {index_path}")
    return pdf_repo_path, pdf_downloads_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Masterclass PDF and Markdown with timestamp.")
    parser.add_argument("--title", required=True, help="Title of the document")
    parser.add_argument("--subtitle", default="Comprehensive Theory, Step-by-Step Actions, and Lessons Learned", help="Subtitle")
    parser.add_argument("--tag", default="Milestone Progress", help="Tag/Header badge (e.g. Milestone 1 & 2)")
    parser.add_argument("--input", required=True, help="Path to input HTML or Markdown file")
    parser.add_argument("--filename", required=True, help="Base output filename (without extension)")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    is_md = args.input.endswith(".md")
    build_masterclass_doc(
        title=args.title,
        subtitle=args.subtitle,
        tag=args.tag,
        content_html_or_md=content,
        filename_base=args.filename,
        is_markdown=is_md
    )
