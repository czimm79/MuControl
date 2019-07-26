# import nidaqmx
# with nidaqmx.Task() as task: # Instantiates nidaqmx.Task() as task for the indented block
#     task.ai_channels.add_ai_voltage_chan('Dev1/ai0')
#     datum = task.read()
#     print(datum)


# to get connected devices, type in console:
# import nidaqmx.system
# system = nidaqmx.system.System.local()
# print(system.driver_version)
# devices = [device for device in system.devices]
# print(devices)
import nidaqmx
from nidaqmx.stream_readers import (
    AnalogSingleChannelReader, AnalogMultiChannelReader)
import matplotlib.pyplot as plt
import numpy as np
sample_time = 1  #s
s_freq = 380 # samples/s
num_samples = sample_time*s_freq
buffer = 1
with nidaqmx.Task() as readTask:
    readTask.ai_channels.add_ai_voltage_chan('Dev1/ai0')
    readTask.timing.cfg_samp_clk_timing(rate = s_freq,
        sample_mode = nidaqmx.constants.AcquisitionType.CONTINUOUS) # Set the rate in which the instrument collects data
        #samps_per_chan = buffer)  # Since continuous, this number is the buffer size.

    output = np.zeros([1,100])
    plot_data = np.zeros([1,1000])
    # data = readTask.read(number_of_samples_per_channel=num_samples,
    #     timeout = nidaqmx.constants.WAIT_INFINITELY)
    reader = AnalogMultiChannelReader(readTask.in_stream)
    readTask.start()
    ptr = 0
    total_output = np.zeros([1,0])
    while ptr < 10:
        ptr += 1
        reader.read_many_sample(data = output,
                            number_of_samples_per_channel = 100)
        total_output = np.append(total_output, output)
        plot_data = np.roll(plot_data, -100) # Roll plot_data 100 data points to the left
        # print('Output Shape ' + str(output.shape))
        # print('plot_data shape ' + str(plot_data.shape))
        # print('total_output shape ' + str(total_output.shape))
        plot_data[0][-100:] = output[0] # Replace last 100 datapoints with the new data.


print(plot_data[0])
x = np.arange(0, len(plot_data[0]))
y = plot_data[0]

plt.plot(x, y)
plt.show()
