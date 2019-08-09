### Old To-Do
**Version 1.0**
* See if values changes in the parameter tree can be passed non-chalantly to the thread
    * If not, figure out how to make it happen. May need to use QMutex?
        * Check examples that involve sending snippets of info to a QThread for calculations.
        * Check the thread with campangola for the golden rules of using threading.
* Collect key presses from the user that can then change the parameter values.
    * Consider putting phase/direction of field in paramter tree..
        - Maybe even get fancy with an arrow plot to show direction?
- Get default values from a csv file, parse through a Configuration class. This will enable the user to set keybinds, set device ID, default frequency, amplitude, etc.
* Write thread functions
    * nidaqmx reader
    * nidaqmx writer
- Link the thread functions with the changing parameter tree
- Can I pull the FFT and max from the data without a significant performance hit?
    - If not, could send these calculations to another QThread.
- Need more resolution, but to see a smaller portion of the wave.
- Need faster response time on keybinds, how fast the write is.

- Been having a lot of trouble writing data effectively. Every update to the buffer is overwriting, resulting in a wave that shifts approximately every second or so. The rate of skip is affected by the size of the output array.
    - I could try using register_every_n_samples_transferred_from_buffer_event that can count how many samples have been output, then once all of them are gone, supply more. (I THINK THIS IS THE WAY TO DO IT, based off of how MatLAB adds a listener a La : https://www.mathworks.com/help/daq/examples/generate-continuous-and-background-signals-using-ni-devices.html)
    - Look up the DAQWriteOffset error, wtf is happening there?

- Continuing - I can follow this example https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019Mg6SAE&l=en-US
    - Set nidaqmx.task.out_stream.regen_mode to this nidaqmx.constants.RegenerationMode.DONT_ALLOW_REGENERATION (https://nidaqmx-python.readthedocs.io/en/latest/constants.html)
    - Experiment with when to push data to the buffer by setting ao_data_xfer_req_cond with nidaqmx.constants.OutputDataTransferCondition. Look on line 32.
        - ON_BOARD_MEMORY_EMPTY
        - ON_BOARD_MEMORY_HALF_FULL_OR_LESS
        - ON_BOARD_MEMORY_LESS_THAN_FULL

-self.chan[i].ao_data_xfer_req_cond = nidaqmx.constants.OutputDataTransferCondition.ON_BOARD_MEMORY_HALF_FULL_OR_LESS