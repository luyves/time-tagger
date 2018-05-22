# -*- coding: utf-8 -*-
"""
Created on Wed May  2 12:17:57 2018

@author: Luis Villegas
"""

from PyQt5 import QtCore, QtWidgets, QtGui

import numpy as np
import pyqtgraph as pg
import sys
#import os
#import time
from id800 import TDC
from photon_gui import Ui_photons

class AppWindow(QtWidgets.QMainWindow,Ui_photons):
    def __init__(self):
        super(AppWindow,self).__init__()
        self.setupUi(self)
        self.statusbar.showMessage("No connection established")
        self.TDC = TDC()
        
        # Channelmask
        self.ch = 5
        self.num_plots = 3
#        self.num_plots = np.shape(self.TDC.getChannel(self.ch))[0] + 1 # +1 for total
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(0,128,0),(19,234,201),
                       (195,46,212),(250,194,5)]
        
        # Attempt connection to TDC
#        connection_prompt = QtWidgets.QMessageBox.question(self, "Startup",
#                                                              "Establish connections?",
#                                                              QtWidgets.QMessageBox.Yes |
#                                                              QtWidgets.QMessageBox.No)
        # Input impedance - 50 Ohms default
        self.TDC.switchTermination(True)
        self.input50btn.toggled.connect(self.impedance)
        
         # Self testing (random params)
        self.selftest_check.stateChanged.connect(self.paramsUpdate)
        self.runButton.clicked.connect(self.setTimer)
        
        # Plot updater
        self.bin = 50 #ms
        self.plotmeta()
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updatemeta)
        self.timer.start(self.bin)
        self.playbackBtn.clicked.connect(self.playback)

    def playback(self):
        if self.playbackBtn.isChecked():
            self.timer.stop()
            self.playbackBtn.setText("Plot")
        else:
            self.timer.start(self.bin)
            self.playbackBtn.setText("Stop")
            
    def setTimer(self):
        """ WIP, tuneable parameter (changes the binning)
        """
        self.timer.setInterval(5*np.random.randint(1,30))
        
    def impedance(self):
        """ Done
        """
        if self.input50btn.isChecked():
#            print("cincuenta")
            self.TDC.switchTermination(True)
        elif self.input1000btn.isChecked():
#            print("mil")
            self.TDC.switchTermination(False)
        else:
            pass
        
    def paramsUpdate(self):
        """ Placeholder func
        """
        if self.selftest_check.isChecked():
            try:
                self.ch
            except:
                self.ch = np.random.randint(1,6) #3
            self.sp = np.random.randint(3,5) #4
            self.br = np.random.randint(3,6) #3
            self.ds = np.random.randint(8,12) #10
            
            channels = QtWidgets.QListWidgetItem("Channels: "+str(self.TDC.getChannel(self.ch)))
            signal_period = QtWidgets.QListWidgetItem("Signal period: "+str(self.sp*20)+" ns")
            burst = QtWidgets.QListWidgetItem("Number of bursts: "+str(self.br))
            distance = QtWidgets.QListWidgetItem("Duty cycle: "+str(80*self.ds)+" ns")
            self.paramsList.addItem(channels)
            self.paramsList.addItem(signal_period)
            self.paramsList.addItem(burst)
            self.paramsList.addItem(distance)
        else:
            self.paramsList.clear()
                                              
                                              
    def testfunc(self):
        """ Placeholder func
        """
        
#        item = QtWidgets.QListWidgetItem("Item "+str(np.random.randint(0,10)))
#        self.paramsList.addItem(item)
#        print(self.)
        
    def runSelfTest(self):
        self.TDC.selfTest(self.ch,self.sp,self.br,self.ds)
        
    def plotInit(self):
        """ The only important part of this is generating the curves and
        figures.
        """
        plt = self.counts_plot
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(0,128,0),(19,234,201),
                       (195,46,212),(250,194,5)]
        self.startTime = pg.ptime.time()
        
        data = self.timestamps[:]
        self.curves = ['self.curve{}'.format(i) for i in range(self.num_plots)]
        self.figures = ['self.fig{}'.format(i) for i in range(self.num_plots)]
        for i in range(self.num_plots):
            exec('{} = plt.addPlot(row={},col=0)'.format(self.figures[i],i+1))
            exec('{} = {}.plot()'.format(self.curves[i],self.figures[i]))
            exec('{}.setData(data,pen=self.colors[i%len(self.colors)],pensize=3)'.format(self.curves[i]))
        
    def getCounts(self):
        """ WIP need to get the last timestamp
        """
        test = False
        if test:
            self.TDC.getLastTimestamps(freeze=True)
            timestamps = self.TDC.timestamps[:]
            channels = self.TDC.channels[:]
            valid = self.TDC.valid.value
            print("tests")
        else:
            timestamps = np.loadtxt("timestamps.bin")
            channels = np.loadtxt("channels.bin")
            valid = len(timestamps)
            print("data read")
        timebase = self.TDC.timebase
        
        try:
            # Checks buffer to see if you have gotten any timetags already
            # and parse the valid timestamps in the same buffer call
            newstart = np.where(timestamps==min(self.lasttag))[0][0]
            self.vtimestamps = timestamps[newstart:valid]
            self.vchannels = channels[newstart:valid]
        except:
            self.vtimestamps = timestamps[:valid]
            self.vchannels = channels[:valid]
        all_channels = set(self.vchannels)
        counts = [timebase*self.vtimestamps[np.where(self.vchannels==
                                                     list(all_channels)[i])] for i in range(len(all_channels))]

        self.lasttag = []
        self.datacount = []
        binning = self.bin*1e-3 # in miliseconds
        
        # clicks counter (time < 1ms in general)
        for channeltag in counts:
            t = next((i for i in channeltag if i-channeltag[0]> binning),
                 None)
            try:
                self.datacount.append(np.where(channeltag==t)[0][0])
                self.lasttag.append(t)
            except:
                pass
            
         # alternative method, a bit more expensive
#            for t in channeltag:
#                if t-channeltag[0] > (self.bin*1e-3):
#                    self.lasttag.append(t)
#                    self.datacount.append(np.where(channeltag==t)[0][0])
#                    return None # only get the first one
        
    def update(self):
        self.getCounts()
        if not self.datacount:
            pass
        else:
            for i in range(self.num_plots):
                exec('{}.setData(self.ch{}data,pen=self.colors[i%len(self.colors)],pensize=3)'.format(self.curves[i],i))
    
    def plotmeta(self):
        plt = self.counts_plot
        self.startTime = pg.ptime.time()
        self.chunkSize = 100
        self.maxChunks = 10
        self.ptr = 0
        
        for i in range(self.num_plots):
            exec('self.p{} = plt.addPlot(row={},col=0)'.format(i,i+1))
            exec('self.p{}.setXRange(-10,0)'.format(i))
            exec('self.plots{} = []'.format(i))
            exec('self.data{} = np.empty((self.chunkSize+1,2))'.format(i))
        plots = ['self.p{}'.format(i) for i in range(self.num_plots)]
        exec('{}.setLabel(\'bottom\',\'Time\', \'s\')'.format(plots[-1]))
        
    def updatemeta(self):
        now = pg.ptime.time()
#        for j in range(len(self.plots0)):    
#            for i in range(self.num_plots):
#                exec('self.plots{}[j].setPos(-(now-self.startTime),0)'.format(i))
        for j in range(len(self.plots0)):
            for i in range(self.num_plots):
                exec('self.plots{}[j].setPos(-(now-self.startTime),0)'.format(i))
        k = self.ptr % self.chunkSize
        if k == 0:
            for i in range(self.num_plots):
                exec('self.curve{} = self.p{}.plot()'.format(i,i))
                exec('self.plots{}.append(self.curve{})'.format(i,i))
                exec('self.last{} = self.data{}[-1]'.format(i,i))
                exec('self.data{} = np.empty((self.chunkSize+1,2))'.format(i))
                exec('self.data{}[0] = self.last{}'.format(i,i))
            while len(self.plots0) > self.maxChunks:
                for i in range(self.num_plots):
                    exec('self.c{} = self.plots{}.pop(0)'.format(i,i))
                    exec('self.p{}.removeItem(self.c{})'.format(i,i))
        else:
            for i in range(self.num_plots):
                exec('self.curve{} = self.plots{}[-1]'.format(i,i))
                
        for i in range(self.num_plots):
            exec('self.data{}[k+1,0] = now-self.startTime'.format(i))
            ran = np.floor(np.random.random()+0.1)
            exec('self.data{}[k+1,1] = ran'.format(i))
            exec("""self.curve{}.setData(x=self.data{}[:k+2,0],
                 y=self.data{}[:k+2,1])""".format(i,i,i))
        
        self.ptr +=1
    
    def mockPlot(self):
        plt = self.counts_plot
        self.curves = ['self.curve{}'.format(i) for i in range(self.num_plots)]
        self.figures = ['self.fig{}'.format(i) for i in range(self.num_plots)]
        self.ptr = 0
        self.startTime = pg.ptime.time()
        for i in range(self.num_plots):
            exec('{} = plt.addPlot(row={},col=0)'.format(self.figures[i],i+1))
            exec('{} = {}.plot()'.format(self.curves[i],self.figures[i]))
            self.data = np.random.random(size=100)
            exec('{}.setData(self.data,pen=self.colors[i%len(self.colors)],pensize=3)'.format(self.curves[i]))
#        self.figobjects = [eval(self.figures[i]) for i in range(self.num_plots)]
#        self.curveobjects = [exec(self.curves[i]) for i in range(self.num_plots)]
    
    def mockUpdate(self):
        self.nowTime = pg.ptime.time()
        for i in range(self.num_plots):
            self.data[:-1] = self.data[1:]
            self.data[-1] = np.random.random()
            exec('{}.setData(self.data,pen=self.colors[i%len(self.colors)],pensize=3)'.format(self.curves[i]))
            exec('{}.setPos(self.nowTime-self.startTime,0)'.format(self.curves[i]))
        
    def connectionTest(self):
        if not self.TDC.connection:
            choice = QtWidgets.QMessageBox.question(self, "Connection Fail",
                                                    """Couldn't connect to TDC. Try again?""",
                                                    QtWidgets.QMessageBox.Yes |
                                                    QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                self.TDC = TDC()
                self.connectionTest()
            else:
                error_dialogue = QtWidgets.QErrorMessage()
                error_dialogue.showMessage("""Restart the application and 
                                           try again.""")
        else:
            self.id800_led.setPixmap(QtGui.QPixmap("icons/led-green-on.png"))
    
def main():
    app = QtWidgets.QApplication(sys.argv)   
    main_window = AppWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()