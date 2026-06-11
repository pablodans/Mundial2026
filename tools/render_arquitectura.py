#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render PNG (paleta pastel, fondo claro) del diagrama de arquitectura para el README.
Uso: python tools/render_arquitectura.py"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import assets_lib as A  # noqa: E402

# ---------- paleta pastel ----------
BG0, BG1 = (246, 248, 253), (234, 239, 248)
CARD, CARD_B = (255, 255, 255), (224, 230, 241)
TITULO = (54, 62, 84)
BODY = (78, 88, 112)
SUB = (140, 150, 172)
HEAD_TXT = (45, 52, 72)
MONO = (54, 140, 104)
NEG = (212, 110, 110)
POS = (76, 160, 120)
ARROW = (168, 180, 202)
GOLD_B, GOLD_F, GOLD_T = (222, 194, 96), (248, 237, 202), (120, 96, 26)
LAV = (210, 199, 242)      # datos
MINT = (176, 226, 206)     # calibracion
SKY = (190, 216, 244)      # modelo
PEACH = (247, 219, 172)    # monte carlo
GRN = (190, 230, 204)      # resultados
KPI_BG = (255, 255, 255)

W, H = 1500, 880


def card(d, x, y, w, h, titulo, head_color):
    A.rrect(d, x, y, w, h, 14, fill=CARD, outline=CARD_B, width=1.4)
    A.rrect(d, x, y, w, 30, 14, fill=head_color, outline=None)
    A.rrect(d, x, y + 16, w, 14, 0, fill=head_color, outline=None)  # tapa esquinas inferiores del header
    A.texto(d, x + w / 2, y + 15, titulo, A.font("bold", 14.5), HEAD_TXT, anchor="mm")


def bullet(d, x, y, color):
    d.ellipse([(x) * A.S, (y - 3) * A.S, (x + 6) * A.S, (y + 3) * A.S], fill=color)


def main():
    img, d = A.lienzo(W, H, BG0)
    A.gradiente_vertical(d, W, H, BG0, BG1)

    # ---- Header ----
    A.texto(d, W / 2, 38, "PREDICTOR MONTE CARLO — MUNDIAL 2026", A.font("bold", 31), TITULO, anchor="mm")
    A.texto(d, W / 2, 66,
            "Elo observado · altitud · desgaste · presión · estilo  →  goles Poisson × Dixon–Coles  →  "
            "10.000 simulaciones acumulativas por ronda",
            A.font("reg", 13.5), SUB, anchor="mm")

    # ---- KPI strip ----
    kpis = [("48", "SELECCIONES", "12 grupos · 16 sedes", LAV),
            ("10K", "SIMULACIONES", "en cada ronda de partidos", PEACH),
            ("5", "MUNDIALES", "calibración (80 cruces reales)", GRN),
            ("↻", "ACUMULATIVO", "el Elo se reajusta con cada resultado", LAV)]
    kx, kw, kgap = 40, 343, 12
    for i, (num, lab, sub, col) in enumerate(kpis):
        x = kx + i * (kw + kgap)
        A.rrect(d, x, 92, kw, 46, 11, fill=KPI_BG, outline=CARD_B, width=1.3)
        A.rrect(d, x, 92, 8, 46, 4, fill=col)
        A.texto(d, x + 22, 115, num, A.font("bold", 22), TITULO, anchor="lm")
        A.texto(d, x + 78, 108, lab, A.font("sb", 11), BODY, anchor="lm")
        A.texto(d, x + 78, 124, sub, A.font("reg", 10), SUB, anchor="lm")

    # ---- Pipeline cards ----
    cy, ch = 168, 322
    cards = [
        ("FUENTES DE DATOS", 40, 296, LAV),
        ("CALIBRACIÓN", 360, 232, MINT),
        ("MODELO DE PARTIDO", 616, 300, SKY),
        ("MOTOR MONTE CARLO", 940, 320, PEACH),
        ("RESULTADOS", 1284, 176, GRN),
    ]
    for t, x, w, col in cards:
        card(d, x, cy, w, ch, t, col)

    # Card 1: datos
    items = [("Elo — eloratings.net", "fuerza base por selección"),
             ("Ranking FIFA", "referencia cuantitativa"),
             ("Transfermarkt", "valores + 5 jugadores (+ portero)"),
             ("Sedes + altitud", "CDMX 2240 m · Guadalajara 1566 m"),
             ("Estilos de juego", "posesión · ritmo · ofensivo/def."),
             ("Histórico 5 Mundiales", "marcadores + Elo pre-torneo"),
             ("Fixture oficial", "sorteo dic-2025 · 72 partidos")]
    yy = cy + 52
    for it, ds in items:
        bullet(d, 58, yy, LAV)
        A.texto(d, 72, yy - 1, it, A.font("sb", 12), BODY, anchor="lm")
        A.texto(d, 72, yy + 13, ds, A.font("reg", 10), SUB, anchor="lm")
        yy += 37

    # Card 2: calibracion
    bx = 378
    A.texto(d, bx, cy + 52, "Backtest MLE", A.font("sb", 12.5), BODY, anchor="lm")
    A.texto(d, bx, cy + 67, "5 Mundiales · 80 cruces reales", A.font("reg", 10), SUB, anchor="lm")
    A.linea(d, [(bx, cy + 84), (bx + 196, cy + 84)], CARD_B, 1.2)
    A.texto(d, bx, cy + 100, "parámetros calibrados con datos:", A.font("reg", 10.5), SUB, anchor="lm")
    for i, p in enumerate(["ELO_DIV   = 250", "KO_FACTOR = 0.87", "DC_RHO    = −0.10"]):
        A.texto(d, bx, cy + 124 + i * 22, p, A.font("sb", 12.5), MONO, anchor="lm")
    A.linea(d, [(bx, cy + 196), (bx + 196, cy + 196)], CARD_B, 1.2)
    A.texto(d, bx, cy + 216, "El favorito por Elo gana el", A.font("reg", 10.5), SUB, anchor="lm")
    A.texto(d, bx, cy + 234, "70% de los cruces de KO", A.font("sb", 12.5), (196, 150, 60), anchor="lm")
    A.texto(d, bx, cy + 250, "(30% son sorpresas reales)", A.font("reg", 10), SUB, anchor="lm")

    # Card 3: modelo
    mx = 634
    A.texto(d, mx, cy + 52, "Elo efectivo =", A.font("sb", 12.5), BODY, anchor="lm")
    lineas = [("base (Elo observado)", BODY, None),
              ("+ localía (anfitrión MEX/USA/CAN)", BODY, POS),
              ("− altitud (rivales no adaptados)", BODY, NEG),
              ("− desgaste (fatiga acumulada)", BODY, NEG),
              ("+ presión (“ganar o nada”)", BODY, POS)]
    for i, (txt, c, sign) in enumerate(lineas):
        A.texto(d, mx + 12, cy + 74 + i * 20, txt, A.font("reg", 11), c, anchor="lm")
    A.linea(d, [(mx, cy + 178), (mx + 264, cy + 178)], CARD_B, 1.2)
    A.texto(d, mx, cy + 198, "estilo  →  apertura del partido", A.font("sb", 12), BODY, anchor="lm")
    A.texto(d, mx, cy + 222, "goles ~ Poisson × Dixon–Coles", A.font("sb", 12.5), (70, 130, 200), anchor="lm")
    A.texto(d, mx, cy + 238, "distribución exacta del marcador", A.font("reg", 10), SUB, anchor="lm")
    A.rrect(d, mx, cy + 252, 264, 32, 8, fill=(232, 241, 252), outline=SKY, width=1.4)
    A.texto(d, mx + 132, cy + 268, "→ 1X2 · marcador · over/under", A.font("sb", 11.5), (60, 100, 160), anchor="mm")

    # Card 4: monte carlo
    cx = 958
    pasos = [("1", "Fase de grupos — 72 partidos", None),
             ("2", "Tabla → clasifican 32", "12 primeros + 12 segundos + 8 mejores 3.º"),
             ("3", "Eliminación R32 → Final", "90' → prórroga → penales"),
             ("4", "Agregación", "campeón = moda · prob = frecuencia")]
    yy = cy + 54
    for num, t, ds in pasos:
        A.texto(d, cx, yy, num, A.font("bold", 14), (210, 140, 40), anchor="lm")
        A.texto(d, cx + 20, yy, t, A.font("sb", 12), BODY, anchor="lm")
        if ds:
            A.texto(d, cx + 20, yy + 15, ds, A.font("reg", 10), SUB, anchor="lm")
        yy += 48
    # badge x10.000
    A.rrect(d, cx, cy + 250, 150, 56, 12, fill=PEACH, outline=(228, 188, 120), width=1.6)
    A.texto(d, cx + 75, cy + 270, "× 10.000", A.font("bold", 24), (120, 80, 20), anchor="mm")
    A.texto(d, cx + 75, cy + 292, "SIMULACIONES / RONDA", A.font("sb", 9.5), (150, 110, 50), anchor="mm")
    A.texto(d, cx + 170, cy + 268, "se repite el", A.font("reg", 10.5), (190, 140, 70), anchor="lm")
    A.texto(d, cx + 170, cy + 283, "torneo y se", A.font("reg", 10.5), (190, 140, 70), anchor="lm")
    A.texto(d, cx + 170, cy + 298, "promedia", A.font("reg", 10.5), (190, 140, 70), anchor="lm")

    # Card 5: resultados
    rx = 1302
    outs = [("% avanza", BODY), ("% cuartos", BODY), ("% semifinal", BODY), ("% final", BODY),
            ("% TÍTULO", (196, 150, 60))]
    yy = cy + 54
    for t, c in outs:
        kind = "bold" if t == "% TÍTULO" else "sb"
        A.texto(d, rx, yy, t, A.font(kind, 13), c, anchor="lm")
        yy += 26
    A.linea(d, [(rx, cy + 192), (rx + 140, cy + 192)], CARD_B, 1.2)
    A.texto(d, rx, cy + 212, "por partido:", A.font("reg", 10.5), SUB, anchor="lm")
    for i, t in enumerate(["1X2", "marcador probable", "over / under"]):
        A.texto(d, rx, cy + 234 + i * 21, t, A.font("sb", 12), (70, 150, 110), anchor="lm")

    # ---- flechas entre tarjetas ----
    arr_y = cy + ch / 2
    for x0, x1 in [(336, 360), (592, 616), (916, 940), (1260, 1284)]:
        A.linea(d, [(x0, arr_y), (x1 - 4, arr_y)], ARROW, 2.4)
        d.polygon([((x1 - 4) * A.S, (arr_y - 5) * A.S), ((x1 - 4) * A.S, (arr_y + 5) * A.S),
                   (x1 * A.S, arr_y * A.S)], fill=ARROW)

    # ---- bucle de feedback (Elo dinamico) ----
    loop_y = cy + ch + 30
    A.rrect(d, 535, loop_y - 14, 430, 28, 14, fill=GOLD_F, outline=GOLD_B, width=1.6)
    A.texto(d, 750, loop_y, "↻  Elo dinámico — cada resultado real reajusta el Elo (K adaptativo)",
            A.font("sb", 12), GOLD_T, anchor="mm")

    # ---- timeline ----
    ty = 590
    A.texto(d, W / 2, ty, "PROCESO ACUMULATIVO · 10.000 simulaciones en CADA ronda",
            A.font("bold", 16), TITULO, anchor="mm")
    A.texto(d, W / 2, ty + 20,
            "la predicción se rehace tras cada jornada con el Elo ya actualizado — se vuelve más fiable a medida que se juega",
            A.font("reg", 11.5), SUB, anchor="mm")

    etapas = [("PRE-TORNEO", "Elo a priori", False), ("RONDA", "Jornada 1", False),
              ("RONDA", "Jornada 2", False), ("RONDA", "Jornada 3", False),
              ("ELIMINACIÓN", "Octavos", True), ("ELIMINACIÓN", "Cuartos", True),
              ("ELIMINACIÓN", "Semis", True), ("CAMPEÓN", "Final", True)]
    bw, bh, bgap = 160, 74, 10
    bx0 = (W - (len(etapas) * bw + (len(etapas) - 1) * bgap)) / 2
    by = ty + 42
    for i, (lab, nom, oro) in enumerate(etapas):
        x = bx0 + i * (bw + bgap)
        es_titulo = (i == len(etapas) - 1)
        fill = GOLD_F if es_titulo else CARD
        borde = GOLD_B if es_titulo else (CARD_B if not oro else (228, 210, 160))
        A.rrect(d, x, by, bw, bh, 12, fill=fill, outline=borde, width=1.8 if es_titulo else 1.3)
        lab_col = GOLD_T if es_titulo else ((190, 150, 70) if oro else (130, 142, 168))
        nom_col = GOLD_T if es_titulo else TITULO
        A.texto(d, x + bw / 2, by + 18, lab, A.font("sb", 10.5), lab_col, anchor="mm")
        A.texto(d, x + bw / 2, by + 42, nom, A.font("bold", 14.5), nom_col, anchor="mm")
        A.texto(d, x + bw / 2, by + 61, "10.000 sims", A.font("reg", 10), SUB, anchor="mm")
        if i < len(etapas) - 1:
            ax = x + bw
            A.linea(d, [(ax, by + bh / 2), (ax + bgap - 2, by + bh / 2)], ARROW, 2)

    # flecha de retorno acumulativa
    A.texto(d, W / 2, by + bh + 30,
            "resultados reales de la ronda → actualizan el Elo (K adaptativo) → la siguiente ronda "
            "se simula con info nueva  ↻  los pronósticos se afinan jornada a jornada",
            A.font("sb", 11.5), (150, 130, 90), anchor="mm")

    # ---- footer ----
    A.linea(d, [(40, H - 40), (W - 40, H - 40)], CARD_B, 1.2)
    A.texto(d, 40, H - 22,
            "Reproducible (semilla 2026) · sin dependencias (Python stdlib) · datos jun-2026: eloratings.net · FIFA · Transfermarkt · Wikipedia",
            A.font("reg", 10.5), SUB, anchor="lm")

    ruta = os.path.join(ROOT, "docs", "diagrama_arquitectura.png")
    A.finalizar(img, W, H, ruta)
    print("Imagen ->", ruta)


if __name__ == "__main__":
    main()
