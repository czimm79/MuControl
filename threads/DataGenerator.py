import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot

class Generator(QtCore.QThread):
    ''' Class that generates data on demand.'''
    newData = QtCore.pyqtSignal(object) # Designates that this class will have an output signal 'newData'

    def __init__(self, chunksize=100, delay=20, multi=10):
        super().__init__()
        self.chunksize = chunksize
        self.delay = delay
        self.multi = multi
        self.mutex = QtCore.QMutex()
        self.output = np.zeros([1,self.chunksize])
        self.running = False

    def run(self):
        ''' This method runs when the thread is started.'''
        self.running = True
        while self.running:
            try:
                #self.mutex.lock()
                self.output = self.multi * np.random.normal(size=(6, self.chunksize))
                #self.mutex.unlock()
                self.newData.emit(self.output) # send the new output to the pyqtSignal 'newData'
                QtCore.QThread.msleep(self.delay)
            except Exception as e:
                print(str(e))
                pass
