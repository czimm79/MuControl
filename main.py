import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import sys
from threads.DataGenerator import Generator
from ParameterTree import MyParamTree
from ConfigurationClass import Configuration
from threads.Reader import SignalReader
from threads.Writer import SignalWriter

# from fbs_runtime.application_context.PyQt5 import ApplicationContext

class MyPlotWidget(pg.PlotWidget):
    """
    This class is a simple wrapper around the pg.PlotWidget to capture keypresses
    when the plot is the active widget.
    """
    keyPressed = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)  # By default the plot is the keyboard focus

    def keyPressEvent(self, event):
        """ When a key is pressed, pass it up to the PyQt event handling system. """
        super().keyPressEvent(event)
        self.keyPressed.emit(event.key())


class MyWindow(QtGui.QMainWindow):
    """
    Setting up the main window. Anything with 'self' refers to the main window. This is the
    module that everything connects into.
    """

    def __init__(self, appctxt):
        super().__init__()  # Inherit everything from QMainWindow
        self.ptr = 1  # Variable ptr belongs to 'self', AKA this class, AKA the main window
        self.config = Configuration(appctxt)
        self.linewidth = 1
        self.curvecolors = ['b', 'g', 'r', 'c', 'y', 'm']
        self.pens = [pg.mkPen(i, width=self.linewidth) for i in self.curvecolors]
        self.set_style()
        self.initUI()
        self.initThreads(self.config)  # Initialize the threads using the configuration values

        self.p1.keyPressed.connect(self.t.on_key)  # Connect keyPresses to param tree

    def set_style(self):
        """ Simply set some config options and themes. """
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)

    def initUI(self):
        """ Create all the widgets and place them in a layout """
        self.setWindowTitle('MuControl v0.5.0')
        # self.setWindowIcon(QtGui.QIcon(os.getcwd() + os.sep + 'static' + os.sep + 'icon.png'))
        self.resize(1200, 800)

        # Create a main box to hold everything
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)  # Put it in the center of the main window
        layout = QtWidgets.QGridLayout()  # The structure to which we add widgets.
        self.mainbox.setLayout(layout)  # Set the layout of the main box
        # Everything from now on is put inside the main box.

        # Create the plot widget
        self.p1 = MyPlotWidget()
        # self.p1.enableAutoRange('xy', False)

        # Create a button
        # self.btn = QtWidgets.QPushButton('Toggle a stupid sin wave.')
        # self.btn.clicked.connect(self.on_button_clicked) # Connect it to my method

        # Create a label
        self.lbl = QtWidgets.QLabel('<p>I like 2 BOLD <strong>words</strong></p>')

        # Parameter Tree
        self.t = MyParamTree(self.config)
        self.t.paramChange.connect(self.change)
        # Add widgets to the layout in their proper positions
        layout.addWidget(self.t, 1, 0, 1, 1)  # row, col, rowspan, colspan
        layout.addWidget(self.p1, 0, 0)
        # layout.addWidget(self.btn, 2, 0)
        layout.addWidget(self.lbl, 0, 1)

    def initThreads(self, config):
        """ Initialize the readThread and writeThread using configurations."""


        # # Instantiate the readThread
        # self.readThread = SignalReader(
        #     daq_name=config.daq_name,
        #     readchannel_list=config.readchannel_list,
        #     daq_rate=config.daq_rate,
        #     readchunksize=config.readchunksize
        #     ) # Instantiate the readThread
        #
        # self.readThread.newData.connect(self.on_new_data_update_plot) # Connect the data from the thread to my method
        # self.readThread.start()
        #
        # # Instantiate the writeThread
        # self.writeThread = SignalWriter(
        #     funcg_name=config.funcg_name,
        #     writechannel_list=config.writechannel_list,
        #     funcg_rate=config.funcg_rate,
        #     writechunksize=config.writechunksize,
        #     zcoeff=config.zcoeff,
        #     # Default wave values
        #     vmulti=self.t.getParamValue('Voltage Multiplier'),
        #     freq=self.t.getParamValue('Frequency'),
        #     camber=self.t.getParamValue('Field Camber'),
        #     zphase=self.t.getParamValue('Z-Phase'),
        #     )

        self.writeThread = Generator(2, 10)
        self.writeThread.newData.connect(self.on_new_data_update_plot)

    def on_new_data_update_plot(self, incomingData):
        """ Each time the thread sends data, plot every row as a new line."""
        self.p1.clear()  # Clear last update's lines
        for i in range(0, np.shape(incomingData)[0]):  # For each row in incomingData
            # Plot all rows
            self.p1.plot(incomingData[i], clear=False, pen=self.pens[i])

    def change(self, param, changes):
        """Every time a change is made in the parameter tree, it comes here to be processed."""
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

            # Logic for sending changes to writeThread
            if path[1] == 'Toggle':
                self.toggle_writeThread(data)
            if path[1] == 'Voltage Multiplier':
                self.writeThread.vmulti = data  # TODO: Change ylims depending on vmulti
                # self.vmulti = self.t.getParamValue('Voltage Multiplier')
                # self.p1.setYRange(-self.vmulti, self.vmulti)
            if path[1] == 'Frequency':
                self.writeThread.freq = data
            if path[1] == 'Field Camber':
                self.writeThread.camber = data
            if path[1] == 'Z-Phase':
                self.writeThread.zphase = data

    def toggle_writeThread(self, data):
        """When a checkbox is changed, it starts or stops the writeThread."""
        if data is True:
            self.writeThread.start()

        elif data is False:
            # self.writeThread.writeTask.close() # TODO: Uncomment this to add nidaqmx functionality
            self.writeThread.running = False


if __name__ == '__main__':
    # appctxt = ApplicationContext()  # FBS : 1. Instantiate ApplicationContext
    appctxt = None
    app = QtWidgets.QApplication([])  # Initialize application

    w = MyWindow(appctxt)  # Instantiate my window
    w.show()  # Show it

    # exit_code = appctxt.app.exec_() # FBS : 2. Invoke appctxt.app.exec_()
    exit_code = app.exec_()
    sys.exit(exit_code)

