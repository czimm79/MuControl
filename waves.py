import numpy as np

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
        self.start_frac = 0.0
        self.counter = 0
        self.calib_counter = 0

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
        chunkspersec = funcg_rate // writechunksize
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

        chunkspersec = funcg_rate // writechunksize
        waves_per_chunk = f / chunkspersec  # 20 / 100 = 1/5
        start_frac = waves_per_chunk % 1

        freq_shifter = self.calib_counter * (2 * np.pi * start_frac)
        self.calib_counter += 1

        t = np.linspace(start=0, stop=ω / chunkspersec, num=writechunksize)
        output = np.array([
            calib_xamp * np.cos(t + freq_shifter),
            calib_yamp * np.cos(t + (np.pi / 2) + freq_shifter),
            calib_zamp * np.cos(t + np.pi + freq_shifter)
        ])
        return output

