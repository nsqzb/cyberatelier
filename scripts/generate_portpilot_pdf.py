"""Génère le PDF PortPilot depuis son énoncé Markdown synchronisé.

Dépendance d’édition uniquement : reportlab (jamais nécessaire à l’application).
Usage : python3 scripts/generate_exercises.py && python3 scripts/generate_portpilot_pdf.py
"""
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent.parent

def main():
    import reportlab
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer
    fonts=Path(reportlab.__file__).parent/'fonts'
    for name,file in [('Atelier','Vera.ttf'),('AtelierBold','VeraBd.ttf'),('AtelierItalic','VeraIt.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('Atelier',normal='Atelier',bold='AtelierBold',italic='AtelierItalic',boldItalic='AtelierBold')
    styles={
      'body':ParagraphStyle('body',fontName='Atelier',fontSize=9,leading=14,spaceAfter=6,allowWidows=False,allowOrphans=False),
      'label':ParagraphStyle('label',fontName='Atelier',fontSize=9,leading=14,spaceAfter=7,keepWithNext=True),
      'title':ParagraphStyle('title',fontName='AtelierBold',fontSize=22,leading=28,spaceAfter=18,textColor=colors.HexColor('#187e75')),
      'h2':ParagraphStyle('h2',fontName='AtelierBold',fontSize=15,leading=20,spaceBefore=18,spaceAfter=9,keepWithNext=True),
      'h3':ParagraphStyle('h3',fontName='AtelierBold',fontSize=12,leading=17,spaceBefore=14,spaceAfter=8,keepWithNext=True),
      'h4':ParagraphStyle('h4',fontName='AtelierBold',fontSize=10,leading=15,spaceBefore=12,spaceAfter=7,keepWithNext=True,textColor=colors.HexColor('#187e75')),
      'code':ParagraphStyle('code',fontName='Courier',fontSize=7.3,leading=10.5,leftIndent=8,rightIndent=8,spaceBefore=5,spaceAfter=9,backColor=colors.HexColor('#f1f4f8')),
      'list':ParagraphStyle('list',fontName='Atelier',fontSize=9,leading=14,leftIndent=12,firstLineIndent=-8,spaceAfter=5),
    }
    def inline(text):
        text=text.replace('—','-').replace('–','-').replace('→','->').replace('\u2011','-')
        text=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',text)
        text=escape(text)
        text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
        text=re.sub(r'(?<!\*)\*([^*]+)\*',r'<i>\1</i>',text)
        text=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',text)
        return text
    text=(ROOT/'content/portpilot.md').read_text(encoding='utf-8')
    story=[];code=[];fenced=False
    for line in text.splitlines():
        if line.strip() in ('<details>', '</details>'):
            continue
        summary=re.fullmatch(r'<summary>(.*?)</summary>',line.strip())
        if summary:
            story.append(Paragraph(inline(summary[1]),styles['h4']))
            continue
        if line.startswith('```'):
            if fenced:
                story.append(Preformatted('\n'.join(code),styles['code'],maxLineLength=98,splitChars=' ',newLineChars='  '));code=[]
            fenced=not fenced
            continue
        if fenced: code.append(line);continue
        if not line.strip(): continue
        if line.startswith('<!--'): continue
        match=re.match(r'^(#{1,4}) (.*)',line)
        if match:
            level=len(match[1]);style='title' if level==1 else 'h'+str(level)
            story.append(Paragraph(inline(match[2]),styles[style]));continue
        style='list' if re.match(r'^(- |\d+\. )',line) else ('label' if re.fullmatch(r'\*\*[^*]+\*\*',line.strip()) else 'body')
        story.append(Paragraph(inline(line),styles[style]))
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Atelier',8);canvas.setFillColor(colors.HexColor('#60768b'))
        canvas.drawString(42,26,'Cyber Atelier | PortPilot | Exercices guidés')
        canvas.drawRightString(A4[0]-42,26,str(doc.page));canvas.restoreState()
    target=ROOT/'web/downloads/PortPilot.pdf'
    doc=SimpleDocTemplate(str(target),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=42,title='PortPilot - Exercices guidés',author='Cyber Atelier')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('PDF PortPilot synchronisé.')

if __name__=='__main__': main()
