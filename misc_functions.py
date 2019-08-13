import numpy as np


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

    t = np.linspace(start=0, stop=ω / chunkspersec, num=funcg_rate//chunkspersec)

    output = np.array([
        I*(np.sin(ζ)*np.cos(t) - np.sin(θ)*np.cos(ζ)*np.sin(t)),  # x-coils
        I*(np.cos(ζ)*np.cos(t) - np.sin(θ)*np.sin(ζ)*np.sin(t)),  # y-coils
        zcoeff*I*(np.cos(θ)*np.sin(t))                            # z-coils
    ])
    return output


def generate_calib_waves(funcg_rate, writechunksize, calib_xamp, calib_yamp, calib_zamp, f=20):
    """ Generate three sin waves for calibration at 20Hz, 90 degrees out of phase from all."""

    ω = 2 * np.pi * f

    chunkspersec = funcg_rate // writechunksize  # Should be 10

    t = np.linspace(start=0, stop=ω / chunkspersec, num=funcg_rate//chunkspersec)
    output = np.array([
        np.cos(t),
        np.cos(t + (np.pi / 2)),
        np.cos(t + np.pi)
    ])
    return output