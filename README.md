# Predictor Monte Carlo — Mundial 2026

![Arquitectura del predictor](docs/diagrama_arquitectura.png)

Simulador probabilístico de la Copa Mundial de la FIFA 2026 (48 equipos, 12 grupos,
sedes en México, EE.UU. y Canadá). Estima probabilidades de avanzar, llegar a cada
ronda y ganar el título corriendo el torneo completo miles de veces.

El modelo parte de un **observable cuantitativo objetivo** (el Elo de
[eloratings.net](https://www.eloratings.net/)) y lo ajusta partido a partido por
**altitud**, **desgaste** y **presión**. Las predicciones se **recalculan
condicionadas a los resultados reales** que se van cargando conforme avanza el Mundial.

> El diagrama de arriba (fuentes de datos → modelo → Monte Carlo, y el bucle acumulativo)
> también está como vectorial en [docs/diagrama_arquitectura.svg](docs/diagrama_arquitectura.svg).
> Las imágenes PNG se regeneran con `python tools/render_arquitectura.py` y
> `python tools/render_bracket.py` (requieren Pillow; el modelo en sí no tiene dependencias).

## Uso rápido

```bash
# (Windows) el alias de la Store interfiere con "python"; usa la ruta del intérprete o py
python scripts/run_prediccion.py                 # 10.000 simulaciones (rápido), semilla 2026
python scripts/run_prediccion.py --sims 80000    # la predicción publicada del repo (más estable)
python tests/test_modelo.py                       # pruebas (también con pytest)
```

Salidas: [data/prediccion_resultados.json](data/prediccion_resultados.json) (ranking
completo) y [docs/prediccion_resultados.md](docs/prediccion_resultados.md) (resumen).

Sin dependencias externas: solo la librería estándar de Python 3.10+.

## El modelo

Cada equipo tiene un **Elo base** observado (eloratings.net, independiente del ranking
FIFA, que se guarda solo como referencia). En cada partido se calcula un *Elo efectivo*:

```
elo_eff = elo_base
          + localía         (anfitrión jugando en su país: México / EE.UU. / Canadá)
          − penal_altitud    (jugar en altura por encima de la altitud a la que el equipo se adapta)
          − penal_desgaste   (fatiga acumulada; crece con cada partido y prórroga, se recupera con descanso)
          + bonus_presión    (última jornada de grupos, equipo obligado a ganar)
```

Los goles de cada equipo son **Poisson** independientes con media
`λ = GOAL_BASE · factor_goles · (1 + apertura) · exp(±GAMMA · ΔElo_eff / ELO_DIV)`, donde
`factor_goles = 1` en la fase de grupos y `= KO_FACTOR (<1)` en eliminatorias. El **Elo
fija el favorito**; el **estilo** y la **presión** fijan el *carácter* del partido (la
`apertura`: más/menos goles y varianza, sin cambiar quién gana). En eliminatorias
`KO_FACTOR < 1` cierra los partidos (calibrado con el histórico). Eliminatorias:
90′ → prórroga → penales.

Agregación sobre las N corridas: **campeón = moda**; probabilidades = **frecuencia**;
puntos de grupo = **media**.

### Factores
- **Altura**: las sedes mexicanas (CDMX 2240 m, Guadalajara 1566 m) penalizan a los
  no adaptados; México, Ecuador, Colombia, Sudáfrica e Irán apenas la sufren. El
  **fixture es el calendario oficial**: los 72 partidos de grupos llevan su
  emparejamiento, fecha y sede reales del calendario publicado el 6-dic-2025
  (ver `scripts/construir_fixture.py`).
- **Desgaste**: la penalización por fatiga es creciente, así que pesa más en cuartos,
  semis y final, y se agrava con prórrogas y poco descanso.
- **Presión "ganar o nada"**: en la 3ª jornada de grupos un equipo con ≤3 puntos recibe
  empuje y juega un partido más abierto.
- **Estilo de juego**: cada selección tiene atributos (posesión, ofensivo/defensivo,
  ritmo) que abren o cierran el partido (`data/estilos.json`).
- **Histórico**: `data/historico_mundiales.json` (cruces de los 5 últimos Mundiales)
  calibra el modelo vía `scripts/calibrar.py` (de ahí sale `KO_FACTOR`).
- **Mejora con el torneo**: carga resultados reales y vuelve a predecir (ver abajo).

## Predicción por partido

Distribución exacta de un partido (sin simular), con todo el contexto (Elo, altitud,
localía, estilo):

```bash
python scripts/predecir_partido.py id H1A            # un partido del fixture por su id
python scripts/predecir_partido.py vs Argentina Mexico
python scripts/predecir_partido.py jornada 1         # todos los pendientes de la jornada
```

Devuelve **1X2** (gana/empata/pierde), **marcador más probable**, **top-5 marcadores**,
**over/under 2.5** y goles esperados. Incluye la corrección **Dixon-Coles** (`DC_RHO`),
que ajusta los marcadores bajos (sube empates 0-0/1-1) respecto al Poisson puro.

## Predicción en vivo y Elo dinámico (conforme se juega)

```bash
python scripts/actualizar_resultados.py listar                 # ids de partido y pendientes
python scripts/actualizar_resultados.py grupo A1A 2 1          # marcador real de un partido
python scripts/actualizar_resultados.py bracket "Eq1,...,Eq32" # fijar el cuadro oficial de 32
python scripts/actualizar_resultados.py elim R32-0 Francia     # ganador de un cruce
python scripts/run_prediccion.py                               # re-predice condicionado
```

Cada resultado cargado hace dos cosas: (1) **se fija** (no se resimula) y (2) **mueve el
Elo** de los equipos con la fórmula de eloratings (margen de goles + **K adaptativo**: el
primer resultado mueve más el Elo y los siguientes menos, al haber más información). Así la
predicción del partido 2 usa el Elo actualizado por el partido 1, la del 3 por el 1+2,
etc. — el bucle de aprendizaje que mejora cada jornada. Para una predicción 100% a priori,
deja [data/resultados_reales.json](data/resultados_reales.json) vacío.

## Estructura

```
data/      selecciones.csv · estilos.json · sedes.json · fixture_completo.json · jugadores.json
           historico_mundiales.json · elo_historico.json · resultados_reales.json
src/mundial2026/   datos · modelo · fatiga · torneo · montecarlo · elo_dinamico · prediccion_partido
scripts/   construir_fixture.py · run_prediccion.py · predecir_partido.py · predecir_bracket.py
           mc_jornada.py · actualizar_resultados.py · calibrar.py
tools/     render_arquitectura.py · render_bracket.py · assets_lib.py   (PNGs del README; usan Pillow)
tests/     test_modelo.py
docs/      prediccion_resultados.md · diagrama_arquitectura.(svg|png) · bracket_prediccion.png  (generados)
```

## Datos y fuentes

48 selecciones con: Elo (eloratings.net), ranking y puntos FIFA, valor de mercado de
plantilla (Transfermarkt), palmarés e historial mundialista (títulos, participaciones,
finales, semifinales), altitud de adaptación y atributos de estilo. Más 5 jugadores
clave por selección **incluido el portero** (`jugadores.json`), cruces de los 5 últimos
Mundiales (`historico_mundiales.json`) y las 16 sedes con su altitud (`sedes.json`).
Grupos del sorteo oficial del 5-dic-2025. Recopilado en junio 2026; cifras de equipos
fuera del top-50 FIFA estimadas y marcadas como tales.

> **Elo vs FIFA, jugadores**: el Elo y el ranking FIFA son sistemas distintos y ambos
> miden *selecciones*, no jugadores. El modelo usa el Elo como fuerza base; el ranking
> FIFA es solo referencia. Los jugadores clave (y el portero) son **contexto informativo**
> en los datos: la fuerza del equipo ya está en el Elo/valor, así que no se vuelven a
> contar como input del motor para no duplicar el efecto.

## Calibración (con datos reales)

`scripts/calibrar.py` calibra el modelo contra el histórico, en dos partes:

1. **Tasas agregadas** de la fase eliminatoria (goles/equipo, % prórroga, % penales)
   del modelo vs los 5 últimos Mundiales → de aquí sale `KO_FACTOR` (los partidos de
   eliminación son más cerrados).
2. **Backtest por máxima verosimilitud**: usando el **Elo pre-Mundial real**
   ([data/elo_historico.json](data/elo_historico.json), de eloratings.net) y los
   **marcadores reales** de 80 cruces, ajusta el coeficiente Elo→goles (de donde sale
   **`ELO_DIV`**) y `GOAL_BASE` maximizando la verosimilitud Poisson.

El backtest también sugiere el `DC_RHO` de Dixon-Coles (ρ<0, más empates bajos).

Resultados del backtest: el favorito por Elo gana el **70 %** de los cruces KO (el 30 %
restante son las sorpresas reales del fútbol), `ELO_DIV` óptimo ~250 y `KO_FACTOR` ~0.87.
Salvedades honestas: (1) el backtest se apoya en 80 cruces de equipos relativamente
parejos, así que extrapolar a duelos muy desiguales de grupos tiene incertidumbre; (2) el
ρ óptimo crudo sale exagerado por el exceso de empates de la muestra KO (partidos a
prórroga), por eso se adopta un `DC_RHO=-0.10` moderado (rango de literatura). El resto de
coeficientes (altitud, fatiga, presión, localía, estilo, K adaptativo) están en
[src/mundial2026/modelo.py](src/mundial2026/modelo.py) y son ajustables.

## Predicción completa del torneo (cuadro previsto)

La predicción **completa** sale del Monte Carlo (`run_prediccion.py`): probabilidades de
avanzar / llegar a cada ronda / ser campeón para las 48 selecciones. La predicción
publicada aquí se obtuvo simulando el torneo completo **80.000 veces**. A partir de ahí,
`predecir_bracket.py` arma el **camino más probable** desde la R32 hasta el título —el
ganador previsto de cada cruce según el modelo— y lo dibuja:

```bash
python scripts/run_prediccion.py --sims 80000   # probabilidades completas (data/ + docs/)
python scripts/predecir_bracket.py              # cuadro R32 -> campeón (data/prediccion_bracket.json)
python tools/render_bracket.py                  # PNG del cuadro (requiere Pillow)
```

![Cuadro previsto del Mundial 2026](docs/bracket_prediccion.png)

> ⚠️ **Esta predicción cambia ronda a ronda.** El cuadro de arriba es la foto de **hoy**,
> *antes de arrancar el Mundial* (predicción 100 % a priori). Cada vez que se cargan
> resultados reales con `actualizar_resultados.py`, el Elo dinámico se reajusta (K
> adaptativo), lo ya jugado se fija en vez de simularse, y tanto las probabilidades como
> el cuadro previsto se **recalculan** — afinándose jornada a jornada. El campeón previsto,
> los cruces y los porcentajes de hoy **no son** los que verás tras la fase de grupos.

El cuadro respeta el esqueleto **oficial** de la R32 (las llaves 1E–3ABCDF, etc.); los
8 mejores terceros se asignan a sus huecos respetando los grupos elegibles de cada llave.
El % de cada caja es la probabilidad que da el modelo a ese equipo de ganar ese cruce.

> Nota: cuando varios terceros podrían encajar en varios huecos, se toma **una** asignación
> válida (la primera que satisface las elegibilidades), que puede no coincidir con la tabla
> exacta (Anexo C) que aplicaría la FIFA en ese escenario concreto. El esqueleto de llaves y
> las elegibilidades sí son las oficiales.

## Bitácora — corazonada de la jornada 2

> Anotado el **18-jun-2026**, antes de jugarse la jornada 2. **Esto NO es la salida del
> modelo** (las probabilidades frías están en [docs/prediccion_resultados.md](docs/prediccion_resultados.md)
> y el top-3 de marcadores sale de `predecir_partido.py`). Es un *pick* **subjetivo**: de los
> 3 marcadores más probables de cada partido elijo **uno** (★), guiado por lo que se vio de
> verdad en la ronda 1 — quién remató mucho sin convertir, qué defensas hicieron agua y qué
> arqueros están en racha. Cuando se juegue la jornada comparamos: probabilidad fría vs corazonada.

| Partido | Top-3 (★ = pick) | Por qué, según la J1 |
|---|---|---|
| Chequia–Sudáfrica | 1-1 · **★2-1** · 2-0 | Chequia filtró 2 con Corea; Sudáfrica no marcó pero esto es a todo o nada |
| México–Corea del Sur | **★2-1** · 1-1 · 2-0 | México sólido y en altura; Corea ya demostró que hace goles |
| Suiza–Bosnia | **★2-0** · 1-1 · 2-1 | Suiza tiró 26 veces sin premio; ante Bosnia por fin convierte |
| Canadá–Catar | **★2-0** · 3-0 · 2-1 | Abunada no salva dos veces seguidas; Canadá de local |
| Escocia–Marruecos | 1-1 · 2-1 · **★1-2** | Escocia ganó siendo superada 20-3; Marruecos jugó mejor que Brasil |
| Brasil–Haití | **★3-0** · 2-0 · 4-0 | Brasil viene picado del 1-1; descarga contra el más débil |
| EE.UU.–Australia | 1-1 · **★2-1** · 1-2 | EE.UU. fue un avión (4-1); a Australia se le acaba la suerte del arquero |
| Turquía–Paraguay | 1-1 · 1-2 · **★2-1** | Turquía mereció ganarle a Australia (30 remates); Paraguay hizo agua |
| Alemania–Costa de Marfil | **★2-0** · 3-0 · 2-1 | Alemania a otro nivel, pero Marfil defiende mejor que Curazao |
| Ecuador–Curazao | **★3-0** · 2-0 · 4-0 | Ecuador dolido por perder; Curazao ya encajó 7 |
| Países Bajos–Suecia | 1-1 · **★2-1** · 2-0 | Naranja filtró 2 con Japón; Suecia (5 goles) te marca seguro |
| Túnez–Japón | 0-2 · **★0-3** · 0-4 | Japón brilló ante Países Bajos; a Túnez ya le hicieron 5 |
| Bélgica–Irán | 1-1 · **★2-1** · 1-0 | Bélgica fue floja, pero su jerarquía termina pesando; Irán igual marca |
| Nueva Zelanda–Egipto | **★1-1** · 1-0 · 2-1 | Los dos empataron y compiten; choque parejo de medianos |
| España–Arabia Saudita | 3-0 · **★2-0** · 4-0 | España gana sí o sí, pero Al-Owais (9 atajadas) le frena la goleada |
| Uruguay–Cabo Verde | 2-0 · **★1-1** · 2-1 | La corazonada del torneo: Uruguay sigue sin puntería y Vozinha vuelve a tapar todo |
| Francia–Irak | **★3-0** · 2-0 · 4-0 | Francia firme (3-1) contra un Irak que encajó 4 |
| Noruega–Senegal | **★2-1** · 2-0 · 1-1 | Haaland enchufado; Senegal tiene con qué descontar |
| Argentina–Austria | 2-0 · **★2-1** · 1-1 | Argentina manda, pero Austria (3 goles en J1) le hace uno |
| Jordania–Argelia | **★1-1** · 2-1 · 1-0 | Argelia fue inofensiva con Argentina; reacciona y reparten |
| Portugal–Uzbekistán | 2-0 · 1-1 · **★2-1** | Portugal gana pero sigue despilfarrando (Ronaldo falló 2 claras) |
| Colombia–RD Congo | 3-0 · 4-0 · **★2-0** | Colombia clínica, pero RD Congo le aguantó a Portugal: no será goleada |
| Inglaterra–Ghana | **★3-0** · 2-0 · 4-0 | Inglaterra hizo 4; Ghana ya dejó el arco en cero, pero acá no alcanza |
| Panamá–Croacia | **★0-2** · 1-1 · 0-1 | Panamá no marcó en J1; Modrić y Kovačić alcanzan |

**Las tres que más me laten (más allá de la probabilidad):**
1. **Uruguay 1-1 Cabo Verde** — si Vozinha repite lo de España, Uruguay (28 remates y 1 gol ante Arabia) se vuelve a frustrar. El batacazo emocional de la ronda.
2. **Escocia 1-2 Marruecos** — Escocia ganó "robando"; Marruecos jugó de igual a igual con Brasil. Me late que se da vuelta el favoritismo del modelo.
3. **España 2-0 Arabia** — gana España, pero con Al-Owais en racha no hay goleada.

## Licencia y descargo de responsabilidad

Este proyecto se publica bajo la licencia **MIT** (ver [LICENSE](LICENSE)): cualquiera
puede usarlo, copiarlo, modificarlo y distribuirlo libremente.

> ⚠️ **Descargo de responsabilidad.** Este software es un ejercicio estadístico y se
> ofrece **"tal cual", sin garantía de ningún tipo**. Las predicciones, probabilidades,
> cuadros y resultados que genera son **estimaciones de un modelo**, no hechos ni
> certezas, y **pueden ser erróneos**. El autor **no se responsabiliza** de ningún
> efecto, decisión, resultado, pérdida o daño —económico o de cualquier otra índole—
> derivado del uso de este algoritmo o de sus salidas. **Quien lo use lo hace bajo su
> propia y exclusiva responsabilidad.** En particular, esto **no es** consejo de apuestas
> ni asesoramiento financiero; apostar conlleva riesgo y es responsabilidad de cada uno.
