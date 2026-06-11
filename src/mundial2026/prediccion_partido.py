# -*- coding: utf-8 -*-
"""
Prediccion de UN partido: distribucion exacta del marcador (sin simular).

A partir de las medias de gol de Poisson (las mismas lambdas que usa el motor, con todos
los ajustes de contexto: Elo efectivo, altitud, localia, fatiga, presion, estilo) se
calcula analiticamente la matriz de probabilidades de marcador y de ahi:
  - 1X2 (prob. de victoria local / empate / victoria visitante)
  - marcador mas probable y top-5 marcadores
  - over/under 2.5 goles y goles esperados de cada equipo

Opcionalmente aplica la correccion de Dixon-Coles (par.DC_RHO != 0) sobre los marcadores
bajos (0-0, 1-0, 0-1, 1-1), que el Poisson independiente no captura del todo.
"""
import math
from . import modelo


def _pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def lambdas_partido(eq_a, eq_b, par, *, altitud_m=0.0, pais_sede=None,
                    fatiga_a=0.0, fatiga_b=0.0, presion_a=False, presion_b=False,
                    factor_goles=1.0):
    """Medias de gol esperadas de cada equipo en el contexto dado (sin samplear)."""
    ea = modelo.elo_efectivo(eq_a, par, altitud_m=altitud_m, pais_sede=pais_sede,
                             fatiga=fatiga_a, presion=presion_a)
    eb = modelo.elo_efectivo(eq_b, par, altitud_m=altitud_m, pais_sede=pais_sede,
                             fatiga=fatiga_b, presion=presion_b)
    apertura = modelo.apertura_estilo(eq_a, eq_b, par)
    if presion_a or presion_b:
        apertura += par.PRESION_APERTURA
    return modelo.lambdas(ea, eb, par, apertura=apertura, factor_goles=factor_goles)


def predecir(eq_a, eq_b, par, *, altitud_m=0.0, pais_sede=None,
             fatiga_a=0.0, fatiga_b=0.0, presion_a=False, presion_b=False,
             factor_goles=1.0, maxg=10):
    la, lb = lambdas_partido(eq_a, eq_b, par, altitud_m=altitud_m, pais_sede=pais_sede,
                             fatiga_a=fatiga_a, fatiga_b=fatiga_b,
                             presion_a=presion_a, presion_b=presion_b, factor_goles=factor_goles)
    # Matriz de probabilidad de marcador con (opcional) correccion Dixon-Coles
    pa = [_pmf(i, la) for i in range(maxg + 1)]
    pb = [_pmf(j, lb) for j in range(maxg + 1)]
    matriz = {}
    total = 0.0
    for i in range(maxg + 1):
        for j in range(maxg + 1):
            p = pa[i] * pb[j] * modelo.tau_dixon_coles(i, j, la, lb, par.DC_RHO)
            matriz[(i, j)] = p
            total += p
    for k in matriz:
        matriz[k] /= total  # renormaliza (cola truncada + Dixon-Coles)

    p_local = sum(p for (i, j), p in matriz.items() if i > j)
    p_empate = sum(p for (i, j), p in matriz.items() if i == j)
    p_visit = sum(p for (i, j), p in matriz.items() if i < j)
    p_over = sum(p for (i, j), p in matriz.items() if i + j >= 3)
    top = sorted(matriz.items(), key=lambda kv: -kv[1])[:5]

    return {
        "equipo_a": eq_a["pais"], "equipo_b": eq_b["pais"],
        "lambda_a": round(la, 2), "lambda_b": round(lb, 2),
        "p_gana_a": round(100 * p_local, 1),
        "p_empate": round(100 * p_empate, 1),
        "p_gana_b": round(100 * p_visit, 1),
        "marcador_probable": {"a": top[0][0][0], "b": top[0][0][1],
                              "prob": round(100 * top[0][1], 1)},
        "top_marcadores": [{"a": i, "b": j, "prob": round(100 * p, 1)} for (i, j), p in top],
        "p_over_2_5": round(100 * p_over, 1),
        "p_under_2_5": round(100 * (1 - p_over), 1),
        "goles_esperados_a": round(la, 2),
        "goles_esperados_b": round(lb, 2),
    }
