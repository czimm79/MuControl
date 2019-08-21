import numpy as np
from pyqtgraph.Qt import QtCore
import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader
from misc_functions import find_ni_devices


class SignalReader(QtCore.QThread):
    """A QThread that periodically reads the voltages output by the data acquisition card.

    Attributes:
        daq_name (str): name given to the NI card by the drivers
        readchannel_list (list): list containing all of the connected channels
        daq_rate (int): rate at which the NI DAQ card collects data
        readchunksize (int): The QThread waits until there is *readchunksize* values in the buffer before emitting
        output (ndarray): the numpy array holding the voltage values, this object gets emit through the newData signal
        running (bool): used to control the state of the run loop from outside this thread

    """

    newData = QtCore.pyqtSignal(object)  # Designates that this class will have an output signal 'newData'
    errorMessage = QtCore.pyqtSignal(object)

    def __init__(self, daq_name, readchannel_list, daq_rate, readchunksize, delay=20):
        super().__init__()
        self.daq_name = daq_name
        self.readchannel_list = readchannel_list
        self.daq_rate = daq_rate
        self.readchunksize = readchunksize
        self.output = np.zeros([len(self.readchannel_list), self.readchunksize])
        self.running = False

    def run(self):
        """Runs when the start method is called on the thread.

        First, a nidaqmx is started using the Python with structure, which automatically stops the task when it is
        exited. Next, the thread tries to open the channels, but if it fails, emits an error signal. Next, the timing
        is set including the DAQ rate and sample mode. If not, again, it will emit an error.

        A multi-channel reader is defined and attached to the in_stream according to the nidaqmx structure. The task is
        start which then enables control over the reader. While the running bool is true, the thread waits for there to
        be *readchunksize* values, then emits them as an array.

        """
        self.running = True
        with nidaqmx.Task() as readTask:

            # Add input channels
            for index, i in enumerate(self.readchannel_list):
                channel_string = self.daq_name + '/' + i
                try:  # RSE = Referenced Single Ended
                    readTask.ai_channels.add_ai_voltage_chan(channel_string,
                                                             terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
                except Exception as e:
                    if index == 0:
                        self.errorMessage.emit(
                            "Couldn't initialize the read channels - is the read device name correct? "
                            f'Devices connected: {find_ni_devices()}')
                        return

            # Set timing and acquisition mode
            try:
                readTask.timing.cfg_samp_clk_timing(
                    rate=self.daq_rate,
                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
            except Exception as e:
                self.errorMessage.emit("Couldn't start the read task - is the read device name correct? "
                                       f'Devices connected: {find_ni_devices()}')
                return

            # Define the reader and start the *task*
            reader = AnalogMultiChannelReader(readTask.in_stream)
            readTask.start()

            # Waits until there are *readchunksize* values in the buffer and emits the output array
            while self.running:
                try:
                    reader.read_many_sample(data=self.output,
                                            number_of_samples_per_channel=self.readchunksize)
                    self.output = np.around(self.output, 4)
                    self.newData.emit(self.output)
                except Exception as e:
                    print(str(e))
                    pass
