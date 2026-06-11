# -*- coding: utf-8 -*-
"""
Monte Carlo: corre N mundiales completos y agrega.

  - Campeon -> MODA (variable categorica): el campeon mas frecuente (con empates de moda).
  - Avanza/Octavos/Cuartos/Semis/Final/Titulo -> FRECUENCIA relativa (= probabilidad).
  - Puntos de grupo -> MEDIA.

Reproducible: misma semilla + mismos datos -> mismos numeros.
"""
import random
from collections import Counter, defaultdict

from . import datos, elo_dinamico, torneo
from .modelo import Parametros


def run(n=10000, seed=2026, par=None, selecciones=None, fixture=None, resultados_reales=None):
    par = par or Parametros()
    sel = selecciones or datos.cargar_selecciones()
    fixture = fixture or datos.cargar_fixture()
    resultados_reales = resultados_reales if resultados_reales is not None else datos.cargar_resultados_reales()
    # Elo dinamico: los resultados ya jugados mueven el Elo de cada equipo, de modo que los
    # partidos pendientes se simulan con el Elo "vivo" (mejora la prediccion de jornadas 2, 3...).
    sel = elo_dinamico.aplicar_a_selecciones(sel, fixture, resultados_reales, par)
    rng = random.Random(seed)

    cont = {k: Counter() for k in ("avanza", "octavos", "cuartos", "semis", "final", "campeon")}
    puntos_sum = defaultdict(float)

    for _ in range(n):
        r = torneo.simular_mundial(sel, fixture, par, rng, resultados_reales)
        for t in r["clasificados"]:
            cont["avanza"][t] += 1
        for t in r["alcanzaron"]["Octavos"]:
            cont["octavos"][t] += 1
        for t in r["alcanzaron"]["Cuartos"]:
            cont["cuartos"][t] += 1
        for t in r["alcanzaron"]["Semifinal"]:
            cont["semis"][t] += 1
        for t in r["alcanzaron"]["Final"]:
            cont["final"][t] += 1
        cont["campeon"][r["campeon"]] += 1
        for t, pp in r["puntos"].items():
            puntos_sum[t] += pp

    ranking = []
    for t in sel:
        ranking.append({
            "pais": t,
            "grupo": sel[t]["grupo"],
            "elo": round(sel[t]["elo"], 0),
            "p_avanza": round(100 * cont["avanza"][t] / n, 1),
            "p_octavos": round(100 * cont["octavos"][t] / n, 1),
            "p_cuartos": round(100 * cont["cuartos"][t] / n, 1),
            "p_semis": round(100 * cont["semis"][t] / n, 1),
            "p_final": round(100 * cont["final"][t] / n, 1),
            "p_titulo": round(100 * cont["campeon"][t] / n, 1),
            "puntos_grupo_media": round(puntos_sum[t] / n, 2),
        })
    ranking.sort(key=lambda r: (-r["p_titulo"], -r["p_final"], -r["p_semis"]))

    freq_moda = cont["campeon"].most_common(1)[0][1]
    co_modas = sorted([c for c, f in cont["campeon"].items() if f == freq_moda])

    return {
        "n": n,
        "seed": seed,
        "ranking": ranking,
        "campeon_moda": {"paises": co_modas, "frecuencia": freq_moda,
                         "porcentaje": round(100 * freq_moda / n, 1)},
        "distribucion_campeon": dict(cont["campeon"].most_common()),
    }
