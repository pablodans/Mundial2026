#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecuta la prediccion Monte Carlo del Mundial 2026 y escribe:
  - data/prediccion_resultados.json   (ranking completo + distribucion del campeon)
  - docs/prediccion_resultados.md      (resumen legible)

Uso:
  python scripts/run_prediccion.py                 # 10.000 simulaciones, semilla 2026
  python scripts/run_prediccion.py --sims 50000    # mas simulaciones (mas estable)
  python scripts/run_prediccion.py --seed 7        # otra semilla
  python scripts/run_prediccion.py --top 24        # filas mostradas en consola/markdown
"""
import argparse, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from mundial2026 import datos, montecarlo  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Predictor Monte Carlo del Mundial 2026")
    ap.add_argument("--sims", type=int, default=10000, help="numero de simulaciones (def. 10000)")
    ap.add_argument("--seed", type=int, default=2026, help="semilla (def. 2026)")
    ap.add_argument("--top", type=int, default=24, help="filas a mostrar (def. 24)")
    args = ap.parse_args()

    res = montecarlo.run(n=args.sims, seed=args.seed)
    ranking = res["ranking"]
    n = res["n"]
    moda = res["campeon_moda"]

    reales = datos.cargar_resultados_reales()
    n_jugados = len(reales["fase_grupos"])
    cond = f" · condicionado a {n_jugados} partido(s) ya jugado(s)" if n_jugados else ""

    # ---- Consola ----
    print("=" * 78)
    print(f" PREDICTOR MONTE CARLO - MUNDIAL 2026  ({n} sims, seed={res['seed']}){cond}")
    print("=" * 78)
    if len(moda["paises"]) == 1:
        print(f"\n>>> CAMPEON MAS PROBABLE (moda): {moda['paises'][0]}  "
              f"({moda['frecuencia']}/{n} = {moda['porcentaje']:.1f}%)\n")
    else:
        print(f"\n>>> MODA EMPATADA: {', '.join(moda['paises'])}  "
              f"(cada uno {moda['porcentaje']:.1f}%)\n")
    print(f"{'#':>2}  {'Seleccion':22} {'Gr':>2} {'Elo':>5} {'Avanza':>7} {'Cuartos':>8} "
          f"{'Semis':>7} {'Final':>7} {'Titulo':>7} {'PtsGr':>6}")
    print("-" * 86)
    for i, r in enumerate(ranking[:args.top], 1):
        print(f"{i:>2}  {r['pais']:22} {r['grupo']:>2} {r['elo']:>5.0f} "
              f"{r['p_avanza']:>6.1f}% {r['p_cuartos']:>7.1f}% {r['p_semis']:>6.1f}% "
              f"{r['p_final']:>6.1f}% {r['p_titulo']:>6.1f}% {r['puntos_grupo_media']:>6.2f}")

    # ---- JSON ----
    out = {
        "meta": {
            "simulaciones": n, "seed": res["seed"],
            "modelo": "Elo observado + ajustes (altitud, desgaste, presion) + Poisson + Monte Carlo",
            "partidos_reales_cargados": n_jugados,
            "agregacion": {"campeon": "moda", "probabilidades": "frecuencia", "puntos_grupo": "media"},
        },
        "campeon_moda": moda,
        "ranking": ranking,
        "distribucion_campeon": res["distribucion_campeon"],
    }
    json.dump(out, open(datos.ruta("data", "prediccion_resultados.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\nResultados completos -> data/prediccion_resultados.json")

    escribir_markdown(res, reales, args.top)
    print("Resumen -> docs/prediccion_resultados.md")


def escribir_markdown(res, reales, top):
    ranking, n, moda = res["ranking"], res["n"], res["campeon_moda"]
    p_top = moda["porcentaje"] / 100.0
    err = 100 * math.sqrt(p_top * (1 - p_top) / n)
    n_jug = len(reales["fase_grupos"])
    M = []
    M.append("# Resultados de la prediccion — Mundial 2026\n")
    M.append(f"Modelo **Elo observado + altitud + desgaste + presion + Poisson + Monte Carlo** · "
             f"**{n} simulaciones** · semilla `{res['seed']}` (reproducible).")
    if n_jug:
        M.append(f"\n> Prediccion **condicionada** a {n_jug} partido(s) ya jugado(s) "
                 f"(cargados en `data/resultados_reales.json`).")
    if len(moda["paises"]) == 1:
        M.append(f"\n## 🏆 Campeon mas probable (moda): **{moda['paises'][0]}** — "
                 f"{moda['frecuencia']}/{n} ({moda['porcentaje']:.1f}%)\n")
    else:
        M.append(f"\n## 🏆 Moda empatada: **{' / '.join(moda['paises'])}** — "
                 f"cada uno {moda['porcentaje']:.1f}%\n")
    M.append(f"> Error estandar de la probabilidad de titulo del favorito: ±{err:.2f} pts "
             f"con {n} simulaciones. Sube `--sims` para estabilizar.\n")
    M.append(f"## Tabla de probabilidades (top {top} por % de titulo)\n")
    M.append("| # | Seleccion | Gr | Elo | Avanza | Cuartos | Semis | Final | **Titulo** | Pts grupo |")
    M.append("|---|-----------|:--:|:---:|:------:|:-------:|:-----:|:-----:|:----------:|:---------:|")
    for i, r in enumerate(ranking[:top], 1):
        M.append(f"| {i} | {r['pais']} | {r['grupo']} | {r['elo']:.0f} | {r['p_avanza']:.0f}% | "
                 f"{r['p_cuartos']:.0f}% | {r['p_semis']:.0f}% | {r['p_final']:.0f}% | "
                 f"**{r['p_titulo']:.1f}%** | {r['puntos_grupo_media']:.2f} |")
    M.append("\n## Factores del modelo\n")
    M.append("- **Fuerza base**: Elo observado de eloratings.net (observable cuantitativo objetivo).")
    M.append("- **Altitud**: penalizacion Elo a equipos no adaptados que juegan en sedes de altura "
             "(Ciudad de Mexico 2240 m, Guadalajara 1566 m). Mexico, Ecuador, Colombia, Sudafrica e Iran "
             "apenas la sufren por su altitud de adaptacion.")
    M.append("- **Localia**: +Elo a los anfitriones (Mexico, EE.UU., Canada) jugando en su pais.")
    M.append("- **Desgaste**: la fatiga se acumula partido a partido (mas con prorrogas) y se recupera "
             "parcialmente con el descanso; penaliza mas en rondas avanzadas.")
    M.append("- **Presion**: en la 3a jornada de grupos, el equipo obligado a ganar recibe un empuje "
             "y el partido se abre (mas goles, mas varianza).")
    M.append("- **Condicionamiento**: los resultados reales cargados se fijan; solo se simula lo pendiente.\n")
    M.append("*Reproducir: `python scripts/run_prediccion.py`. "
             "Cargar resultados: `python scripts/actualizar_resultados.py`.*\n")
    open(datos.ruta("docs", "prediccion_resultados.md"), "w", encoding="utf-8").write("\n".join(M))


if __name__ == "__main__":
    main()
