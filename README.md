# MuControl

This repository contains MuControl, an open-source Python application intended for the manipulation and monitoring of electric signals for 3D electromagnet systems. This software was developed as part of the publication

> **An experimental design for the control and assembly of superparamagnetic microwheels** <br/>
> E.J. Roth, C.J. Zimmermann, D. Disharoon. T.O. Tasci, D.W.M. Marr, K.B. Neeves <br/>
> In *Review of Scientific Instruments* (to be submitted)

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

#### Version 1.0.4
Switched controller polling library to XInputs-Python (improves overall app performance.
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
Written by Coy Zimmermann in 2019 as part of my PhD thesis work on magnetically propelled microwheels in Dr. David W.M.
Marr's group at the Colorado School of Mines.
