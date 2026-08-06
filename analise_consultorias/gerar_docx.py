#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de DOSSIE (.docx) de consultoria, no estilo do dossie do Limendes.

Uso como biblioteca:
    from gerar_docx import Dossie
    d = Dossie("Ultra Online - Raphael", "Analise de Consultorias | ICOMM / TF")
    d.kpis([("Faturamento inicial","R$ 260.953","fev/2026"),
            ("Faturamento atual","R$ 1.026.854","jun/2026"),
            ("Crescimento","+293%","~3x em ~5 meses")])
    d.h1("1. Resultado")
    d.p("texto ...")
    d.tabela(["Mes","Faturamento"], [["fev","260.953"],["jun","1.026.854"]])
    d.salvar("/caminho/Dossie_Raphael.docx")

Sem estado global; cada Dossie e um documento independente.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# paleta
AZUL = RGBColor(0x1F, 0x39, 0x64)      # titulos
CINZA = RGBColor(0x55, 0x55, 0x55)     # subtitulo/legenda
VERDE = RGBColor(0x1B, 0x7A, 0x3D)     # destaque positivo
PRETO = RGBColor(0x22, 0x22, 0x22)


class Dossie:
    def __init__(self, titulo, subtitulo=""):
        self.doc = Document()
        base = self.doc.styles["Normal"]
        base.font.name = "Calibri"
        base.font.size = Pt(10.5)
        base.font.color.rgb = PRETO

        t = self.doc.add_paragraph()
        r = t.add_run(titulo)
        r.bold = True
        r.font.size = Pt(20)
        r.font.color.rgb = AZUL
        if subtitulo:
            s = self.doc.add_paragraph()
            rs = s.add_run(subtitulo)
            rs.font.size = Pt(10.5)
            rs.font.color.rgb = CINZA

    def kpis(self, itens):
        """itens = [(rotulo, valor, legenda), ...] -> uma linha de 'cards'."""
        tab = self.doc.add_table(rows=1, cols=len(itens))
        tab.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, (rotulo, valor, legenda) in enumerate(itens):
            cel = tab.rows[0].cells[i]
            p1 = cel.paragraphs[0]
            p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rr = p1.add_run(rotulo.upper())
            rr.font.size = Pt(8)
            rr.font.color.rgb = CINZA
            p2 = cel.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rv = p2.add_run(valor)
            rv.bold = True
            rv.font.size = Pt(16)
            rv.font.color.rgb = VERDE if valor.strip().startswith("+") else AZUL
            if legenda:
                p3 = cel.add_paragraph()
                p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
                rl = p3.add_run(legenda)
                rl.font.size = Pt(8)
                rl.font.color.rgb = CINZA
        self.doc.add_paragraph()

    def h1(self, texto):
        p = self.doc.add_paragraph()
        p.space_before = Pt(10)
        r = p.add_run(texto)
        r.bold = True
        r.font.size = Pt(14)
        r.font.color.rgb = AZUL

    def h2(self, texto):
        p = self.doc.add_paragraph()
        r = p.add_run(texto)
        r.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = PRETO

    def p(self, texto, italico=False):
        p = self.doc.add_paragraph()
        r = p.add_run(texto)
        r.italic = italico
        if italico:
            r.font.color.rgb = CINZA
        return p

    def bullet(self, texto):
        self.doc.add_paragraph(texto, style="List Bullet")

    def tabela(self, cabecalho, linhas):
        tab = self.doc.add_table(rows=1, cols=len(cabecalho))
        try:
            tab.style = "Light Grid Accent 1"
        except Exception:
            tab.style = "Table Grid"
        for i, c in enumerate(cabecalho):
            cel = tab.rows[0].cells[i]
            run = cel.paragraphs[0].add_run(str(c))
            run.bold = True
            run.font.size = Pt(9.5)
        for linha in linhas:
            cells = tab.add_row().cells
            for i, v in enumerate(linha):
                run = cells[i].paragraphs[0].add_run("" if v is None else str(v))
                run.font.size = Pt(9.5)
        self.doc.add_paragraph()
        return tab

    def salvar(self, caminho):
        self.doc.save(caminho)
        return caminho
