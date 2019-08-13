import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from PyQt5.QtCore import Qt
from ConfigurationClass import Configuration


class MyParamTree(ParameterTree):
    paramChange = QtCore.pyqtSignal(object, object)  # MyParamTree outputs a signal with param and changes.

    def __init__(self, config):
        """
        Initialize the parameter tree.

        :param config: instantiated config object containing configuration values
        """
        super().__init__()
        self.params = [
            {'name': 'Signal Design Parameters', 'type': 'group', 'children': [
                {'name': 'Toggle Output', 'type': 'bool', 'value': False, 'tip': "Toggle the output"},
                {'name': 'Voltage Multiplier', 'type': 'float', 'value': config.defaults['vmulti'], 'step': 0.25},
                {'name': 'Frequency', 'type': 'float', 'value': config.defaults['freq'], 'step': 10, 'siPrefix': True, 'suffix': 'Hz'},
                {'name': 'Z-Phase', 'type': 'float', 'value': config.defaults['zphase'], 'step': 90},
                {'name': 'Field Camber', 'type': 'int', 'value': config.defaults['camber'], 'step': 1, 'siPrefix': True, 'suffix': '°'}
            ]},
            {'name': 'Calibration', 'type': 'group', 'children': [
                {'name': 'Output Mode', 'type': 'list', 'values': ['Normal', 'Calibration'], 'value': 'Normal'},
                {'name': 'Calibration X-Voltage Ampl.', 'type': 'float', 'value': config.defaults['calib_xamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name': 'Calibration Y-Voltage Ampl.', 'type': 'float', 'value': config.defaults['calib_yamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name': 'Calibration Z-Voltage Ampl.', 'type': 'float', 'value': config.defaults['calib_zamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name': 'Z-Coefficient', 'type': 'float', 'value': config.defaults['zcoeff'], 'step': 0.001}

            ]}
        ]

        # Create my parameter object and link it to methods
        self.p = Parameter.create(name='self.params', type='group', children=self.params)
        self.setParameters(self.p, showTop=False)

        self.p.sigTreeStateChanged.connect(self.sendChange) # When the params change, send to method to emit.

        # Connect keyPresses
        self.setFocusPolicy(Qt.NoFocus)

    def sendChange(self, param, changes):
        self.paramChange.emit(param, changes)

    def getParamValue(self, child, branch='Signal Design Parameters'):
        """Get the current value of a parameter."""
        return self.p.param(branch, child).value()

    def setParamValue(self, child, value, branch='Signal Design Parameters'):
        """Set the current value of a parameter."""
        return self.p.param(branch, child).setValue(value)

    def stepParamValue(self, child, delta, branch='Signal Design Parameters'):
        """Change a parameter by a delta. Can be negative or positive."""
        param = self.p.param(branch, child)
        curVal = param.value()
        newVal = curVal + delta
        return param.setValue(newVal)

    def on_key(self, key):
        """ On a keypress on the plot widget, forward the keypress to the correct function below."""
        qtk = QtCore.Qt
        # Its necessary to have this func map because the key is simply an integer I need to check against
        # the key dictionary in QtCore.Qt.
        func_map ={
            qtk.Key_Left: self.Key_Left,
            qtk.Key_Right: self.Key_Right,
            qtk.Key_Up: self.Key_Up,
            qtk.Key_Down: self.Key_Down,
            qtk.Key_G: self.Key_G,
            qtk.Key_F: self.Key_F,
            qtk.Key_B: self.Key_B,
            qtk.Key_V: self.Key_V,
            qtk.Key_Q: self.Key_Q,
            qtk.Key_W: self.Key_W,
            qtk.Key_T: self.Key_T
        }
        func = func_map.get(key, lambda: 'Not bound yet')
        return func()


    def Key_Left(self):
        self.setParamValue('Z-Phase', 90)

    def Key_Right(self):
        self.setParamValue('Z-Phase', 270)

    def Key_Up(self):
        self.setParamValue('Z-Phase', 0)

    def Key_Down(self):
        self.setParamValue('Z-Phase', 180)

    def Key_G(self):
        self.stepParamValue('Frequency', 10)

    def Key_F(self):
        self.stepParamValue('Frequency', -10)

    def Key_B(self):
        self.stepParamValue('Field Camber', 10)

    def Key_V(self):
        self.stepParamValue('Field Camber', -10)

    def Key_Q(self):
        self.stepParamValue('Voltage Multiplier', -0.25)

    def Key_W(self):
        self.stepParamValue('Voltage Multiplier', 0.25)

    def Key_T(self):
        """Toggles the toggle value"""
        curbool = self.getParamValue('Toggle Output')
        setbool = not curbool
        self.setParamValue('Toggle Output', setbool)

    def on_gamepad_event(self, gamepadEvent):
        """
        Parses the incoming gamepad events and forwards it to the appropriate keybind function below.
        For ease and less repetition, some buttons are forwarded to the keyboard functions.
        Args:
            gamepadEvent (list): incoming list from the controller class of format ['button', val]. ex. ['LJOY', 45]
        """
        func_map = {
            'BTN_WEST': self.Key_Q,
            'BTN_NORTH': self.Key_W,
            'BTN_EAST': self.Key_B,
            'BTN_SOUTH': self.Key_V,
            'LJOY': self.Joystick_Left
        }
        func = func_map.get(gamepadEvent[0], lambda: 'Not bound yet')
        if gamepadEvent[0] == 'LJOY':
            return func(gamepadEvent[1])
        else:
            return func()

    def Joystick_Left(self, degree):
        degree = 360 - degree  # convert joystick degrees to a zphase that makes sense
        self.setParamValue('Z-Phase', degree)

