# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 16:01:10 2018

@author: Luis Villegas
"""
from ctypes import WinDLL,c_long,cast,create_string_buffer,POINTER,byref,c_int,c_uint,c_ubyte
from os import path,chdir
from time import sleep

dll_path_b = None

if dll_path_b is not None:
    pass
else:
#    dll_path = path.join(path.dirname(__file__),'tdcbase.dll')
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

rs = lib.TDC_setTimestampBufferSize(timestamp_count)
switch(rs)

rs = lib.TDC_setExposureTime(100)
switch(rs)
rs = lib.TDC_setCoincidenceWindow(100) # 8ns
switch(rs)

channelMask = c_ubyte()
coincWin = c_uint()
expTime = c_uint()

lib.TDC_getDeviceParams.argtypes = [c_int,c_int,c_int]

lib.TDC_getDeviceParams(channelMask,coincWin,expTime)

test_channel = 3
signal_period = 4 #4*20ns = 80ns
signal_burst = 3
burst_distance = 10 #10*80ns = 800ns

rs = lib.TDC_configureSelfTest(test_channel,signal_period,
                               signal_burst,burst_distance)
print(">>> Setting up self test")
switch(rs)

print(">>> Collecting")
sleep(5)
lib.TDC_freezeBuffers(1)

array_type = c_int*timestamp_count

timestamps = array_type()
timestamps_ptr = cast(timestamps, POINTER(c_int))
chans = array_type()
chans_ptr = cast(timestamps, POINTER(c_int))
valid = c_int()
valid_ptr = cast(timestamps, POINTER(c_int))

lib.TDC_getLastTimestamps.argtypes = [c_int, POINTER(c_int),
                                      POINTER(c_int), POINTER(c_int)]
rs = lib.TDC_getLastTimestamps(1,timestamps_ptr,chans_ptr,valid_ptr)
switch(rs)

lib.TDC_deInit()