class Configuration():
    ''' Contains all of the *mostly* static configurable constants. '''
    def __init__(self):
        # Reading
        self.daq_name = 'Dev1'
        self.readchannel_list = ['ai0','ai1','ai2','ai3','ai4','ai5']
        self.daq_rate = 2500 # Rate at which the DAQ collects data in samples per second
        self.chunksize = 100 # The reader waits until there are [chunksize] data points and pushes them to the plot

        # Writing
        self.funcg_name = 'cDAQ1Mod1'
        self.writechannel_list = [0, 1, 2]
        self.funcg_rate = 1000
        self.writechunksize = 1000
        # ParamTree
        self.defaults = {
            'vmulti' : 1.0,
            'freq' : 10,
            'zphase' : 0,
            'camber' : 0,
            'xvoltamp' : 1.0,
            'yvoltamp' : 1.0,
            'zvoltamp' : 1.0,
            }

        self.zcoeff = '0.653'
