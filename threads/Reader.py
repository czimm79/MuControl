import numpy as np
from pyqtgraph.Qt import QtCore
import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader



class SignalReader(QtCore.QThread):
    """ Thread that periodically reads the voltages output by the data aquisition card."""

    newData = QtCore.pyqtSignal(object) # Designates that this class will have an output signal 'newData'

    def __init__(self, daq_name, readchannel_list, daq_rate, readchunksize, delay=20):
        super().__init__()
        self.daq_name = daq_name
        self.readchannel_list = readchannel_list
        self.daq_rate = daq_rate
        self.readchunksize = readchunksize
        self.output = np.zeros([len(self.readchannel_list),self.readchunksize])
        self.running = False

    def run(self):
        """ This method runs when the thread is started."""
        self.running = True
        with nidaqmx.Task() as readTask:
            #Add input channels
            for i in self.readchannel_list:
                channel_string = self.daq_name + '/' + i
                readTask.ai_channels.add_ai_voltage_chan(channel_string,
                terminal_config=nidaqmx.constants.TerminalConfiguration.RSE) # RSE = Referenced Single Ended

            readTask.timing.cfg_samp_clk_timing(
                rate = self.daq_rate,
                sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS) # Set the rate in which the instrument collects data
                #samps_per_chan = buffer)  # Since continuous, this number is the buffer size.


            reader = AnalogMultiChannelReader(readTask.in_stream)
            readTask.start()
            while self.running:
                try:
                    reader.read_many_sample(data = self.output,
                                        number_of_samples_per_channel = self.readchunksize)
                    self.output = np.around(self.output, 4)
                    self.newData.emit(self.output)
                except Exception as e:
                    print(str(e))
                    pass
