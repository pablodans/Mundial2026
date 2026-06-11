# Resultados de la prediccion — Mundial 2026

Modelo **Elo observado + altitud + desgaste + presion + Poisson + Monte Carlo** · **300 simulaciones** · semilla `2026` (reproducible).

## 🏆 Campeon mas probable (moda): **Espana** — 80/300 (26.7%)

> Error estandar de la probabilidad de titulo del favorito: ±2.55 pts con 300 simulaciones. Sube `--sims` para estabilizar.

## Tabla de probabilidades (top 24 por % de titulo)

| # | Seleccion | Gr | Elo | Avanza | Cuartos | Semis | Final | **Titulo** | Pts grupo |
|---|-----------|:--:|:---:|:------:|:-------:|:-----:|:-----:|:----------:|:---------:|
| 1 | Espana | H | 2155 | 100% | 66% | 53% | 40% | **26.7%** | 7.95 |
| 2 | Argentina | J | 2113 | 99% | 58% | 39% | 25% | **13.3%** | 7.66 |
| 3 | Francia | I | 2062 | 99% | 52% | 31% | 20% | **10.0%** | 7.09 |
| 4 | Brasil | C | 1988 | 98% | 41% | 24% | 14% | **8.3%** | 6.95 |
| 5 | Inglaterra | L | 2021 | 99% | 43% | 26% | 16% | **8.0%** | 6.71 |
| 6 | Portugal | K | 1986 | 98% | 42% | 20% | 10% | **5.7%** | 6.46 |
| 7 | Alemania | E | 1922 | 99% | 34% | 18% | 8% | **3.7%** | 6.39 |
| 8 | Colombia | K | 1977 | 99% | 38% | 22% | 9% | **3.3%** | 6.60 |
| 9 | Ecuador | E | 1935 | 98% | 31% | 15% | 7% | **2.7%** | 6.74 |
| 10 | Mexico | A | 1868 | 97% | 28% | 14% | 5% | **2.7%** | 7.02 |
| 11 | Suiza | B | 1885 | 98% | 28% | 15% | 6% | **2.3%** | 6.31 |
| 12 | Croacia | L | 1908 | 94% | 26% | 13% | 5% | **2.3%** | 5.62 |
| 13 | Paises Bajos | F | 1944 | 94% | 28% | 11% | 5% | **2.0%** | 6.14 |
| 14 | Paraguay | D | 1833 | 76% | 18% | 6% | 3% | **2.0%** | 4.50 |
| 15 | Japon | F | 1906 | 92% | 28% | 13% | 6% | **1.7%** | 5.56 |
| 16 | Noruega | I | 1916 | 90% | 32% | 16% | 4% | **1.3%** | 5.28 |
| 17 | Uruguay | H | 1892 | 94% | 22% | 8% | 4% | **1.3%** | 5.15 |
| 18 | Belgica | G | 1888 | 98% | 26% | 11% | 1% | **0.7%** | 6.52 |
| 19 | Austria | J | 1800 | 85% | 19% | 5% | 1% | **0.7%** | 4.57 |
| 20 | Suecia | F | 1745 | 74% | 8% | 3% | 1% | **0.7%** | 3.91 |
| 21 | Turquia | D | 1816 | 75% | 17% | 6% | 2% | **0.3%** | 4.24 |
| 22 | Chequia | A | 1733 | 70% | 9% | 3% | 1% | **0.3%** | 3.82 |
| 23 | Canada | B | 1793 | 93% | 15% | 6% | 3% | **0.0%** | 5.78 |
| 24 | Corea del Sur | A | 1756 | 81% | 15% | 5% | 2% | **0.0%** | 4.32 |

## Factores del modelo

- **Fuerza base**: Elo observado de eloratings.net (observable cuantitativo objetivo).
- **Altitud**: penalizacion Elo a equipos no adaptados que juegan en sedes de altura (Ciudad de Mexico 2240 m, Guadalajara 1566 m). Mexico, Ecuador, Colombia, Sudafrica e Iran apenas la sufren por su altitud de adaptacion.
- **Localia**: +Elo a los anfitriones (Mexico, EE.UU., Canada) jugando en su pais.
- **Desgaste**: la fatiga se acumula partido a partido (mas con prorrogas) y se recupera parcialmente con el descanso; penaliza mas en rondas avanzadas.
- **Presion**: en la 3a jornada de grupos, el equipo obligado a ganar recibe un empuje y el partido se abre (mas goles, mas varianza).
- **Condicionamiento**: los resultados reales cargados se fijan; solo se simula lo pendiente.

*Reproducir: `python scripts/run_prediccion.py`. Cargar resultados: `python scripts/actualizar_resultados.py`.*
