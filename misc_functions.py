import numpy as np


def generate_waves(funcg_rate, writechunksize, vmulti, freq, camber, zphase, zcoeff):
    '''
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
    '''
    I = vmulti
    f = freq
    ω = 2 * np.pi * f
    θ = np.radians(camber)
    ζ = np.radians(zphase)

    if funcg_rate % writechunksize == 0:
        chunkspersec = funcg_rate // writechunksize # calculation of this integer allows for uniform frequency if the
                                                    # chunksize is evenly divisible in funcg_rate
    else:
        raise Exception('funcg_rate cannot be evenly divided by writechunk size.')


    t = np.linspace(start=0, stop=ω/chunkspersec, num=funcg_rate//chunkspersec)
    output = np.array([
        I*(np.sin(ζ)*np.cos(t) - np.sin(θ)*np.cos(ζ)*np.sin(t)), # x-coils
        I*(np.cos(ζ)*np.cos(t) - np.sin(θ)*np.sin(ζ)*np.sin(t)), # y-coils
        zcoeff*I*(np.cos(θ)*np.sin(t))                           # z-coils
    ])
    return output


# # Code block for testing
# if __name__ == '__main__':
#     from ConfigurationClass import Configuration
#     import matplotlib.pyplot as plt
#     config = Configuration()
#     testout = generate_waves(
#         config.writechunksize,
#         config.funcg_rate,
#         config.defaults['vmulti'],
#         config.defaults['freq'],
#         config.defaults['camber'],
#         config.defaults['zphase'],
#         config.zcoeff
#     )
#     print(len(testout[0]))
#     plt.plot(t, testout[0])
#     plt.plot(t, testout[1])
#     plt.plot(t, testout[2])
#     plt.show()
