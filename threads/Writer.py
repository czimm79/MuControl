import numpy as np
from pyqtgraph.Qt import QtCore
import nidaqmx
from nidaqmx.stream_writers import AnalogMultiChannelWriter

class SignalWriter(QtCore.QThread):
    ''' Thread that outputs signals to the function generator according to parameters.'''
    def __init__(self, funcg_name, writechannel_list, funcg_rate, writechunksize, def_amps, def_freq, def_zphase,
        delay=20):
        super().__init__()
        self.funcg_name = funcg_name
        self.writechannel_list = writechannel_list
        self.funcg_rate = funcg_rate
        self.writechunksize = writechunksize
        # Changing values, these are simply defaults when the class is instantiated
        self.amps = def_amps # array of 3 values
        self.freq = def_freq # single integer
        self.zphase = def_zphase # single integer

        self.output = np.zeros([len(self.writechannel_list), self.writechunksize]) # pre-allocate arrays
        self.running = False
        self.delay = self.writechunksize / self.funcg_rate

    def run(self):
        ''' This method runs when the thread is started.'''
        self.running = True
        self.writeTask = nidaqmx.Task()
        # Add input channels
        for i in self.writechannel_list:
            channel_string = self.funcg_name + '/' + f'ao{i}'
            self.chan[i] = self.writeTask.ao_channels.add_ao_voltage_chan(channel_string) # RSE = Referenced Single Ended
            #self.chan[i].
        # Set the generation rate, and buffer size.
        self.writeTask.timing.cfg_samp_clk_timing(
            rate = self.funcg_rate,
            sample_mode = nidaqmx.constants.AcquisitionType.FINITE) # Set the rate in which the instrument collects data
            #samps_per_chan = self.funcg_rate * 2)  # Since continuous, this number is the buffer size.

        #self.writeTask.out_stream.relative_to = nidaqmx.constants.WriteRelativeTo.FIRST_SAMPLE

        self.x = np.linspace(start=0, stop=2*np.pi*self.freq, num=self.writechunksize)
        self.output = np.array([
            self.amps[0] * np.sin(self.x),
            self.amps[1] * np.sin(self.x + np.pi/2),
            self.amps[2] * np.sin(self.x + self.zphase*np.pi/180)
            ])

        self.writeTask.register_done_event(self.callback_done)
        # self.writeTask.register_every_n_samples_transferred_from_buffer_event(
        #     sample_interval=self.writechunksize,
        #     callback_method=self.callback_transfer)


        # Initialize the writer
        self.writer = AnalogMultiChannelWriter(self.writeTask.out_stream)

        # Write the first set of data into the output buffer
        self.writer.write_many_sample(data = self.output)

        self.writeTask.start()

        # while self.running:
        #     QtCore.QThread.msleep(1000)
        #     self.writeTask.stop()
        #     self.writer.write_many_sample(data = self.output)
        #     self.writeTask.start()

    def callback_done(self, task_handle, status, callback_data):
        self.x = np.linspace(start=0, stop=2*np.pi*self.freq, num=self.writechunksize)
        self.output = np.array([
            self.amps[0] * np.sin(self.x),
            self.amps[1] * np.sin(self.x + np.pi/2),
            self.amps[2] * np.sin(self.x + self.zphase*np.pi/180)
            ])
        self.writeTask.stop()
        self.writeTask.write(data = self.output)
        self.writeTask.start()


        return 0

    def callback_transfer(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        print('got to the callback')
        print(number_of_samples)
        self.writeTask.stop()
        self.x = np.linspace(start=0, stop=2*np.pi*self.freq, num=self.writechunksize)
        self.output = np.array([
            self.amps[0] * np.sin(self.x),
            self.amps[1] * np.sin(self.x + np.pi/2),
            self.amps[2] * np.sin(self.x + self.zphase*np.pi/180)
            ])
        self.writer.write_many_sample(data = self.output)
        self.writeTask.start()
        return 0
        # while self.running: # Add new data to the buffer
        #     self.writeTask.wait_until_done()
        #     QtCore.QThread.msleep(1000)
        #
        #
        #     self.x = np.linspace(start=0, stop=2*np.pi*self.freq, num=self.funcg_rate)
        #     self.output = np.array([
        #         self.amps[0] * np.sin(self.x),
        #         self.amps[1] * np.sin(self.x + np.pi/2),
        #         self.amps[2] * np.sin(self.x + self.zphase*np.pi/180)
        #         ])
        #     #self.writeTask.wait_until_done()
        #     print(writer.write_many_sample(data = self.output))
        #                             #number_of_samples_per_channel = self.writechunksize)
            #self.writeTask.start()

            #self.writeTask.wait_until_done()
