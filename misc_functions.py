import numpy as np
import nidaqmx


def generate_waves(funcg_rate, writechunksize, vmulti, freq, camber, zphase, zcoeff):
    """
    Given all signal parameters, a chunk of signal will be calculated and output.

    INPUTS:
    funcg_rate : the rate at which samples are written from the function generator
    writechunksize : chunk size of signal to be calculated
    vmulti : voltage multiplier
    freq : frequency of wave in Hz
    camber : camber angle of field
    zphase : direction of the lowest(?) z point in the field
    zcoeff : a coefficient to account for zcoils being assymetric in a setup

    OUTPUT:
    a [3,writechunksize] array of signal data
    """
    I = vmulti
    f = freq
    ω = 2 * np.pi * f
    θ = np.radians(camber)
    ζ = np.radians(zphase)

    chunkspersec = funcg_rate // writechunksize  # Should be 10

    t = np.linspace(start=0, stop=ω / chunkspersec, num=funcg_rate // chunkspersec)

    output = np.array([
        I * (np.sin(ζ) * np.cos(t) - np.sin(θ) * np.cos(ζ) * np.sin(t)),  # x-coils
        -I * (np.cos(ζ) * np.cos(t) + np.sin(θ) * np.sin(ζ) * np.sin(t)),  # y-coils
        zcoeff * I * (np.cos(θ) * np.sin(t))  # z-coils
    ])
    return output


def generate_calib_waves(funcg_rate, writechunksize, calib_xamp, calib_yamp, calib_zamp, f=20):
    """ Generate three sin waves for calibration at 20Hz, 90 degrees out of phase from all."""

    ω = 2 * np.pi * f

    chunkspersec = funcg_rate // writechunksize  # Should be 10

    t = np.linspace(start=0, stop=ω / chunkspersec, num=funcg_rate // chunkspersec)
    output = np.array([
        calib_xamp * np.cos(t),
        calib_yamp * np.cos(t + (np.pi / 2)),
        calib_zamp * np.cos(t + np.pi)
    ])
    return output


def find_ni_devices():
    system = nidaqmx.system.System.local()
    dev_name_list = []
    for device in system.devices:
        assert device is not None
        # device looks like "Device(name=cDAQ1Mod1)"
        dev_name = str(device).replace(')', '').split('=')[1]
        dev_name_list.append(dev_name)
    return str(dev_name_list)


def xy_to_cylindrical(x, y):
    """
    Convert the x and y coordinates from the joystick into degrees from 0 to 360.
    Args:
        x: x coordinate from joystick
        y: y coordinate from joystick

    Returns:
        magnitude: magnitude of x,y vector
        degrees: degrees from 0-360 starting from the positive y axis, clockwise
    """

    magnitude = np.around(np.linalg.norm((x, y)), 2)
    degrees = np.degrees(np.arctan2(x, y))
    degrees = degrees % 360  # Modulo division accounts for negative degree values pi to 2pi.
    degrees = np.around(degrees, 0)  # Round to the nearest integer
    return magnitude, degrees

