# -*- coding: utf-8 -*-
"""
Elo dinamico: actualiza el Elo de cada seleccion con cada resultado real ya jugado,
usando la formula de World Football Elo Ratings (eloratings.net).

Asi, conforme se cargan resultados (data/resultados_reales.json), el Elo "vivo" de cada
equipo se mueve segun rindio mejor o peor de lo esperado, y las predicciones de los
partidos siguientes (jornada 2, 3, eliminatorias) usan ese Elo actualizado. Es el bucle
"el resultado del partido 1 mejora la prediccion del partido 2".

Formula:
    We = 1 / (10^(-dr/400) + 1)         dr = Elo_a - Elo_b (con localia/altitud del partido)
    W  = 1 (victoria) / 0.5 (empate) / 0 (derrota)
    G  = factor de margen de goles (1, 1.5, o (11+dif)/8 si dif>=3)
    Elo'_a = Elo_a + K * G * (W - We);   Elo'_b = Elo_b - mismo delta (suma cero)
"""
from . import modelo


def _factor_goles(dif):
    if dif <= 1:
        return 1.0
    if dif == 2:
        return 1.5
    return (11 + dif) / 8.0


def _we(elo_a, elo_b):
    return 1.0 / (10 ** (-(elo_a - elo_b) / 400.0) + 1.0)


def _k_efectivo(par, n_partidos):
    """K adaptativo: decrece con los partidos ya jugados por el equipo en el torneo."""
    return par.K_MUNDIAL / (1.0 + par.K_ADAPT_TASA * n_partidos)


def _aplicar(elo, a, b, ga, gb, par, jugados, altitud_m=0.0, pais_sede=None):
    """Actualiza in-place `elo` tras un partido a(ga)-b(gb). `jugados` cuenta partidos previos
    por equipo (para el K adaptativo). Cada equipo ajusta con SU propio K (no es suma cero
    salvo cuando ambos llevan los mismos partidos, p.ej. la 1a jornada)."""
    ea = elo[a] + _ventaja_contexto(a, b, altitud_m, pais_sede, par, elo)
    eb = elo[b] + _ventaja_contexto(b, a, altitud_m, pais_sede, par, elo)
    we_a = _we(ea, eb)
    w_a = 1.0 if ga > gb else (0.5 if ga == gb else 0.0)
    g = _factor_goles(abs(ga - gb))
    ka = _k_efectivo(par, jugados.get(a, 0))
    kb = _k_efectivo(par, jugados.get(b, 0))
    elo[a] += ka * g * (w_a - we_a)
    elo[b] += kb * g * ((1.0 - w_a) - (1.0 - we_a))
    jugados[a] = jugados.get(a, 0) + 1
    jugados[b] = jugados.get(b, 0) + 1


def _ventaja_contexto(equipo, rival, altitud_m, pais_sede, par, elo):
    """Ajuste de localia + altitud para el equipo (puntos Elo) en el resultado esperado."""
    # Reusa la logica de modelo pero solo localia y altitud (no fatiga/presion).
    ajuste = 0.0
    if pais_sede is not None and equipo in modelo._ANFITRIONES \
            and pais_sede == modelo._PAIS_SEDE_DE.get(equipo):
        ajuste += par.VENTAJA_LOCALIA
    return ajuste  # la penalizacion por altitud se aplica via elo_efectivo en la prediccion;
    # para We mantenemos solo localia (la altitud afecta el juego, no la "expectativa" pura).


def elo_actualizado(sel, fixture, resultados_reales, par=None):
    """Devuelve {pais: elo_vivo} partiendo del Elo base y aplicando los resultados ya jugados
    en orden cronologico (fase de grupos por jornada; luego eliminatorias si estan cargadas)."""
    par = par or modelo.Parametros()
    elo = {p: sel[p]["elo"] for p in sel}
    reales = resultados_reales.get("fase_grupos", {})
    if not reales:
        return elo
    # Indexar partidos del fixture por id para conocer sede/altitud/equipos
    by_id = {m["id"]: m for m in fixture["fase_grupos"]}
    partidos_jugados = [by_id[pid] for pid in reales if pid in by_id]
    # Orden cronologico: jornada y luego id (estable)
    partidos_jugados.sort(key=lambda m: (m["jornada"], m["id"]))
    conteo = {}  # partidos ya procesados por equipo (para el K adaptativo)
    for m in partidos_jugados:
        r = reales[m["id"]]
        _aplicar(elo, m["local"], m["visitante"],
                 r["local_goles"], r["visitante_goles"], par, conteo,
                 altitud_m=m["altitud_m"], pais_sede=m["pais_sede"])
    return elo


def aplicar_a_selecciones(sel, fixture, resultados_reales, par=None):
    """Devuelve una copia de `sel` con el campo 'elo' reemplazado por el Elo vivo."""
    elo = elo_actualizado(sel, fixture, resultados_reales, par)
    nuevo = {}
    for p, t in sel.items():
        copia = dict(t)
        copia["elo_base"] = t["elo"]
        copia["elo"] = elo[p]
        nuevo[p] = copia
    return nuevo
