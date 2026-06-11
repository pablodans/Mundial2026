#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monte Carlo por partido de una jornada: tira cada partido N veces con jugar_partido()
(el mismo motor que el torneo) y tabula 1X2, goles medios y marcador modal.

Uso: python scripts/mc_jornada.py [jornada] [--sims N] [--seed S]
Sirve para contrastar la simulacion contra el predictor analitico (predecir_partido.py)."""
import argparse, os, random, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from mundial2026 import datos, elo_dinamico, modelo  # noqa: E402
from mundial2026.modelo import Parametros  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jornada", nargs="?", type=int, default=1)
    ap.add_argument("--sims", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()

    par = Parametros()
    sel = datos.cargar_selecciones()
    fixture = datos.cargar_fixture()
    reales = datos.cargar_resultados_reales()
    sel = elo_dinamico.aplicar_a_selecciones(sel, fixture, reales, par)
    rng = random.Random(a.seed)

    partidos = [m for m in fixture["fase_grupos"] if m["jornada"] == a.jornada
                and m["id"] not in reales["fase_grupos"]]
    print(f"Monte Carlo jornada {a.jornada}  ({a.sims} sims/partido, seed {a.seed})\n")
    for m in partidos:
        a_eq, b_eq = sel[m["local"]], sel[m["visitante"]]
        w = d = l = 0
        ga_tot = gb_tot = 0
        marcadores = Counter()
        for _ in range(a.sims):
            ga, gb = modelo.jugar_partido(a_eq, b_eq, par, rng,
                                          altitud_m=m["altitud_m"], pais_sede=m["pais_sede"])
            ga_tot += ga; gb_tot += gb
            marcadores[(ga, gb)] += 1
            if ga > gb: w += 1
            elif ga < gb: l += 1
            else: d += 1
        n = a.sims
        (mga, mgb), cnt = marcadores.most_common(1)[0]
        print(f"{m['local']} vs {m['visitante']}  [{m['sede']}, {m['altitud_m']} m]")
        print(f"  Goles medios: {ga_tot/n:.2f} - {gb_tot/n:.2f}   "
              f"1X2: {100*w/n:.1f} / {100*d/n:.1f} / {100*l/n:.1f}   "
              f"modal: {mga}-{mgb} ({100*cnt/n:.1f}%)")


if __name__ == "__main__":
    main()
