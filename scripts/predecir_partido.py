#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prediccion detallada de UN partido o de una JORNADA completa, con el Elo dinamico ya
actualizado por los resultados reales cargados (data/resultados_reales.json).

Uso:
  python scripts/predecir_partido.py id A1B            # un partido del fixture por su id
  python scripts/predecir_partido.py vs Espana Uruguay # dos equipos (contexto neutral)
  python scripts/predecir_partido.py jornada 1         # todos los partidos pendientes de la jornada 1

El flujo previsto: predecir la jornada 1, cargar sus resultados con actualizar_resultados.py,
y volver a predecir la jornada 2 -> el Elo se habra movido con lo ocurrido.
"""
import argparse, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from mundial2026 import datos, elo_dinamico, prediccion_partido  # noqa: E402
from mundial2026.modelo import Parametros  # noqa: E402

PRESION_UMBRAL_PTS = 3  # mismo criterio que el motor


def _imprimir(pred, sede=None, altitud=None):
    a, b = pred["equipo_a"], pred["equipo_b"]
    ctx = f"  [{sede}, {altitud} m]" if sede else ""
    print(f"\n{a}  vs  {b}{ctx}")
    print(f"  Goles esperados: {a} {pred['lambda_a']} - {pred['lambda_b']} {b}")
    print(f"  1X2:  gana {a} {pred['p_gana_a']}%   |   empate {pred['p_empate']}%   "
          f"|   gana {b} {pred['p_gana_b']}%")
    mp = pred["marcador_probable"]
    print(f"  Marcador mas probable: {mp['a']}-{mp['b']} ({mp['prob']}%)")
    tops = "  ".join(f"{m['a']}-{m['b']}:{m['prob']}%" for m in pred["top_marcadores"])
    print(f"  Top marcadores: {tops}")
    print(f"  Over 2.5: {pred['p_over_2_5']}%   Under 2.5: {pred['p_under_2_5']}%")


def _elo_vivo(par):
    sel = datos.cargar_selecciones()
    fixture = datos.cargar_fixture()
    reales = datos.cargar_resultados_reales()
    sel = elo_dinamico.aplicar_a_selecciones(sel, fixture, reales, par)
    return sel, fixture, reales


def main():
    ap = argparse.ArgumentParser(description="Prediccion por partido (Mundial 2026)")
    ap.add_argument("modo", choices=["id", "vs", "jornada"])
    ap.add_argument("args", nargs="+")
    a = ap.parse_args()
    par = Parametros()
    sel, fixture, reales = _elo_vivo(par)

    if a.modo == "vs":
        x, y = a.args[0], a.args[1]
        if x not in sel or y not in sel:
            raise SystemExit(f"Equipo desconocido. Ej validos: {', '.join(list(sel)[:6])} ...")
        _imprimir(prediccion_partido.predecir(sel[x], sel[y], par))
        return

    by_id = {m["id"]: m for m in fixture["fase_grupos"]}
    if a.modo == "id":
        pid = a.args[0]
        if pid not in by_id:
            raise SystemExit(f"id desconocido: {pid} (usa actualizar_resultados.py listar)")
        partidos = [by_id[pid]]
    else:  # jornada
        j = int(a.args[0])
        partidos = [m for m in fixture["fase_grupos"] if m["jornada"] == j]

    # Para la presion en jornada 3 necesitariamos la tabla; aqui la aproximamos como False
    # (el Monte Carlo si la modela). Mostramos solo partidos aun no jugados.
    mostrados = 0
    for m in partidos:
        if m["id"] in reales["fase_grupos"]:
            continue
        pred = prediccion_partido.predecir(
            sel[m["local"]], sel[m["visitante"]], par,
            altitud_m=m["altitud_m"], pais_sede=m["pais_sede"])
        _imprimir(pred, sede=m["sede"], altitud=m["altitud_m"])
        mostrados += 1
    if mostrados == 0:
        print("No hay partidos pendientes que predecir en esa seleccion.")


if __name__ == "__main__":
    main()
