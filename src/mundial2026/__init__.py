"""
Predictor Monte Carlo del Mundial 2026.

Modelo: fuerza base = Elo observado (eloratings.net) ajustado dinamicamente por
altitud de la sede, desgaste acumulado y presion de "ganar si o si"; goles ~ Poisson;
fase de grupos + eliminacion directa simuladas N veces. Las predicciones se
condicionan a los resultados reales que se vayan cargando en data/resultados_reales.json.
"""
__version__ = "1.0.0"
