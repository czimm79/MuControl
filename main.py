# Public Libraries
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import sys
from time import sleep

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
    """ The main window of the application.

    Setting up the main window. Anything with 'self' refers to the main window. This is the
    module that everything connects into.
    """

    def __init__(self):
        super().__init__()  # Inherit everything from the Qt "QMainWindow" class

        # Instantiate class in settings.py which contains the settings UI AND the persistent QSettings values
        self.config = SettingsWindow()

        set_style()  # Pulled in from misc_functions, simply sets background and foreground colors for plots

        # Call setup methods below
        self.initUI()
        self.initThreads(self.config)

        self.p1.keyPressed.connect(self.t.on_key)  # Connect keyPresses on signal plot to Param Tree

    def initUI(self):
        """
        This method instantiates every widget and arranges them all inside the main window. This is where the
        puzzle pieces are assembled.
        """
        # General window properties
        self.setWindowTitle('MuControl v1.0.0')
        self.resize(1280, 720)  # Non- maximized size
        self.setWindowState(QtCore.Qt.WindowMaximized)

        # Make menu bar at the top of the window
        mainMenu = self.menuBar()
        mainMenu.setStyleSheet("""QMenuBar { background-color: #F0F0F0; }""")  # Makes the menu bar grey-ish
        fileMenu = mainMenu.addMenu('File')  # Adds the file button

        # Settings button
        settingsButton = QtGui.QAction("&Settings", self)
        settingsButton.setShortcut('Ctrl+Alt+S')
        settingsButton.triggered.connect(self.config.show)  # when the settings button is clicked, window is shown
        fileMenu.addAction(settingsButton)  # Adds the settings button to the file menu

        # Exit Button
        exitButton = QtWidgets.QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        # Create an empty box to hold all the following widgets
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)  # Put it in the center of the main window
        layout = QtWidgets.QGridLayout()  # All the widgets will be in a grid in the main box
        self.mainbox.setLayout(layout)  # set the layout

        # Instantiate the plots from plots.py
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
        self.p2.setSizePolicy(self.p1.sizePolicy())  # 2D plot size = 3D plot size

        # Create control descriptions
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
        # self.keyboardlbl.setFont(QtGui.QFont("Default", 11))  # Optionally, change font size
        # self.gamepadlbl.setFont(QtGui.QFont("Default", 11))

        # Create plot labels
        self.p1lbl = QtWidgets.QLabel('<b><u>Live Signal Plot</u></b>')
        self.p2lbl = QtWidgets.QLabel('<b><u>Parametrized Output Visualization</u></b>')

        # Parameter Tree widget
        self.t = MyParamTree(self.config)  # From ParameterTree.py
        self.t.paramChange.connect(self.change)  # Connect the output signal from changes in the param tree to change

        # Add widgets to the layout in their proper positions
        layout.addWidget(self.p1lbl, 0, 0)
        layout.addWidget(self.p2lbl, 0, 1)
        layout.addWidget(self.t, 3, 0, 1, 2)  # row, col, rowspan, colspan
        layout.addWidget(self.p1, 1, 0)
        layout.addWidget(self.keyboardlbl, 2, 0, 1, 3)
        layout.addWidget(self.gamepadlbl, 2, 1, 1, 3)
        layout.addWidget(self.p2, 1, 1)

    def initThreads(self, config):
        """Initialize the readThread and writeThread using configurations.

        Args:
            config: The previously instantiated SettingsWindow class containing the persistent QSettings values

        """
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
                self.p1.on_new_data_update_plot)  # Connect the signal from the thread to the plotting method
            self.readThread.errorMessage.connect(self.error_handling)  # Connect error signal from readThread
            self.readThread.start()  # Start the read loop, runs the run() method in the readThread

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
            self.writeThread.errorMessage.connect(self.error_handling)  # Connect error signal from writeThread

        elif debug_mode:
            # For debugging purposes, don't initialize the NI part but instead use a random data generator
            self.writeThread = Generator(0.2, 10)
            self.writeThread.newData.connect(self.p1.on_new_data_update_plot)

        # Lastly, initialize and connect the controller input listening thread
        self.gamepadThread = ControllerThread()
        self.gamepadThread.newGamepadEvent.connect(self.t.on_gamepad_event)
        self.gamepadThread.start()

    def change(self, param, changes):
        """Parses the value change signals coming in from the Parameter Tree.

        When a parameter is changed in the Parameter Tree by the UI, keyboard, or gamepad, the Parameter Tree sends a
        signal to this method. The signal contains the param and changes args. This method uses if statements
        to filter the corresponding value changes and send them to their proper places.

        Args:
            param: Name of the parameter being changed
            changes: an iterable which contains one or more value change signals

        """
        for param, change, data in changes:
            path = self.t.p.childPath(param)

            # Logic for sending changes to writeThread
            if path[1] == 'Toggle Output':
                self.toggle_writeThread(data)
            if path[1] == 'Voltage Multiplier':
                self.writeThread.vmulti = data  # Modifies the vmulti parameter in the writeThread
                self.p1.setYRange(-data, data)  # Adjusts the Y axis plot range as necessary
                self.p2.vmulti = data  # Updates the parameter in the 3D plot class
                self.p2.plot_data()  # Updates the plot with the new values
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
        """A sub-method that starts or stops the writeThread when a toggle is requested.

        Args:
            data: a boolean, whether the checkbox is checked or not

        """
        if data is True:  # If the box is checked
            self.writeThread.start()

        elif data is False:
            self.writeThread.running = False

    def error_handling(self, error_message):
        """When an error signal is sent to this method, show an error box with the message inside.

        Args:
            error_message: signal from either the writeThread or readThread containing the error message

        """
        error_box = QtWidgets.QErrorMessage()
        error_box.setModal(True)  # Cannot do other things in the app while this window is open
        error_box.showMessage(error_message)
        error_box.exec_()

    def closeEvent(self, evnt):
        """ This method runs when Qt detects the main window closing. Used to gracefully end threads.

        The purpose of this method is to try and gracefully close threads to avoid persisting processes or bugs with
        the National Instruments cards.

        Args:
            evnt: dummy variable, unused

        """

        # Close controller thread
        self.gamepadThread.running = False

        # Close writeThread
        self.writeThread.running = False
        # self.writeThread.terminate()

        if not debug_mode:
            # Close readThread
            self.readThread.running = False
            # self.readThread.terminate()
        sleep(0.3)


if __name__ == '__main__':

    if not fbs_mode:  # The normal way to start a PyQt app when Python is installed
        app = QtWidgets.QApplication([])  # Initialize application
        w = MyWindow()  # Instantiate my window
        w.show()  # Show it
        exit_code = app.exec_()

    elif fbs_mode:  # When housed in an exe, this boilerplate code from fbs is used instead.
        from fbs_runtime.application_context.PyQt5 import ApplicationContext

        appctxt = ApplicationContext()  # FBS : 1. Instantiate ApplicationContext
        w = MyWindow()  # Instantiate my window
        w.show()  # Show it
        exit_code = appctxt.app.exec_()  # FBS : 2. Invoke appctxt.app.exec_()

    sys.exit(exit_code)
