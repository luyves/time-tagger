# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 15:08:31 2018

@author: Luis Villegas
"""

from ctypes import WinDLL,c_long,create_string_buffer,POINTER,byref,c_int,c_uint,c_ubyte
from time import sleep
import os


class TDC:
    def __init__(self, libpath = None):
        if libpath is not None:
            self.libpath = libpath
        else:
            self.libpath = os.path.join(os.path.dirname(__file__),'tdcbase.dll')
        self.dll_lib = WinDLL(self.libpath)
        
        # Timebase
        self.timebase = self.dll_lib.TDC_getTimeBase()
        
        # Activate
        rs = self.dll_lib.TDC_init(-1) # Accept every device
        self.switch(rs)
        
        # Select channels to use (id800 userguide)
        # 0 = none         8 = 4
        # 1 = 1            9 = 1,4
        # 2 = 2           10 = 2,4
        # 3 = 1,2         11 = 1,2,4
        # 4 = 3           12 = 3,4
        # 5 = 1,3         13 = 1,3,4
        # 6 = 2,3         14 = 2,3,4
        # 7 = 1,2,3       15 = 1,2,3,4 """
        self.channels = 0xff # All
        rs = self.dll_lib.TDC_enableChannels(self.channels)
        self.switch(rs)
        
        # Histogram params
        self.hist_bincount = 40
        self.binwidth = 250
        self.timestamp_count = 10000
        rs = self.dll_lib.TDC_setHistogramParams(self.binwidth,self.hist_bincount)
        self.switch(rs)
        
        
        
        
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
    
        