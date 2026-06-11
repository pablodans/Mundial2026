# -*- coding: utf-8 -*-
"""
Pruebas del modelo. Ejecutables con pytest o directamente:
    python tests/test_modelo.py
"""
import os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from mundial2026 import datos, montecarlo, torneo  # noqa: E402
from mundial2026.modelo import Parametros, elo_efectivo, penalizacion_altitud, ganador_eliminatoria  # noqa: E402
from mundial2026.fatiga import fatiga_tras_jugar  # noqa: E402


def test_datos_48_equipos_y_12_grupos():
    sel = datos.cargar_selecciones()
    assert len(sel) == 48, f"se esperaban 48 selecciones, hay {len(sel)}"
    grupos = {}
    for t in sel.values():
        grupos.setdefault(t["grupo"], []).append(t)
    assert len(grupos) == 12, "deben ser 12 grupos"
    assert all(len(v) == 4 for v in grupos.values()), "cada grupo debe tener 4 equipos"


def test_fixture_72_partidos():
    fx = datos.cargar_fixture()
    assert len(fx["fase_grupos"]) == 72


def test_altitud_penaliza_a_no_adaptados():
    par = Parametros()
    # Un equipo de tierras bajas (adaptacion 50 m) sufre en Ciudad de Mexico (2240 m)...
    p_bajo = penalizacion_altitud(2240, 50, par)
    # ...y uno adaptado a la altura (2240 m) no sufre nada.
    p_alto = penalizacion_altitud(2240, 2240, par)
    assert p_bajo > 0 and p_alto == 0
    assert p_bajo <= par.ALT_PENAL_MAX


def test_localia_anfitrion_suma_elo():
    sel = datos.cargar_selecciones()
    par = Parametros()
    base = elo_efectivo(sel["Mexico"], par)
    en_casa = elo_efectivo(sel["Mexico"], par, pais_sede="Mexico")
    assert en_casa == base + par.VENTAJA_LOCALIA


def test_fatiga_crece_y_satura():
    par = Parametros()
    f0 = 0.0
    f1 = fatiga_tras_jugar(f0, par)
    f2 = fatiga_tras_jugar(f1, par)
    assert f2 > f1 > f0
    # Con prorroga acumula mas que sin ella
    assert fatiga_tras_jugar(f1, par, hubo_prorroga=True) > f2


def test_estilo_abre_o_cierra_el_partido():
    from mundial2026.modelo import apertura_estilo
    par = Parametros()
    ofensivo = {"tendencia": "ofensivo", "ritmo": "alto"}
    defensivo = {"tendencia": "defensivo", "ritmo": "bajo"}
    assert apertura_estilo(ofensivo, ofensivo, par) > 0      # dos ofensivos -> mas goles
    assert apertura_estilo(defensivo, defensivo, par) < 0    # dos cerrados -> menos goles


def test_selecciones_traen_estilo_y_5_jugadores():
    sel = datos.cargar_selecciones()
    assert all("tendencia" in t and "ritmo" in t for t in sel.values())
    jug = datos.cargar_jugadores()
    assert len(jug) == 48
    # Cada seleccion tiene al menos un portero entre sus jugadores clave
    assert all(any(j["posicion"] == "POR" for j in lista) for lista in jug.values())


def test_ko_mas_cerrado_que_grupos():
    par = Parametros()
    assert par.KO_FACTOR < 1.0  # los partidos de eliminacion producen menos goles


def test_reproducibilidad():
    a = montecarlo.run(n=80, seed=123)
    b = montecarlo.run(n=80, seed=123)
    assert a["distribucion_campeon"] == b["distribucion_campeon"]
    assert a["ranking"][0]["pais"] == b["ranking"][0]["pais"]


def test_condicionamiento_resultado_real():
    """Si fijamos goleadas de un equipo, su prob. de avanzar debe subir respecto al a priori."""
    sel = datos.cargar_selecciones()
    fx = datos.cargar_fixture()
    par = Parametros()
    # Partidos de Cabo Verde (grupo H, el mas debil del grupo de Espana/Uruguay)
    ids_cabo = [m["id"] for m in fx["fase_grupos"]
                if "Cabo Verde" in (m["local"], m["visitante"])]
    base = montecarlo.run(n=120, seed=5, selecciones=sel, fixture=fx,
                          resultados_reales={"fase_grupos": {}, "bracket_r32": [], "eliminatorias": {}})
    p_base = next(r["p_avanza"] for r in base["ranking"] if r["pais"] == "Cabo Verde")
    # Forzamos 3 victorias 3-0 de Cabo Verde
    reales = {"fase_grupos": {}, "bracket_r32": [], "eliminatorias": {}}
    for m in fx["fase_grupos"]:
        if m["id"] in ids_cabo:
            if m["local"] == "Cabo Verde":
                reales["fase_grupos"][m["id"]] = {"local_goles": 3, "visitante_goles": 0}
            else:
                reales["fase_grupos"][m["id"]] = {"local_goles": 0, "visitante_goles": 3}
    cond = montecarlo.run(n=120, seed=5, selecciones=sel, fixture=fx, resultados_reales=reales)
    p_cond = next(r["p_avanza"] for r in cond["ranking"] if r["pais"] == "Cabo Verde")
    assert p_cond > p_base, f"condicionar deberia subir el avance: base={p_base} cond={p_cond}"


def test_prediccion_partido_distribucion_coherente():
    from mundial2026 import prediccion_partido
    sel = datos.cargar_selecciones()
    par = Parametros()
    pred = prediccion_partido.predecir(sel["Espana"], sel["Cabo Verde"], par)
    # Las tres opciones del 1X2 suman ~100
    assert abs(pred["p_gana_a"] + pred["p_empate"] + pred["p_gana_b"] - 100) < 0.5
    assert abs(pred["p_over_2_5"] + pred["p_under_2_5"] - 100) < 0.5
    # El favorito por Elo (Espana) debe tener mas prob de ganar que el rival
    assert pred["p_gana_a"] > pred["p_gana_b"]


def test_elo_dinamico_se_mueve_con_resultados():
    from mundial2026 import elo_dinamico
    sel = datos.cargar_selecciones()
    fixture = datos.cargar_fixture()
    par = Parametros()
    # Buscamos un partido y simulamos una sorpresa: gana el equipo de menor Elo por goleada
    m = fixture["fase_grupos"][0]
    a, b = m["local"], m["visitante"]
    debil, fuerte = (a, b) if sel[a]["elo"] < sel[b]["elo"] else (b, a)
    gl = (3, 0) if debil == a else (0, 3)
    reales = {"fase_grupos": {m["id"]: {"local_goles": gl[0], "visitante_goles": gl[1]}},
              "bracket_r32": [], "eliminatorias": {}}
    elo = elo_dinamico.elo_actualizado(sel, fixture, reales, par)
    # El equipo debil sube su Elo tras ganar; el fuerte baja
    assert elo[debil] > sel[debil]["elo"]
    assert elo[fuerte] < sel[fuerte]["elo"]
    # Suma cero (lo que uno gana, el otro lo pierde)
    assert abs((elo[debil] - sel[debil]["elo"]) + (elo[fuerte] - sel[fuerte]["elo"])) < 1e-6


def test_dixon_coles_sube_empates_bajos():
    from mundial2026 import prediccion_partido
    sel = datos.cargar_selecciones()
    # Partido parejo (mas empates posibles): dos equipos de Elo similar
    a, b = "Belgica", "Suiza"
    sin_dc = prediccion_partido.predecir(sel[a], sel[b], Parametros(DC_RHO=0.0))
    con_dc = prediccion_partido.predecir(sel[a], sel[b], Parametros(DC_RHO=-0.10))
    assert con_dc["p_empate"] > sin_dc["p_empate"]
    # Sigue siendo una distribucion valida
    assert abs(con_dc["p_gana_a"] + con_dc["p_empate"] + con_dc["p_gana_b"] - 100) < 0.5


def test_k_adaptativo_decrece_con_partidos():
    from mundial2026 import elo_dinamico
    par = Parametros()
    k0 = elo_dinamico._k_efectivo(par, 0)
    k1 = elo_dinamico._k_efectivo(par, 1)
    k2 = elo_dinamico._k_efectivo(par, 2)
    assert k0 > k1 > k2          # mas partidos jugados -> menor ajuste
    assert k0 == par.K_MUNDIAL   # el primero usa el K base


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(fns)} pruebas OK")
    return ok == len(fns)


if __name__ == "__main__":
    sys.exit(0 if _run_all() else 1)
