
def ResetMemristor(awg_handle,  channel, No_Pulses, Amplitude = -2.0):

    """
    Arguments:
    Awg_handle -- The AT_AWG handle
    device -- the AnalogDiscovery2 device handle.
    
    Purpose:
    Reads the conductance of a selected memristor, assuming there is one and only one.
    """
    import time
    import dwfpy as dwf
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import threading
    import ctypes
    
    from Configure_Instrument.Configure_AWG import Generate_waveform
   
    
    # Parameters for waveform generation on AT_AWG to read
    
    #Amplitude = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
    #Amplitude = -2.0 # Voltage for reset
    #Offset = Amplitude/2
    
    Frequency = 5# in khz # TimePeriod = 200e-06
    NoPulses = No_Pulses
    #Measurement_duration = NoPulses * TimePeriod    



    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude,Frequency, NoPulses, channel) 
    time.sleep(0.2)

    return None
     