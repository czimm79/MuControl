# MuControl
Created by Coy Zimmermann

### To-Do
**Version 0.5**
- Version Complete! Contains full read/write/control functionality with non-customizable keybinds.

**Version 1.0**
- **DONE** Enable a .ini file in which the following properties can be changed:
    - Read/Write buffer constants
    - NI device names
- Add a calibration mode
- Add in controller capabilities for plug and play controller
- Add in a QLabel widget that shows the current keybinds and a tip that the keybinds only work when the figure
    is the last thing that has been clicked!

**Version 1.1**
- Add a parametric plot of the signals to maybe see a circle in 3D. Would have to account for the zcoeff.


**Tips**
- To enable FFT in the app, modify fourier transform function and add a double division sign in the slices. Located in pyqtgraph/graphicsItems/PlotDataItem
