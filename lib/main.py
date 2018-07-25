# -*- coding: utf-8 -*-
"""
Created on Wed May  2 12:17:57 2018

@author: Luis Villegas
"""

from PyQt5 import QtCore, QtWidgets, QtGui

import numpy as np
import pyqtgraph as pg
import sys
from id800 import TDC
from photon_gui_s import Ui_photons

class AppWindow(QtWidgets.QMainWindow,Ui_photons):
    def __init__(self):
        super(AppWindow,self).__init__()
        self.setupUi(self)
        self.statusbar.showMessage("No connection established")
        self.TDC = TDC()
#        self.connectionTest()
        
        # Channelmask
        self.ch = 1
        self.num_plots = np.shape(self.TDC.getChannel(self.ch))[0] + 1 # +1 for total
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(0,128,0),(19,234,201),
                       (195,46,212),(250,194,5)]
        
        # Input impedance - 50 Ohms default
        self.TDC.switchTermination(True)
        self.input50btn.toggled.connect(self.impedance)
        
         # Self testing (random params)
        self.selftest_check.stateChanged.connect(self.paramsUpdate)
        self.runButton.clicked.connect(self.setTimer)
        
        # Histogram settings
        self.lineEdit_bincount.setText(str(self.TDC.hist_bincount))
        self.lineEdit_binwidth.setText(str(self.TDC.binwidth))
        self.lineEdit_exptime.setText(str(self.TDC.expTime.value))
        self.refreshBtn.clicked.connect(self.refreshHistVals)
        
        # Plot updater
        self.bin = 50 #ms
        self.initCountsPlot()
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateCountsPlot)
        self.timer.start(self.bin*0.85)
        self.playbackBtn.clicked.connect(self.playback)
        self.timebinning.activated.connect(self.changeBinning)
    
    def changeBinning(self,index):
        """ Change binning size. Options are:
        0: 30ms, 1:50ms, 2:100ms, 3:200ms
        """
        if index==0:
            self.bin = 30
        elif index==1:
            self.bin = 50
        elif index==2:
            self.bin = 100
        elif index==3:
            self.bin = 200
        else:
            pass
        self.timer.setInterval(self.bin)
            
    def playback(self):
        """ Start or stop plotting
        """
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
        """ TDC input impedance (50 or 1000)
        """
        if self.input50btn.isChecked():
#            print("cincuenta")
            self.TDC.switchTermination(True)
        elif self.input1000btn.isChecked():
#            print("mil")
            self.TDC.switchTermination(False)
        else:
            pass
    
    def refreshHistVals(self):
        bincount = int(self.lineEdit_bincount.text())
        binwidth = int(self.lineEdit_binwidth.text())
        exptime = int(self.lineEdit_exptime.text())
        self.TDC.dll_lib.TDC_setExposureTime(exptime)
        self.TDC.setHistogramParams(bincount,binwidth,False)
    
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
        
    def runSelfTest(self):
        self.TDC.selfTest(self.ch,self.sp,self.br,self.ds)
    
    def initHistPlot(self):
        if self.histBox.isChecked:
            channelA = self.chanAbox.currentIndex()
            channelB = self.chanBbox.currentIndex()            
            self.TDC.getHistogram(channelA,channelB)
        else:
            self.TDC.getHistogram()

        self.lineEdit_toobig.setText(self.TDC.toobig)
        self.lineEdit_toosmall.setText(self.TDC.toosmall)
        
        self.hfigure = self.hist_plot.addPlot()
#        self.hfigure.addLegend()
        self.hfigure.setLabel('bottom', 'Time diffs','µs')            
        self.hcurve = self.hfigure.plot()
        
        self.hcurve.setData(self.TDC.hist)
        
    
    def initCountsPlot(self):
        self.startTime = pg.ptime.time()
        self.chunkSize = 100
        self.maxChunks = 6
        self.ptr = 0
        
        self.figures = ['self.p{}'.format(i) for i in range(self.num_plots)]
        self.curves = [[] for i in range(self.num_plots)]
        self.curve = ['self.curve{}'.format(i) for i in range(self.num_plots)]
        self.data = [np.zeros((self.chunkSize+1,2)) for i in range(self.num_plots)]
        
        for i in range(self.num_plots):
            exec('self.p{} = self.counts_plot.addPlot(row={},col=0)'.format(i,i+1))
            exec('self.p{}.addLegend()'.format(i))
            exec('self.p{}.setXRange(-10,0)'.format(i))
        self.figures = [eval(self.figures[i]) for i in range(self.num_plots)]
        
        all_channels = self.TDC.getChannel(self.ch)
        self.counts_plot_names = ['Channel {}'.format(i) for i in all_channels]
        self.counts_plot_names.append("Global")
        self.figures[-1].setLabel('bottom','Time', 's')
        
        self.TDC.getLastTimestamps(True)
        
    def getCounts(self):
        """ Obtains cumulative number counts for given binning size for 
        every channel each time it's called. Used to update counts plot.
        """
        
        test = True
        if test:
            self.TDC.getLastTimestamps()
            timestamps = self.TDC.timebase*np.array(self.TDC.timestamps)
            channels = np.array(self.TDC.channels)
            valid = self.TDC.valid.value
            self.statusbar.showMessage("Timestamps: buffered {}".format(str(valid)))
        else:
            timestamps = np.loadtxt("timestamps.bin")
            channels = np.loadtxt("channels.bin")
            valid = len(timestamps)
            
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
        counts = [self.vtimestamps[np.where(self.vchannels==
                                            list(all_channels)[i])] for i in range(len(all_channels))]
        # Find counts in binsize
        self.lasttag = []
        self.datacount = []
        binning = (self.bin)*1e-3 # in miliseconds
        
        # Clicks counter (exec time < 1ms in general)
        for channeltag in counts:
            t = next((i for i in channeltag if i-channeltag[0]> binning),
                 None)
            try:
                self.datacount.append(np.where(channeltag==t)[0][0])
                # Per channel clicks
                self.lasttag.append(t)
            except:
                pass
        # Total clicks
        tt = next((i for i in self.vtimestamps if i-self.vtimestamps[0] > binning),
                  None)
        try:
            self.datacount.append(np.where(self.vtimestamps==tt)[0][0])
            self.lasttag.append(tt)
        except:
            pass

    def updateCountsPlot(self):
        self.getCounts()
        now = pg.ptime.time()
        for i in range(self.num_plots):
            for c in self.curves[i]:
                c.setPos(-(now-self.startTime),0)
        k = self.ptr % self.chunkSize
        if k == 0:
            for i in range(self.num_plots):
                if self.ptr == 0:
                    exec('self.curve[i] = self.figures[i].plot(name=self.counts_plot_names[i])')
                else:
                    exec('self.curve[i] = self.figures[i].plot()')
                self.curves[i].append(self.curve[i])
                last = self.data[i][-1]
                self.data[i] = np.empty((self.chunkSize+1,2))
                self.data[i][0] = last
            for i in range(self.num_plots):
                while len(self.curves[i]) > self.maxChunks:
                    c = self.curves[i].pop(0)
                    self.figures[i].removeItem(c)
        else:
            for i in range(self.num_plots):
                self.curve[i] = self.curves[i][-1]
        for i in range(self.num_plots):
            self.data[i][k+1,0] = now-self.startTime
            try:
                self.data[i][k+1,1] = self.datacount[i]
            except:
                self.data[i][k+1,1] = 0
            self.curve[i].setData(x=self.data[i][:k+2,0],y=self.data[i][:k+2,1],
                      pen=self.colors[i%len(self.colors)],pensize=3)
        self.ptr += 1
    
    def connectionTest(self):
        """ TDC connection test
        """
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
            self.id800_led.setPixmap(QtGui.QPixmap("icons/green-led-on.png"))
    
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Exit', 
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
        if reply == QtGui.QMessageBox.Yes:
            self.TDC.close()
            event.accept()
        else:
            event.ignore()
    
def main():
    app = QtWidgets.QApplication(sys.argv)   
    main_window = AppWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()