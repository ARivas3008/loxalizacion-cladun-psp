#!/usr/bin/env python3
"""Construye un PDF legible desde la guía Markdown del repositorio.

Dependencias DE PUBLICACIÓN: reportlab>=4,<5, mistune>=3,<4.
La edición de diálogos en el navegador no exige estas dependencias.
"""
from __future__ import annotations
import argparse
from html import escape
from pathlib import Path
import re

import mistune
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, Preformatted, HRFlowable

INK=colors.HexColor('#172337')
SUB=colors.HexColor('#43526b')
ACCENT=colors.HexColor('#047e82')
LIGHT=colors.HexColor('#e7f1f3')
BEIGE=colors.HexColor('#f4f6fa')
BORDER=colors.HexColor('#dbe1eb')
PAGE_W,PAGE_H=A4
ROOT=Path(__file__).resolve().parents[1]


def register_fonts():
    found=[
      ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
      ('C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf'),
    ]
    pair=next(((Path(x),Path(y)) for x,y in found if Path(x).exists() and Path(y).exists()),None)
    if pair:
        pdfmetrics.registerFont(TTFont('LocalSans',str(pair[0])))
        pdfmetrics.registerFont(TTFont('LocalSansBold',str(pair[1])))
        pdfmetrics.registerFontFamily('LocalSans',normal='LocalSans',bold='LocalSansBold',italic='LocalSans',boldItalic='LocalSansBold')
        return 'LocalSans','LocalSansBold'
    return 'Helvetica','Helvetica-Bold'


def text_inline(children):
    def rec(node):
        typ=node.get('type')
        if typ=='text':return escape(node.get('raw',''))
        if typ=='codespan':return '<font color="#026974">'+escape(node.get('raw',''))+'</font>'
        if typ in ('softbreak','linebreak'):return '<br/>'
        if typ in ('strong','emphasis'):
            tag='b' if typ=='strong' else 'i'
            return '<'+tag+'>'+''.join(rec(x) for x in node.get('children',[]))+'</'+tag+'>'
        if typ=='link':
            href=escape(node.get('attrs',{}).get('url',''),quote=True)
            return '<link href="'+href+'" color="#047e82">'+''.join(rec(x) for x in node.get('children',[]))+'</link>'
        return escape(node.get('raw','')) if 'raw' in node else ''.join(rec(x) for x in node.get('children',[]))
    return ''.join(rec(x) for x in children)


def plain_inline(children):
    return re.sub(r'<[^>]+>','',text_inline(children))


def page_canvas(can,doc):
    can.saveState()
    can.setFillColor(INK);can.rect(0,PAGE_H-15*mm,PAGE_W,15*mm,fill=1,stroke=0)
    can.setFillColor(colors.white);can.setFont('LocalSansBold' if 'LocalSansBold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',8)
    can.drawString(18*mm,PAGE_H-10*mm,'CLADUN  /  MANUAL DE REVISIÓN DE TEXTOS')
    can.setStrokeColor(BORDER);can.line(17*mm,17*mm,PAGE_W-17*mm,17*mm)
    can.setFillColor(SUB);can.setFont('LocalSans' if 'LocalSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',7.3)
    can.drawString(18*mm,12*mm,'Guía de trabajo · Rama revision-manual-dialogos · Edición experimental')
    can.drawRightString(PAGE_W-18*mm,12*mm,f'{doc.page}')
    can.restoreState()


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--entrada',type=Path,default=ROOT/'docs/GUIA_EDICION_MANUAL.md')
    ap.add_argument('--salida',type=Path,default=ROOT/'docs/GUIA_EDICION_MANUAL.pdf')
    args=ap.parse_args(argv)
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    font,bold=register_fonts()
    styles={
      'main':ParagraphStyle('main',fontName=font,fontSize=9.35,leading=14.6,textColor=INK,spaceAfter=7,splitLongWords=True),
      'title':ParagraphStyle('title',fontName=bold,fontSize=23,leading=28,textColor=INK,spaceBefore=15,spaceAfter=14),
      'h2':ParagraphStyle('h2',fontName=bold,fontSize=13.2,leading=18,textColor=ACCENT,spaceBefore=15,spaceAfter=8,keepWithNext=True),
      'h3':ParagraphStyle('h3',fontName=bold,fontSize=10.6,leading=14,textColor=INK,spaceBefore=11,spaceAfter=6,keepWithNext=True),
      'item':ParagraphStyle('item',fontName=font,fontSize=8.95,leading=13.3,textColor=INK,leftIndent=12,firstLineIndent=-8,spaceAfter=4),
      'table':ParagraphStyle('table',fontName=font,fontSize=8,leading=10.5,textColor=INK),
      'code':ParagraphStyle('code',fontName='Courier',fontSize=7,leading=10,textColor=INK,leftIndent=4,spaceAfter=7),
      'micro':ParagraphStyle('micro',fontName=font,fontSize=8,leading=11,textColor=SUB)
    }
    story=[]
    doc=SimpleDocTemplate(str(args.salida),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,
      topMargin=23*mm,bottomMargin=22*mm,title='Guía profesional de corrección de textos - Cladun PSP',author='Proyecto de localización de Cladun',subject='Edición de CSV, hablantes, fuente PSP, QA')
    src=args.entrada.read_text(encoding='utf-8')
    parser=mistune.create_markdown(renderer='ast',plugins=['table'])
    tokens=parser(src)
    def render_table(node):
        rows=[];header_count=0
        for sec in node.get('children',[]):
            if sec.get('type')=='table_head':
                rows.append([Paragraph(text_inline(c.get('children',[])),styles['table']) for c in sec.get('children',[])])
                header_count=1
            elif sec.get('type')=='table_body':
                for rr in sec.get('children',[]):
                    rows.append([Paragraph(text_inline(c.get('children',[])),styles['table']) for c in rr.get('children',[])])
        if not rows:return
        n=max(len(x) for x in rows)
        rows=[x+[Paragraph('',styles['table'])]*(n-len(x)) for x in rows]
        width=doc.width/n
        table=Table(rows,colWidths=[width]*n,repeatRows=header_count,hAlign='LEFT')
        table.setStyle(TableStyle([
           ('BACKGROUND',(0,0),(-1,0),LIGHT),('BOX',(0,0),(-1,-1),.45,BORDER),
           ('GRID',(0,0),(-1,-1),.35,BORDER),('VALIGN',(0,0),(-1,-1),'TOP'),
           ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
           ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ]))
        story.append(table);story.append(Spacer(1,5*mm))
    def render_list(node):
        ordered=node.get('attrs',{}).get('ordered',False)
        idx=node.get('attrs',{}).get('start',1)
        for item in node.get('children',[]):
            fragments=[]
            for t in item.get('children',[]):
                if t['type'] in ('block_text','paragraph'):
                    fragments.append(text_inline(t.get('children',[])))
                elif t['type']=='block_code':
                    if fragments:story.append(Paragraph((f'{idx}.' if ordered else '•')+'  '+''.join(fragments),styles['item']));fragments=[]
                    story.append(Preformatted(t.get('raw',''),styles['code'],maxLineLength=79,splitChars=' /_-'))
                else:fragments.append(text_inline(t.get('children',[])))
            if fragments:story.append(Paragraph((f'{idx}.' if ordered else '•')+'  '+' '.join(fragments),styles['item']))
            idx+=1
        story.append(Spacer(1,2*mm))
    # Page 1: distinctive cover with subtitle and context before body.
    story.append(Spacer(1,4*mm))
    story.append(Paragraph('Manual de corrección<br/>de textos y hablantes',styles['title']))
    story.append(Paragraph('Cladun: This Is an RPG! · PSP USA · Revisión manual segura',
        ParagraphStyle('subtitle',parent=styles['main'],fontName=bold,textColor=ACCENT,fontSize=10.6,leading=16,spaceAfter=10)))
    story.append(HRFlowable(width='100%',thickness=1.2,color=ACCENT,spaceBefore=3,spaceAfter=10))
    story.append(Paragraph('Este manual explica cómo corregir una frase, conservar los identificadores originales, regenerar el guion con nombres de interlocutor y distinguir errores de traducción de problemas de tipografía dentro de PPSSPP.',styles['main']))
    story.append(Paragraph('<b>Ejemplo verificado en el corpus:</b> la captura muestra «Joven frené tico», pero el CSV contiene «Joven frenético». Una separación visual no debe corregirse de forma automática eliminando tildes.',styles['main']))
    story.append(Spacer(1,7*mm))
    cells=[['EDICIÓN','INTEGRIDAD','LECTURA'],['Solo la columna «espanol»','9.237 filas y offsets intactos','Guion por escena y hablante']]
    tt=Table([[Paragraph(c,styles['table']) for c in row] for row in cells],colWidths=[doc.width/3]*3)
    tt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('BACKGROUND',(0,1),(-1,1),BEIGE),('BOX',(0,0),(-1,-1),.6,BORDER),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),11),('TOPPADDING',(0,0),(-1,-1),10)]))
    story.append(tt)
    story.append(Spacer(1,8*mm))
    story.append(Paragraph('Contenido: herramientas · edición guiada · hablantes 0x6E · fuente PSP · validación · incidencias y publicación.',styles['micro']))
    story.append(PageBreak())
    for index,node in enumerate(tokens):
        typ=node.get('type')
        if typ=='heading':
            level=node.get('attrs',{}).get('level',2)
            # The first Markdown heading is already represented on the cover.
            if level==1:continue
            story.append(Paragraph(text_inline(node.get('children',[])),styles['h2'] if level==2 else styles['h3']))
        elif typ=='paragraph':
            story.append(Paragraph(text_inline(node.get('children',[])),styles['main']))
        elif typ=='blank_line':continue
        elif typ=='list':render_list(node)
        elif typ=='table':render_table(node)
        elif typ=='block_code':
            raw=node.get('raw','').rstrip('\n')
            story.append(Preformatted(raw,styles['code'],maxLineLength=78,splitChars=' /_-'))
            story.append(Spacer(1,3*mm))
        elif typ=='block_quote':
            s=' '.join(text_inline(x.get('children',[])) for x in node.get('children',[]))
            story.append(Paragraph(s,styles['main']))
        else:pass
    doc.build(story,onFirstPage=page_canvas,onLaterPages=page_canvas)
    print(f'{args.salida} ({args.salida.stat().st_size} bytes)')

if __name__=='__main__':main()
