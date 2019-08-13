import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

import sys
from threads.DataGenerator import Generator
from ParameterTree import MyParamTree
from ConfigurationClass import Configuration
from threads.Reader import SignalReader
from threads.Writer import SignalWriter


# Import statements for app installer packaging
# from fbs_runtime.application_context.PyQt5 import ApplicationContext

# Import plot classes
from plots import SignalPlot, ThreeDPlot


class MyWindow(QtGui.QMainWindow):
    """
    Setting up the main window. Anything with 'self' refers to the main window. This is the
    module that everything connects into.
    """

    def __init__(self, appctxt):
        super().__init__()  # Inherit everything from QMainWindow
        self.ptr = 1  # Variable ptr belongs to 'self', AKA this class, AKA the main window
        self.config = Configuration(appctxt)

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
        self.resize(1600, 900)  # Non- maximized size
        self.setWindowState(QtCore.Qt.WindowMaximized)

        # Create a main box to hold everything
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)  # Put it in the center of the main window
        layout = QtWidgets.QGridLayout()  # The structure to which we add widgets.
        self.mainbox.setLayout(layout)  # Set the layout of the main box
        # Everything from now on is put inside the main box.

        # Create the plot widget
        self.p1 = SignalPlot()
        self.p1.setYRange(-self.config.defaults['vmulti'], self.config.defaults['vmulti'])
        self.p2 = ThreeDPlot(
            funcg_rate=self.config.funcg_rate,
            writechunksize=self.config.writechunksize,
            vmulti=self.config.defaults['vmulti'],
            freq=self.config.defaults['freq'],
            camber=self.config.defaults['camber'],
            zphase=self.config.defaults['zphase'],
        )

        self.p2.setSizePolicy(self.p1.sizePolicy())
        # self.p1.enableAutoRange('xy', False)

        # Create a label
        self.lbl = QtWidgets.QLabel(
            '<h3> Keyboard Controls </h3>\
            <span style="font-size: 10pt;">To enable keyboard controls, left click once anywhere on the signal plot. </span> \
            <p> <strong> Toggle Output:  </strong> T; <strong> +Voltage Multiplier: </strong> W; <strong> -Voltage Multiplier: </strong> Q </p> \
            <p> <strong> +Frequency: </strong> G, <strong> -Frequency: </strong> F; <strong> +Camber: </strong> B; \
            <strong> -Camber: </strong> V </p>'
        )
        self.lbl.setFont(QtGui.QFont("Default", 11))

        # Parameter Tree
        self.t = MyParamTree(self.config)
        self.t.paramChange.connect(self.change)
        # Add widgets to the layout in their proper positions
        layout.addWidget(self.t, 2, 0, 1, 2)#, 1, 1)  # row, col, rowspan, colspan
        layout.addWidget(self.p1, 0, 0)#, 1, 2)
        layout.addWidget(self.lbl, 1, 0, 1, 3)
        layout.addWidget(self.p2, 0, 1)#, 1, 2)

    def initThreads(self, config):
        """ Initialize the readThread and writeThread using configurations."""


        # Instantiate the readThread
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
        #     zcoeff=config.defaults['zcoeff'],
        #     # Default wave values
        #     vmulti=self.t.getParamValue('Voltage Multiplier'),
        #     freq=self.t.getParamValue('Frequency'),
        #     camber=self.t.getParamValue('Field Camber'),
        #     zphase=self.t.getParamValue('Z-Phase'),
        #     )

        self.writeThread = Generator(0.2, 10)
        self.writeThread.newData.connect(self.p1.on_new_data_update_plot)

    def change(self, param, changes):
        """Every time a change is made in the parameter tree, it comes here to be processed."""
        for param, change, data in changes:
            path = self.t.p.childPath(param)

            # Logic for sending changes to writeThread
            if path[1] == 'Toggle Output':
                self.toggle_writeThread(data)
            if path[1] == 'Voltage Multiplier':
                self.writeThread.vmulti = data
                self.p1.setYRange(-data, data)
                self.p2.vmulti = data
                self.p2.plot_data()
            if path[1] == 'Frequency':
                self.writeThread.freq = data
                self.p2.freq = data
                self.p2.plot_data()
            if path[1] == 'Field Camber':
                self.writeThread.camber = data
                self.p2.camber = data
                self.p2.plot_data()
            if path[1] == 'Z-Phase':
                self.writeThread.zphase = data
                self.p2.zphase = data
                self.p2.plot_data()
            if path[1] == 'Z-Coefficient':
                self.writeThread.zcoeff = data
            if path[1] == 'Output Mode':
                if data == 'Calibration':
                    self.writeThread.calib_mode = True
                elif data == 'Normal':
                    self.writeThread.calib_mode = False

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

