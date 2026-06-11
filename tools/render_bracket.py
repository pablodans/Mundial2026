#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renderiza data/prediccion_bracket.json como un cuadro de eliminacion PNG (paleta pastel)
para el README.  Uso: python tools/render_bracket.py"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import assets_lib as A  # noqa: E402

# ---------- paleta pastel ----------
BG0, BG1 = (244, 247, 252), (233, 238, 247)
BORDE = (208, 216, 230)
CAJA = (255, 255, 255)
TXT_PERDEDOR = (150, 159, 176)
WIN_FILL = (214, 236, 224)      # menta suave
WIN_BORDE = (143, 205, 176)
WIN_TXT = (28, 64, 48)
ORO_FILL = (247, 232, 176)
ORO_BORDE = (224, 197, 92)
ORO_TXT = (92, 74, 18)
CONECT = (197, 207, 224)
TITULO = (52, 60, 84)
SUB = (122, 132, 154)
HEADER = (108, 120, 146)

W, H = 1690, 1010
COL_W = 150
GAP = 34
X_LEFT = [30 + i * (COL_W + GAP) for i in range(4)]          # R32,Oct,QF,SF
X_CENTER = X_LEFT[3] + COL_W + GAP                            # final/campeon
X_RIGHT = [X_CENTER + COL_W + GAP + i * (COL_W + GAP) for i in range(4)]  # SF,QF,Oct,R32
TOP, BOT = 132, 980
BOXH = 30


def cargar():
    return json.load(open(os.path.join(ROOT, "data", "prediccion_bracket.json"), encoding="utf-8"))


def media(ys):
    return [(ys[i] + ys[i + 1]) / 2 for i in range(0, len(ys), 2)]


def caja(draw, x, y, nombre, ganador, p=None, oro=False):
    es_ganador = oro or (ganador is not None and nombre == ganador)
    if oro:
        fill, borde, txt = ORO_FILL, ORO_BORDE, ORO_TXT
    elif es_ganador:
        fill, borde, txt = WIN_FILL, WIN_BORDE, WIN_TXT
    else:
        fill, borde, txt = CAJA, BORDE, TXT_PERDEDOR
    A.rrect(draw, x, y - BOXH / 2, COL_W, BOXH, 7, fill=fill, outline=borde, width=1.4)
    kind = "bold" if es_ganador else "reg"
    A.texto_ajustado(draw, x + COL_W / 2 - (9 if (p is not None and es_ganador) else 0),
                     y, nombre, kind, 12.5, txt, COL_W - 16)
    if p is not None and es_ganador:
        A.texto(draw, x + COL_W - 7, y, f"{p:.0f}", A.font("sb", 9.5), borde, anchor="rm")


def conector(draw, x0, y_top, y_bot, x1, y_mid):
    """Une dos cajas (en x0, alturas y_top/y_bot) con la caja siguiente (x1, y_mid)."""
    xm = x0 + COL_W + GAP / 2
    A.linea(draw, [(x0 + COL_W, y_top), (xm, y_top)], CONECT, 1.6)
    A.linea(draw, [(x0 + COL_W, y_bot), (xm, y_bot)], CONECT, 1.6)
    A.linea(draw, [(xm, y_top), (xm, y_bot)], CONECT, 1.6)
    A.linea(draw, [(xm, y_mid), (x1, y_mid)], CONECT, 1.6)


def lado(draw, data, ganadores_por_ronda, izquierda=True):
    # Columnas: izquierda R32->SF de fuera hacia el centro; derecha en espejo
    # (R32 al extremo derecho, SF junto al centro).
    xs = X_LEFT if izquierda else list(reversed(X_RIGHT))
    # idx base en cada ronda para este lado
    base = {"R32": 0, "Octavos": 0, "Cuartos": 0, "Semifinal": 0} if izquierda \
        else {"R32": 8, "Octavos": 4, "Cuartos": 2, "Semifinal": 1}
    # alturas R32: 16 cajas
    step = (BOT - TOP) / 16
    yR32 = [TOP + (i + 0.5) * step for i in range(16)]
    yOct = media(yR32)
    yQF = media(yOct)
    ySF = media(yQF)
    cols_y = [yR32, yOct, yQF, ySF]
    rondas = ["R32", "Octavos", "Cuartos", "Semifinal"]
    # participantes por columna: R32 = clasificados del lado; resto = ganadores ronda previa
    parts = []
    orden = data["clasificados_orden"]
    parts.append(orden[0:16] if izquierda else orden[16:32])
    for rd in ["R32", "Octavos", "Cuartos"]:
        crs = data["rounds"][rd]
        if izquierda:
            crs = crs[:len(crs) // 2]
        else:
            crs = crs[len(crs) // 2:]
        parts.append([c["ganador"] for c in crs])

    for ci, (xcol, ys, participantes) in enumerate(zip(xs, cols_y, parts)):
        rd = rondas[ci]
        crs_rd = data["rounds"][rd]
        # cruces de este lado y ronda
        if izquierda:
            crs_lado = crs_rd[:len(crs_rd) // 2]
        else:
            crs_lado = crs_rd[len(crs_rd) // 2:]
        for bi, nombre in enumerate(participantes):
            cruce = crs_lado[bi // 2]
            x = xcol
            caja(draw, x, ys[bi], nombre, cruce["ganador"], p=cruce.get("p"))
        # conectores hacia la columna siguiente (si existe)
        if ci < 3:
            y_next = cols_y[ci + 1]
            for j in range(len(y_next)):
                if izquierda:
                    conector(draw, xcol, ys[2 * j], ys[2 * j + 1], xs[ci + 1], y_next[j])
                else:
                    # dibujar de derecha a izquierda (espejo)
                    xm = xcol - GAP / 2
                    A.linea(draw, [(xcol, ys[2 * j]), (xm, ys[2 * j])], CONECT, 1.6)
                    A.linea(draw, [(xcol, ys[2 * j + 1]), (xm, ys[2 * j + 1])], CONECT, 1.6)
                    A.linea(draw, [(xm, ys[2 * j]), (xm, ys[2 * j + 1])], CONECT, 1.6)
                    A.linea(draw, [(xm, y_next[j]), (xs[ci + 1] + COL_W, y_next[j])], CONECT, 1.6)
    return ySF[0]


def main():
    data = cargar()
    img, d = A.lienzo(W, H, BG0)
    A.gradiente_vertical(d, W, H, BG0, BG1)

    # Titulo
    A.texto(d, W / 2, 40, "MUNDIAL 2026 — CUADRO PREVISTO", A.font("bold", 30), TITULO, anchor="mm")
    n_reales = data["meta"].get("partidos_reales_cargados", 0)
    sub = ("Camino más probable según el modelo (Elo + altitud + desgaste + presión, Monte Carlo). "
           + (f"Condicionado a {n_reales} partido(s) jugado(s)." if n_reales
              else "Predicción a priori — antes de arrancar el torneo."))
    A.texto(d, W / 2, 70, sub, A.font("reg", 13.5), SUB, anchor="mm")
    A.texto(d, W / 2, 90, "Se recalcula ronda a ronda conforme se cargan resultados reales.",
            A.font("reg", 12), SUB, anchor="mm")

    # Headers de columna
    labels_izq = ["32avos", "Octavos", "Cuartos", "Semis"]
    for x, lab in zip(X_LEFT, labels_izq):
        A.texto(d, x + COL_W / 2, 116, lab, A.font("sb", 12), HEADER, anchor="mm")
    for x, lab in zip(X_RIGHT, list(reversed(labels_izq))):
        A.texto(d, x + COL_W / 2, 116, lab, A.font("sb", 12), HEADER, anchor="mm")
    A.texto(d, X_CENTER + COL_W / 2, 116, "FINAL", A.font("bold", 12.5), ORO_BORDE, anchor="mm")

    ysf_izq = lado(d, data, None, izquierda=True)
    ysf_der = lado(d, data, None, izquierda=False)

    # Finalistas (ganadores de semifinal) en la columna central + campeon arriba
    semis = data["rounds"]["Semifinal"]
    final = data["rounds"]["Final"][0]
    fin_izq, fin_der = semis[0]["ganador"], semis[1]["ganador"]
    yc = (ysf_izq + ysf_der) / 2
    cxc = X_CENTER + COL_W / 2
    # conectores semifinal -> finalista
    A.linea(d, [(X_LEFT[3] + COL_W, ysf_izq), (X_CENTER, yc - 55)], CONECT, 1.6)
    A.linea(d, [(X_RIGHT[0], ysf_der), (X_CENTER + COL_W, yc + 55)], CONECT, 1.6)
    # cajas finalistas (el ganador de la final queda resaltado)
    caja(d, X_CENTER, yc - 55, fin_izq, final["ganador"], p=final.get("p"))
    caja(d, X_CENTER, yc + 55, fin_der, final["ganador"], p=final.get("p"))

    # Caja campeon (oro) grande, arriba al centro, con tallo hasta el finalista ganador
    camp = data["campeon"]
    cw, ch = 248, 66
    cyy = 232
    y_fin_ganador = (yc - 55) if final["ganador"] == fin_izq else (yc + 55)
    A.linea(d, [(cxc, cyy + ch / 2), (cxc, y_fin_ganador - BOXH / 2)], ORO_BORDE, 1.8)
    A.rrect(d, cxc - cw / 2, cyy - ch / 2, cw, ch, 15, fill=ORO_FILL, outline=ORO_BORDE, width=2.4)
    A.texto(d, cxc, cyy - 15, "CAMPEÓN", A.font("sb", 12.5), ORO_TXT, anchor="mm")
    A.texto_ajustado(d, cxc, cyy + 12, camp, "bold", 25, ORO_TXT, cw - 26)

    # nota pie
    A.texto(d, W / 2, H - 16,
            "Generado por scripts/predecir_bracket.py + tools/render_bracket.py · "
            "el % es la probabilidad del modelo de que ese equipo gane el cruce",
            A.font("reg", 11), SUB, anchor="mm")

    ruta = os.path.join(ROOT, "docs", "bracket_prediccion.png")
    A.finalizar(img, W, H, ruta)
    print("Imagen ->", ruta)


if __name__ == "__main__":
    main()
