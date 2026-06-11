# -*- coding: utf-8 -*-
"""Carga de datos del proyecto (selecciones, sedes, fixture, jugadores, resultados reales)."""
import csv, json, os

# Raiz del proyecto = dos niveles por encima de este archivo (src/mundial2026/datos.py)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ruta(*partes):
    return os.path.join(ROOT, *partes)


_ESTILO_DEFAULT = {"posesion": 50, "estilo": "mixto", "tendencia": "equilibrado", "ritmo": "medio"}


def cargar_selecciones():
    """Devuelve {pais: dict} con campos numericos convertidos y el estilo de juego fusionado."""
    sel = {}
    enteros = ("fifa_rank", "titulos", "participaciones", "finales",
               "semifinales", "altitud_casa_m")
    flotantes = ("fifa_puntos", "elo", "valor_mercado_meur")
    with open(ruta("data", "selecciones.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for c in enteros:
                r[c] = int(r[c])
            for c in flotantes:
                r[c] = float(r[c])
            sel[r["pais"]] = r
    estilos = cargar_estilos()
    for pais, t in sel.items():
        t.update(estilos.get(pais, _ESTILO_DEFAULT))
    return sel


def cargar_estilos():
    p = ruta("data", "estilos.json")
    if not os.path.exists(p):
        return {}
    return json.load(open(p, encoding="utf-8"))["estilos"]


def cargar_sedes():
    return json.load(open(ruta("data", "sedes.json"), encoding="utf-8"))["sedes"]


def cargar_fixture():
    return json.load(open(ruta("data", "fixture_completo.json"), encoding="utf-8"))


def cargar_jugadores():
    return json.load(open(ruta("data", "jugadores.json"), encoding="utf-8"))["jugadores"]


def cargar_resultados_reales():
    """Resultados ya jugados. Tolerante: si no existe, devuelve estructura vacia."""
    p = ruta("data", "resultados_reales.json")
    if not os.path.exists(p):
        return {"fase_grupos": {}, "bracket_r32": [], "eliminatorias": {}}
    d = json.load(open(p, encoding="utf-8"))
    d.setdefault("fase_grupos", {})
    d.setdefault("bracket_r32", [])
    d.setdefault("eliminatorias", {})
    # Descarta claves de documentacion (empiezan por '_')
    d["fase_grupos"] = {k: v for k, v in d["fase_grupos"].items() if not k.startswith("_")}
    d["eliminatorias"] = {k: v for k, v in d["eliminatorias"].items() if not k.startswith("_")}
    return d


ANFITRIONES = {"Mexico", "Estados Unidos", "Canada"}
