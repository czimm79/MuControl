import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
import sys, os
from threads.DataGenerator import Generator
from parametertree import MyParamTree

class MyWindow(QtGui.QMainWindow):
    ''' Setting up the main window. Anything with 'self' refers to the main window.'''
    def __init__(self):
        super().__init__() # Inherit everything from QWidget
        self.curve1 = np.sin(np.arange(0,100,step=0.1)) # placeholder toggle curve
        self.curvecolors = ['b','g','r','c','y','m']
        self.readThread = Generator() # Instantiate my thread
        self.readThread.newData.connect(self.on_new_data_update_plot) # Connect the data from the thread to my method
        self.set_style()
        self.initUI()

    def set_style(self):
        ''' Simply set some config options and themes. '''
        app.setStyle("Fusion")
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)

    def initUI(self):
        ''' Create all the widgets and place them in a layout '''
        self.setWindowTitle('MuControl v0.1.0')
        self.setWindowIcon(QtGui.QIcon(os.getcwd() + os.sep + 'static' + os.sep + 'icon.png'))
        self.resize(1200,800)

        # Create a main box to hold everything
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox) # Put it in the center of the main window
        layout = QtWidgets.QGridLayout() # The structure to which we add widgets.
        self.mainbox.setLayout(layout) # Set the layout of the main box
                                       # Everything from now on is put inside the main box.

        # Create the plot widget
        self.p1 = pg.PlotWidget()
        #self.p1.enableAutoRange('xy', False)

        # Create a button
        self.btn = QtWidgets.QPushButton('Toggle a stupid sin wave.')
        self.btn.clicked.connect(self.on_button_clicked) # Connect it to my method

        #   Checkbox
        self.check = QtWidgets.QCheckBox('A Fucking Checkbox that raves')
        self.check.stateChanged.connect(self.call_data_gen_while_check) # Connect it to my method

        # Parameter Tree
        self.t = MyParamTree()

        # Add widgets to the layout in their proper positions
        layout.addWidget(self.t, 0, 0, 1, 1) # row, col, rowspan, colspan
        layout.addWidget(self.p1, 1, 0)
        layout.addWidget(self.btn, 2, 0)
        layout.addWidget(self.check, 0, 1)


    def on_button_clicked(self):
        ''' When the button is clicked, toggle plotting self.curve1 '''
        if self.ptr:
            self.p1.plot(self.curve1, pen='k')
        else:
            self.p1.clear()
        self.ptr = not self.ptr


    def on_new_data_update_plot(self, incomingData):
        ''' Each time the thread sends data, plot every row as a new line.'''
        self.p1.clear()
        for i in range(0,np.shape(incomingData)[0]): # For each row in incomingData
            # Plot all rows
            self.p1.plot(incomingData[i], clear=False, pen=self.curvecolors[i])


    def call_data_gen_while_check(self, int):
        ''' Only run the thread when the checkbox is checked.'''
        if self.check.isChecked():
            self.readThread.start()
        else:
            self.readThread.running = False
            self.p1.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication([]) # Initialize application
    w = MyWindow() # Instantiate my window
    w.show() # Show it
    sys.exit(app.exec_())
