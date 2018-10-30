# Config file for hunahpy objects


### TDC config ###
""" This two parameters are ALWAYS necessary for a TDC object """
timestamp_count = 1000000 # buffer size (i.e. number of events saved in memory at any given time)
channels_enabled = 0xff # all channels


### GUI ###
""" These parameters only affect the graphical user interface (GUI) """
# Histogram
binwidth = 10000 # in timebase units, 1 timebase units roughly equals 81 ps
bincount = 5000 # number of bins in the histogram
# Coincidence counters
exposure_time = 100 # in milliseconds
coincidence_window = 100 # in bins

""" These parameters only affect the graphical user interface (GUI) """
# How to save files:
# cont=True  generates ONLY ONE data file with all registered time-tags.
#			 Default value.
# cont=False generates <total_runs> = n data files with <timestamp_count> total
#            events each.
#			 Recommended for initial experiments to prevent computer crashes.
#
# Data files generated will have the following syntax:
#		'YYMMDD-HHMM_filename.file_extension'
# Example:
#		'180617-1604_testing.bin'
cont = True
total_runs = '20' # if cont=False, total number of data files to be created
filename = 'testing'
file_extension = '.bin'

