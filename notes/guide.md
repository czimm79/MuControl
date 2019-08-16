#Guide
##Variables
####WRITE
- daq_rate : Rate at which the DAQ collects data in samples per second
- readchunksize : The reader waits until there are [readchunksize] data points then emits



## Prepping for installer export:
1) Move config.ini to `src/main/resources/base`
2) Switch filepath in ConfigurationClass to the appctxt dependent one.
3) In main.py, switch appctxt comments on and remove old PyQt5 ones.