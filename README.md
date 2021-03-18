# MuControl

This repository contains MuControl, an open-source Python application intended for the manipulation and monitoring of electric signals for 3D electromagnet systems. This software was developed as part of the publication

> **An experimental design for the control and assembly of superparamagnetic microwheels** <br/>
> E.J. Roth, C.J. Zimmermann, D. Disharoon. T.O. Tasci, D.W.M. Marr, K.B. Neeves <br/>
> Review of Scientific Instruments (2020).


The goal of this app is to:

1. Output calculated signals to a *National Instruments (NI)* function generator to create a constant magnitude
   rotating 3-D magnetic field
2. Monitor the signals using a data acquisition card (NI) and resistor array (physical setup not covered in this guide)
   by plotting the input live
3. Allow for field parameters to be easily adjusted by using a graphical user interface, keyboard, or gamepad
4. Eliminate the need for the user to have any coding knowledge
5. Provide easy to understand visualizations
6. Eliminate the performance issues and frequent crashes of MATLAB
7. Provide a platform that can be extended with more features and advanced functionality (gradient tracking,
   computer vision, corkscrew modalities)
   
From the introduction of the [MuControl User Guide](https://czimm79.github.io/mucontrol-userguide/index.html).


## Changelog

#### Version 1.1

* Added swarm modalities -> Rolling, Corkscrew, Flipping, Switchback.
* Increased signal refresh rate to 40 1/s to allow for more complex swarm modalities.
* Switchback swarm can now be directed in any arbitrary direction during motion.
* Parameter Tree updated to allow for switching of swarm modalities, keybinds added and listed in UI.
* Code for swarm modalities renamed to ones that will be mentioned in my paper.

* Removed the setting for write signal generation rate, moving it to Python only modification.
* Moved the WaveGenerator class containing the field math to more appropriately named `waves.py`
* Refactored Qt compatible sleeps into a clean function in `misc_functions.py`


#### Version 1.0.4
Switched controller polling library to XInputs-Python (improves overall app performance).
Added functionality for non-multiple of 10 frequencies. All integers now produce the correct wave.

#### Version 1.0.3
Fixed bug where on certain computers the gamepad thread was not being terminated, resulting in a laggy experience. If it does not close, it is now
forcefully terminated.

#### Version 1.0.2
First distribution to collaborators. Minor documentation changes. App now pauses for 0.4 seconds before closing 
to insure threads are closed.

#### Version 1.0.0
Fully complete application. Quality control on multiple computers did not yield any bugs.. yet. User guide
is included and located in the help menu.


## Extra Info
Written by Coy Zimmermann in 2019-2021 as part of my PhD thesis work on magnetically propelled microwheels in Dr. David W.M.
Marr's group at the Colorado School of Mines.
