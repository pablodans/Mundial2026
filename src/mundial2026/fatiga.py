# -*- coding: utf-8 -*-
"""
Modelo de desgaste acumulado a lo largo del torneo.

La fatiga de cada seleccion crece con cada partido jugado (mas si hubo prorroga)
y se recupera parcialmente con el descanso entre partidos. Como la penalizacion
Elo por fatiga (ver modelo.penalizacion_fatiga) es creciente, el desgaste pesa
mas en las rondas finales: justo el "el campeonato pasa factura conforme avanza".
"""


def fatiga_tras_jugar(fatiga_previa, par, hubo_prorroga=False):
    """Nueva fatiga acumulada despues de disputar un partido y descansar hasta el siguiente."""
    carga = par.FAT_CARGA_PARTIDO + (par.FAT_CARGA_PRORROGA if hubo_prorroga else 0.0)
    return (fatiga_previa + carga) * par.FAT_RECUPERA


def nuevo_registro_fatiga(selecciones):
    return {pais: 0.0 for pais in selecciones}
