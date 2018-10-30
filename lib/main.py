# -*- coding: utf-8 -*-
"""
Created on Wed May  2 12:17:57 2018

@author: Luis Villegas
"""

from PyQt5 import QtCore, QtWidgets, QtGui

from ctypes import c_double
import numpy as np
import pyqtgraph as pg
import sys
import config
from os import getcwd
from time import strftime
from hunahpy import TDC
from pathlib import Path
from photon_gui_s import Ui_photons

class AppWindow(QtWidgets.QMainWindow,Ui_photons):
    def __init__(self):
        super(AppWindow,self).__init__()
        self.setupUi(self)
        self.statusbar.showMessage("No connection established")
        self.TDC = TDC()
        self.connectionTest()

        # Channelmask
        self.ch = 3
        self.num_plots = np.shape(self.TDC.getChannel(self.ch))[0] + 1 # +1 for total
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(0,128,0),(19,234,201),
                       (195,46,212),(250,194,5)]
        
        # Input impedance - 50 Ohms default
        self.TDC.switchTermination(True)
        self.input50btn.toggled.connect(self.impedance)
        
        # Histogram settings
        self.lineEdit_bincount.setText(str(self.TDC.bincount))
        self.lineEdit_binwidth.setText(str(self.TDC.binwidth))
        self.refreshBtn.clicked.connect(self.refreshHistVals)
        
        # Plot updater
        self.bin = 50 # ms
        self.initCountsPlot()
        self.initHistPlot()
        
        # Timers
        self.timer = pg.QtCore.QTimer()
        self.htimer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.updateCountsPlot)
        self.htimer.timeout.connect(self.updateHistPlot)
        self.timer.start(self.bin*0.5)
        self.htimer.start(1000)
        self.playbackBtn.clicked.connect(self.playback)
        self.timebinning.activated.connect(self.changeBinning)
        
        # Data saving
        self.file_extension = config.file_extension
        self.filename = strftime('%y%m%d')+'-'+strftime('%H%M')+'_'+config.filename
        self.total_runs = config.total_runs
        self.runButton.clicked.connect(self.saveFile)
        self.runButton.clicked.connect(self.nextFile)
            # Updating save parameters
        self.ccounter = 0
        self.ccounter_true = 0
        self.fcounter_zfill = len(config.total_runs)
        self.ccounter_label = f"{self.ccounter}".zfill(self.fcounter_zfill)
        self.progressbar.setMaximum(int(config.timestamp_count))
        self.counter_finalval.display(int(config.total_runs))
            # Check if file already exists
        self.filenameLabel.setText(self.filename+self.file_extension)
        self.datapath = getcwd()[:-3]+'data\\'+self.filenameLabel.text()
        
        while True:
            myfile = Path(self.datapath)
            if myfile.is_file():
                self.ccounter_true += 1
            else:
                break

        # Write to file
        self.cont = config.cont
        if not isinstance(self.cont,bool):
            self.cont = False
        if self.cont:
            self.runButton.setText("Close")
            print(self.datapath)
            self.TDC.writeTimestamps(self.datapath,binary=False)
            self.counter_finalval.display(int(1))
                
        # Help
        self.paramsUpdate()        
        
    def runSelfTest(self):
        """ TDC self test, mainly for debugging
        """
        self.TDC.configureSelfTest(3, 20, 50, 5000)
    
    def saveFile(self):
        """ Saves buffer data to filenameLabel
        """
        if not self.cont:
            print(self.datapath)
            with open(self.datapath,'w') as f:
                for i in range(len(self.TDC.timestamps)):
                    f.write("%s,%s\n" % (self.TDC.timestamps[i], self.TDC.channels[i]))
        else:
            self.TDC.writeTimestamps()

    
    def nextFile(self):
        """ Clears event buffer and opens next file to be saved. If this is the
        last file to be created, stop updating
        """
        if not self.cont:
            if self.ccounter < int(config.total_runs):
                self.ccounter += 1
                self.ccounter_true += 1
                self.ccounter_label = f"{self.ccounter_true}".zfill(self.fcounter_zfill)
                self.counter_currentval.display(self.ccounter)
                self.filename = strftime('%y%m%d')+'-'+strftime('%H%M')+'_'+config.filename
                self.filenameLabel.setText(self.filename+self.file_extension)
                self.TDC.getLastTimestamps(reset=True)
                self.progressbar.setValue(0)
                print(self.filenameLabel.text())
            else:
                self.timer.stop()
                self.htimer.stop()
        else:
            self.filename = strftime('%y%m%d')+'-'+strftime('%H%M')+'_'+config.filename
            self.filenameLabel.setText(self.filename+self.file_extension)
            self.datapath = getcwd()[:-3]+'data\\'+self.filenameLabel.text()
    
    def changeBinning(self,index):
        """ Change binning size. Options are:
        0: 30ms, 1:50ms, 2:100ms, 3:200ms, 4:1s
        """
        if index==0:
            self.bin = 30
        elif index==1:
            self.bin = 50
        elif index==2:
            self.bin = 100
        elif index==3:
            self.bin = 200
        elif index==4:
            self.bin = 1000
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
        
    def impedance(self):
        """ TDC input impedance (50 or 1000)
        """
        if self.input50btn.isChecked():
            self.TDC.switchTermination(True)
        elif self.input1000btn.isChecked():
            self.TDC.switchTermination(False)
        else:
            pass
    
    def refreshHistVals(self):
        """ Refresh histogram values
        """
        bincount = int(self.lineEdit_bincount.text())
        binwidth = int(self.lineEdit_binwidth.text())
        exptime = int(self.lineEdit_exptime.text())
        self.TDC.dll_lib.TDC_setExposureTime(exptime)
        self.TDC.setHistogramParams(bincount,binwidth)
    
    def paramsUpdate(self):
        """ Add initial config. params.
        """
        channels = QtWidgets.QListWidgetItem("Channels: "+str(self.TDC.getChannel(self.ch)))
        buffer = QtWidgets.QListWidgetItem("Buffer size: "+str(self.TDC.timestamp_count))
        nfiles = QtWidgets.QListWidgetItem("Total files: "+str(self.total_runs))
        blank = QtWidgets.QListWidgetItem("   ")
        pth_m = QtWidgets.QListWidgetItem("Current working path: ")
        pth = QtWidgets.QListWidgetItem(getcwd())
        self.paramsList.addItem(channels)
        self.paramsList.addItem(buffer)
        self.paramsList.addItem(nfiles)
        self.paramsList.addItem(blank)
        self.paramsList.addItem(pth_m)
        self.paramsList.addItem(pth)
    
    def initHistPlot(self):
        """ Initializes histogram plot
        """
        if self.histBox.isChecked:
            channelA = self.chanAbox.currentIndex()
            channelB = self.chanBbox.currentIndex()            
            self.TDC.getHistogram(channelA,channelB)
        else:
            self.TDC.getHistogram()

        self.lineEdit_toobig.setText(str(self.TDC.toobig.value))
        self.lineEdit_toosmall.setText(str(self.TDC.toosmall.value))
        
        self.hfigure = self.hist_plot.addPlot(row=0,col=0)
        self.hfigure.setLabel('bottom', 'Time diffs (ns)')            
        self.hcurve = self.hfigure.plot()
        self.hdata = np.array(self.TDC.hist)
        self.hpeak = max(set(self.hdata))
        self.hbins = np.linspace(1,self.TDC.bincount,self.TDC.bincount)*self.TDC.bins2ns.value
        self.hcurve.setData(x=self.hbins, y=self.hdata,
                            fillLevel=0, brush=(0,0,255,150))
        self.hfigure.setRange(yRange=[0,self.hpeak])
        
    def updateHistPlot(self):
        """ Histogram updater
        """
        if self.histBox.isChecked:
            channelA = self.chanAbox.currentIndex()
            channelB = self.chanBbox.currentIndex()            
            self.TDC.getHistogram(channelA,channelB)
        else:
            self.TDC.getHistogram()
        self.lineEdit_toobig.setText(str(self.TDC.toobig.value))
        self.lineEdit_toosmall.setText(str(self.TDC.toosmall.value))
        self.hdata = np.array(self.TDC.hist)
        self.hcurrentpeak = max(set(self.hdata))
        if self.hcurrentpeak > self.hpeak:
            self.hfigure.setRange(yRange=[0,self.hcurrentpeak])
        self.hbins = np.linspace(1,self.TDC.bincount,
                                 self.TDC.bincount)*self.TDC.bins2ns.value
        self.hcurve.setData(x=self.hbins, y=self.hdata,
                            fillLevel=0, brush=(0,0,255,150))
        
    def initCountsPlot(self):
        """ Initializes counts plot
        """
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
            exec('self.p{}.setDownsampling(mode=\'peak\')'.format(i))
            exec('self.p{}.setXRange(-10,0)'.format(i))
        self.figures = [eval(self.figures[i]) for i in range(self.num_plots)]
        
        all_channels = self.TDC.getChannel(self.ch)
        self.counts_plot_names = ['Channel {}'.format(i) for i in all_channels]
        self.counts_plot_names.append("Global")
        self.figures[-1].setLabel('bottom','Time', 's')
        
        self.TDC.getLastTimestamps(True)
        
    def getCounts(self):
        """ Read counts from buffer, integrate acoording to binning
        Outputs integrated value
        """
        test = True
        if test:
            self.TDC.getLastTimestamps()
            timestamps = self.TDC.timebase*np.array(self.TDC.timestamps)
            channels = np.array(self.TDC.channels)
            valid = self.TDC.valid.value
            self.statusbar.showMessage("Timestamps: buffered {}".format(str(valid))+
                                       "/"+str(self.TDC.timestamp_count))
            if valid<self.TDC.timestamp_count:
                self.progressbar.setValue(valid)
            else:
                # Save a new file
                if not self.cont:
                    self.saveFile()
                    self.nextFile()
                
        else:
            # for debugging
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
            
        all_channels = self.TDC.getChannel(self.ch) #set(self.vchannels)
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
                self.datacount.append(0)
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
        """ Counts updater
        """
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
    
    def update(self):
        self.updateCountsPlot()
        self.updateHistPlot()
    
    def connectionTest(self):
        """ TDC initial connection test
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
            self.id800_led.setPixmap(QtGui.QPixmap("icons/green-led-on.png"))
    
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Exit', 
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    
        if reply == QtGui.QMessageBox.Yes:
            print(">>> Closing... ", end="")
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
