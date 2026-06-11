# Resultados de la prediccion — Mundial 2026

Modelo **Elo observado + altitud + desgaste + presion + Poisson + Monte Carlo** · **10000 simulaciones** · semilla `2026` (reproducible).

## 🏆 Campeon mas probable (moda): **Espana** — 2479/10000 (24.8%)

> Error estandar de la probabilidad de titulo del favorito: ±0.43 pts con 10000 simulaciones. Sube `--sims` para estabilizar.

## Tabla de probabilidades (top 24 por % de titulo)

| # | Seleccion | Gr | Elo | Avanza | Cuartos | Semis | Final | **Titulo** | Pts grupo |
|---|-----------|:--:|:---:|:------:|:-------:|:-----:|:-----:|:----------:|:---------:|
| 1 | Espana | H | 2155 | 100% | 64% | 48% | 35% | **24.8%** | 7.94 |
| 2 | Argentina | J | 2113 | 100% | 58% | 41% | 28% | **17.7%** | 7.76 |
| 3 | Francia | I | 2062 | 98% | 50% | 32% | 20% | **11.0%** | 7.02 |
| 4 | Inglaterra | L | 2021 | 99% | 45% | 27% | 15% | **7.6%** | 6.84 |
| 5 | Brasil | C | 1988 | 98% | 40% | 23% | 11% | **5.3%** | 6.90 |
| 6 | Portugal | K | 1986 | 98% | 39% | 22% | 11% | **4.9%** | 6.33 |
| 7 | Colombia | K | 1977 | 99% | 38% | 21% | 11% | **4.7%** | 6.58 |
| 8 | Paises Bajos | F | 1944 | 96% | 33% | 17% | 8% | **3.0%** | 6.14 |
| 9 | Ecuador | E | 1935 | 98% | 32% | 16% | 7% | **2.8%** | 6.66 |
| 10 | Alemania | E | 1922 | 98% | 30% | 15% | 7% | **2.6%** | 6.54 |
| 11 | Croacia | L | 1908 | 94% | 28% | 13% | 6% | **2.1%** | 5.55 |
| 12 | Noruega | I | 1916 | 90% | 28% | 13% | 6% | **2.0%** | 5.33 |
| 13 | Japon | F | 1906 | 94% | 28% | 13% | 5% | **1.9%** | 5.71 |
| 14 | Suiza | B | 1885 | 97% | 26% | 12% | 5% | **1.6%** | 6.35 |
| 15 | Uruguay | H | 1892 | 92% | 25% | 11% | 4% | **1.6%** | 5.17 |
| 16 | Belgica | G | 1888 | 96% | 27% | 12% | 4% | **1.6%** | 6.49 |
| 17 | Mexico | A | 1868 | 98% | 25% | 11% | 4% | **1.0%** | 7.03 |
| 18 | Paraguay | D | 1833 | 76% | 16% | 6% | 2% | **0.7%** | 4.43 |
| 19 | Turquia | D | 1816 | 73% | 14% | 5% | 2% | **0.6%** | 4.25 |
| 20 | Austria | J | 1800 | 82% | 15% | 5% | 2% | **0.5%** | 4.41 |
| 21 | Canada | B | 1793 | 96% | 16% | 5% | 1% | **0.3%** | 6.09 |
| 22 | Escocia | C | 1770 | 78% | 12% | 4% | 1% | **0.2%** | 4.23 |
| 23 | Iran | G | 1764 | 85% | 13% | 4% | 1% | **0.2%** | 4.87 |
| 24 | Marruecos | C | 1755 | 76% | 11% | 3% | 1% | **0.2%** | 4.08 |

## Factores del modelo

- **Fuerza base**: Elo observado de eloratings.net (observable cuantitativo objetivo).
- **Altitud**: penalizacion Elo a equipos no adaptados que juegan en sedes de altura (Ciudad de Mexico 2240 m, Guadalajara 1566 m). Mexico, Ecuador, Colombia, Sudafrica e Iran apenas la sufren por su altitud de adaptacion.
- **Localia**: +Elo a los anfitriones (Mexico, EE.UU., Canada) jugando en su pais.
- **Desgaste**: la fatiga se acumula partido a partido (mas con prorrogas) y se recupera parcialmente con el descanso; penaliza mas en rondas avanzadas.
- **Presion**: en la 3a jornada de grupos, el equipo obligado a ganar recibe un empuje y el partido se abre (mas goles, mas varianza).
- **Condicionamiento**: los resultados reales cargados se fijan; solo se simula lo pendiente.

*Reproducir: `python scripts/run_prediccion.py`. Cargar resultados: `python scripts/actualizar_resultados.py`.*
