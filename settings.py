from pyqtgraph.Qt import QtWidgets, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.Qt import QtWidgets, QtGui


class SettingsWindow(QtWidgets.QDialog):
    """
    Class that constructs and holds the settings in a dialog box.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setModal(True)
        self.resize(400, 800)
        self.params = [
            {'name': 'Read Parameters', 'type': 'group', 'children': [
                {'name': 'DAQ Name', 'type': 'str', 'value': 'Dev1'},
                {'name': 'Read Channel List', 'type': 'str', 'value': "['ai0', 'ai1', 'ai2', 'ai3', 'ai4', 'ai5']"},
                {'name': 'DAQ Read Rate [sps]', 'type': 'int', 'value': 1000},
                {'name': 'Read Chunk Size', 'type': 'int', 'value': 100}
            ]},
            {'name': 'Write Parameters', 'type': 'group', 'children': [
                {'name': 'Function Gen. Name', 'type': 'str', 'value': 'cDAQ1Mod1'},
                {'name': 'Write Channel List', 'type': 'str', 'value': '[0, 1, 2]'},
                {'name': 'Generation Rate [sps]', 'type': 'int', 'value': 8000}
            ]},
            {'name': 'Default Signal Values', 'type': 'group', 'children': [
                {'name': 'Z-Coefficient', 'type': 'float', 'value': 0.653, 'step': 0.001},
                {'name': 'Voltage Multiplier', 'type': 'float', 'value': 1.0, 'step': 0.25},
                {'name': 'Frequency', 'type': 'float', 'value': 10, 'step': 10, 'siPrefix': True,
                 'suffix': 'Hz'},
                {'name': 'Field Camber', 'type': 'int', 'value': 90, 'step': 1, 'siPrefix': True,
                 'suffix': '°'}
            ]}
        ]
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

    def closeEvent(self, evnt):
        print('Dialog was closed.')
        # TODO Write values to QSettings
