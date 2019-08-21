import numpy as np
from pyqtgraph.Qt import QtCore


class Generator(QtCore.QThread):
    """Debugging thread that generates random data to send to the plot in place of the national instruments cards.

    Uses np.random.normal to generate random data in a loop. Data is then emitted using the custom signal.

    """
    newData = QtCore.pyqtSignal(object)  # Designates that this class will have an output signal 'newData'

    def __init__(self, multi, freq, chunksize=100, delay=20):
        super().__init__()
        self.chunksize = chunksize
        self.delay = delay
        self.multi = multi
        self.freq = freq
        self.output = np.zeros([6, self.chunksize])
        self.running = False

    def run(self):
        """ This method runs when the thread is started."""
        self.running = True
        while self.running:
            try:
                self.output = self.multi * np.random.normal(size=(6, self.chunksize))
                self.newData.emit(self.output)  # send the new output to the pyqtSignal 'newData'
                QtCore.QThread.msleep(self.delay)
            except Exception as e:
                print(str(e))
                pass
