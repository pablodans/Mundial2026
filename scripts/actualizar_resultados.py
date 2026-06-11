#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carga resultados reales conforme avanza el Mundial, para que la prediccion se
recalcule CONDICIONADA a lo ya ocurrido.

Fase de grupos (por id de partido del fixture, p.ej. A1A):
  python scripts/actualizar_resultados.py grupo A1A 2 1
  python scripts/actualizar_resultados.py listar            # ver ids y partidos pendientes

Fijar el cuadro oficial de 32 (orden de cruce, paises separados por coma):
  python scripts/actualizar_resultados.py bracket "Francia,Mexico,Brasil,..."

Resultado de un cruce de eliminacion (Ronda-indice base 0):
  python scripts/actualizar_resultados.py elim R32-0 Francia

Tras cargar, vuelve a ejecutar:  python scripts/run_prediccion.py
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from mundial2026 import datos  # noqa: E402

RUTA = datos.ruta("data", "resultados_reales.json")


def cargar_raw():
    d = json.load(open(RUTA, encoding="utf-8"))
    d.setdefault("fase_grupos", {})
    d.setdefault("bracket_r32", [])
    d.setdefault("eliminatorias", {})
    return d


def guardar(d):
    json.dump(d, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def listar():
    fixture = datos.cargar_fixture()
    reales = cargar_raw()["fase_grupos"]
    print(f"{'ID':6} {'Gr':>2} {'J':>1}  {'Local':22} {'Visitante':22} {'Sede':18} {'Resultado'}")
    print("-" * 100)
    for m in fixture["fase_grupos"]:
        r = reales.get(m["id"])
        marcador = f"{r['local_goles']}-{r['visitante_goles']}" if r else "pendiente"
        print(f"{m['id']:6} {m['grupo']:>2} {m['jornada']:>1}  {m['local']:22} "
              f"{m['visitante']:22} {m['sede']:18} {marcador}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]

    if cmd == "listar":
        listar()
        return

    d = cargar_raw()
    if cmd == "grupo":
        pid, gl, gv = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        fixture = datos.cargar_fixture()
        ids = {m["id"] for m in fixture["fase_grupos"]}
        if pid not in ids:
            raise SystemExit(f"ID de partido desconocido: {pid} (usa 'listar')")
        d["fase_grupos"][pid] = {"local_goles": gl, "visitante_goles": gv}
        print(f"Registrado {pid}: {gl}-{gv}")
    elif cmd == "bracket":
        equipos = [x.strip() for x in sys.argv[2].split(",") if x.strip()]
        if len(equipos) != 32:
            raise SystemExit(f"El bracket necesita 32 equipos (recibidos {len(equipos)})")
        validos = set(datos.cargar_selecciones())
        desconocidos = [e for e in equipos if e not in validos]
        if desconocidos:
            raise SystemExit(f"Equipo(s) desconocido(s): {', '.join(desconocidos)} "
                             f"(usa los nombres exactos de selecciones.csv)")
        d["bracket_r32"] = equipos
        print("Bracket oficial de 32 fijado.")
    elif cmd == "elim":
        clave, ganador = sys.argv[2], sys.argv[3]
        if ganador not in datos.cargar_selecciones():
            raise SystemExit(f"Equipo desconocido: {ganador} "
                             f"(usa el nombre exacto de selecciones.csv)")
        d["eliminatorias"][clave] = {"ganador": ganador}
        print(f"Registrado cruce {clave}: ganador {ganador}")
    else:
        print(__doc__)
        return
    guardar(d)
    print("Hecho. Ejecuta: python scripts/run_prediccion.py")


if __name__ == "__main__":
    main()
