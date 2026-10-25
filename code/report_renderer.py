from __future__ import annotations
import html
import re
from pathlib import Path
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import LongTable,PageBreak,Paragraph,Preformatted,Spacer,TableStyle
from svglib.svglib import svg2rlg
from report_theme import PALE,RULE
ROOT=Path(__file__).resolve().parent.parent
SUBMISSION=ROOT/'docs'
PDF_DOCUMENTS=()
INLINE_TOKEN=re.compile(r"(`[^`]+`|\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*)")

def inline_markup(text: str) -> str:
    chunks: list[str] = []
    position = 0
    for match in INLINE_TOKEN.finditer(text):
        chunks.append(html.escape(text[position : match.start()]))
        token = match.group(0)
        if token.startswith("`"):
            chunks.append(f'<font name="PlexKR" color="#2A2F36">{html.escape(token[1:-1])}</font>')
        elif token.startswith("**"):
            chunks.append(f"<b>{html.escape(token[2:-2])}</b>")
        else:
            label, target = re.match(r"\[([^\]]+)\]\(([^)]+)\)", token).groups()
            safe_label = html.escape(label)
            safe_target = html.escape(target, quote=True)
            if target.startswith(("https://", "http://")):
                chunks.append(f'<link href="{safe_target}" color="#007F79"><u>{safe_label}</u></link>')
            elif target.split("#")[0] in PDF_DOCUMENTS:
                section = PDF_DOCUMENTS.index(target.split("#")[0]) + 1
                chunks.append(f'<link href="#section-{section}" color="#007F79"><u>{safe_label}</u></link>')
            else:
                chunks.append(f'<font color="#007F79">{safe_label}</font>')
        position = match.end()
    chunks.append(html.escape(text[position:]))
    return "".join(chunks).replace("  ", " &nbsp;")

def table_widths(rows: list[list[str]], available: float) -> list[float]:
    columns = len(rows[0])
    proportions = {
        2: [0.39, 0.61],
        3: [0.22, 0.40, 0.38],
        4: [0.34, 0.22, 0.22, 0.22],
        5: [0.30, 0.21, 0.21, 0.14, 0.14],
    }
    weights = proportions.get(columns, [1 / columns] * columns)
    return [available * weight for weight in weights]

def make_table(rows: list[list[str]], styles: dict[str, ParagraphStyle], available: float) -> LongTable:
    style_name = "table_small" if len(rows[0]) >= 5 else "table"
    cells = [[Paragraph(inline_markup(cell), styles["table_header"] if index == 0 else styles[style_name])
              for cell in row] for index, row in enumerate(rows)]
    table = LongTable(cells, colWidths=table_widths(rows, available), repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(PALE)),
                ("FONTNAME", (0, 0), (-1, 0), "PlexKR-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor(RULE)),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 2.0 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2.0 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.7 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.7 * mm),
            ]
        )
    )
    return table

def markdown_flowables(path: Path, styles: dict[str, ParagraphStyle], available: float) -> list:
    lines = path.read_text(encoding="utf-8").splitlines()
    story: list = []
    paragraph: list[str] = []
    seen_heading = False
    table_rows: list[list[str]] = []
    code_lines: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(part.strip() for part in paragraph)), styles["body"]))
            paragraph.clear()

    def flush_table() -> None:
        if not table_rows:
            return
        if len(table_rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in table_rows[1]):
            del table_rows[1]
        table = make_table(table_rows.copy(), styles, available)
        table.spaceAfter = 3 * mm
        story.append(table)
        table_rows.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            flush_table()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["code"], maxLineLength=96))
                code_lines.clear()
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            table_rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
            continue
        flush_table()
        if not stripped:
            flush_paragraph()
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            heading_text = heading.group(2)
            if level == 1:
                if seen_heading:
                    story.append(PageBreak())
                seen_heading = True
                numbered = re.match(r"^(\d{2})\s+(.+)$", heading_text)
                if numbered:
                    heading_text = (f'<font name="PlexKR-Light" size="32" color="#B7BEC8">{numbered.group(1)}</font>'
                                    f' &nbsp;{html.escape(numbered.group(2))}')
                else:
                    heading_text = inline_markup(heading_text)
            else:
                heading_text = inline_markup(heading_text)
            story.append(Paragraph(heading_text, styles[f"h{level}"]))
            continue
        image = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", stripped)
        if image:
            flush_paragraph()
            target = (path.parent / image.group(2)).resolve()
            if not target.is_relative_to(SUBMISSION.resolve()) or target.suffix.lower() != ".svg":
                raise ValueError("Only local submission SVG figures are supported")
            drawing = svg2rlg(str(target))
            if not isinstance(drawing, Drawing) or not drawing.width or not drawing.height:
                raise ValueError("Unusable SVG figure")
            set_svg_fonts(drawing)
            scale = min(available / drawing.width, 275 / drawing.height)
            drawing.scale(scale, scale)
            drawing.width *= scale
            drawing.height *= scale
            story.append(drawing)
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if bullet or ordered:
            flush_paragraph()
            marker = "•" if bullet else f"{ordered.group(1)}."
            content = bullet.group(1) if bullet else ordered.group(2)
            story.append(Paragraph(inline_markup(content), styles["bullet"], bulletText=marker))
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped.lstrip("> ")), styles["quote"]))
            continue
        if stripped.startswith(("그림 ", "Figure ")):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped), styles["caption"]))
            continue
        paragraph.append(stripped)

    flush_paragraph()
    flush_table()
    if code_lines:
        story.append(Preformatted("\n".join(code_lines), styles["code"], maxLineLength=96))
    return story

def set_svg_fonts(node) -> None:
    if isinstance(node, String):
        is_bold = "bold" in str(getattr(node, "fontName", "")).lower()
        node.fontName = "PlexKR-Bold" if is_bold else "PlexKR"
    for child in getattr(node, "contents", []):
        set_svg_fonts(child)
