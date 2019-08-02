import random
import numpy as np
number_of_channels = 6
from ConfigurationClass import Configuration
import matplotlib.pyplot as plt
#[random.uniform(-10, 10) for _ in range(number_of_channels)]

config = Configuration()
freq = config.defaults['freq']
x = np.linspace(start=0, stop=2*np.pi*freq, num=config.writechunksize)
y = np.array(
    [np.sin(2*x),
    np.sin(x)]
    )

plt.plot(x,y)
