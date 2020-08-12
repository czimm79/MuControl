from pyqtgraph.Qt import QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtWidgets, QtGui
import ast  # For literal interpretations of settings inputs


class SettingsWindow(QtWidgets.QDialog):
    """Class which wraps around a QDialog window, housing a parameter tree that communicates with QSettings.

    Attributes:
        default_params: a nested dictionary containing the same parameters as params, but with an assigned value. This
            is utilized when there are no QSettings already available on the computer.
        params: same structure as default_params but with settings read in from QSettings
        qsettings: an instantiated version of QSettings, where all of the persistent settings are saved on the host
            computer.
        qss: all of the save locations of values in QSettings, in the form "Read Parameters/DAQ Name"
        t: the settings parameter tree object
    """
    def __init__(self):
        super().__init__()

        # General Window Settings
        self.setWindowTitle('Settings')
        self.setModal(True)  # Cannot do other things in the app while this window is open
        self.resize(200, 500)

        self.default_params = [  # The default parameters
            {'name': 'Read Parameters', 'type': 'group', 'children': [
                {'name': 'DAQ Name', 'type': 'str', 'value': "Dev1"},
                {'name': 'Read Channel List', 'type': 'str', 'value': "['ai0', 'ai1', 'ai2', 'ai3', 'ai4', 'ai5']"},
                {'name': 'DAQ Read Rate [sps]', 'type': 'int', 'value': 1000},
                {'name': 'Read Chunk Size', 'type': 'int', 'value': 100}
            ]},
            {'name': 'Write Parameters', 'type': 'group', 'children': [
                {'name': 'Function Gen. Name', 'type': 'str', 'value': "cDAQ1Mod1"},
                {'name': 'Write Channel List', 'type': 'str', 'value': '[0, 1, 2]'},
                {'name': 'Generation Rate [sps]', 'type': 'int', 'value': 8000}
            ]},
            {'name': 'Default Signal Values', 'type': 'group', 'children': [
                {'name': 'Z-Coefficient', 'type': 'float', 'value': 0.653, 'step': 0.001},
                {'name': 'Voltage Multiplier', 'type': 'float', 'value': 1.0, 'step': 0.25},
                {'name': 'Frequency', 'type': 'float', 'value': 20, 'step': 10, 'siPrefix': True,
                 'suffix': 'Hz'},
                {'name': 'Z-Phase', 'type': 'int', 'value': 270, 'step': 1},
                {'name': 'Field Camber', 'type': 'int', 'value': 60, 'step': 1, 'siPrefix': True,
                 'suffix': '°'}
            ]}
        ]

        # Settings
        self.qsettings = QtCore.QSettings("MarrLabCSM", "MuControl")  # Instantiate settings object
        self.qss = self.get_parameter_strings()  # pulling all default strings

        # Edge case: if this is the first time running the program or the settings are missing, use defaults.
        if self.qsettings.value(self.qss[0]) is None:
            self.save_default_settings()

        self.params = [
            {'name': 'Read Parameters', 'type': 'group', 'children': [
                {'name': 'DAQ Name', 'type': 'str', 'value': self.qsettings.value(self.qss[0])},
                {'name': 'Read Channel List', 'type': 'str', 'value': self.qsettings.value(self.qss[1])},
                {'name': 'DAQ Read Rate [sps]', 'type': 'int', 'value': self.qsettings.value(self.qss[2])},
                {'name': 'Read Chunk Size', 'type': 'int', 'value': self.qsettings.value(self.qss[3])}
            ]},
            {'name': 'Write Parameters', 'type': 'group', 'children': [
                {'name': 'Function Gen. Name', 'type': 'str', 'value': self.qsettings.value(self.qss[4])},
                {'name': 'Write Channel List', 'type': 'str', 'value': self.qsettings.value(self.qss[5])},
                {'name': 'Generation Rate [sps]', 'type': 'int', 'value': self.qsettings.value(self.qss[6])}
            ]},
            {'name': 'Default Signal Values', 'type': 'group', 'children': [
                {'name': 'Z-Coefficient', 'type': 'float', 'value': self.qsettings.value(self.qss[7]), 'step': 0.001},
                {'name': 'Voltage Multiplier', 'type': 'float', 'value': self.qsettings.value(self.qss[8]), 'step': 0.25},
                {'name': 'Frequency', 'type': 'float', 'value': self.qsettings.value(self.qss[9]), 'step': 10,
                 'siPrefix': True, 'suffix': 'Hz'},
                {'name': 'Z-Phase', 'type': 'int', 'value': self.qsettings.value(self.qss[10]), 'step': 1},
                {'name': 'Field Camber', 'type': 'int', 'value': self.qsettings.value(self.qss[11]), 'step': 1,
                 'siPrefix': True, 'suffix': '°'}
            ]}
        ]
        # Load the above parameter object into the parameter tree widget
        self.p = Parameter.create(name='self.params', type='group', children=self.params)
        self.t = ParameterTree()
        self.t.setParameters(self.p, showTop=False)

        # Save button
        self.savebtn = QtWidgets.QPushButton('Save and Close')
        self.savebtn.clicked.connect(self.close)

        # Set layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.t)
        layout.addWidget(QtWidgets.QLabel('After clicking the save button below, restart the application to use the'\
                                          ' new settings!'))
        layout.addWidget(self.savebtn)
        self.setLayout(layout)

        # Initialize variable aliases
        self.initialize_variable_aliases()

    def get_parameter_strings(self):
        """
        Look through the parameter dictionary and return a list of strings.

        Returns:
            qss: a list of strings with formatting 'branch/child'
        """
        # qss
        qsettings_strings = []
        for branch in self.default_params:
            for child in branch['children']:
                qsettings_strings.append(f"{branch['name']}/{child['name']}")

        return qsettings_strings

    def getParamValue(self, branch, child):
        """Get the current value of a parameter."""
        return self.p.param(branch, child).value()

    def save_settings(self):
        """
        Goes through the parameter tree and saves each setting into the QSettings object.
        """

        for string in self.qss:
            branch = string.split('/')[0]
            child = string.split('/')[1]
            val = self.p.param(branch, child).value()
            self.qsettings.setValue(string, val)

    def save_default_settings(self):
        """
        Go through the default parameter tree and save its values into the QSettings memory.
        """
        for branch in self.default_params:
            for index, child in enumerate(branch['children']):
                self.qsettings.setValue(f"{branch['name']}/{child['name']}", child['value'])


    def initialize_variable_aliases(self):
        """
        This method transforms the pretty to read settings descriptions into the variables used throughout
        the rest of the code.
        """
        # READ
        self.daq_name = self.getParamValue('Read Parameters', 'DAQ Name')
        self.readchannel_list = ast.literal_eval(self.getParamValue('Read Parameters', 'Read Channel List'))
        self.daq_rate = int(self.getParamValue('Read Parameters', 'DAQ Read Rate [sps]'))
        self.readchunksize = int(self.getParamValue('Read Parameters', 'Read Chunk Size'))

        # WRITE
        self.funcg_name = self.getParamValue('Write Parameters', 'Function Gen. Name')
        self.writechannel_list = ast.literal_eval(self.getParamValue('Write Parameters', 'Write Channel List'))
        self.funcg_rate = int(self.getParamValue('Write Parameters', 'Generation Rate [sps]'))
        self.writechunksize = 200
        print(f'Signal Refresh Rate = {self.funcg_rate / self.writechunksize}')

        # DEFAULT SIGNAL VALUES
        self.defaults = {
            'vmulti': float(self.getParamValue('Default Signal Values', 'Voltage Multiplier')),
            'freq': int(self.getParamValue('Default Signal Values', 'Frequency')),
            'camber': int(self.getParamValue('Default Signal Values', 'Field Camber')),
            'zphase': int(self.getParamValue('Default Signal Values', 'Z-Phase')),
            'zcoeff': float(self.getParamValue('Default Signal Values', 'Z-Coefficient')),
            'calib_xamp': 1,
            'calib_yamp': 1,
            'calib_zamp': 1
            }


    def closeEvent(self, evnt):
        print('Dialog was closed.')
        self.save_settings()
