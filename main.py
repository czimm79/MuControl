import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys, os
from threads.DataGenerator import Generator
from ParameterTree import MyParamTree
from ConfigurationClass import Configuration
from threads.Reader import SignalReader
from threads.Writer import SignalWriter

class MyPlotWidget(pg.PlotWidget):
    ''' This class exists just to capture keypresses when the plot is the active widget.'''
    keyPressed = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.keyPressed.emit(event.key())



class MyWindow(QtGui.QMainWindow):
    ''' Setting up the main window. Anything with 'self' refers to the main window.'''
    def __init__(self):
        super().__init__() # Inherit everything from QMainWindow
        self.ptr = 1 # Variable ptr belongs to 'self', AKA this class, AKA the main window
        self.curve1 = np.sin(np.arange(0,100,step=0.1)) # placeholder toggle curve
        self.curvecolors = ['b','g','r','c','y','m']
        self.set_style()
        self.initUI()
        self.initThreads()

        self.p1.keyPressed.connect(self.t.on_key) # Connect keyPresses to param tree



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
        self.p1 = MyPlotWidget()

        #self.p1.enableAutoRange('xy', False)

        # Create a button
        # self.btn = QtWidgets.QPushButton('Toggle a stupid sin wave.')
        # self.btn.clicked.connect(self.on_button_clicked) # Connect it to my method

        # Create a label
        self.lbl = QtWidgets.QLabel('<p>I like 2 BOLD <strong>words</strong></p>')

        # Parameter Tree
        self.t = MyParamTree()
        self.t.paramChange.connect(self.change)
        # Add widgets to the layout in their proper positions
        layout.addWidget(self.t, 1, 0, 1, 1) # row, col, rowspan, colspan
        layout.addWidget(self.p1, 0, 0)
        #layout.addWidget(self.btn, 2, 0)
        layout.addWidget(self.lbl, 0, 1)

    def initThreads(self):
        ''' Initialize the readThread and writeThread using configurations.'''
        config = Configuration()
        #readThread
        self.readThread = SignalReader(
            daq_name=config.daq_name,
            readchannel_list=config.readchannel_list,
            daq_rate=config.daq_rate,
            chunksize=config.chunksize
            )
        self.readThread.newData.connect(self.on_new_data_update_plot) # Connect the data from the thread to my method
        self.readThread.start()
        #writeThread
        self.writeThread = SignalWriter(
            funcg_name=config.funcg_name,
            writechannel_list=config.writechannel_list,
            funcg_rate=config.funcg_rate,
            writechunksize=config.writechunksize,
            # Default wave values
            def_amps = self.t.getParamValue('Voltage Multiplier') * np.array([
                self.t.getParamValue('X-Voltage Amplitude', branch='Passive Output Signal Properties'),
                self.t.getParamValue('Y-Voltage Amplitude', branch='Passive Output Signal Properties'),
                self.t.getParamValue('Z-Voltage Amplitude', branch='Passive Output Signal Properties')
            ]),
            def_freq = self.t.getParamValue('Frequency'),
            def_zphase = self.t.getParamValue('Z-Phase'),
            )

        #multi = self.t.getParamValue('Voltage Multiplier'),
        #freq = self.t.getParamValue('Frequency') # Instantiate my thread with default values

    def on_button_clicked(self):
        ''' When the button is clicked, toggle plotting self.curve1 '''
        pass
        #self.t.stepParamValue('Voltage Multiplier', 1)


    def on_new_data_update_plot(self, incomingData):
        ''' Each time the thread sends data, plot every row as a new line.'''
        self.p1.clear() # Clear last update's lines
        for i in range(0,np.shape(incomingData)[0]): # For each row in incomingData
            # Plot all rows
            self.p1.plot(incomingData[i], clear=False, pen=self.curvecolors[i])


    def change(self, param, changes):
        '''Every time a change is made in the parameter tree, it comes here to be processed.'''
        print("tree changes: ")
        for param, change, data in changes:
            path = self.t.p.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            print(f'  path:  {path}')
            print(self.t.getParamValue('Toggle'))
            print(f'  parameter: {childName}')
            print(f'  change:    {change}')
            print(f'  data:      {str(data)}')
            print('  ----------')

            # Logic for sending changes to writeThread (writeThread later)
            if path[1] == 'Toggle':
                self.toggle_writeThread(data)
            if path[1] == 'Frequency':
                self.writeThread.freq = data


    def toggle_writeThread(self, data):
        '''When a checkbox is changed, it starts or stops the writeThread.'''
        if data == True:
            self.writeThread.start()

        elif data == False:
            self.writeThread.running = False



if __name__ == '__main__':
    app = QtWidgets.QApplication([]) # Initialize application
    w = MyWindow() # Instantiate my window
    w.show() # Show it
    sys.exit(app.exec_())
