"""Render only privacy-filtered Markdown sources; no private source files are read."""
from pathlib import Path
import argparse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer

from report_renderer import markdown_flowables
from report_theme import ACCENT, INK, MUTED, draw_mark, make_styles, register_fonts

ROOT = Path(__file__).resolve().parent.parent


class Report(BaseDocTemplate):
    def __init__(self, path, styles, brief=False, applicant=''):
        super().__init__(str(path), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm,
                         topMargin=29*mm, bottomMargin=20*mm,
                         title='Mintech Internship | Project brief' if brief else 'Mintech Internship | Engineering report',
                         author=applicant, creator='build_reports.py',
                         subject='Privacy-filtered AI-assisted record validation and synthetic-data analysis')
        self.brief = brief
        self.applicant = applicant
        self.styles = styles
        self.heading_count = 0
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='report', frames=[frame], onPage=self.draw_page))

    def beforeDocument(self):
        self.heading_count = 0

    def afterFlowable(self, item):
        if isinstance(item, Paragraph) and item.style.name == 'Heading1Korean':
            self.heading_count += 1
            key = f'chapter-{self.heading_count}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(item.getPlainText(), key, level=0)

    def draw_page(self, canv, doc):
        canv.saveState()
        width, height = self.pagesize
        x = self.leftMargin
        if canv.getPageNumber() == 1 and not self.brief:
            draw_mark(canv, x, height-144, 29)
            canv.setFillColor(colors.HexColor(INK))
            canv.setFont('PlexKR-Bold', 18)
            canv.drawString(x+40, height-141, 'MINTECH INTERNSHIP REPORT')
            canv.setFillColor(colors.HexColor(MUTED))
            canv.setFont('PlexKR', 10)
            canv.drawString(x, height-280, 'STUDENT ENGINEERING PORTFOLIO')
            canv.setFillColor(colors.HexColor(INK))
            canv.setFont('PlexKR-Light', 34)
            canv.drawString(x, height-336, 'Mintech internship')
            canv.drawString(x, height-383, 'Engineering and AI')
            canv.setFillColor(colors.HexColor(ACCENT))
            canv.setFont('PlexKR-Bold', 20)
            canv.drawString(x, height-434, 'A record-validation project')
            canv.setFillColor(colors.HexColor(MUTED))
            canv.setFont('PlexKR', 11)
            canv.drawString(x, height-505, 'Supervised manufacturing support and')
            canv.drawString(x, height-525, 'AI-assisted follow-up design and software checks.')
            if self.applicant:
                canv.setFillColor(colors.HexColor(INK))
                canv.setFont('PlexKR', 13)
                canv.drawString(x, height-580, self.applicant)
            canv.setFont('PlexKR', 9)
            canv.drawString(x, height-710, 'Software fixtures and synthetic data | Student follow-up project')
        else:
            draw_mark(canv, x, height-53, 18)
            canv.setFillColor(colors.HexColor(INK))
            canv.setFont('PlexKR-Bold', 9)
            canv.drawString(x+25, height-49, 'MINTECH INTERNSHIP REPORT')
            canv.setFillColor(colors.HexColor(MUTED))
            canv.setFont('PlexKR-Light', 9.5)
            canv.drawRightString(width-self.rightMargin, height-49, 'Project brief' if self.brief else 'Engineering report')
            canv.setStrokeColor(colors.HexColor('#838B93'))
            canv.setLineWidth(.45)
            canv.line(x, height-69, width-self.rightMargin, height-69)
            canv.setFont('PlexKR', 10.5)
            canv.drawRightString(width-self.rightMargin, 28,
                                 str(canv.getPageNumber() if self.brief else canv.getPageNumber()-1))
            if self.applicant:
                canv.setFont('PlexKR', 9)
                canv.drawString(x, 28, self.applicant)
        canv.restoreState()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'reports')
    parser.add_argument('--applicant', default='', help='Optional name for a private submission copy')
    args = parser.parse_args()
    register_fonts()
    destination = args.out
    destination.mkdir(exist_ok=True)
    for filename, brief in [('engineering_report', False), ('project_brief', True)]:
        styles = make_styles()
        for style in styles.values():
            style.wordWrap = None
        styles['h1'].fontSize = 24 if brief else 20
        styles['h1'].leading = 32 if brief else 30
        styles['body'].fontSize = 10.2
        styles['body'].leading = 16
        styles['body'].spaceAfter = 8
        styles['h2'].spaceBefore = 12
        styles['h2'].spaceAfter = 7
        for key in ['table', 'table_header']:
            styles[key].fontSize = 9
            styles[key].leading = 13.5
        doc = Report(destination/(filename+'.pdf'), styles, brief=brief, applicant=args.applicant)
        story = [] if brief else [Spacer(1, doc.height-1), PageBreak()]
        story.extend(markdown_flowables(ROOT/'docs'/(filename+'.md'), styles, doc.width))
        doc.multiBuild(story, canvasmaker=canvas.Canvas)
    print('Built two privacy-filtered PDFs')


if __name__ == '__main__':
    main()
