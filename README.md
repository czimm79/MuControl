# MuControl
Created by Coy Zimmermann

### To-Do
**Version 1.0**
- See if values changes in the parameter tree can be passed non-chalantly to the thread
    - If not, figure out how to make it happen. May need to use QMutex?
        - Check examples that involve sending snippets of info to a QThread for calculations.
        - Check the thread with campangola for the golden rules of using threading.
- Collect key presses from the user that can then change the parameter values.
    - Consider putting phase/direction of field in paramter tree..
        - Maybe even get fancy with an arrow plot to show direction?
- Get default values from a csv file, parse through a Configuration class. This will enable the user to set keybinds, set device ID, default frequency, amplitude, etc.
- Write thread functions
    - nidaqmx reader
    - nidaqmx writer
- Link the thread functions with the changing parameter tree
- Can I pull the FFT and max from the data without a significant performance hit?
    - If not, could send these calculations to another QThread.

**Version 1.1**
- Add a parametric plot of the signals to maybe see a circle in 3D. Would have to account for the zcoeff.
