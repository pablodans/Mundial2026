# Resultados de la prediccion — Mundial 2026

Modelo **Elo observado + altitud + desgaste + presion + Poisson + Monte Carlo** · **20000 simulaciones** · semilla `2026` (reproducible).

## 🏆 Campeon mas probable (moda): **Espana** — 4895/20000 (24.5%)

> Error estandar de la probabilidad de titulo del favorito: ±0.30 pts con 20000 simulaciones. Sube `--sims` para estabilizar.

## Tabla de probabilidades (top 16 por % de titulo)

| # | Seleccion | Gr | Elo | Avanza | Cuartos | Semis | Final | **Titulo** | Pts grupo |
|---|-----------|:--:|:---:|:------:|:-------:|:-----:|:-----:|:----------:|:---------:|
| 1 | Espana | H | 2155 | 100% | 64% | 48% | 35% | **24.5%** | 7.94 |
| 2 | Argentina | J | 2113 | 100% | 58% | 41% | 28% | **17.5%** | 7.75 |
| 3 | Francia | I | 2062 | 98% | 50% | 32% | 20% | **10.9%** | 7.02 |
| 4 | Inglaterra | L | 2021 | 99% | 44% | 26% | 15% | **7.5%** | 6.83 |
| 5 | Brasil | C | 1988 | 98% | 39% | 22% | 11% | **5.3%** | 6.89 |
| 6 | Portugal | K | 1986 | 98% | 39% | 22% | 11% | **5.2%** | 6.32 |
| 7 | Colombia | K | 1977 | 99% | 38% | 21% | 10% | **4.6%** | 6.58 |
| 8 | Paises Bajos | F | 1944 | 96% | 33% | 17% | 8% | **3.2%** | 6.16 |
| 9 | Ecuador | E | 1935 | 98% | 33% | 16% | 7% | **2.9%** | 6.66 |
| 10 | Alemania | E | 1922 | 98% | 31% | 15% | 6% | **2.6%** | 6.53 |
| 11 | Croacia | L | 1908 | 94% | 28% | 13% | 6% | **2.1%** | 5.56 |
| 12 | Japon | F | 1906 | 94% | 28% | 13% | 5% | **1.9%** | 5.69 |
| 13 | Noruega | I | 1916 | 90% | 28% | 13% | 5% | **1.9%** | 5.34 |
| 14 | Uruguay | H | 1892 | 91% | 25% | 11% | 5% | **1.7%** | 5.14 |
| 15 | Belgica | G | 1888 | 96% | 27% | 12% | 4% | **1.7%** | 6.46 |
| 16 | Suiza | B | 1885 | 97% | 26% | 12% | 4% | **1.6%** | 6.34 |

## Factores del modelo

- **Fuerza base**: Elo observado de eloratings.net (observable cuantitativo objetivo).
- **Altitud**: penalizacion Elo a equipos no adaptados que juegan en sedes de altura (Ciudad de Mexico 2240 m, Guadalajara 1566 m). Mexico, Ecuador, Colombia, Sudafrica e Iran apenas la sufren por su altitud de adaptacion.
- **Localia**: +Elo a los anfitriones (Mexico, EE.UU., Canada) jugando en su pais.
- **Desgaste**: la fatiga se acumula partido a partido (mas con prorrogas) y se recupera parcialmente con el descanso; penaliza mas en rondas avanzadas.
- **Presion**: en la 3a jornada de grupos, el equipo obligado a ganar recibe un empuje y el partido se abre (mas goles, mas varianza).
- **Condicionamiento**: los resultados reales cargados se fijan; solo se simula lo pendiente.

*Reproducir: `python scripts/run_prediccion.py`. Cargar resultados: `python scripts/actualizar_resultados.py`.*
