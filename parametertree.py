import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

class MyParamTree(ParameterTree):
    paramChange = QtCore.pyqtSignal(object, object) # MyParamTree outputs a signal with param and changes.

    def __init__(self):
        super().__init__()
        self.params = [
            {'name': 'Signal Design Parameters', 'type': 'group', 'children': [
                {'name': 'Toggle', 'type': 'bool', 'value': False, 'tip': "Toggle the output"},
                {'name': 'Current Multiplier', 'type': 'float', 'value': 1, 'step': 0.25, 'limits': (0,4)},
                {'name': 'Frequency', 'type': 'float', 'value': 10, 'step': 10},
                {'name': 'Z-Phase', 'type': 'float', 'value': 0, 'step': 90}
            ]}
        ]

        # Create my parameter object and link it to methods
        self.p = Parameter.create(name='self.params', type='group', children=self.params)
        self.setParameters(self.p, showTop=False)

        # for child in self.p.children():
        #     child.sigValueChanging.connect(self.valueChanging)

        self.p.sigTreeStateChanged.connect(self.sendChange) # When the params change, send to method to emit.

    # def valueChanging(self, param, value):
    #     print(f"Value changing (not finalized): {param} {value}")


    def sendChange(self, param, changes):
        self.paramChange.emit(param, changes)

    def getParamValue(self, child, branch='Signal Design Parameters'):
        '''Get the current value of a parameter.'''
        return self.p.param(branch, child).value()
