"""Typography shared by the anonymized reports."""
from pathlib import Path

from reportlab.lib import colors

from reportlab.lib.styles import ParagraphStyle

from reportlab.pdfbase import pdfmetrics

from reportlab.lib.fonts import addMapping

from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent.parent

FONT_DIR = ROOT / 'assets/fonts'

INK = '#111418'

BODY = '#2A2F36'

MUTED = '#8A919C'

ACCENT = '#007F79'

PALE = '#E9F4F2'

RULE = '#D0D5D9'

def register_fonts():
    for weight, alias in [('Regular', 'PlexKR'), ('Bold', 'PlexKR-Bold'), ('Light', 'PlexKR-Light')]:
        font = FONT_DIR / f'IBMPlexSansKR-{weight}.ttf'
        if not font.is_file():
            raise FileNotFoundError(f'Missing bundled font: {font.name}')
        pdfmetrics.registerFont(TTFont(alias, str(font)))
    addMapping('PlexKR', 0, 0, 'PlexKR')
    addMapping('PlexKR', 1, 0, 'PlexKR-Bold')

def make_styles():
    common = dict(fontName='PlexKR', textColor=colors.HexColor(BODY), wordWrap='CJK')

    def style(name, **kwargs):
        return ParagraphStyle(name, **(common | kwargs))

    return {
        'h1': style('Heading1Korean', fontName='PlexKR-Bold', fontSize=21, leading=34,
                    textColor=colors.HexColor(INK), spaceAfter=17, keepWithNext=True),
        'h2': style('Heading2Korean', fontName='PlexKR-Bold', fontSize=13.5, leading=21,
                    textColor=colors.HexColor(INK), spaceBefore=16, spaceAfter=8, keepWithNext=True),
        'h3': style('Heading3Korean', fontName='PlexKR-Bold', fontSize=10.5, leading=17,
                    textColor=colors.HexColor(INK), spaceBefore=10, spaceAfter=5, keepWithNext=True),
        'body': style('BodyKorean', fontSize=10.5, leading=17.5, spaceAfter=9),
        'bullet': style('BulletKorean', fontSize=10.5, leading=17.5, leftIndent=14,
                       firstLineIndent=0, bulletIndent=2, spaceAfter=9),
        'quote': style('QuoteKorean', fontName='PlexKR-Bold', fontSize=12, leading=20,
                      textColor=colors.HexColor(ACCENT), backColor=colors.HexColor(PALE),
                      borderColor=colors.HexColor(RULE), borderWidth=.5,
                      borderPadding=12, leftIndent=12, rightIndent=12,
                      spaceBefore=7, spaceAfter=18),
        'code': style('CodeKorean', fontSize=8.8, leading=15, leftIndent=10, rightIndent=10,
                     backColor=colors.HexColor('#F5F7F9'), borderPadding=9,
                     spaceBefore=8, spaceAfter=15),
        'table': style('TableKorean', fontSize=9.5, leading=14.5),
        'table_small': style('TableSmallKorean', fontSize=9, leading=14),
        'table_header': style('TableHeaderKorean', fontName='PlexKR-Bold', fontSize=9.5,
                              leading=14.5, textColor=colors.HexColor(INK)),
        'toc_title': style('ContentsTitle', fontName='PlexKR-Bold', fontSize=24, leading=34,
                           textColor=colors.HexColor(INK), spaceAfter=23),
        'toc_1': style('ContentsEntry', fontSize=10.5, leading=27, spaceAfter=7,
                       leftIndent=0, firstLineIndent=0, rightIndent=20),
        'caption': style('CaptionKorean', fontSize=8.5, leading=13.5,
                         textColor=colors.HexColor('#737D86'), spaceBefore=7, spaceAfter=12),
    }

def draw_mark(canv, x, y, size):
    # A record/coupon motif for this report, not an official company logo.
    unit = size * .42
    gap = size - 2 * unit
    for dx, dy, fill in [(0, 0, '#111418'), (unit + gap, 0, '#007F79'),
                         (0, unit + gap, '#007F79'), (unit + gap, unit + gap, '#A9D6CF')]:
        canv.setFillColor(colors.HexColor(fill))
        canv.roundRect(x + dx, y + dy, unit, unit, size * .055, stroke=0, fill=1)
