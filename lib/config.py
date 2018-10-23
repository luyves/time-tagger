# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 15:26:44 2018

@author: Luis Villegas
"""
# Time tags
timestamp_count = 1000000 # buffer size (i.e. number of events saved in memory at any given time).
channels_enabled = 0xff # all channels.
# Time differences histogram
binwidth = 10000 # in timebase units. 1 timebase units roughly equals 81 ps.
bincount = 5000 # number of bins in the histogram.
# Coincidence counters
exposure_time = 100 # in milliseconds.
coincidence_window = 100 # in bins.
# Saving files
"""
Recomiendo guardar los datos tomando en cuenta que incluyan lo siguiente:
+ Iniciales del proyecto (e.g. 'MOT')
+ Identificador o acrónimo del experimento (e.g. 'FWM')
+ Iniciales de quien realiza el experimento (e.g. 'LYV')
+ La extensión de archivo. Inicialmente y para archivos medianos, usar '.bin' o '.dat' puede funcionar bien. Sin embargo, a medida que se diseñen experimentos que generen muchos más datos, recomiendo acercarse a utilizar HDF5 (para todo lo que necesiten saber al respecto: https://bit.ly/2uUWltH)

El programa asigna la fecha actual (y la hora con minutos) de experimento de manera automática. Uno puede verificar el formato del nombre de archivo con el que se guardará en la ventana princial junto a la etiqueta de 'Save as'.

Un nombre de archivo adecuado podría ser '180819-1024_MOT_FWM_LYV.dat'.

Hay dos maneras de generar archivos de datos de acuerdo al parámetro <cont> (de "continouous"):
+ Un sólo archivo, sin límite superior de eventos registrados. (cont=True)
+ Múltiples archivos con <timestamp_count> eventos en cada uno. (cont=False)
"""
cont = True
filename = 'G2L_APDs_' # CC for 'Classical Correlations'
file_extension = '.bin'
total_runs = '20' # total number of data files to be created; irrelevant if cont=True
