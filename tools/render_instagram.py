#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera imágenes para Instagram (Historia 1080x1920 y Publicación 1080x1350) que
promocionan el repo: 3 slides — portada, qué usa el modelo, predicción preliminar.

Diseño dark premium, sin emojis (Segoe UI no los rasteriza). Lee los números reales de
data/prediccion_resultados.json.  Uso: python tools/render_instagram.py"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import assets_lib as A  # noqa: E402

# ---------- paleta ----------
BG0, BG1 = (17, 21, 48), (45, 26, 73)
WHITE = (248, 250, 254)
MUTED = (178, 186, 212)
GOLD = (247, 201, 99)
MINT = (104, 224, 188)
LAV = (180, 162, 248)
TRACK = (52, 58, 96)
RING = (60, 66, 112)
REPO = "github.com/pablodans/Mundial2026"

# Nombres con tilde para mostrar (los datos usan ASCII: "Espana", "Mexico", ...)
DISPLAY = {
    "Espana": "España", "Mexico": "México", "Japon": "Japón", "Turquia": "Turquía",
    "Belgica": "Bélgica", "Tunez": "Túnez", "Paises Bajos": "Países Bajos",
    "Sudafrica": "Sudáfrica", "Panama": "Panamá", "Peru": "Perú", "Iran": "Irán",
}


def disp(nombre):
    return DISPLAY.get(nombre, nombre)


def top3():
    r = json.load(open(os.path.join(ROOT, "data", "prediccion_resultados.json"), encoding="utf-8"))
    meta = r["meta"]["simulaciones"]
    top = [(x["pais"], x["p_titulo"]) for x in r["ranking"][:3]]
    return meta, top


# ---------- bloques (devuelven (alto, fn(y))) ----------
def b_gap(h):
    return h, (lambda y: None)


def b_chip(d, cx, text, accent):
    f = A.font("sb", 22)
    w, _ = A._ancho(d, text, f)
    pw, ph = w + 56, 50

    def fn(y):
        A.rrect(d, cx - pw / 2, y, pw, ph, ph / 2, fill=None, outline=accent, width=2.2)
        A.texto(d, cx, y + ph / 2, text, f, accent, anchor="mm")
    return ph, fn


def b_lines(d, cx, maxw, text, kind, size, color, lf=1.12):
    lines = A.envolver(d, text, kind, size, maxw)
    lh = size * lf

    def fn(y):
        for i, ln in enumerate(lines):
            A.texto(d, cx, y + i * lh + lh / 2, ln, A.font(kind, size), color, anchor="mm")
    return len(lines) * lh, fn


def b_bullets(d, cx, maxw, items, accent, size=29):
    indent, lh, gap = 42, size * 1.26, 20
    rows, total = [], 0
    for it in items:
        lines = A.envolver(d, it, "reg", size, maxw - indent)
        h = len(lines) * lh
        rows.append((lines, h))
        total += h + gap
    total -= gap
    x0 = cx - maxw / 2

    def fn(y):
        yy = y
        for lines, h in rows:
            d.ellipse([x0 * A.S, (yy + lh / 2 - 7) * A.S, (x0 + 14) * A.S, (yy + lh / 2 + 7) * A.S], fill=accent)
            for i, ln in enumerate(lines):
                A.texto(d, x0 + indent, yy + i * lh + lh / 2, ln, A.font("reg", size), WHITE, anchor="lm")
            yy += h + gap
    return total, fn


def b_bars(d, cx, maxw, data, size=32):
    maxv = max(v for _, v, _ in data)
    row_h, gap = 92, 20
    x0 = cx - maxw / 2

    def fn(y):
        yy = y
        for label, val, col in data:
            A.texto(d, x0, yy + 6, label, A.font("bold", size), WHITE, anchor="lm")
            A.texto(d, x0 + maxw, yy + 6, f"{val:.1f}%".replace(".", ","), A.font("black", size), col, anchor="rm")
            by = yy + size + 8
            A.rrect(d, x0, by, maxw, 18, 9, fill=TRACK)
            A.rrect(d, x0, by, max(18, maxw * val / maxv), 18, 9, fill=col)
            yy += row_h + gap
    return len(data) * row_h + (len(data) - 1) * gap, fn


def b_pill(d, cx, text, accent, size=25):
    f = A.font("bold", size)
    w, _ = A._ancho(d, text, f)
    pw, ph = w + 64, 62

    def fn(y):
        A.rrect(d, cx - pw / 2, y, pw, ph, ph / 2, fill=accent)
        A.texto(d, cx, y + ph / 2, text, f, (18, 20, 44), anchor="mm")
    return ph, fn


# ---------- slides ----------
def slide_portada(d, W, gs):
    cx, maxw = W / 2, W - 180
    return [
        b_chip(d, cx, "PROYECTO ABIERTO · MUNDIAL 2026", GOLD),
        b_gap(40 * gs),
        b_lines(d, cx, maxw, "SIMULÉ EL MUNDIAL 2026", "black", 66, WHITE, lf=1.06),
        b_gap(6 * gs),
        b_lines(d, cx, maxw, "80.000 VECES", "black", 104, GOLD, lf=1.0),
        b_gap(40 * gs),
        b_lines(d, cx, maxw, "Un algoritmo Monte Carlo que escribí yo mismo, "
                "alimentado con datos cuantitativos de varias fuentes.", "light", 32, MUTED, lf=1.28),
        b_gap(50 * gs),
        b_pill(d, cx, "REPOSITORIO DE LIBRE ACCESO", MINT),
    ]


def slide_datos(d, W, gs):
    cx, maxw = W / 2, W - 150
    items = [
        "Elo de eloratings.net (fuerza base)",
        "Ranking y puntos FIFA",
        "Valor de plantilla — Transfermarkt",
        "Palmarés e historial mundialista (títulos, finales, semis, participaciones)",
        "Altitud: altura de la sede + adaptación de cada equipo",
        "Estilo de juego (ofensivo / defensivo · ritmo)",
        "Penalidad por desgaste (fatiga acumulada)",
        "Bonus de presión: “hay que ganar o ganar”",
        "5 jugadores clave por equipo, incluido el portero, con métricas de rendimiento",
    ]
    return [
        b_chip(d, cx, "QUÉ MIRA EL MODELO", LAV),
        b_gap(34 * gs),
        b_lines(d, cx, maxw, "Datos que pesa en cada partido", "black", 50, WHITE, lf=1.06),
        b_gap(40 * gs),
        b_bullets(d, cx, maxw, items, MINT, size=29),
    ]


def slide_prediccion(d, W, gs, meta, top):
    cx, maxw = W / 2, W - 180
    colores = [GOLD, LAV, MINT]
    data = [(disp(p), v, colores[i]) for i, (p, v) in enumerate(top)]
    camp, cp = top[0]
    return [
        b_chip(d, cx, "PREDICCIÓN PRELIMINAR", GOLD),
        b_gap(28 * gs),
        b_lines(d, cx, maxw, "CAMPEÓN MÁS PROBABLE", "sb", 30, MUTED, lf=1.1),
        b_gap(6 * gs),
        b_lines(d, cx, maxw, disp(camp).upper(), "black", 96, GOLD, lf=1.0),
        b_gap(30 * gs),
        b_bars(d, cx, maxw, data),
        b_gap(34 * gs),
        b_lines(d, cx, maxw, f"Sale de simular el torneo completo {meta:,} veces"
                .replace(",", "."), "sb", 28, WHITE, lf=1.2),
        b_gap(14 * gs),
        b_lines(d, cx, maxw, "Es solo el punto de partida: el modelo se nutre de los "
                "resultados reales y afina la predicción ronda tras ronda.", "light", 29, MUTED, lf=1.28),
    ]


def fondo(d, W, H):
    A.gradiente_vertical(d, W, H, BG0, BG1)
    # anillos suaves de fondo
    for (ccx, ccy, rad) in [(W + 60, 180, 360), (-80, H - 220, 420), (W - 120, H - 120, 180)]:
        d.ellipse([(ccx - rad) * A.S, (ccy - rad) * A.S, (ccx + rad) * A.S, (ccy + rad) * A.S],
                  outline=RING, width=int(2 * A.S))


def cabecera_pie(d, W, header_y, footer_y, page_idx, n=3):
    A.texto(d, W / 2, header_y, "MUNDIAL 2026   ·   PREDICTOR MONTE CARLO",
            A.font("sb", 20), (140, 150, 184), anchor="mm")
    # puntos de carrusel
    dot_y = footer_y - 58
    spacing = 26
    x0 = W / 2 - spacing * (n - 1) / 2
    for i in range(n):
        x = x0 + i * spacing
        if i == page_idx:
            d.ellipse([(x - 6) * A.S, (dot_y - 6) * A.S, (x + 6) * A.S, (dot_y + 6) * A.S], fill=GOLD)
        else:
            d.ellipse([(x - 5) * A.S, (dot_y - 5) * A.S, (x + 5) * A.S, (dot_y + 5) * A.S],
                      outline=(110, 118, 156), width=int(1.6 * A.S))
    A.texto(d, W / 2, footer_y - 16, REPO, A.font("bold", 23), GOLD, anchor="mm")
    A.texto(d, W / 2, footer_y + 14, "CÓDIGO ABIERTO · LIBRE ACCESO · LINK ABAJO",
            A.font("sb", 17), (140, 150, 184), anchor="mm")


def render(fmt, slides_def, meta, top):
    nombre, W, H, header_y, footer_y, cy0, cy1, gs = fmt
    for idx, build in enumerate(slides_def):
        img, d = A.lienzo(W, H, BG0)
        fondo(d, W, H)
        cabecera_pie(d, W, header_y, footer_y, idx)
        blocks = build(d, W, gs, meta, top)
        total = sum(h for h, _ in blocks)
        y = cy0 + max(0, (cy1 - cy0 - total) / 2)
        for h, fn in blocks:
            fn(y)
            y += h
        out = os.path.join(ROOT, "docs", "instagram", f"{nombre}_{idx + 1}.png")
        A.finalizar(img, W, H, out)
        print("Imagen ->", out)


def main():
    os.makedirs(os.path.join(ROOT, "docs", "instagram"), exist_ok=True)
    meta, top = top3()
    slides = [
        lambda d, W, gs, m, t: slide_portada(d, W, gs),
        lambda d, W, gs, m, t: slide_datos(d, W, gs),
        lambda d, W, gs, m, t: slide_prediccion(d, W, gs, m, t),
    ]
    # nombre, W, H, header_y, footer_y, cy0, cy1, gap_scale
    formatos = [
        ("historia", 1080, 1920, 175, 1790, 320, 1690, 1.6),
        ("publicacion", 1080, 1350, 100, 1280, 215, 1180, 1.0),
    ]
    for fmt in formatos:
        render(fmt, slides, meta, top)


if __name__ == "__main__":
    main()
