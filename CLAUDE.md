# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Monte Carlo predictor for the 2026 World Cup (48 teams, 12 groups). It simulates the
full tournament thousands of times and reports each nation's probabilities (advance,
each knockout round, title). The base strength is the **observed eloratings.net Elo**,
adjusted per match by **altitude, accumulated fatigue, and "must-win" pressure**.
Predictions can be **conditioned on real results** loaded as the tournament progresses.

## Commands

Windows note: the Microsoft Store alias shadows `python`/`python3`. Use the real
interpreter path (e.g. `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`) or `py`.

```
python scripts/construir_fixture.py     # regenerate data/fixture_completo.json from selecciones.csv + sedes.json
python scripts/run_prediccion.py        # run the prediction (default 10000 sims, seed 2026)
python scripts/run_prediccion.py --sims 50000 --seed 7 --top 24
python scripts/actualizar_resultados.py listar    # see match ids / load real results (grupo|bracket|elim)
python scripts/predecir_partido.py id H1A          # single-match distribution (or: vs A B | jornada N)
python scripts/calibrar.py              # compare model vs historico_mundiales.json; grid-search GOAL_BASE
python tests/test_modelo.py             # run tests directly (also works under pytest)
```

Stdlib only (Python 3.10+); no dependencies. A full 10k-sim run takes ~5 s.

## Architecture

Data lives in `data/` (CSV + JSON); the model is the `src/mundial2026/` package;
`scripts/` are the CLI entry points (they prepend `src/` to `sys.path`). Outputs are
written to `data/prediccion_resultados.json` and `docs/prediccion_resultados.md`.

The simulation chain — read these together to understand it:
1. **`modelo.py`** — the core. `Parametros` holds every tunable coefficient. `elo_efectivo()`
   computes a per-match Elo from base Elo ± localía/altitude/fatigue/pressure; `apertura_estilo()`
   converts both teams' play-style into how open the match is (goal total/variance, NOT who
   wins); `lambdas()` maps the Elo gap to two Poisson goal rates (× `factor_goles`);
   `jugar_partido()` / `ganador_eliminatoria()` play a match. Knockout passes
   `factor_goles=KO_FACTOR` (<1, knockout games are tighter) and resolves 90′ → mini-Poisson
   extra time → Elo-biased penalties.
2. **`fatiga.py`** — `fatiga_tras_jugar()`: fatigue accrues per match (more on extra time),
   partially recovers between matches. The Elo penalty for it is increasing, so desgaste
   bites hardest in late rounds.
3. **`torneo.py`** — `simular_grupos()` plays the 72 group matches **ordered by matchday**
   (so the post-matchday-2 table is known before matchday-3 pressure is evaluated, and
   fatigue advances in time); `simular_eliminatoria()` runs R32→Final. Both consult
   `resultados_reales`: group matches with a real score aren't simulated; `bracket_r32`
   fixes the official bracket (else it's shuffled each sim to marginalize pairing
   uncertainty); finished knockout ties use their real winner.
4. **`montecarlo.py`** — `run()` loops N sims and aggregates: champion → **mode**,
   round probabilities → **frequency**, group points → **mean**. Before the loop it calls
   `elo_dinamico.aplicar_a_selecciones()` so pending matches simulate with the live Elo.
5. **`elo_dinamico.py`** — applies the eloratings update (goal-margin factor + **adaptive K**:
   `_k_efectivo()` = `K_MUNDIAL/(1+K_ADAPT_TASA·n)`, so each team's first result moves its Elo
   most and later ones less) for each already-played group match in chronological order,
   returning a `sel` copy with `elo` replaced by the live value. Because each team uses its own
   K, updates are NOT zero-sum except when both have played the same number of games (e.g.
   matchday 1). This is the "result of match 1 improves the match-2 prediction" loop.
6. **`prediccion_partido.py`** — single-match prediction WITHOUT simulating: builds the exact
   score matrix (`modelo.tau_dixon_coles` correction included) and returns 1X2 / most-likely
   score / top-5 / over-under.

Dixon-Coles is on (`DC_RHO=-0.10`). It is applied in BOTH the analytic predictor and the
simulator: `modelo.muestrear_marcador()` does rejection sampling (envelope = two independent
Poissons) when `DC_RHO != 0`, so the Monte Carlo and the per-match predictor stay consistent.
This adds ~40% wall-time to a 10k run (still ~7 s).

## Conventions that matter

- **Reproducibility**: a single `random.Random(seed)` is threaded through everything as
  `rng`. Group standings sort over `sorted(teams)` *before* any random tiebreak so string
  iteration order can't perturb RNG consumption. Preserve deterministic ordering before
  any `rng.*` call when editing group/knockout logic.
- **`ELO_DIV` is the main calibration knob** (lower = Elo matters more = sharper favourites).
  It is no longer hand-picked: `ELO_DIV=250`, `KO_FACTOR=0.87` and the direction of `DC_RHO`
  come from `scripts/calibrar.py`, a max-likelihood Poisson/Dixon-Coles backtest of
  `data/elo_historico.json` (real pre-tournament Elo) against the real 90' scores in
  `data/historico_mundiales.json`. The raw ρ optimum is exaggerated by the KO sample's excess
  of draws (extra-time games), so `DC_RHO=-0.10` is a deliberately moderate (literature-range)
  value, not the raw fit. Re-run if those files change; surface is flat (80 ties) — guidance, not gospel.
- **Hosts mapping**: `modelo._PAIS_SEDE_DE` maps host country (as written in
  `selecciones.csv`, e.g. "Estados Unidos") to the venue's `pais` field in `sedes.json`
  (e.g. "USA"). Localía only triggers when both match.
- **Live updates**: editing `data/resultados_reales.json` (directly or via
  `actualizar_resultados.py`) is how the model "improves as matches are played". Match
  ids come from the fixture (e.g. `A1A`); knockout keys are `Ronda-índice` (0-based).

## Data files

`selecciones.csv` (Elo/FIFA/value/history/altitude) is enriched at load time by
`datos.cargar_selecciones()` which merges `estilos.json` (play-style attributes) into each
team dict — so `modelo` can read `t["tendencia"]`/`t["ritmo"]`. `jugadores.json` has 5 key
players per team **including a goalkeeper** (descriptive only — not a model input, to avoid
double-counting strength already in Elo/value). `historico_mundiales.json` (last 5 World
Cups' knockout ties, with 90' scores) and `elo_historico.json` (pre-tournament Elo per
team) are consumed only by `calibrar.py` for the MLE backtest. `sedes.json` holds the 16 venues
with altitude. `fixture_completo.json` is generated from the **official 2026 calendar**
embedded as the `CALENDARIO` table in `construir_fixture.py` (all 72 group matches with
their real pairing, date and venue, unveiled 6-Dec-2025). `fecha` is informative only —
the engine orders by `jornada` then `id`. The altitude-driving venues are Ciudad de
Mexico (2240 m) and Guadalajara (1566 m); `construir_fixture.py` validates that each group
has its 4 teams and 6 unique pairings before writing.

## Data provenance

48 teams from the official 5-Dec-2025 draw; Elo from eloratings.net, FIFA rank/points,
Transfermarkt squad values, goalkeepers, play-styles, and World Cup history collected
June 2026. Figures for teams outside the FIFA top-50 are estimated and flagged as such.
Mexico City (2240 m) and Guadalajara (1566 m) are the venues that actually drive the
altitude factor. `KO_FACTOR=0.87` was set from `calibrar.py` against the historical
knockout goal rate.
