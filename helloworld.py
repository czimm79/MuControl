import random
import numpy as np
number_of_channels = 6
from ConfigurationClass import Configuration
import matplotlib.pyplot as plt
#[random.uniform(-10, 10) for _ in range(number_of_channels)]

config = Configuration()
freq = config.defaults['freq']
t = np.linspace(0,2*np.pi,10)
zcoeff = 0.653
I = 2.1
ζ = 0.1
θ = 0.2
output = np.array([
    I*(np.sin(ζ)*np.cos(t) - np.sin(θ)*np.cos(ζ)*np.sin(t)), # x-coils
    I*(np.cos(ζ)*np.cos(t) - np.sin(θ)*np.sin(ζ)*np.sin(t)), # y-coils
    zcoeff*I*(np.cos(θ)*np.sin(t))                           # z-coils
])

print(output.shape)
