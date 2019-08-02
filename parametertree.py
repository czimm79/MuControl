import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
from PyQt5.QtCore import Qt
from ConfigurationClass import Configuration


class MyParamTree(ParameterTree):
    paramChange = QtCore.pyqtSignal(object, object) # MyParamTree outputs a signal with param and changes.

    def __init__(self):
        super().__init__()
        self.configs = Configuration()
        self.defaults = self.configs.defaults
        self.params =[
            {'name': 'Signal Design Parameters', 'type': 'group', 'children': [
                {'name': 'Toggle', 'type': 'bool', 'value': False, 'tip': "Toggle the output"},
                {'name': 'Voltage Multiplier', 'type': 'float', 'value': self.defaults['vmulti'], 'step': 0.25},
                {'name': 'Frequency', 'type': 'float', 'value': self.defaults['freq'], 'step': 10, 'siPrefix': True, 'suffix': 'Hz'},
                {'name': 'Z-Phase', 'type': 'float', 'value': self.defaults['zphase'], 'step': 90},
                {'name': 'Field Camber', 'type': 'int', 'value': self.defaults['camber'], 'step': 1, 'siPrefix': True, 'suffix': '°'}
            ]},
            {'name' : 'Passive Output Signal Properties', 'type': 'group', 'children': [
                {'name' : 'X-Voltage Amplitude', 'type': 'float', 'value': self.defaults['xvoltamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name' : 'Y-Voltage Amplitude', 'type': 'float', 'value': self.defaults['yvoltamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'},
                {'name' : 'Z-Voltage Amplitude', 'type': 'float', 'value': self.defaults['zvoltamp'], 'step': 0.1, 'siPrefix': True, 'suffix': 'V'}
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
        '''Get the current value of a parameter.'''
        return self.p.param(branch, child).value()

    def setParamValue(self, child, value, branch='Signal Design Parameters'):
        '''Set the current value of a parameter.'''
        return self.p.param(branch, child).setValue(value)

    def stepParamValue(self, child, delta, branch='Signal Design Parameters'):
        '''Change a parameter by a delta. Can be negative or positive.'''
        param = self.p.param(branch, child)
        curVal = param.value()
        newVal = curVal + delta
        return param.setValue(newVal)


    def on_key(self, key):
        ''' On a keypress on the plot widget, forward the keypress to the correct function below.'''
        qtk = QtCore.Qt
        # Its necessary to have this func map because the key is simply an integer I need to check against
        # the key dictionary in QtCore.Qt.
        func_map ={
        qtk.Key_Left : self.Key_Left,
        qtk.Key_Right : self.Key_Right,
        qtk.Key_Up : self.Key_Up,
        qtk.Key_Down : self.Key_Down,
        qtk.Key_G : self.Key_G,
        qtk.Key_F : self.Key_F
        }
        func = func_map.get(key, lambda: 'Not bound yet')
        return func()


    def Key_Left(self):
        print('Left')
        self.setParamValue('Z-Phase', 90)

    def Key_Right(self):
        print('Right')
        self.setParamValue('Z-Phase', 270)

    def Key_Up(self):
        print('Up')
        self.setParamValue('Z-Phase', 0)

    def Key_Down(self):
        print('Down')
        self.setParamValue('Z-Phase', 180)

    def Key_G(self):
        print('G')
        self.stepParamValue('Frequency', 10)

    def Key_F(self):
        print('F')
        self.stepParamValue('Frequency', -10)
