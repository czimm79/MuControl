# Public Libraries
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys

# Custom modules
from threads.DataGenerator import Generator
from ParameterTree import MyParamTree
from settings import SettingsWindow
from threads.Reader import SignalReader
from threads.Writer import SignalWriter
from threads.Controller import ControllerThread
from plots import SignalPlot, ThreeDPlot
from misc_functions import set_style

debug_mode = True  # Switch to either use NI threads or a random data generator.
fbs_mode = False  # Switch to use either the PyQt5 app starting or the FBS container


class MyWindow(QtGui.QMainWindow):
    """ The main window of the application
    Setting up the main window. Anything with 'self' refers to the main window. This is the
    module that everything connects into.
    """

    def __init__(self):
        super().__init__()  # Inherit everything from the Qt "QMainWindow" class

        self.config = SettingsWindow()  # Load in the settings module

        set_style()
        self.initUI()
        self.initThreads(self.config)  # Initialize the threads using the configuration values

        self.p1.keyPressed.connect(self.t.on_key)  # Connect keyPresses to param tree


    def initUI(self):
        """ Create all the widgets and place them in a layout """
        # General window properties
        self.setWindowTitle('MuControl v1.0.0')
        self.resize(1600, 900)  # Non- maximized size
        self.setWindowState(QtCore.Qt.WindowMaximized)

        # Make menu bar at the top of the window
        mainMenu = self.menuBar()
        # mainMenu.setStyleSheet("""QMenuBar { background-color: #F0F0F0; }""")

        fileMenu = mainMenu.addMenu('File')

        # Settings button
        settingsButton = QtGui.QAction("&Settings", self)
        settingsButton.setShortcut('Ctrl+Alt+S')
        self.settings = SettingsWindow()
        settingsButton.triggered.connect(self.settings.show)
        fileMenu.addAction(settingsButton)

        # Exit Button
        exitButton = QtWidgets.QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

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

        # Create control labels
        self.keyboardlbl = QtWidgets.QLabel(
            '<h3> Keyboard Controls </h3>\
            <span style="font-size: 10pt;">To enable keyboard controls, left click once anywhere on the signal plot. </span> \
            <p> <strong> Toggle Output:  </strong> T; <strong> +Voltage Multiplier: </strong> W; <strong> -Voltage Multiplier: </strong> Q </p> \
            <p> <strong> +Frequency: </strong> G, <strong> -Frequency: </strong> F; <strong> +Camber: </strong> B; \
            <strong> -Camber: </strong> V </p>'
        )
        self.gamepadlbl = QtWidgets.QLabel(
            '<h3> Gamepad Controls </h3>\
            <span style="font-size: 10pt;">To enable gamepad controls, plug in the controller before starting the program. </span> \
            <p> <strong> Toggle Output:  </strong> Left Thumb Click; <strong> +Voltage Multiplier: </strong> RT; <strong> -Voltage Multiplier: </strong> LT </p> \
            <p> <strong> +Frequency: </strong> Y, <strong> -Frequency: </strong> X; <strong> +Camber: </strong> B; \
            <strong> -Camber: </strong> A </p>'
        )
        # self.keyboardlbl.setFont(QtGui.QFont("Default", 11))
        # self.gamepadlbl.setFont(QtGui.QFont("Default", 11))

        # Create plot labels
        self.p1lbl = QtWidgets.QLabel('<b><u>Live Signal Plot</u></b>')
        self.p2lbl = QtWidgets.QLabel('<b><u>Parametrized Output Visualization</u></b>')

        # Parameter Tree
        self.t = MyParamTree(self.config)
        self.t.paramChange.connect(self.change)
        # Add widgets to the layout in their proper positions
        layout.addWidget(self.p1lbl, 0, 0)
        layout.addWidget(self.p2lbl, 0, 1)
        layout.addWidget(self.t, 3, 0, 1, 2)  # , 1, 1)  # row, col, rowspan, colspan
        layout.addWidget(self.p1, 1, 0)  # , 1, 2)
        layout.addWidget(self.keyboardlbl, 2, 0, 1, 3)
        layout.addWidget(self.gamepadlbl, 2, 1, 1, 3)
        layout.addWidget(self.p2, 1, 1)  # , 1, 2)

    def initThreads(self, config):
        """ Initialize the readThread and writeThread using configurations."""
        if not debug_mode:

            # Instantiate the readThread
            self.readThread = SignalReader(
                daq_name=config.daq_name,
                readchannel_list=config.readchannel_list,
                daq_rate=config.daq_rate,
                readchunksize=config.readchunksize
            )

            # Connect the outputs of the readThread and start it
            self.readThread.newData.connect(
                self.p1.on_new_data_update_plot)  # Connect the data from the thread to the plotting method
            self.readThread.errorMessage.connect(self.error_handling)
            self.readThread.start()

            # Instantiate the writeThread
            self.writeThread = SignalWriter(
                funcg_name=config.funcg_name,
                writechannel_list=config.writechannel_list,
                funcg_rate=config.funcg_rate,
                writechunksize=config.writechunksize,
                zcoeff=config.defaults['zcoeff'],
                # Default wave values
                vmulti=self.t.getParamValue('Voltage Multiplier'),
                freq=self.t.getParamValue('Frequency'),
                camber=self.t.getParamValue('Field Camber'),
                zphase=self.t.getParamValue('Z-Phase'),
                calib_xamp=self.t.getParamValue('Calibration X-Voltage Ampl.', branch='Calibration'),
                calib_yamp=self.t.getParamValue('Calibration Y-Voltage Ampl.', branch='Calibration'),
                calib_zamp=self.t.getParamValue('Calibration Z-Voltage Ampl.', branch='Calibration'),
            )
            # Connect the error output
            self.writeThread.errorMessage.connect(self.error_handling)
        elif debug_mode:
            # For debugging purposes, doesn't initialize the NI part but instead plots random data
            self.writeThread = Generator(0.2, 10)
            self.writeThread.newData.connect(self.p1.on_new_data_update_plot)

        # Connect the controller input listening thread
        self.gamepadThread = ControllerThread()
        self.gamepadThread.newGamepadEvent.connect(self.t.on_gamepad_event)
        self.gamepadThread.start()

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
            if path[1] == 'Calibration X-Voltage Ampl.':
                self.writeThread.calib_xamp = data
            if path[1] == 'Calibration Y-Voltage Ampl.':
                self.writeThread.calib_yamp = data
            if path[1] == 'Calibration Z-Voltage Ampl.':
                self.writeThread.calib_zamp = data

    def toggle_writeThread(self, data):
        """When a checkbox is changed, it starts or stops the writeThread."""
        if data is True:
            self.writeThread.start()

        elif data is False:
            if not debug_mode:
                self.writeThread.writeTask.close()

            self.writeThread.running = False

    def error_handling(self, error_message):
        error_box = QtWidgets.QErrorMessage()
        error_box.setModal(True)  # Cannot do other things in the app while this window is open
        error_box.showMessage(error_message)
        error_box.exec_()

    def closeEvent(self, evnt):

        # Close controller thread
        self.gamepadThread.terminate()

        if not debug_mode:
            # Close writeThread
            if self.writeThread.running is True:
                self.writeThread.writeTask.close()
                self.writeThread.terminate()

            # Close readThread
            self.readThread.terminate()
        elif debug_mode:
            self.writeThread.terminate()


if __name__ == '__main__':
    if not fbs_mode:
        app = QtWidgets.QApplication([])  # Initialize application
        w = MyWindow()  # Instantiate my window
        w.show()  # Show it
        exit_code = app.exec_()

    elif fbs_mode:
        from fbs_runtime.application_context.PyQt5 import ApplicationContext

        appctxt = ApplicationContext()  # FBS : 1. Instantiate ApplicationContext
        w = MyWindow()  # Instantiate my window
        w.show()  # Show it
        exit_code = appctxt.app.exec_()  # FBS : 2. Invoke appctxt.app.exec_()

    sys.exit(exit_code)
