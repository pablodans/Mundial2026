# -*- coding: utf-8 -*-
"""
Simulacion de un Mundial completo: fase de grupos -> eliminacion directa.

Ambas fases se CONDICIONAN a los resultados reales que se hayan cargado:
  - Fase de grupos: si un partido (por su id de fixture) ya tiene marcador real,
    se usa ese marcador en vez de simularlo.
  - Eliminacion: si 'bracket_r32' fija el cuadro oficial, se usa; si no, se sortea
    al azar entre los 32 clasificados (marginaliza la incertidumbre del emparejamiento).
    Cruces ya jugados (por clave "Ronda-indice") usan su ganador real.

El desgaste (fatiga) y la presion ("ganar si o si" en la 3a jornada) ajustan el Elo
efectivo partido a partido (ver modelo.py).
"""
from collections import defaultdict

from . import modelo
from .fatiga import fatiga_tras_jugar, nuevo_registro_fatiga

RONDAS = ["R32", "Octavos", "Cuartos", "Semifinal", "Final"]
# Umbral de puntos tras 2 jornadas por debajo del cual un equipo juega la 3a "a ganar o nada".
PRESION_UMBRAL_PTS = 3


def _orden_clasificacion(puntos, gf, gc, rng):
    # (pts, dif de goles, goles a favor, azar) -> mayor es mejor
    return (puntos, gf - gc, gf, rng.random())


def simular_grupos(sel, fixture, par, rng, resultados_reales):
    """Devuelve (clasificados[32], puntos_por_equipo, fatiga, set_mejores_terceros)."""
    reales = resultados_reales.get("fase_grupos", {})
    tabla = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))  # grupo -> equipo -> [pts, gf, gc]
    equipos_grupo = defaultdict(set)
    fatiga = nuevo_registro_fatiga(sel)

    partidos = fixture["fase_grupos"]
    for jornada in (1, 2, 3):
        jugaron = set()
        for m in [x for x in partidos if x["jornada"] == jornada]:
            g, a, b = m["grupo"], m["local"], m["visitante"]
            equipos_grupo[g].add(a)
            equipos_grupo[g].add(b)

            # Presion solo en la ultima jornada y solo para quien no esta comodo.
            presion_a = presion_b = False
            if jornada == 3:
                presion_a = tabla[g][a][0] <= PRESION_UMBRAL_PTS
                presion_b = tabla[g][b][0] <= PRESION_UMBRAL_PTS

            if m["id"] in reales:
                ga = reales[m["id"]]["local_goles"]
                gb = reales[m["id"]]["visitante_goles"]
            else:
                ga, gb = modelo.jugar_partido(
                    sel[a], sel[b], par, rng,
                    altitud_m=m["altitud_m"], pais_sede=m["pais_sede"],
                    fatiga_a=fatiga[a], fatiga_b=fatiga[b],
                    presion_a=presion_a, presion_b=presion_b)

            tabla[g][a][1] += ga; tabla[g][a][2] += gb
            tabla[g][b][1] += gb; tabla[g][b][2] += ga
            if ga > gb:
                tabla[g][a][0] += 3
            elif gb > ga:
                tabla[g][b][0] += 3
            else:
                tabla[g][a][0] += 1; tabla[g][b][0] += 1
            jugaron.add(a); jugaron.add(b)

        # Desgaste tras la jornada (sin prorrogas en fase de grupos)
        for eq in jugaron:
            fatiga[eq] = fatiga_tras_jugar(fatiga[eq], par)

    # Clasificacion por grupo
    primeros, segundos, terceros = [], [], []
    puntos = {}
    for g in sorted(equipos_grupo):
        eq = sorted(equipos_grupo[g])  # orden determinista antes del azar (reproducibilidad)
        clas = sorted(eq, key=lambda t: _orden_clasificacion(*tabla[g][t], rng), reverse=True)
        primeros.append(clas[0])
        segundos.append(clas[1])
        terceros.append((clas[2], tabla[g][clas[2]]))
        for t in eq:
            puntos[t] = tabla[g][t][0]

    # 8 mejores terceros
    terceros.sort(key=lambda x: _orden_clasificacion(*x[1], rng), reverse=True)
    mejores_terceros = [t for t, _ in terceros[:8]]
    clasificados = primeros + segundos + mejores_terceros  # 12 + 12 + 8 = 32
    return clasificados, puntos, fatiga, set(mejores_terceros)


def simular_eliminatoria(sel, clasificados, par, rng, fatiga, resultados_reales):
    """Devuelve (campeon, finalistas, alcanzaron) donde alcanzaron[ronda] = set de equipos."""
    bracket_oficial = resultados_reales.get("bracket_r32", [])
    elim_reales = resultados_reales.get("eliminatorias", {})

    if len(bracket_oficial) == 32:
        ronda_actual = list(bracket_oficial)
    else:
        ronda_actual = list(clasificados)
        rng.shuffle(ronda_actual)  # sorteo del cuadro

    alcanzaron = {r: set() for r in RONDAS}
    finalistas = []
    for ronda in RONDAS:
        for t in ronda_actual:
            alcanzaron[ronda].add(t)
        siguiente = []
        for i in range(0, len(ronda_actual), 2):
            a, b = ronda_actual[i], ronda_actual[i + 1]
            clave = f"{ronda}-{i // 2}"
            if clave in elim_reales and elim_reales[clave].get("ganador"):
                ganador = elim_reales[clave]["ganador"]
                prorroga = bool(elim_reales[clave].get("prorroga", False))
            else:
                ganador, prorroga, _ = modelo.ganador_eliminatoria(
                    sel[a], sel[b], par, rng,
                    fatiga_a=fatiga[a], fatiga_b=fatiga[b])
            perdedor = b if ganador == a else a
            # Desgaste: el ganador sigue (mas carga si hubo prorroga); el perdedor ya no juega.
            fatiga[ganador] = fatiga_tras_jugar(fatiga[ganador], par, hubo_prorroga=prorroga)
            siguiente.append(ganador)
        if ronda == "Semifinal":
            finalistas = list(siguiente)
        ronda_actual = siguiente

    campeon = ronda_actual[0]
    return campeon, finalistas, alcanzaron


def simular_mundial(sel, fixture, par, rng, resultados_reales):
    clasificados, puntos, fatiga, mejores_terceros = simular_grupos(
        sel, fixture, par, rng, resultados_reales)
    campeon, finalistas, alcanzaron = simular_eliminatoria(
        sel, clasificados, par, rng, fatiga, resultados_reales)
    return {
        "clasificados": clasificados,
        "puntos": puntos,
        "mejores_terceros": mejores_terceros,
        "campeon": campeon,
        "finalistas": finalistas,
        "alcanzaron": alcanzaron,
    }
