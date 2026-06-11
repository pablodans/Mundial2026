#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construye el CUADRO de eliminacion oficial del Mundial 2026 (R32 -> Final) con el
ganador previsto de cada cruce segun el modelo, y lo escribe en
data/prediccion_bracket.json.

Como se decide cada cosa:
  - Posiciones de grupo (1.o / 2.o / 3.o): se ordenan los 4 equipos de cada grupo por
    los PUNTOS MEDIOS de grupo del Monte Carlo (data/prediccion_resultados.json), con el
    Elo como desempate. Los 8 mejores terceros salen de comparar los 12 terceros por esos
    mismos puntos medios.
  - Estructura del cuadro: el esqueleto OFICIAL de la R32 (las llaves 1E-3ABCDF, etc., tal
    como las publico la FIFA). Los terceros se asignan a sus huecos respetando los grupos
    elegibles de cada hueco (emparejamiento valido por backtracking).
  - Ganador de cada cruce: se simula el cruce K veces con modelo.ganador_eliminatoria
    (90' -> prorroga -> penales) y avanza el que gana la mayoria; se arrastra la fatiga
    ronda a ronda como en el motor. Se guarda la probabilidad del ganador previsto.

NOTA: es la prediccion A PRIORI (o condicionada a lo ya cargado en resultados_reales.json).
Es un cuadro "camino mas probable"; las probabilidades reales de cada equipo de llegar a
cada ronda estan en run_prediccion.py. El cuadro CAMBIA conforme se cargan resultados.

Uso: python scripts/predecir_bracket.py [--sims-cruce 4000] [--seed 2026]
"""
import argparse, json, os, random, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from mundial2026 import datos, elo_dinamico, montecarlo, modelo  # noqa: E402
from mundial2026.modelo import Parametros  # noqa: E402
from mundial2026.fatiga import nuevo_registro_fatiga, fatiga_tras_jugar  # noqa: E402

# Esqueleto oficial de la R32: 16 cruces en orden plano (mitad izquierda 8 + derecha 8).
# Cada hueco es ("1"|"2", grupo) o ("3", {grupos elegibles}).
SLOTS = [
    # --- Mitad izquierda ---
    [("1", "E"), ("3", {"A", "B", "C", "D", "F"})],
    [("1", "I"), ("3", {"C", "D", "F", "G", "H"})],
    [("2", "A"), ("2", "B")],
    [("1", "F"), ("2", "C")],
    [("2", "K"), ("2", "L")],
    [("1", "H"), ("2", "J")],
    [("1", "D"), ("3", {"B", "E", "F", "I", "J"})],
    [("1", "G"), ("3", {"A", "E", "H", "I", "J"})],
    # --- Mitad derecha ---
    [("1", "C"), ("2", "F")],
    [("2", "E"), ("2", "I")],
    [("1", "A"), ("3", {"C", "E", "F", "H", "I"})],
    [("1", "L"), ("3", {"E", "H", "I", "J", "K"})],
    [("1", "J"), ("2", "H")],
    [("2", "D"), ("2", "G")],
    [("1", "B"), ("3", {"E", "F", "G", "I", "J"})],
    [("1", "K"), ("3", {"D", "E", "I", "J", "L"})],
]
RONDAS = ["R32", "Octavos", "Cuartos", "Semifinal", "Final"]


def standings_desde_mc(ranking_mc):
    """De la salida del Monte Carlo: 1.o/2.o/3.o por grupo (orden por puntos medios, Elo
    de desempate) y los 8 mejores terceros."""
    por_grupo = {}
    for r in ranking_mc:
        por_grupo.setdefault(r["grupo"], []).append(r)
    primeros, segundos, terceros = {}, {}, {}
    candidatos_3 = []
    for g, equipos in por_grupo.items():
        ordenados = sorted(equipos, key=lambda r: (r["puntos_grupo_media"], r["elo"]), reverse=True)
        primeros[g] = ordenados[0]["pais"]
        segundos[g] = ordenados[1]["pais"]
        terceros[g] = ordenados[2]["pais"]
        candidatos_3.append((g, ordenados[2]["pais"], ordenados[2]["puntos_grupo_media"], ordenados[2]["elo"]))
    candidatos_3.sort(key=lambda x: (x[2], x[3]), reverse=True)
    grupos_3_clasifican = [g for g, _p, _pt, _e in candidatos_3[:8]]
    return primeros, segundos, terceros, grupos_3_clasifican


def asignar_terceros(grupos_3, slots):
    """Empareja cada grupo tercero clasificado a un hueco '3' cuyos grupos elegibles lo
    admitan (backtracking con heuristica MRV). Devuelve dict id_hueco -> grupo."""
    huecos = []  # (indice_slot, lado, set_elegible)
    for si, slot in enumerate(slots):
        for lado, (tipo, val) in enumerate(slot):
            if tipo == "3":
                huecos.append((si, lado, set(val)))
    grupos = list(grupos_3)
    asign = {}

    def backtrack(restantes_huecos, restantes_grupos):
        if not restantes_huecos:
            return True
        # MRV: el hueco con menos candidatos validos primero
        restantes_huecos.sort(key=lambda h: len(h[2] & set(restantes_grupos)))
        si, lado, elig = restantes_huecos[0]
        for g in list(restantes_grupos):
            if g in elig:
                asign[(si, lado)] = g
                if backtrack(restantes_huecos[1:], [x for x in restantes_grupos if x != g]):
                    return True
                del asign[(si, lado)]
        return False

    if not backtrack(list(huecos), grupos):
        raise SystemExit(f"No hay asignacion valida de terceros para {grupos}")
    return asign


def construir_orden_32(primeros, segundos, terceros, grupos_3, slots):
    asign_3 = asignar_terceros(grupos_3, slots)
    orden = []
    for si, slot in enumerate(slots):
        for lado, (tipo, val) in enumerate(slot):
            if tipo == "1":
                orden.append(primeros[val])
            elif tipo == "2":
                orden.append(segundos[val])
            else:
                g = asign_3[(si, lado)]
                orden.append(terceros[g])
    return orden  # 32 paises en orden de cruce


def predecir_cruces(orden32, sel, par, rng, sims_cruce):
    fatiga = nuevo_registro_fatiga(sel)
    ronda_actual = list(orden32)
    rounds = {}
    for ronda in RONDAS:
        cruces = []
        siguiente = []
        for i in range(0, len(ronda_actual), 2):
            a, b = ronda_actual[i], ronda_actual[i + 1]
            ganadores = Counter()
            prorrogas = 0
            for _ in range(sims_cruce):
                g, pr, _ = modelo.ganador_eliminatoria(
                    sel[a], sel[b], par, rng, fatiga_a=fatiga[a], fatiga_b=fatiga[b])
                ganadores[g] += 1
                prorrogas += 1 if pr else 0
            ganador = ganadores.most_common(1)[0][0]
            p = round(100 * ganadores[ganador] / sims_cruce, 1)
            cruces.append({"a": a, "b": b, "ganador": ganador, "p": p})
            fatiga[ganador] = fatiga_tras_jugar(fatiga[ganador], par,
                                                hubo_prorroga=(prorrogas > sims_cruce / 2))
            siguiente.append(ganador)
        rounds[ronda] = cruces
        ronda_actual = siguiente
    return rounds, ronda_actual[0]


def main():
    ap = argparse.ArgumentParser(description="Cuadro predicho del Mundial 2026")
    ap.add_argument("--sims-cruce", type=int, default=4000, help="sims por cruce (def. 4000)")
    ap.add_argument("--sims-grupos", type=int, default=20000, help="sims MC para standings si hace falta")
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()

    par = Parametros()
    sel = elo_dinamico.aplicar_a_selecciones(
        datos.cargar_selecciones(), datos.cargar_fixture(), datos.cargar_resultados_reales(), par)

    ruta_mc = datos.ruta("data", "prediccion_resultados.json")
    if os.path.exists(ruta_mc):
        ranking_mc = json.load(open(ruta_mc, encoding="utf-8"))["ranking"]
    else:
        ranking_mc = montecarlo.run(n=a.sims_grupos, seed=a.seed)["ranking"]

    primeros, segundos, terceros, grupos_3 = standings_desde_mc(ranking_mc)
    orden32 = construir_orden_32(primeros, segundos, terceros, grupos_3, SLOTS)

    rng = random.Random(a.seed)
    rounds, campeon = predecir_cruces(orden32, sel, par, rng, a.sims_cruce)

    reales = datos.cargar_resultados_reales()
    out = {
        "meta": {
            "descripcion": "Cuadro 'camino mas probable' R32->Final segun el modelo. "
                           "Cambia conforme se cargan resultados reales.",
            "sims_por_cruce": a.sims_cruce, "seed": a.seed,
            "partidos_reales_cargados": len(reales["fase_grupos"]),
            "terceros_clasifican_grupos": grupos_3,
        },
        "clasificados_orden": orden32,
        "rounds": rounds,
        "campeon": campeon,
    }
    json.dump(out, open(datos.ruta("data", "prediccion_bracket.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # Resumen por consola
    print(f"Cuadro predicho (seed {a.seed}, {a.sims_cruce} sims/cruce):\n")
    for ronda in RONDAS:
        print(f"== {ronda} ==")
        for c in rounds[ronda]:
            print(f"  {c['a']:20} vs {c['b']:20} -> {c['ganador']:20} ({c['p']}%)")
        print()
    print(f">>> CAMPEON PREVISTO: {campeon}")
    print("Guardado en data/prediccion_bracket.json")


if __name__ == "__main__":
    main()
