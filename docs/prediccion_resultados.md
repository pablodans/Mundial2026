# Resultados de la prediccion — Mundial 2026

Modelo **Elo observado + altitud + desgaste + presion + Poisson + Monte Carlo** · **10000 simulaciones** · semilla `2026` (reproducible).

## 🏆 Campeon mas probable (moda): **Espana** — 2420/10000 (24.2%)

> Error estandar de la probabilidad de titulo del favorito: ±0.43 pts con 10000 simulaciones. Sube `--sims` para estabilizar.

## Tabla de probabilidades (top 8 por % de titulo)

| # | Seleccion | Gr | Elo | Avanza | Cuartos | Semis | Final | **Titulo** | Pts grupo |
|---|-----------|:--:|:---:|:------:|:-------:|:-----:|:-----:|:----------:|:---------:|
| 1 | Espana | H | 2155 | 100% | 64% | 48% | 35% | **24.2%** | 7.93 |
| 2 | Argentina | J | 2113 | 100% | 57% | 40% | 27% | **17.2%** | 7.73 |
| 3 | Francia | I | 2062 | 99% | 51% | 33% | 20% | **11.1%** | 7.02 |
| 4 | Inglaterra | L | 2021 | 99% | 43% | 27% | 15% | **7.7%** | 6.83 |
| 5 | Brasil | C | 1988 | 98% | 40% | 22% | 12% | **5.5%** | 6.83 |
| 6 | Portugal | K | 1986 | 98% | 40% | 21% | 11% | **5.1%** | 6.32 |
| 7 | Colombia | K | 1977 | 99% | 39% | 21% | 10% | **4.7%** | 6.60 |
| 8 | Paises Bajos | F | 1944 | 96% | 33% | 17% | 8% | **3.5%** | 6.09 |

## Factores del modelo

- **Fuerza base**: Elo observado de eloratings.net (observable cuantitativo objetivo).
- **Altitud**: penalizacion Elo a equipos no adaptados que juegan en sedes de altura (Ciudad de Mexico 2240 m, Guadalajara 1566 m). Mexico, Ecuador, Colombia, Sudafrica e Iran apenas la sufren por su altitud de adaptacion.
- **Localia**: +Elo a los anfitriones (Mexico, EE.UU., Canada) jugando en su pais.
- **Desgaste**: la fatiga se acumula partido a partido (mas con prorrogas) y se recupera parcialmente con el descanso; penaliza mas en rondas avanzadas.
- **Presion**: en la 3a jornada de grupos, el equipo obligado a ganar recibe un empuje y el partido se abre (mas goles, mas varianza).
- **Condicionamiento**: los resultados reales cargados se fijan; solo se simula lo pendiente.

*Reproducir: `python scripts/run_prediccion.py`. Cargar resultados: `python scripts/actualizar_resultados.py`.*
