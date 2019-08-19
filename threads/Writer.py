import numpy as np
from pyqtgraph.Qt import QtCore
import nidaqmx
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from misc_functions import generate_waves, generate_calib_waves, find_ni_devices


class SignalWriter(QtCore.QThread):
    """
    Thread that outputs signals to the function generator according to parameters.
    Keep in mind that the __init__ method only runs once to establish properties and default values.
    """
    errorMessage = QtCore.pyqtSignal(object)

    def __init__(self,
                 funcg_name, writechannel_list,  # Inherent parameters of the funcg
                 funcg_rate, writechunksize, zcoeff,  # Parameters that influence the resolution and rate, and zcoeff
                 vmulti, freq, camber, zphase,   # Signal Design Parameters
                 calib_xamp, calib_yamp, calib_zamp  # Calibration parameters
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

    def run(self):
        """ This method runs when the thread is started using start()."""
        self.running = True
        self.writeTask = nidaqmx.Task()  # Start the task

        # Add input channels
        for index, i in enumerate(self.writechannel_list):
            channel_string = self.funcg_name + '/' + f'ao{i}'
            try:
                self.writeTask.ao_channels.add_ao_voltage_chan(channel_string) # RSE = Referenced Single Ended
            except Exception as e:
                if index == 0:
                    self.errorMessage.emit('Could not open write channels. Are device names correct?'
                                           f" Devices connected: {find_ni_devices()}")
                    return

        # Set the generation rate, and buffer size.
        self.writeTask.timing.cfg_samp_clk_timing(
            rate = self.funcg_rate,
            sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS) # Set the rate in which the instrument collects data


        # Set more properties
        self.writeTask.out_stream.regen_mode = nidaqmx.constants.RegenerationMode.DONT_ALLOW_REGENERATION
        self.writeTask.out_stream.output_buf_size = 1600

        self.writeTask.register_every_n_samples_transferred_from_buffer_event(
            sample_interval=self.writechunksize,
            callback_method=self.add_more_data)

        # Initialize the writer
        self.writer = AnalogMultiChannelWriter(self.writeTask.out_stream)

        if not self.calib_mode:
            self.output = generate_waves(
                funcg_rate=self.funcg_rate,
                writechunksize=self.writechunksize,
                vmulti=self.vmulti,
                freq=self.freq,
                camber=self.camber,
                zphase=self.zphase,
                zcoeff=self.zcoeff)
        elif self.calib_mode:
            self.output = generate_calib_waves(
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

        self.writer.write_many_sample(data=self.output)  # if a data point is slightly late.
        self.writeTask.start()

    def add_more_data(self, task_handle, every_n_samples_event_type, number_of_samples, callback_data):
        """ This function is called every writechunksize to add another chunk of data to the buffer."""

        if not self.calib_mode:
            self.output = generate_waves(
                funcg_rate=self.funcg_rate,
                writechunksize=self.writechunksize,
                vmulti=self.vmulti,
                freq=self.freq,
                camber=self.camber,
                zphase=self.zphase,
                zcoeff=self.zcoeff)
        elif self.calib_mode:
            self.output = generate_calib_waves(
                funcg_rate=self.funcg_rate,
                writechunksize=self.writechunksize,
                calib_xamp=self.calib_xamp,
                calib_yamp=self.calib_yamp,
                calib_zamp=self.calib_zamp
            )

        self.writer.write_many_sample(data=self.output)

        return 0
