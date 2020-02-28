import numpy as np
import nidaqmx
import pyqtgraph as pg


class WaveGenerator:
    """A class containing the wave generating functions.

    Attributes:
        last_freq (float): a variable which stores the last frequency generated. This allows the wave generator
            to "know" if it needs to start the next wave chunk a portion through the wave
        waves_per_chunk (float): How many Hz happens in the writechunksize chunk.
        start_frac (float): The fraction of wave that was generated on the last chunk
    """
    def __init__(self):
        self.last_freq = 20
        self.waves_per_chunk = 2.0
        self.start_frac = 0.0
        self.counter = 0

    def generate_waves(self, funcg_rate, writechunksize, vmulti, freq, camber, zphase, zcoeff):
        """
        Given all signal parameters, a chunk of signal will be calculated and output.

        Args:
            funcg_rate : the rate at which samples are written from the function generator
            writechunksize : chunk size of signal to be calculated
            vmulti : voltage multiplier
            freq : frequency of wave in Hz
            camber : camber angle of field
            zphase : direction of the lowest(?) z point in the field
            zcoeff : a coefficient to account for zcoils being assymetric in a setup

        Returns:
            a [3,writechunksize] array of signal data
        """
        # Redefine input variables into shorthand characters
        I = vmulti
        f = freq
        ω = 2 * np.pi * f
        θ = np.radians(camber)
        ζ = np.radians(zphase)

        # Calculate some needed variables for the rest
        chunkspersec = funcg_rate // writechunksize  # Should be 10
        waves_per_chunk = f / chunkspersec
        start_frac = waves_per_chunk % 1

        t = np.linspace(start=0, stop=ω / chunkspersec, num=writechunksize)

        if self.last_freq != f:  # Then we can start generating waves as normal, starting from y=0
            self.counter = 0
            self.last_freq = f

        elif self.last_freq == f:
            self.counter += 1

        freq_shifter = self.counter * (2 * np.pi * start_frac)

        output = np.array([
            I * (np.sin(ζ) * np.cos(t + freq_shifter) - np.sin(θ) * np.cos(ζ) * np.sin(t + freq_shifter)),  # x-coils
            -I * (np.cos(ζ) * np.cos(t + freq_shifter) + np.sin(θ) * np.sin(ζ) * np.sin(t + freq_shifter)),  # y-coils
            zcoeff * I * (np.cos(θ) * np.sin(t + freq_shifter))  # z-coils
        ])

        return output

    def generate_calib_waves(self, funcg_rate, writechunksize, calib_xamp, calib_yamp, calib_zamp, f=20):
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


def set_style():
    """ Simply set some config options and themes. """
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOptions(antialias=True)
