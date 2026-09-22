import os
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

FIGURES_DIR = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/reports/figures"

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=130, bottom=130, left=160, right=160):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
                <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
                <w:insideV w:val="none"/>
                <w:left w:val="none"/>
                <w:right w:val="none"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)

def format_runs(p, text):
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**'):
            run = p.add_run(token[2:-2])
            run.bold = True
        elif token.startswith('*') and token.endswith('*'):
            run = p.add_run(token[1:-1])
            run.italic = True
        elif token.startswith('`') and token.endswith('`'):
            run = p.add_run(token[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0x0F, 0x76, 0x6E)
        else:
            p.add_run(token)

def add_figure_with_caption(doc, img_filename, caption_text, width_inches=6.2):
    img_path = os.path.join(FIGURES_DIR, img_filename)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.keep_with_next = False
        
        # Caption styling
        tokens = caption_text.split(":", 1)
        if len(tokens) == 2:
            r_bold = p_cap.add_run(tokens[0] + ":")
            r_bold.bold = True
            r_bold.font.size = Pt(9.5)
            r_bold.font.name = 'Calibri'
            r_bold.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

            r_text = p_cap.add_run(tokens[1])
            r_text.italic = True
            r_text.font.size = Pt(9.5)
            r_text.font.name = 'Calibri'
            r_text.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
        else:
            r_text = p_cap.add_run(caption_text)
            r_text.italic = True
            r_text.font.size = Pt(9.5)
            r_text.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

def build_docx(md_path, docx_path):
    doc = Document()

    # 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

        # Header / Footer
        header = section.header
        p_head = header.paragraphs[0]
        p_head.text = "Tianjin University DEX-ROB Lab | Autonomous Bimanual DOM Robot Pipeline"
        p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_head.runs[0].font.name = 'Calibri'
        p_head.runs[0].font.size = Pt(8.5)
        p_head.runs[0].font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.text = "Confidential — Internal Academic & Engineering Milestone Report"
        p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_foot.runs[0].font.name = 'Calibri'
        p_foot.runs[0].font.size = Pt(8.5)
        p_foot.runs[0].font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(5)

    NAVY = RGBColor(0x1B, 0x36, 0x5D)
    SLATE = RGBColor(0x33, 0x41, 0x55)
    AMBER = RGBColor(0xD9, 0x77, 0x06)

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_table = False
    table_lines = []
    in_code_block = False
    code_block_lines = []

    def process_table(t_lines):
        rows_data = []
        for line in t_lines:
            if '|' in line:
                parts = [p.strip() for p in line.strip().strip('|').split('|')]
                if all(set(p) <= set('-: ') for p in parts if p):
                    continue
                rows_data.append(parts)
        if not rows_data:
            return

        num_cols = max(len(r) for r in rows_data)
        table = doc.add_table(rows=len(rows_data), cols=num_cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(table)

        for r_idx, row in enumerate(rows_data):
            tr = table.rows[r_idx]
            is_header = (r_idx == 0)
            for c_idx, cell_text in enumerate(row):
                if c_idx < len(tr.cells):
                    cell = tr.cells[c_idx]
                    cell.text = ""
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2.5)
                    p.paragraph_format.space_before = Pt(2.5)
                    cell_clean = cell_text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                    format_runs(p, cell_clean)
                    set_cell_margins(cell, top=120, bottom=120, left=150, right=150)

                    if is_header:
                        set_cell_background(cell, "1B365D")
                        for run in p.runs:
                            run.font.bold = True
                            run.font.size = Pt(9.5)
                            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    else:
                        for run in p.runs:
                            run.font.size = Pt(9.5)
                        if r_idx % 2 == 1:
                            set_cell_background(cell, "F8FAFC")
                        else:
                            set_cell_background(cell, "FFFFFF")
        p_spacer = doc.add_paragraph()
        p_spacer.paragraph_format.space_after = Pt(4)

    def process_code_block(c_lines):
        full_text = "\n".join(c_lines).strip()
        # If the code block is just ASCII diagram, format cleanly
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.right_indent = Inches(0.2)

        run = p.add_run(full_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="10" w:color="1B365D"/><w:top w:val="single" w:sz="4" w:space="4" w:color="E2E8F0"/><w:bottom w:val="single" w:sz="4" w:space="4" w:color="E2E8F0"/><w:right w:val="single" w:sz="4" w:space="4" w:color="E2E8F0"/></w:pBdr>')
        p._element.get_or_add_pPr().append(pBdr)

    for idx, line in enumerate(lines):
        raw_line = line.strip('\r\n')
        stripped = raw_line.strip()

        # Code block handling
        if stripped.startswith('```'):
            if in_code_block:
                process_code_block(code_block_lines)
                code_block_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_block_lines.append(raw_line)
            continue

        # Table handling
        if '|' in stripped:
            in_table = True
            table_lines.append(stripped)
            continue
        else:
            if in_table:
                process_table(table_lines)
                table_lines = []
                in_table = False

        if not stripped:
            continue

        # Headers
        if stripped.startswith('# '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[2:])
            run.font.name = 'Calibri'
            run.font.size = Pt(22)
            run.font.bold = True
            run.font.color.rgb = NAVY

            # Bottom accent border under main title
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="14" w:space="4" w:color="1B365D"/></w:pBdr>')
            p._element.get_or_add_pPr().append(pBdr)

        elif stripped.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[3:])
            run.font.name = 'Calibri'
            run.font.size = Pt(13.5)
            run.font.bold = True
            run.font.color.rgb = NAVY

            # Intercept headings to inject high-res figure at logical transition (Figure 1 only)
            sec_title = stripped[3:].strip()
            if sec_title.startswith("2."):
                # Add Fig 1 right before Section 2
                add_figure_with_caption(doc, "fig1_system_architecture.png",
                                        "Figure 1: End-to-End System Pipeline Architecture — Bridging Volumetric Meshing, PhysX FEM Simulation, MoveIt 2 Kinematics, Isaac Lab Parallel RL, and Closed-Loop Deployment.")


        elif stripped.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[4:])
            run.font.name = 'Calibri'
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = SLATE

        # Ignore markdown image tags so they don't print as raw text
        elif stripped.startswith('!['):
            continue

        # Lists
        elif stripped.startswith('- ') or stripped.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2.5)
            format_runs(p, stripped[2:])

        elif re.match(r'^\d+\.\s', stripped):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(2.5)
            m = re.match(r'^(\d+)\.\s*(.*)', stripped)
            num_str = m.group(1) + ". "
            content = m.group(2)
            r_num = p.add_run(num_str)
            r_num.font.name = 'Calibri'
            r_num.font.bold = True
            r_num.font.color.rgb = NAVY
            format_runs(p, content)

        # Horizontal Rule
        elif stripped.startswith('---'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="CBD5E1"/></w:pBdr>')
            p._element.get_or_add_pPr().append(pBdr)

        # Formula / Callout / Highlights
        elif stripped.startswith('$$') or stripped.endswith('$$'):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            clean_eq = stripped.replace('$$', '').strip()
            clean_eq = (clean_eq
                        .replace('\\mathcal{R}', 'R')
                        .replace('\\cdot', '·')
                        .replace('\\mathbf{1}', '1')
                        .replace('\\mathbf{F}', 'F')
                        .replace('\\text{progress}', 'progress')
                        .replace('\\text{cut}', 'cut')
                        .replace('\\text{stabilize}', 'stabilize')
                        .replace('\\text{secured}', 'secured')
                        .replace('\\text{force}', 'force')
                        .replace('\\text{contact}', 'contact')
                        .replace('\\text{limit}', 'limit')
                        .replace('\\text{crush}', 'crush')
                        .replace('\\text{deform}', 'deform')
                        .replace('\\dot{\\delta}', 'δ̇')
                        .replace('\\Delta', 'Δ')
                        .replace('\\max', 'max')
                        .replace('\\', ''))
            run = p.add_run(clean_eq)
            run.font.name = 'Cambria Math'
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = NAVY


        elif stripped.startswith('> ') or stripped.startswith('**Target Upgrade:**') or stripped.startswith('**Workstation Profile:**'):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.right_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(5)

            content = stripped[2:] if stripped.startswith('> ') else stripped
            format_runs(p, content)

            border_color = "D97706" if ("Upgrade" in stripped or "RAM" in stripped or "Bottleneck" in stripped) else "1B365D"
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="20" w:space="10" w:color="{border_color}"/></w:pBdr>')
            p._element.get_or_add_pPr().append(pBdr)

        # Metadata or standard paragraph
        else:
            p = doc.add_paragraph()
            format_runs(p, stripped)

    if in_table:
        process_table(table_lines)

    doc.save(docx_path)
    print(f"Successfully generated DOCX: {docx_path}")

if __name__ == "__main__":
    md_file = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/reports/bimanual_dom_pipeline_report.md"
    docx_file = "/media/omen/88D2C6C4D2C6B5AA/TianjinUniversity/research/reports/report1_enhanced.docx"
    build_docx(md_file, docx_file)
