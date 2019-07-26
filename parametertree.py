import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

class MyParamTree(ParameterTree):
    def __init__(self):
        super().__init__()
        self.params = [
            {'name': 'Signal Design Parameters', 'type': 'group', 'children': [
                {'name': 'Current Multiplier', 'type': 'float', 'value': 1, 'step': 0.25},
                {'name': 'Frequency', 'type': 'float', 'value': 10, 'step': 10},
                {'name': 'Toggle', 'type': 'bool', 'value': True, 'tip': "Toggle the output"}
            ]}
        ]

        # Create my parameter object and link it to methods
        self.p = Parameter.create(name='self.params', type='group', children=self.params)
        self.p.sigTreeStateChanged.connect(self.change)
        for child in self.p.children():
            child.sigValueChanging.connect(self.valueChanging)

        self.setParameters(self.p, showTop=False)

    def valueChanging(self, param, value):
        print(f"Value changing (not finalized): {param} {value}")


    def change(self, param, changes):
        print("tree changes:")
        for param, change, data in changes:
            path = self.p.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            print('  parameter: %s'% childName)
            print('  change:    %s'% change)
            print('  data:      %s'% str(data))
            print('  ----------')
