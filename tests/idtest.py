# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 16:01:10 2018

@author: Luis Villegas
"""
from ctypes import CDLL, WinDLL,c_long,create_string_buffer,POINTER,byref,c_int,c_uint,c_ubyte
from os import path,chdir

dll_path_b = None

if dll_path_b is not None:
    pass
else:
    dll_path = path.join(path.dirname(__file__),'tdcbase.dll')
    dll_path = "C:\\Users\\Luis Villegas\\Documents\\Física\\LANMAC\\acqsys\\time-tagger\\tdcbase.dll"
#dll_path = "tdcbase.dll"

lib = WinDLL(dll_path)

serial = create_string_buffer(10)
null_ptr = POINTER(c_int)()

def switch(rs):
    if rs == 0: #TDC_Ok
        print("Success")
    elif rs == -1: #TDC_Error
        print("Unspecified error")
    elif rs == 1: #TDC_Timeout
        print("Receive timed out")
    elif rs == 2: #TDC_NotConnected
        print("No connection was established")
    elif rs == 3: #TDC_DriverError
        print("Error accessing the USB driver")
    elif rs == 7: #TDC_DeviceLocked
        print("Can't connect device beause already in use")
    elif rs == 8: #TDC_Unknown
        print("Unknown error")
    elif rs == 9: #TDC_NoDevice
        print("Invalid device number used in call")
    elif rs == 10: #TDC_OutOfRange
        print("Parameter in func. call is out of range")
    elif rs == 11: #TDC_CantOpen
        print("Failed to open specified file")
    else:
        print("????")
    return

timebase = lib.TDC_getTimebase()
print("Timebase {} ps".format(timebase))
rs = lib.TDC_init(-1)

switch(rs)
channels = 0xff

#print("Enabling channel %i",channels)
rs = lib.TDC_enableChannels(channels)
switch(rs)

hist_bincount = 40
binwidth = 250
timestamp_count = 10000
rs = lib.TDC_setHistogramParams(binwidth,hist_bincount)
print(">>> Setting histogram params")
switch(rs)
rs = lib.TDC_setTimestampBufferSize(timestamp_count)
switch(rs)

rs = lib.TDC_setExposureTime(100)
switch(rs)
rs = lib.TDC_setCoincidenceWindow(100) # 8ns
switch(rs)

argc = 2
argv = "test"

if (argc > 1 and argv!="gen"):
    testchan = 3
    sgperiod = 4 #4*20ns
    sgburst = 3
    distburst = 10 #10*80ns
    rs = lib.TDC_configureSelftest(3,4,3,10)
    switch(rs)


lib.TDC_deInit()