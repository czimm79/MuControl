import configparser
import ast

class Configuration:
    """ Reads in all of the configurable constants from config.ini. """
    def __init__(self):
        inifile = configparser.ConfigParser()  # Initialize the configparser
        inifile.read('config.ini')  # read in the config.ini file

        # READ
        self.daq_name = ast.literal_eval(inifile['READ']['daq_name'])
        self.readchannel_list = ast.literal_eval(inifile['READ']['readchannel_list'])
        self.daq_rate = int(inifile['READ']['daq_rate'])
        self.readchunksize = int(inifile['READ']['readchunksize'])

        # WRITE
        self.funcg_name = ast.literal_eval(inifile['WRITE']['funcg_name'])
        self.writechannel_list = ast.literal_eval(inifile['WRITE']['writechannel_list'])
        self.funcg_rate = int(inifile['WRITE']['funcg_rate'])
        self.writechunksize = self.funcg_rate // 10  # This keeps the frequency of the wave uniform.

        # DEFAULT SIGNAL VALUES
        self.defaults = {
            'vmulti': float(inifile['DEFAULT SIGNAL VALUES']['vmulti']),
            'freq': int(inifile['DEFAULT SIGNAL VALUES']['freq']),
            'camber': int(inifile['DEFAULT SIGNAL VALUES']['camber']),
            'zphase': int(inifile['DEFAULT SIGNAL VALUES']['zphase']),
            'calib_xamp': float(inifile['DEFAULT SIGNAL VALUES']['calib_xamp']),
            'calib_yamp': float(inifile['DEFAULT SIGNAL VALUES']['calib_yamp']),
            'calib_zamp': float(inifile['DEFAULT SIGNAL VALUES']['calib_zamp']),
            }

        self.zcoeff = float(inifile['DEFAULT SIGNAL VALUES']['zcoeff'])


if __name__ == '__main__':
    config = Configuration()
    # var = config.daq_name
