import numpy as np
from pyqtgraph.Qt import QtCore
import nidaqmx
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from misc_functions import generate_waves

class SignalWriter(QtCore.QThread):
    '''
    Thread that outputs signals to the function generator according to parameters.
    Keep in mind that the __init__ method only runs once to establish properties and default values.
    '''
    def __init__(self,
        funcg_name, writechannel_list,  # Inherent parameters of the funcg
        funcg_rate, writechunksize, zcoeff,  # Parameters that influence the resolution and rate, and zcoeff
        vmulti, freq, camber, zphase   # Signal Design Parameters
    ):
        super().__init__()  # Inherit properties of a QThread

        # Static variables
        self.funcg_name = funcg_name
        self.writechannel_list = writechannel_list
        self.funcg_rate = funcg_rate
        self.writechunksize = writechunksize
        self.zcoeff = zcoeff

        # Changing variables
        self.vmulti = vmulti
        self.freq = freq # single integer
        self.camber = camber
        self.zphase = zphase # single integer

        # pre-allocate an empty output array
        self.output = np.zeros([len(self.writechannel_list), self.writechunksize])
        self.running = False # Variable to keep track of whether the thread is running.

    def run(self):
        ''' This method runs when the thread is started using start().'''
        self.running = True
        self.writeTask = nidaqmx.Task()  # Start the task

        # Add input channels
        for i in self.writechannel_list:
            channel_string = self.funcg_name + '/' + f'ao{i}'
            self.writeTask.ao_channels.add_ao_voltage_chan(channel_string) # RSE = Referenced Single Ended


        # Set the generation rate, and buffer size.
        self.writeTask.timing.cfg_samp_clk_timing(
            rate = self.funcg_rate,
            sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS) # Set the rate in which the instrument collects data
            #samps_per_chan = 800) # This is the buffer size

        # Set more properties
        self.writeTask.out_stream.regen_mode = nidaqmx.constants.RegenerationMode.DONT_ALLOW_REGENERATION
        self.writeTask.out_stream.output_buf_size = 1600

        self.writeTask.register_every_n_samples_transferred_from_buffer_event(
            sample_interval=self.writechunksize,
            callback_method=self.add_more_data)


        # Initialize the writer
        self.writer = AnalogMultiChannelWriter(self.writeTask.out_stream)


        # Write the first set of data into the output buffer
        self.output = generate_waves(
            funcg_rate = self.funcg_rate,
            writechunksize = self.writechunksize,
            vmulti = self.vmulti,
            freq = self.freq,
            camber = self.camber,
            zphase = self.zphase,
            zcoeff = self.zcoeff)
        self.writer.write_many_sample(data = self.output)
        self.writer.write_many_sample(data = self.output)
        self.writeTask.start()

    def add_more_data(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        ''' This function is called every writechunksize to add another chunk of data to the buffer.'''
        self.output = generate_waves(
            funcg_rate = self.funcg_rate,
            writechunksize = self.writechunksize,
            vmulti = self.vmulti,
            freq = self.freq,
            camber = self.camber,
            zphase = self.zphase,
            zcoeff = self.zcoeff)
        self.writer.write_many_sample(data = self.output)

        return 0
