# Resultados de la prediccion — Mundial 2026

Modelo **Elo observado + altitud + desgaste + presion + Poisson + Monte Carlo** · **80000 simulaciones** · semilla `2026` (reproducible).

> Prediccion **condicionada** a 24 partido(s) ya jugado(s) (cargados en `data/resultados_reales.json`).

## 🏆 Campeon mas probable (moda): **Espana** — 16146/80000 (20.2%)

> Error estandar de la probabilidad de titulo del favorito: ±0.14 pts con 80000 simulaciones. Sube `--sims` para estabilizar.

## Tabla de probabilidades (top 16 por % de titulo)

| # | Seleccion | Gr | Elo | Avanza | Cuartos | Semis | Final | **Titulo** | Pts grupo |
|---|-----------|:--:|:---:|:------:|:-------:|:-----:|:-----:|:----------:|:---------:|
| 1 | Espana | H | 2127 | 98% | 60% | 44% | 30% | **20.2%** | 6.05 |
| 2 | Argentina | J | 2117 | 100% | 60% | 43% | 29% | **18.9%** | 7.94 |
| 3 | Francia | I | 2071 | 100% | 54% | 36% | 22% | **12.8%** | 7.50 |
| 4 | Inglaterra | L | 2052 | 100% | 50% | 32% | 19% | **10.5%** | 8.24 |
| 5 | Colombia | K | 1994 | 100% | 42% | 24% | 13% | **6.1%** | 7.25 |
| 6 | Brasil | C | 1970 | 96% | 38% | 21% | 10% | **4.6%** | 5.63 |
| 7 | Portugal | K | 1959 | 84% | 31% | 17% | 8% | **3.5%** | 4.45 |
| 8 | Paises Bajos | F | 1941 | 97% | 34% | 17% | 8% | **3.3%** | 5.60 |
| 9 | Noruega | I | 1931 | 99% | 33% | 17% | 8% | **3.0%** | 6.14 |
| 10 | Alemania | E | 1929 | 100% | 33% | 17% | 7% | **2.9%** | 6.85 |
| 11 | Japon | F | 1909 | 95% | 30% | 14% | 6% | **2.2%** | 5.44 |
| 12 | Mexico | A | 1876 | 100% | 26% | 12% | 4% | **1.5%** | 7.50 |
| 13 | Ecuador | E | 1881 | 86% | 23% | 10% | 4% | **1.5%** | 3.95 |
| 14 | Croacia | L | 1877 | 87% | 23% | 10% | 4% | **1.4%** | 4.47 |
| 15 | Belgica | G | 1866 | 89% | 23% | 10% | 4% | **1.3%** | 4.98 |
| 16 | Suiza | B | 1859 | 85% | 21% | 9% | 3% | **1.1%** | 4.60 |

## Factores del modelo

- **Fuerza base**: Elo observado de eloratings.net (observable cuantitativo objetivo).
- **Altitud**: penalizacion Elo a equipos no adaptados que juegan en sedes de altura (Ciudad de Mexico 2240 m, Guadalajara 1566 m). Mexico, Ecuador, Colombia, Sudafrica e Iran apenas la sufren por su altitud de adaptacion.
- **Localia**: +Elo a los anfitriones (Mexico, EE.UU., Canada) jugando en su pais.
- **Desgaste**: la fatiga se acumula partido a partido (mas con prorrogas) y se recupera parcialmente con el descanso; penaliza mas en rondas avanzadas.
- **Presion**: en la 3a jornada de grupos, el equipo obligado a ganar recibe un empuje y el partido se abre (mas goles, mas varianza).
- **Condicionamiento**: los resultados reales cargados se fijan; solo se simula lo pendiente.

*Reproducir: `python scripts/run_prediccion.py`. Cargar resultados: `python scripts/actualizar_resultados.py`.*
