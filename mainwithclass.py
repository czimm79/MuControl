import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
import sys


#pg.setConfigOptions(antialias=True)
class DataGenerator(QtCore.QThread):
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




class MyWindow(QtGui.QWidget):
    ''' Main Window '''
    def __init__(self):
        super().__init__() # Inherit everything from QWidget
        self.ptr = True
        self.curve1 = np.sin(np.arange(0,100,step=0.1))
        self.curvecolors = ['b','g','r','c','y','m']
        self.readThread = DataGenerator()
        self.readThread.newData.connect(self.on_new_data_update_plot)
        self.set_style()
        self.initUI()


    def set_style(self):
        ''' Simply set some config options and themes. '''
        app.setStyle("Fusion")
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)

    def initUI(self):
        self.setWindowTitle('MuControl WITH CLASS')

        # Create the plot object
        self.p1 = pg.PlotWidget() # Create the plot widget
        #self.p1.set
        #   Button, connect to method on_button_clicked
        self.btn = QtWidgets.QPushButton('Toggle a stupid sin wave.')
        self.btn.clicked.connect(self.on_button_clicked)

        #   Checkbox
        self.check = QtWidgets.QCheckBox('A Fucking Checkbox that raves')
        self.check.stateChanged.connect(self.call_data_gen_while_check)
        #   Label
        self.lbl = QtWidgets.QLabel('Placeholder')
        # Create a grid layout to manage the widgets size and position
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Add widgets to the layout in their proper positions
        layout.addWidget(self.p1, 1, 0)
        layout.addWidget(self.btn, 2, 0)
        layout.addWidget(self.check, 0, 1)
        layout.addWidget(self.lbl, 0, 0)
        #layout.addWidget(self.win, 1, 0)

    def on_button_clicked(self):
        if self.ptr:
            self.p1.plot(self.curve1, pen='k')
        else:
            self.p1.clear()
        self.ptr = not self.ptr

    def on_new_data_update_plot(self, incomingData):

        self.p1.clear()
        for i in range(0,np.shape(incomingData)[0]): # For each row in incomingData
            # Plot all rows
            self.p1.plot(incomingData[i], clear=False, pen=self.curvecolors[i])


    def call_data_gen_while_check(self, int):
        if self.check.isChecked():
            self.readThread.start()
        else:
            self.readThread.running = False
            self.p1.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication([]) # Initialize application
    w = MyWindow() # Instantiate my window
    w.show()
    sys.exit(app.exec_())
