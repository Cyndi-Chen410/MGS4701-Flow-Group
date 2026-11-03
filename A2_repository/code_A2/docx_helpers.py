from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INK = RGBColor(0x21,0x25,0x29); MUTED = RGBColor(0x6E,0x75,0x7D); ACCENT = RGBColor(0x1F,0x4E,0x79)

def setup(doc):
    st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    pf = st.paragraph_format; pf.space_before = Pt(0); pf.space_after = Pt(5); pf.line_spacing = 1.12
    for s in doc.sections:
        s.top_margin = Cm(2.0); s.bottom_margin = Cm(2.0); s.left_margin = Cm(2.2); s.right_margin = Cm(2.2)

def h1(doc, text, space_before=14):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(space_before); p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(14); r.font.color.rgb = ACCENT
    p.paragraph_format.keep_with_next = True
    # bottom border
    pPr = p._p.get_or_add_pPr(); pbdr = OxmlElement('w:pBdr'); bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),'single'); bottom.set(qn('w:sz'),'6'); bottom.set(qn('w:space'),'2'); bottom.set(qn('w:color'),'D9DEE3')
    pbdr.append(bottom); pPr.append(pbdr)
    return p

def h2(doc, text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text); r.bold = True; r.font.size = Pt(11.5); r.font.color.rgb = INK
    p.paragraph_format.keep_with_next = True
    return p

def para(doc, text, size=10.5, italic=False, color=None, space_after=5, align=None):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space_after)
    if align: p.alignment = align
    # simple bold markup **...**
    parts = text.split('**')
    for i, part in enumerate(parts):
        if not part: continue
        r = p.add_run(part); r.font.size = Pt(size); r.italic = italic
        r.bold = (i % 2 == 1)
        if color: r.font.color.rgb = color
    return p

def bullet(doc, text, size=10.5):
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.first_line_indent = Cm(-0.35)
    parts = text.split('**')
    for i, part in enumerate(parts):
        if not part: continue
        r = p.add_run(part); r.font.size = Pt(size); r.bold = (i % 2 == 1)
    return p

def caption(doc, text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text); r.font.size = Pt(8.5); r.font.color.rgb = MUTED; r.italic = True
    return p

def figure(doc, path, width=6.3):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Inches(width))
    return p

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto'); shd.set(qn('w:fill'),hexcolor)
    tcPr.append(shd)

def table(doc, headers, rows, widths=None, font=8.8, header_bg='1F4E79', align_right_from=1):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ''
        p = hdr[i].paragraphs[0]; r = p.add_run(h); r.bold = True; r.font.size = Pt(font); r.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
        shade(hdr[i], header_bg)
        p.paragraph_format.space_after = Pt(1)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            p = cells[i].paragraphs[0]; p.paragraph_format.space_after = Pt(1)
            r = p.add_run(str(v)); r.font.size = Pt(font)
            if i >= align_right_from and str(v).replace('.','').replace('%','').replace('−','-').replace('-','').isdigit():
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if ri % 2 == 1:
            for c in cells: shade(c, 'F2F5F8')
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Cm(w)
    return t

def page_break(doc):
    doc.add_page_break()

def title_page(doc, title, subtitle, meta_lines):
    for _ in range(3): doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title); r.bold = True; r.font.size = Pt(22); r.font.color.rgb = ACCENT
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(subtitle); r.font.size = Pt(13); r.font.color.rgb = INK
    for _ in range(4): doc.add_paragraph()
    for line in meta_lines:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(line); r.font.size = Pt(10); r.font.color.rgb = MUTED
    doc.add_page_break()
