#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera data/fixture_completo.json a partir del CALENDARIO OFICIAL del Mundial 2026
y data/sedes.json.

A diferencia de la version anterior (que repartia los 6 partidos de cada grupo con un
round-robin sintetico y clavaba una unica fecha por jornada), aqui cada uno de los 72
partidos de fase de grupos lleva su EMPAREJAMIENTO, FECHA y SEDE reales del calendario
publicado el 6-dic-2025 (un dia despues del sorteo). Fuentes cruzadas: ESPN, Wikipedia,
Sky Sports, FIFA.com (jun 2026).

Notas de modelado:
  - El motor ordena los partidos por `jornada` y luego por `id`; la `fecha` es informativa
    (no se usa para fatiga ni para nada calculado), pero se incluye para que el fixture
    refleje el calendario real. Las jornadas reales se escalonan en varios dias.
  - `local`/`visitante` siguen el orden oficial de la FIFA. La LOCALIA solo se activa para
    los anfitriones (Mexico/EE.UU./Canada) jugando en su pais, con independencia del orden.
  - La SEDE determina pais_sede (localia) y altitud. Las sedes mexicanas Ciudad de Mexico
    (2240 m) y Guadalajara (1566 m) son las que mueven el factor altura; Monterrey (427 m)
    es de baja altitud.
"""
import json, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
def p(*a): return os.path.join(ROOT, *a)

# Calendario oficial: (grupo, jornada, fecha, local, visitante, sede)
# Sede usa el nombre tal cual aparece en data/sedes.json (clave del dict de sedes).
CALENDARIO = [
    # --- Grupo A ---
    ("A", 1, "2026-06-11", "Mexico",          "Sudafrica",            "Ciudad de Mexico"),
    ("A", 1, "2026-06-11", "Corea del Sur",   "Chequia",              "Guadalajara"),
    ("A", 2, "2026-06-18", "Chequia",         "Sudafrica",            "Atlanta"),
    ("A", 2, "2026-06-18", "Mexico",          "Corea del Sur",        "Guadalajara"),
    ("A", 3, "2026-06-24", "Chequia",         "Mexico",               "Ciudad de Mexico"),
    ("A", 3, "2026-06-24", "Sudafrica",       "Corea del Sur",        "Monterrey"),
    # --- Grupo B ---
    ("B", 1, "2026-06-12", "Canada",          "Bosnia y Herzegovina", "Toronto"),
    ("B", 1, "2026-06-13", "Catar",           "Suiza",                "San Francisco"),
    ("B", 2, "2026-06-18", "Suiza",           "Bosnia y Herzegovina", "Los Angeles"),
    ("B", 2, "2026-06-18", "Canada",          "Catar",                "Vancouver"),
    ("B", 3, "2026-06-24", "Suiza",           "Canada",               "Vancouver"),
    ("B", 3, "2026-06-24", "Bosnia y Herzegovina", "Catar",           "Seattle"),
    # --- Grupo C ---
    ("C", 1, "2026-06-13", "Brasil",          "Marruecos",            "Nueva York"),
    ("C", 1, "2026-06-13", "Haiti",           "Escocia",              "Boston"),
    ("C", 2, "2026-06-19", "Escocia",         "Marruecos",            "Boston"),
    ("C", 2, "2026-06-19", "Brasil",          "Haiti",                "Filadelfia"),
    ("C", 3, "2026-06-24", "Escocia",         "Brasil",               "Miami"),
    ("C", 3, "2026-06-24", "Marruecos",       "Haiti",                "Atlanta"),
    # --- Grupo D ---
    ("D", 1, "2026-06-12", "Estados Unidos",  "Paraguay",             "Los Angeles"),
    ("D", 1, "2026-06-13", "Australia",       "Turquia",              "Vancouver"),
    ("D", 2, "2026-06-19", "Estados Unidos",  "Australia",            "Seattle"),
    ("D", 2, "2026-06-19", "Turquia",         "Paraguay",             "San Francisco"),
    ("D", 3, "2026-06-25", "Turquia",         "Estados Unidos",       "Los Angeles"),
    ("D", 3, "2026-06-25", "Paraguay",        "Australia",            "San Francisco"),
    # --- Grupo E ---
    ("E", 1, "2026-06-14", "Alemania",        "Curazao",              "Houston"),
    ("E", 1, "2026-06-14", "Costa de Marfil", "Ecuador",              "Filadelfia"),
    ("E", 2, "2026-06-20", "Alemania",        "Costa de Marfil",      "Toronto"),
    ("E", 2, "2026-06-20", "Ecuador",         "Curazao",              "Kansas City"),
    ("E", 3, "2026-06-25", "Ecuador",         "Alemania",             "Nueva York"),
    ("E", 3, "2026-06-25", "Curazao",         "Costa de Marfil",      "Filadelfia"),
    # --- Grupo F ---
    ("F", 1, "2026-06-14", "Paises Bajos",    "Japon",                "Dallas"),
    ("F", 1, "2026-06-14", "Suecia",          "Tunez",                "Monterrey"),
    ("F", 2, "2026-06-20", "Paises Bajos",    "Suecia",               "Houston"),
    ("F", 2, "2026-06-20", "Tunez",           "Japon",                "Monterrey"),
    ("F", 3, "2026-06-25", "Japon",           "Suecia",               "Dallas"),
    ("F", 3, "2026-06-25", "Tunez",           "Paises Bajos",         "Kansas City"),
    # --- Grupo G ---
    ("G", 1, "2026-06-15", "Belgica",         "Egipto",               "Seattle"),
    ("G", 1, "2026-06-15", "Iran",            "Nueva Zelanda",        "Los Angeles"),
    ("G", 2, "2026-06-21", "Belgica",         "Iran",                 "Los Angeles"),
    ("G", 2, "2026-06-21", "Nueva Zelanda",   "Egipto",               "Vancouver"),
    ("G", 3, "2026-06-26", "Egipto",          "Iran",                 "Seattle"),
    ("G", 3, "2026-06-26", "Nueva Zelanda",   "Belgica",              "Vancouver"),
    # --- Grupo H ---
    ("H", 1, "2026-06-15", "Espana",          "Cabo Verde",           "Atlanta"),
    ("H", 1, "2026-06-15", "Arabia Saudita",  "Uruguay",              "Miami"),
    ("H", 2, "2026-06-21", "Espana",          "Arabia Saudita",       "Atlanta"),
    ("H", 2, "2026-06-21", "Uruguay",         "Cabo Verde",           "Miami"),
    ("H", 3, "2026-06-26", "Cabo Verde",      "Arabia Saudita",       "Houston"),
    ("H", 3, "2026-06-26", "Uruguay",         "Espana",               "Guadalajara"),
    # --- Grupo I ---
    ("I", 1, "2026-06-16", "Francia",         "Senegal",              "Nueva York"),
    ("I", 1, "2026-06-16", "Irak",            "Noruega",              "Boston"),
    ("I", 2, "2026-06-22", "Francia",         "Irak",                 "Filadelfia"),
    ("I", 2, "2026-06-22", "Noruega",         "Senegal",              "Nueva York"),
    ("I", 3, "2026-06-26", "Noruega",         "Francia",              "Boston"),
    ("I", 3, "2026-06-26", "Senegal",         "Irak",                 "Toronto"),
    # --- Grupo J ---
    ("J", 1, "2026-06-16", "Argentina",       "Argelia",              "Kansas City"),
    ("J", 1, "2026-06-16", "Austria",         "Jordania",             "San Francisco"),
    ("J", 2, "2026-06-22", "Argentina",       "Austria",              "Dallas"),
    ("J", 2, "2026-06-22", "Jordania",        "Argelia",              "San Francisco"),
    ("J", 3, "2026-06-27", "Argelia",         "Austria",              "Kansas City"),
    ("J", 3, "2026-06-27", "Jordania",        "Argentina",            "Dallas"),
    # --- Grupo K ---
    ("K", 1, "2026-06-17", "Portugal",        "RD Congo",             "Houston"),
    ("K", 1, "2026-06-17", "Uzbekistan",      "Colombia",             "Ciudad de Mexico"),
    ("K", 2, "2026-06-23", "Portugal",        "Uzbekistan",           "Houston"),
    ("K", 2, "2026-06-23", "Colombia",        "RD Congo",             "Guadalajara"),
    ("K", 3, "2026-06-27", "Colombia",        "Portugal",             "Miami"),
    ("K", 3, "2026-06-27", "RD Congo",        "Uzbekistan",           "Atlanta"),
    # --- Grupo L ---
    ("L", 1, "2026-06-17", "Inglaterra",      "Croacia",              "Dallas"),
    ("L", 1, "2026-06-17", "Ghana",           "Panama",               "Toronto"),
    ("L", 2, "2026-06-23", "Inglaterra",      "Ghana",                "Boston"),
    ("L", 2, "2026-06-23", "Panama",          "Croacia",              "Toronto"),
    ("L", 3, "2026-06-27", "Panama",          "Inglaterra",           "Nueva York"),
    ("L", 3, "2026-06-27", "Croacia",         "Ghana",                "Filadelfia"),
]


def main():
    import csv
    grupos = defaultdict(list)
    with open(p("data", "selecciones.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            grupos[r["grupo"]].append(r["pais"])

    sedes = json.load(open(p("data", "sedes.json"), encoding="utf-8"))["sedes"]

    # Validacion: el calendario debe cubrir exactamente los 4 equipos de cada grupo,
    # 6 partidos por grupo, cada par una sola vez.
    equipos_csv = {g: set(v) for g, v in grupos.items()}
    por_grupo = defaultdict(list)
    for fila in CALENDARIO:
        por_grupo[fila[0]].append(fila)
    for g in sorted(equipos_csv):
        partidos_g = por_grupo[g]
        if len(partidos_g) != 6:
            raise SystemExit(f"Grupo {g}: {len(partidos_g)} partidos en CALENDARIO (se esperaban 6)")
        equipos_cal = set()
        pares = set()
        for _, _, _, a, b, sede in partidos_g:
            equipos_cal |= {a, b}
            if sede not in sedes:
                raise SystemExit(f"Sede desconocida en CALENDARIO: {sede!r} (grupo {g})")
            par = frozenset({a, b})
            if par in pares:
                raise SystemExit(f"Par repetido en grupo {g}: {a} vs {b}")
            pares.add(par)
        if equipos_cal != equipos_csv[g]:
            raise SystemExit(f"Grupo {g}: equipos del CALENDARIO {equipos_cal} != CSV {equipos_csv[g]}")

    # Construir los partidos con id estable {grupo}{jornada}{A/B}
    partidos = []
    n_altura = 0
    contador_jornada = defaultdict(int)  # (grupo, jornada) -> 0,1 -> sufijo A,B
    for g, jornada, fecha, a, b, sede in CALENDARIO:
        k = contador_jornada[(g, jornada)]
        contador_jornada[(g, jornada)] += 1
        info = sedes[sede]
        if info["altitud_m"] >= 1000:
            n_altura += 1
        partidos.append({
            "id": f"{g}{jornada}{'AB'[k]}",
            "grupo": g, "jornada": jornada, "fecha": fecha,
            "local": a, "visitante": b,
            "sede": sede, "pais_sede": info["pais"],
            "altitud_m": info["altitud_m"],
        })

    # Orden estable: por id (grupo, jornada, sufijo)
    partidos.sort(key=lambda m: m["id"])

    out = {
        "torneo": "Copa Mundial de la FIFA 2026",
        "formato": "48 equipos, 12 grupos de 4; avanzan 1os, 2os y 8 mejores 3os (32 a eliminacion directa)",
        "grupos": {g: grupos[g] for g in sorted(grupos)},
        "fase_grupos": partidos,
    }
    json.dump(out, open(p("data", "fixture_completo.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"Fixture generado: {len(partidos)} partidos ({n_altura} en sedes de altura >=1000 m) "
          f"-> data/fixture_completo.json")


if __name__ == "__main__":
    main()
