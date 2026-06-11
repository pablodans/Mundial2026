# -*- coding: utf-8 -*-
"""
Modelo de partido: Elo observado ajustado por contexto -> goles Poisson.

Elo efectivo de un equipo en un partido:
    elo_eff = elo_base
              + ventaja de localia (si es anfitrion jugando en su pais)
              - penalizacion por altitud (segun cuanto supere la sede su altitud de adaptacion)
              - penalizacion por desgaste acumulado (fatiga)
              + bonus de presion ("ganar si o si" en la ultima jornada de grupos)

Los goles de cada equipo se modelan como Poisson independientes con media
    lambda = GOAL_BASE * exp(+-GAMMA * dElo / ELO_DIV)
donde dElo es la diferencia de Elo efectivo. La presion ademas abre el partido
(sube GOAL_BASE), aumentando la varianza del marcador.
"""
import math
from dataclasses import dataclass


@dataclass
class Parametros:
    # --- Goles ---
    GOAL_BASE: float = 1.32     # goles esperados por equipo en un partido parejo
    GAMMA: float = 0.42         # sensibilidad de los goles a la diferencia de Elo
    ELO_DIV: float = 250.0      # divisor que convierte diferencia de Elo en "unidades de gol".
                                # Calibrado por maxima verosimilitud sobre los marcadores reales
                                # de 80 cruces de los 5 ultimos Mundiales (scripts/calibrar.py).
    # --- Localia del anfitrion ---
    VENTAJA_LOCALIA: float = 65.0   # bonus Elo para anfitrion (MEX/USA/CAN) jugando en su pais
    # --- Altitud ---
    ALT_UMBRAL_M: float = 500.0     # margen de tolerancia: por debajo no penaliza
    ALT_PENAL_POR_KM: float = 70.0  # puntos Elo perdidos por cada 1000 m por encima de la adaptacion
    ALT_PENAL_MAX: float = 140.0    # tope de penalizacion por altitud
    # --- Desgaste / fatiga ---
    FAT_CARGA_PARTIDO: float = 1.0      # carga de un partido de 90'
    FAT_CARGA_PRORROGA: float = 0.55    # carga extra si hubo prorroga (30' mas)
    FAT_RECUPERA: float = 0.78          # fraccion de fatiga que queda tras descansar entre partidos
    FAT_PENAL_POR_UNIDAD: float = 9.0   # puntos Elo perdidos por unidad de fatiga acumulada
    FAT_PENAL_MAX: float = 90.0         # tope de penalizacion por fatiga
    # --- Presion "ganar si o si" ---
    PRESION_ELO: float = 35.0       # bonus Elo al equipo obligado a ganar (motivacion/empuje)
    PRESION_APERTURA: float = 0.18  # incremento relativo de GOAL_BASE (partido mas abierto)
    # --- Estilo de juego (modula el caracter del partido: goles y varianza, no el favorito) ---
    EST_TENDENCIA: float = 0.06     # apertura por equipo ofensivo (+) o defensivo (-)
    EST_RITMO: float = 0.04         # apertura por ritmo alto (+) o bajo (-)
    EST_APERTURA_MAX: float = 0.30  # tope de apertura por estilo (suma de ambos equipos)
    # --- Eliminacion directa ---
    KO_FACTOR: float = 0.87         # los partidos de KO son mas cerrados que los de grupos
                                    # (menos goles -> mas prorrogas/penales). Calibrado con
                                    # el historico de los 5 ultimos Mundiales (scripts/calibrar.py).
    # --- Penales ---
    PEN_DIV: float = 4000.0         # sesgo (suave) por Elo en la tanda de penales
    # --- Elo dinamico (actualizacion con resultados reales, formula eloratings) ---
    K_MUNDIAL: float = 60.0         # peso base de actualizacion Elo en partidos de Copa del Mundo
    K_ADAPT_TASA: float = 0.15      # K adaptativo: K_eff = K_MUNDIAL / (1 + tasa * partidos_jugados).
                                    # El 1er resultado mueve mas el Elo; los siguientes, menos
                                    # (mas informacion acumulada -> mas confianza). 0 = K constante.
    # --- Dixon-Coles (correccion de marcadores bajos: 0-0, 1-0, 0-1, 1-1) ---
    DC_RHO: float = -0.10           # <0 sube empates bajos. Calibrado (en direccion) con el
                                    # historico; magnitud moderada (rango de literatura). 0 = Poisson puro.


def penalizacion_altitud(altitud_sede, altitud_adaptacion, par):
    """Penalizacion Elo por jugar en altura por encima de la altitud a la que el equipo esta adaptado."""
    exceso = altitud_sede - altitud_adaptacion - par.ALT_UMBRAL_M
    if exceso <= 0:
        return 0.0
    return min(par.ALT_PENAL_MAX, par.ALT_PENAL_POR_KM * exceso / 1000.0)


def penalizacion_fatiga(fatiga, par):
    return min(par.FAT_PENAL_MAX, par.FAT_PENAL_POR_UNIDAD * fatiga)


def elo_efectivo(equipo, par, *, altitud_m=0.0, pais_sede=None,
                 fatiga=0.0, presion=False):
    """Elo de partido de `equipo` (dict de selecciones) ajustado por el contexto."""
    elo = equipo["elo"]
    # Localia: anfitrion jugando en su propio pais
    if pais_sede is not None and equipo["pais"] in _ANFITRIONES and pais_sede == _PAIS_SEDE_DE[equipo["pais"]]:
        elo += par.VENTAJA_LOCALIA
    # Altitud
    elo -= penalizacion_altitud(altitud_m, equipo["altitud_casa_m"], par)
    # Fatiga
    elo -= penalizacion_fatiga(fatiga, par)
    # Presion
    if presion:
        elo += par.PRESION_ELO
    return elo


# Mapeo anfitrion -> nombre de pais tal como aparece en sedes.json ("pais")
_ANFITRIONES = {"Mexico", "Estados Unidos", "Canada"}
_PAIS_SEDE_DE = {"Mexico": "Mexico", "Estados Unidos": "USA", "Canada": "Canada"}


_TENDENCIA_SIGNO = {"ofensivo": +1.0, "equilibrado": 0.0, "defensivo": -1.0}
_RITMO_SIGNO = {"alto": +1.0, "medio": 0.0, "bajo": -1.0}


def apertura_estilo(eq_a, eq_b, par):
    """Cuanto se 'abre' un partido por el estilo de ambos equipos (mas/menos goles totales).

    Dos equipos ofensivos y veloces producen mas goles; dos cerrados, menos. No altera
    quien es favorito (eso lo fija el Elo), solo el caracter y la varianza del marcador.
    """
    a = 0.0
    for eq in (eq_a, eq_b):
        a += par.EST_TENDENCIA * _TENDENCIA_SIGNO.get(eq.get("tendencia", "equilibrado"), 0.0)
        a += par.EST_RITMO * _RITMO_SIGNO.get(eq.get("ritmo", "medio"), 0.0)
    return max(-par.EST_APERTURA_MAX, min(par.EST_APERTURA_MAX, a))


def lambdas(elo_eff_a, elo_eff_b, par, *, apertura=0.0, factor_goles=1.0):
    base = par.GOAL_BASE * factor_goles * (1.0 + apertura)
    d = (elo_eff_a - elo_eff_b) / par.ELO_DIV
    la = base * math.exp(+par.GAMMA * d)
    lb = base * math.exp(-par.GAMMA * d)
    return la, lb


def poisson(lam, rng):
    """Muestreo Poisson (algoritmo de Knuth)."""
    L = math.exp(-lam)
    k = 0
    pr = 1.0
    while True:
        k += 1
        pr *= rng.random()
        if pr <= L:
            return k - 1


def tau_dixon_coles(i, j, la, lb, rho):
    """Factor de correccion de Dixon-Coles sobre los 4 marcadores bajos."""
    if rho == 0.0:
        return 1.0
    if i == 0 and j == 0:
        return 1.0 - la * lb * rho
    if i == 0 and j == 1:
        return 1.0 + la * rho
    if i == 1 and j == 0:
        return 1.0 + lb * rho
    if i == 1 and j == 1:
        return 1.0 - rho
    return 1.0


def muestrear_marcador(la, lb, par, rng):
    """Muestrea (goles_a, goles_b). Con DC_RHO != 0 usa Dixon-Coles via rejection sampling
    (envoltura = dos Poisson independientes), exacto y eficiente porque tau ~ 1."""
    if par.DC_RHO == 0.0:
        return poisson(la, rng), poisson(lb, rng)
    # Cota superior de tau sobre las celdas afectadas
    m = max(1.0, tau_dixon_coles(0, 0, la, lb, par.DC_RHO),
            tau_dixon_coles(0, 1, la, lb, par.DC_RHO),
            tau_dixon_coles(1, 0, la, lb, par.DC_RHO),
            tau_dixon_coles(1, 1, la, lb, par.DC_RHO))
    while True:
        i, j = poisson(la, rng), poisson(lb, rng)
        if rng.random() <= tau_dixon_coles(i, j, la, lb, par.DC_RHO) / m:
            return i, j


def jugar_partido(eq_a, eq_b, par, rng, *, altitud_m=0.0, pais_sede=None,
                  fatiga_a=0.0, fatiga_b=0.0, presion_a=False, presion_b=False,
                  factor_goles=1.0):
    """Devuelve (goles_a, goles_b) para un partido en un contexto dado."""
    ea = elo_efectivo(eq_a, par, altitud_m=altitud_m, pais_sede=pais_sede,
                      fatiga=fatiga_a, presion=presion_a)
    eb = elo_efectivo(eq_b, par, altitud_m=altitud_m, pais_sede=pais_sede,
                      fatiga=fatiga_b, presion=presion_b)
    apertura = apertura_estilo(eq_a, eq_b, par)
    if presion_a or presion_b:
        apertura += par.PRESION_APERTURA
    la, lb = lambdas(ea, eb, par, apertura=apertura, factor_goles=factor_goles)
    return muestrear_marcador(la, lb, par, rng)


def ganador_eliminatoria(eq_a, eq_b, par, rng, *, altitud_m=0.0, pais_sede=None,
                         fatiga_a=0.0, fatiga_b=0.0):
    """Resuelve un cruce a partido unico: 90' -> prorroga -> penales.

    Devuelve (ganador_pais, hubo_prorroga_a, hubo_prorroga_b).
    """
    ga, gb = jugar_partido(eq_a, eq_b, par, rng, altitud_m=altitud_m,
                           pais_sede=pais_sede, fatiga_a=fatiga_a, fatiga_b=fatiga_b,
                           factor_goles=par.KO_FACTOR)
    if ga > gb:
        return eq_a["pais"], False, False
    if gb > ga:
        return eq_b["pais"], False, False
    # Prorroga: mini-Poisson (30') con la misma diferencia de Elo efectivo
    ea = elo_efectivo(eq_a, par, altitud_m=altitud_m, pais_sede=pais_sede, fatiga=fatiga_a)
    eb = elo_efectivo(eq_b, par, altitud_m=altitud_m, pais_sede=pais_sede, fatiga=fatiga_b)
    la, lb = lambdas(ea, eb, par, factor_goles=par.KO_FACTOR)
    xa, xb = poisson(la * 0.4, rng), poisson(lb * 0.4, rng)
    if xa > xb:
        return eq_a["pais"], True, True
    if xb > xa:
        return eq_b["pais"], True, True
    # Penales: leve sesgo por Elo base
    pa = 0.5 + (eq_a["elo"] - eq_b["elo"]) / par.PEN_DIV
    pa = min(max(pa, 0.15), 0.85)
    ganador = eq_a["pais"] if rng.random() < pa else eq_b["pais"]
    return ganador, True, True
