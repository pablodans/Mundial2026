# Resultados de la prediccion — Mundial 2026

Modelo **Elo observado + altitud + desgaste + presion + Poisson + Monte Carlo** · **80000 simulaciones** · semilla `2026` (reproducible).

> Prediccion **condicionada** a 48 partido(s) ya jugado(s) (cargados en `data/resultados_reales.json`).

## 🏆 Campeon mas probable (moda): **Espana** — 16235/80000 (20.3%)

> Error estandar de la probabilidad de titulo del favorito: ±0.14 pts con 80000 simulaciones. Sube `--sims` para estabilizar.

## Tabla de probabilidades (top 12 por % de titulo)

| # | Seleccion | Gr | Elo | Avanza | Cuartos | Semis | Final | **Titulo** | Pts grupo |
|---|-----------|:--:|:---:|:------:|:-------:|:-----:|:-----:|:----------:|:---------:|
| 1 | Espana | H | 2131 | 100% | 61% | 44% | 31% | **20.3%** | 6.31 |
| 2 | Argentina | J | 2130 | 100% | 61% | 44% | 30% | **19.9%** | 8.73 |
| 3 | Francia | I | 2077 | 100% | 54% | 36% | 22% | **12.7%** | 7.84 |
| 4 | Inglaterra | L | 2029 | 100% | 47% | 28% | 16% | **8.2%** | 6.49 |
| 5 | Colombia | K | 1996 | 100% | 42% | 24% | 12% | **6.0%** | 7.43 |
| 6 | Portugal | K | 1978 | 100% | 40% | 22% | 11% | **5.0%** | 5.31 |
| 7 | Brasil | C | 1977 | 100% | 39% | 22% | 11% | **4.8%** | 6.05 |
| 8 | Paises Bajos | F | 1967 | 100% | 38% | 20% | 10% | **4.2%** | 6.71 |
| 9 | Noruega | I | 1941 | 100% | 35% | 18% | 8% | **3.2%** | 6.92 |
| 10 | Alemania | E | 1936 | 100% | 34% | 17% | 8% | **3.1%** | 7.53 |
| 11 | Japon | F | 1916 | 100% | 31% | 15% | 6% | **2.2%** | 5.88 |
| 12 | Mexico | A | 1891 | 100% | 28% | 13% | 5% | **1.7%** | 8.45 |

## Factores del modelo

- **Fuerza base**: Elo observado de eloratings.net (observable cuantitativo objetivo).
- **Altitud**: penalizacion Elo a equipos no adaptados que juegan en sedes de altura (Ciudad de Mexico 2240 m, Guadalajara 1566 m). Mexico, Ecuador, Colombia, Sudafrica e Iran apenas la sufren por su altitud de adaptacion.
- **Localia**: +Elo a los anfitriones (Mexico, EE.UU., Canada) jugando en su pais.
- **Desgaste**: la fatiga se acumula partido a partido (mas con prorrogas) y se recupera parcialmente con el descanso; penaliza mas en rondas avanzadas.
- **Presion**: en la 3a jornada de grupos, el equipo obligado a ganar recibe un empuje y el partido se abre (mas goles, mas varianza).
- **Condicionamiento**: los resultados reales cargados se fijan; solo se simula lo pendiente.

*Reproducir: `python scripts/run_prediccion.py`. Cargar resultados: `python scripts/actualizar_resultados.py`.*
