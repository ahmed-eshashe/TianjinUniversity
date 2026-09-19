import os
import re
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
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
            run.font.color.rgb = RGBColor(0x9C, 0x27, 0xB0)
        else:
            p.add_run(token)

def build_docx(md_path, docx_path):
    doc = Document()
    
    # 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    NAVY = RGBColor(0x1B, 0x36, 0x5D)
    SLATE = RGBColor(0x2C, 0x4D, 0x75)
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
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.space_before = Pt(3)
                    format_runs(p, cell_text)
                    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
                    
                    if is_header:
                        set_cell_background(cell, "1B365D")
                        for run in p.runs:
                            run.font.bold = True
                            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    else:
                        if r_idx % 2 == 1:
                            set_cell_background(cell, "F8F9FA")
                        else:
                            set_cell_background(cell, "FFFFFF")
        p_spacer = doc.add_paragraph()
        p_spacer.paragraph_format.space_after = Pt(6)

    def process_code_block(c_lines):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.right_indent = Inches(0.3)
        
        full_text = "\n".join(c_lines)
        run = p.add_run(full_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        
        # Border & shaded box
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="12" w:color="1B365D"/><w:top w:val="single" w:sz="4" w:space="4" w:color="E0E0E0"/><w:bottom w:val="single" w:sz="4" w:space="4" w:color="E0E0E0"/><w:right w:val="single" w:sz="4" w:space="4" w:color="E0E0E0"/></w:pBdr>')
        p._element.get_or_add_pPr().append(pBdr)

    for line in lines:
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
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[2:])
            run.font.name = 'Calibri'
            run.font.size = Pt(22)
            run.font.bold = True
            run.font.color.rgb = NAVY
            
            # Bottom border line under main title
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="1B365D"/></w:pBdr>')
            p._element.get_or_add_pPr().append(pBdr)

        elif stripped.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[3:])
            run.font.name = 'Calibri'
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = NAVY
            
        elif stripped.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(stripped[4:])
            run.font.name = 'Calibri'
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = SLATE
            
        # Lists
        elif stripped.startswith('- ') or stripped.startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            format_runs(p, stripped[2:])
            
        elif re.match(r'^\d+\.\s', stripped):
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(3)
            content = re.sub(r'^\d+\.\s', '', stripped)
            format_runs(p, content)
            
        # Horizontal Rule
        elif stripped.startswith('---'):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="D3D3D3"/></w:pBdr>')
            p._element.get_or_add_pPr().append(pBdr)

        # Callout / Highlight block
        elif stripped.startswith('> ') or stripped.startswith('**Hardware Upgrade Recommendation:**') or stripped.startswith('**Conclusion & Recommendation:**'):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.right_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            
            content = stripped[2:] if stripped.startswith('> ') else stripped
            format_runs(p, content)
            
            # Left accent border
            border_color = "D97706" if "Hardware" in stripped or "RAM" in stripped else "1B365D"
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="12" w:color="{border_color}"/></w:pBdr>')
            p._element.get_or_add_pPr().append(pBdr)

        # Normal Paragraph
        else:
            p = doc.add_paragraph()
            format_runs(p, stripped)
            
    if in_table:
        process_table(table_lines)
        
    doc.save(docx_path)
    print(f"Successfully generated DOCX: {docx_path}")

if __name__ == "__main__":
    md_file = r"D:\TianjinUniversity\research\reports\weekly_report_2026_09_19.md"
    docx_file = r"D:\TianjinUniversity\research\reports\weekly_report_2026_09_19.docx"
    build_docx(md_file, docx_file)
