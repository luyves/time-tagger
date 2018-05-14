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
from photon_gui import Ui_MainWindow

class AppWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(AppWindow,self).__init__()
        self.setupUi(self)
        self.TDC = TDC()
        self.ch = 15
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
        self.runButton.clicked.connect(self.testfunc)
        
        # Plot updater WIP
        self.mockPlot()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.mockUpdate)
        self.timer.start(50)
#        
    def impedance(self):
        if self.input50btn.isChecked():
#            print("cincuenta")
            self.TDC.switchTermination(True)
        elif self.input1000btn.isChecked():
#            print("mil")
            self.TDC.switchTermination(False)
        else:
            return
        
    def paramsUpdate(self):
        if self.selftest_check.isChecked():
            self.ch = np.random.randint(1,6) #3
            self.sp = np.random.randint(3,5) #4
            self.br = np.random.randint(3,6) #3
            self.ds = np.random.randint(8,12) #10
            
            channels = QtWidgets.QListWidgetItem("Channels: "+str(self.TDC.getChannel(self.ch)))
            signal_period = QtWidgets.QListWidgetItem("Period of signal: "+str(self.sp*20)+" ns")
            burst = QtWidgets.QListWidgetItem("Number of bursts: "+str(self.br))
            distance = QtWidgets.QListWidgetItem("Duty cycle: "+str(80*self.ds)+" ns")
            self.paramsList.addItem(channels)
            self.paramsList.addItem(signal_period)
            self.paramsList.addItem(burst)
            self.paramsList.addItem(distance)
        else:
            self.paramsList.clear()
                                              
                                              
    def testfunc(self):
        item = QtWidgets.QListWidgetItem("Item "+str(np.random.randint(0,10)))
        self.paramsList.addItem(item)
        
    def runSelfTest(self):
        self.TDC.selfTest(self.ch,self.sp,self.br,self.ds)
        
    def mockPlot(self):
        plt = self.counts_plot
        colors = [(255,0,0),(0,255,0),(0,0,255),(0,128,0),(19,234,201),
                   (195,46,212),(250,194,5)]
        
        self.num_plots = np.shape(self.TDC.getChannel(self.ch))[0]
        self.curves = ['self.curve{}'.format(i) for i in range(self.num_plots)]
        self.figures = ['self.fig{}'.format(i) for i in range(self.num_plots)]
        
        for i in range(self.num_plots):
            exec('{} = plt.addPlot(row={},col=0)'.format(self.figures[i],i+1))
            exec('{} = {}.plot()'.format(self.curves[i],self.figures[i]))
            data = np.random.random(size=100)
            exec('{}.setData(data,pen=colors[i%len(colors)],pensize=3)'.format(self.curves[i]))
        
        self.figobjects = [eval(self.figures[i]) for i in range(self.num_plots)]
        self.curveobjects = [exec(self.curves[i]) for i in range(self.num_plots)]

    def mockUpdate(self):
        colors = [(255,0,0),(0,255,0),(0,0,255),(0,128,0),(19,234,201),
                   (195,46,212),(250,194,5)]
        for i in range(self.num_plots):
            data = np.random.random(size=100)
            exec('{}.setData(data,pen=colors[i%len(colors)],pensize=3)'.format(self.curves[i]))
        
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
        
        
    def plot(self):
        plt = self.counts_plot
        x = np.random.normal(size=1000)
        y = np.random.normal(size=1000)
        plt.plot(x, y, pen=None, symbol='o') 
#        
def main():
    app = QtWidgets.QApplication(sys.argv)   
    main_window = AppWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()