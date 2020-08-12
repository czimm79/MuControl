import numpy as np
from pyqtgraph.Qt import QtCore
import nidaqmx
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from misc_functions import WaveGenerator, find_ni_devices


class SignalWriter(QtCore.QThread):
    """A QThread that periodically reads the voltages output by the data acquisition card.

    This thread outputs signals to the function generator according to parameters. These parameters can be modified
    by other threads as this thread simply reads them. Also, keep in mind that the __init__ method only runs once to
    establish properties and default values.

    Attributes:
        funcg_name (str): name given to the NI card by the drivers
        writechannel_list (list): list containing all of the connected channels
        funcg_rate (int): rate at which the NI DAQ card generate data
        writechunksize (int): The QThread adds this amount of data to the buffer at once. Hard coded to be the rate
            divided by 10.
        zcoeff (float): used to calculate the signals, defined in detail other places
        running (bool): used to control the state of the run loop from outside this thread

    """
    errorMessage = QtCore.pyqtSignal(object)

    def __init__(self, funcg_name, writechannel_list, funcg_rate, writechunksize, zcoeff, vmulti, freq, camber, zphase,
                 calib_xamp, calib_yamp, calib_zamp):
        super().__init__()  # Inherit properties of a QThread

        # Static variables
        self.funcg_name = funcg_name
        self.writechannel_list = writechannel_list
        self.funcg_rate = funcg_rate
        self.writechunksize = writechunksize
        self.zcoeff = zcoeff

        # Changing variables
        self.vmulti = vmulti
        self.freq = freq  # single integer
        self.camber = camber
        self.zphase = zphase  # single integer

        # Calibration variables
        self.calib_mode = False  # variable to store whether in calibration mode
        self.calib_xamp = calib_xamp
        self.calib_yamp = calib_yamp
        self.calib_zamp = calib_zamp

        # pre-allocate an empty output array
        self.output = np.zeros([len(self.writechannel_list), self.writechunksize])
        self.running = False  # Variable to keep track of whether the thread is running.

        # Instantiate the WaveGenerator
        self.WaveGen = WaveGenerator()

    def run(self):
        """Runs when the start method is called on the thread.

        First, the output channels are initialized. If the thread can't, it emits an error signal. Next, it sets the
        generation rate and mode. Other properties are set for continuous modulation of the signal.

        The buffer size is set to be 2 times the *writechunksize* to allow for some wiggle room if a data point is a
        microsecond late.

        Next, an event is registered along with the continuous generation mode that signals the **add_more_data**
        method after every *writechunksize* values are transferred from the buffer. This is what allows this run method
        to loop, as the writeTask never truly finishes as data points are constantly being added to the buffer.

        For the first write to the buffer, two *writechunksize* chunks are written to fill up the buffer completely.

        """
        self.running = True
        self.writeTask = nidaqmx.Task()  # Start the task

        # Add input channels
        for index, i in enumerate(self.writechannel_list):
            channel_string = self.funcg_name + '/' + f'ao{i}'
            try:
                self.writeTask.ao_channels.add_ao_voltage_chan(channel_string)
            except Exception as e:
                if index == 0:
                    self.errorMessage.emit('Could not open write channels. Are device names correct?'
                                           f" Devices connected: {find_ni_devices()}")
                    return

        # Set the generation rate, and buffer size.
        self.writeTask.timing.cfg_samp_clk_timing(
            rate=self.funcg_rate,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

        # Set more properties for continuous signal modulation
        self.writeTask.out_stream.regen_mode = nidaqmx.constants.RegenerationMode.DONT_ALLOW_REGENERATION
        self.writeTask.out_stream.output_buf_size = 2 * self.writechunksize

        # Register the listening method to add more data
        self.writeTask.register_every_n_samples_transferred_from_buffer_event(
            sample_interval=self.writechunksize,
            callback_method=self.add_more_data)

        # Initialize the writer
        self.writer = AnalogMultiChannelWriter(self.writeTask.out_stream)

        if not self.calib_mode:
            self.output = self.WaveGen.generate_waves(
                funcg_rate=self.funcg_rate,
                writechunksize=self.writechunksize,
                vmulti=self.vmulti,
                freq=self.freq,
                camber=self.camber,
                zphase=self.zphase,
                zcoeff=self.zcoeff)
        elif self.calib_mode:
            self.output = self.WaveGen.generate_calib_waves(
                funcg_rate=self.funcg_rate,
                writechunksize=self.writechunksize,
                calib_xamp=self.calib_xamp,
                calib_yamp=self.calib_yamp,
                calib_zamp=self.calib_zamp
            )

        # Write the first set of data into the output buffer
        try:
            self.writer.write_many_sample(data=self.output)  # Write two chunks of beginning data to avoid interruption
        except:
            self.errorMessage.emit('Could not write data to the output. Is the output device name correct?'
                                   f" Devices connected: {find_ni_devices()}")
            return

        self.writer.write_many_sample(data=self.output)  # write a second chunk to the buffer

        # Start the task, which will hold the thread at this location, continually calling add_more_data
        self.writeTask.start()

    def add_more_data(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        """This method adds data to the buffer when it is called.

        If running is false, it instead closes the NI writeTask.

        """
        if self.running is True:
            if not self.calib_mode:
                self.output = self.WaveGen.generate_waves(
                    funcg_rate=self.funcg_rate,
                    writechunksize=self.writechunksize,
                    vmulti=self.vmulti,
                    freq=self.freq,
                    camber=self.camber,
                    zphase=self.zphase,
                    zcoeff=self.zcoeff)
            elif self.calib_mode:
                self.output = self.WaveGen.generate_calib_waves(
                    funcg_rate=self.funcg_rate,
                    writechunksize=self.writechunksize,
                    calib_xamp=self.calib_xamp,
                    calib_yamp=self.calib_yamp,
                    calib_zamp=self.calib_zamp
                )
            self.writer.write_many_sample(data=self.output)

        else:
            self.writeTask.close()

        return 0
