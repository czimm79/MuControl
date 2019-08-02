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
        writeTask = nidaqmx.Task()
        # Add input channels
        for i in self.writechannel_list:
            channel_string = self.funcg_name + '/' + f'ao{i}'
            writeTask.ao_channels.add_ao_voltage_chan(channel_string) # RSE = Referenced Single Ended
        # Set the generation rate, and buffer size.
        writeTask.timing.cfg_samp_clk_timing(
            rate = self.funcg_rate,
            sample_mode = nidaqmx.constants.AcquisitionType.FINITE) # Set the rate in which the instrument collects data
            #samps_per_chan = self.funcg_rate * 2)  # Since continuous, this number is the buffer size.

        # Initialize the writer
        writer = AnalogMultiChannelWriter(writeTask.out_stream, auto_start=True)
        # Write the first set of data into the output buffer
        self.x = np.linspace(start=0, stop=2*np.pi*self.freq, num=self.funcg_rate)
        self.output = np.array([
            self.amps[0] * np.sin(self.x),
            self.amps[1] * np.sin(self.x + np.pi/2),
            self.amps[2] * np.sin(self.x + self.zphase*np.pi/180)
            ])
        writer.write_many_sample(data = self.output)
        ###### COuld try using taskhandle.WaitUntilTaskDone(-1)
        # from https://forums.ni.com/t5/Multifunction-DAQ/Using-PFI-to-Trigger-an-Analog-Output-Generation/td-p/3621223?profile.language=en
        # from https://forums.ni.com/t5/Multifunction-DAQ/Multichannel-analog-output-Python-NiDaqmx/m-p/3846472?profile.language=en

        while self.running: # Add new data to the buffer
            writeTask.wait_until_done()
            QtCore.QThread.msleep(1000)


            self.x = np.linspace(start=0, stop=2*np.pi*self.freq, num=self.funcg_rate)
            self.output = np.array([
                self.amps[0] * np.sin(self.x),
                self.amps[1] * np.sin(self.x + np.pi/2),
                self.amps[2] * np.sin(self.x + self.zphase*np.pi/180)
                ])
            #writeTask.wait_until_done()
            print(writer.write_many_sample(data = self.output))
                                    #number_of_samples_per_channel = self.writechunksize)
            #writeTask.start()

            #writeTask.wait_until_done()
