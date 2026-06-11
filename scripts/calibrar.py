#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibracion/validacion del modelo contra el historico de cruces eliminatorios
(data/historico_mundiales.json, ultimos 5 Mundiales).

No hay Elo historico equipo-a-equipo, asi que NO se puede backtestear el favoritismo
partido a partido. Lo que SI se valida son las TASAS AGREGADAS que el modelo debe
reproducir en fase eliminatoria:
  - goles por equipo en los 90'
  - % de partidos que acaban empatados en 90' (van a prorroga)
  - % de partidos resueltos por penales

Ademas hace un mini grid-search de GOAL_BASE para acercar los goles del modelo a los
historicos. Uso:  python scripts/calibrar.py
"""
import json, math, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from mundial2026 import datos  # noqa: E402
from mundial2026 import modelo  # noqa: E402
from mundial2026.modelo import Parametros  # noqa: E402

GAMMA_FIJO = Parametros().GAMMA  # fijamos GAMMA y calibramos ELO_DIV (solo importa el cociente)


def metricas_historico():
    h = json.load(open(datos.ruta("data", "historico_mundiales.json"), encoding="utf-8"))["mundiales"]
    partidos = [m for mundial in h.values() for m in mundial]
    n = len(partidos)
    goles, prorrogas, penales = 0, 0, 0
    for m in partidos:
        gl, gv = (int(x) for x in m["marcador_90"].split("-"))
        goles += gl + gv
        prorrogas += 1 if m.get("prorroga") else 0
        penales += 1 if m.get("penales") else 0
    return {
        "n": n,
        "goles_por_equipo_90": goles / (2 * n),
        "pct_prorroga": 100 * prorrogas / n,
        "pct_penales": 100 * penales / n,
    }


def _cruce_metricas(eq_a, eq_b, par, rng):
    """Juega un cruce KO y devuelve (goles_90_totales, fue_a_prorroga, fue_a_penales)."""
    ga, gb = modelo.jugar_partido(eq_a, eq_b, par, rng, factor_goles=par.KO_FACTOR)
    if ga != gb:
        return ga + gb, False, False
    ea = modelo.elo_efectivo(eq_a, par)
    eb = modelo.elo_efectivo(eq_b, par)
    la, lb = modelo.lambdas(ea, eb, par, factor_goles=par.KO_FACTOR)
    xa, xb = modelo.poisson(la * 0.4, rng), modelo.poisson(lb * 0.4, rng)
    return ga + gb, True, (xa == xb)


def metricas_modelo(par, sel, n=20000, seed=2026):
    rng = random.Random(seed)
    paises = list(sel)
    goles, prorrogas, penales = 0, 0, 0
    for _ in range(n):
        a, b = rng.sample(paises, 2)
        g90, pro, pen = _cruce_metricas(sel[a], sel[b], par, rng)
        goles += g90
        prorrogas += 1 if pro else 0
        penales += 1 if pen else 0
    return {
        "n": n,
        "goles_por_equipo_90": goles / (2 * n),
        "pct_prorroga": 100 * prorrogas / n,
        "pct_penales": 100 * penales / n,
    }


def _logpmf_poisson(k, lam):
    if lam <= 0:
        return -1e9
    return k * math.log(lam) - lam - math.lgamma(k + 1)


def cruces_con_elo():
    """Lista de (elo_local, elo_visitante, goles_local_90, goles_visitante_90) de los cruces
    historicos para los que conocemos el Elo pre-Mundial de ambos equipos."""
    hist = json.load(open(datos.ruta("data", "historico_mundiales.json"), encoding="utf-8"))["mundiales"]
    elo = json.load(open(datos.ruta("data", "elo_historico.json"), encoding="utf-8"))["elo_pre_mundial"]
    obs = []
    for anio, cruces in hist.items():
        elos = elo.get(anio, {})
        for m in cruces:
            a, b = m["local"], m["visitante"]
            if a in elos and b in elos:
                gl, gv = (int(x) for x in m["marcador_90"].split("-"))
                obs.append((elos[a], elos[b], gl, gv))
    return obs


def loglik(obs, goal_base, elo_div):
    """Log-verosimilitud Poisson de los marcadores de 90' bajo lambda = GB*exp(+-GAMMA*dElo/ELO_DIV)."""
    total = 0.0
    for ea, eb, gl, gv in obs:
        d = (ea - eb) / elo_div
        la = goal_base * math.exp(+GAMMA_FIJO * d)
        lb = goal_base * math.exp(-GAMMA_FIJO * d)
        total += _logpmf_poisson(gl, la) + _logpmf_poisson(gv, lb)
    return total


def backtest_mle():
    obs = cruces_con_elo()
    n = len(obs)
    # Grid-search 2D: GOAL_BASE (escala de goles en KO) x ELO_DIV (sensibilidad al Elo)
    mejor = None
    for i in range(13):                       # GB 0.85 .. 1.45
        gb = round(0.85 + 0.05 * i, 2)
        for j in range(19):                   # ELO_DIV 150 .. 600
            ed = 150 + 25 * j
            ll = loglik(obs, gb, ed)
            if mejor is None or ll > mejor[2]:
                mejor = (gb, ed, ll)
    gb_opt, ed_opt, ll_opt = mejor

    # Calibrar rho de Dixon-Coles: maximiza la suma de log(tau) sobre los marcadores
    # observados, usando las lambdas del modelo ya calibrado (GB_opt, ED_opt).
    def _tau(i, j, la, lb, rho):
        if i == 0 and j == 0:
            return 1.0 - la * lb * rho
        if i == 0 and j == 1:
            return 1.0 + la * rho
        if i == 1 and j == 0:
            return 1.0 + lb * rho
        if i == 1 and j == 1:
            return 1.0 - rho
        return 1.0

    obs_mle = obs
    mejor_rho = (0.0, 0.0)  # (rho, suma log-tau)
    for r in [round(-0.25 + 0.01 * t, 2) for t in range(51)]:  # -0.25 .. 0.25
        s = 0.0
        ok = True
        for ea, eb, gl, gv in obs_mle:
            d = (ea - eb) / ed_opt
            la = gb_opt * math.exp(+GAMMA_FIJO * d)
            lb = gb_opt * math.exp(-GAMMA_FIJO * d)
            tau = _tau(gl, gv, la, lb, r)
            if tau <= 0:
                ok = False
                break
            s += math.log(tau)
        if ok and (mejor_rho is None or s > mejor_rho[1]):
            mejor_rho = (r, s)
    rho_opt = mejor_rho[0]

    par = Parametros()
    gb_actual = par.GOAL_BASE * par.KO_FACTOR
    ll_actual = loglik(obs, gb_actual, par.ELO_DIV)

    # Acierto del favorito por Elo (quien tenia mas Elo gano el cruce?) sobre el ganador real
    hist = json.load(open(datos.ruta("data", "historico_mundiales.json"), encoding="utf-8"))["mundiales"]
    elo = json.load(open(datos.ruta("data", "elo_historico.json"), encoding="utf-8"))["elo_pre_mundial"]
    aciertos = ncomp = 0
    for anio, cruces in hist.items():
        e = elo.get(anio, {})
        for m in cruces:
            a, b = m["local"], m["visitante"]
            if a in e and b in e and e[a] != e[b]:
                ncomp += 1
                favorito = a if e[a] > e[b] else b
                if favorito == m["ganador"]:
                    aciertos += 1

    print("\n" + "=" * 64)
    print(" BACKTEST MLE sobre marcadores reales (Elo pre-Mundial -> goles)")
    print("=" * 64)
    print(f"Cruces usados (con Elo de ambos): {n}")
    print(f"Acierto del favorito por Elo: {aciertos}/{ncomp} = {100*aciertos/ncomp:.1f}%  "
          f"(referencia de cuanto 'manda' el Elo en KO)")
    print(f"\n{'modelo':22} {'GOAL_BASE(KO)':>14} {'ELO_DIV':>9} {'logLik/partido':>15}")
    print("-" * 62)
    print(f"{'actual':22} {gb_actual:>14.2f} {par.ELO_DIV:>9.0f} {ll_actual/n:>15.4f}")
    print(f"{'calibrado (MLE)':22} {gb_opt:>14.2f} {ed_opt:>9.0f} {ll_opt/n:>15.4f}")
    ko_factor_sug = round(gb_opt / par.GOAL_BASE, 2)
    print(f"\nSugerencias del backtest:")
    print(f"  ELO_DIV  -> {ed_opt}   (actual {par.ELO_DIV:.0f})")
    print(f"  KO_FACTOR -> {ko_factor_sug}  (= GOAL_BASE_KO {gb_opt} / GOAL_BASE {par.GOAL_BASE})")
    print(f"  DC_RHO   -> {rho_opt:+.2f} (MLE en muestra KO; actual {par.DC_RHO:+.2f}). "
          f"rho<0 sube empates bajos. La muestra KO tiene exceso de empates (prorrogas), "
          f"asi que el optimo esta inflado; se adopta un valor moderado (~-0.10, rango de literatura).")
    print("  Nota: ELO_DIV sale del coeficiente Elo->goles y aplica a TODO el torneo; "
          "GOAL_BASE(KO) solo a eliminacion. Muestra n=%d, tomar como guia, no dogma." % n)


def main():
    sel = datos.cargar_selecciones()
    hist = metricas_historico()
    base = metricas_modelo(Parametros(), sel)

    print("=" * 64)
    print(" CALIBRACION vs HISTORICO (5 ultimos Mundiales, fase eliminatoria)")
    print("=" * 64)
    print(f"{'metrica':28} {'historico':>12} {'modelo':>12}")
    print("-" * 54)
    for k, etiq in [("goles_por_equipo_90", "Goles por equipo (90')"),
                    ("pct_prorroga", "% va a prorroga"),
                    ("pct_penales", "% va a penales")]:
        print(f"{etiq:28} {hist[k]:>12.2f} {base[k]:>12.2f}")
    print(f"\n(historico n={hist['n']} cruces; modelo n={base['n']} cruces aleatorios)")

    # Mini grid-search de GOAL_BASE para acercar los goles del modelo a los historicos
    objetivo = hist["goles_por_equipo_90"]
    mejor = None
    print("\nGrid-search de GOAL_BASE (objetivo goles/equipo = "
          f"{objetivo:.2f}):")
    for gb in [round(1.00 + 0.05 * i, 2) for i in range(13)]:  # 1.00 .. 1.60
        m = metricas_modelo(Parametros(GOAL_BASE=gb), sel, n=8000, seed=99)
        err = abs(m["goles_por_equipo_90"] - objetivo)
        marca = ""
        if mejor is None or err < mejor[1]:
            mejor = (gb, err)
            marca = "  <-- mejor"
        print(f"  GOAL_BASE={gb:.2f}  goles/equipo={m['goles_por_equipo_90']:.2f}  err={err:.3f}{marca}")
    print(f"\nGOAL_BASE sugerido: {mejor[0]:.2f}  (actual por defecto: {Parametros().GOAL_BASE})")
    print("Nota: el historico KO tiende a menos goles (partidos cerrados); el valor por "
          "defecto contempla tambien la fase de grupos.")

    backtest_mle()


if __name__ == "__main__":
    main()
