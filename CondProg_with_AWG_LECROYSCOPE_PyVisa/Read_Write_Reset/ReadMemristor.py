
def ReadMemristor(awg_handle, oscilloscope,  channel):

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
    from Voltage_Data_Osc import acquire_waveform, plot_waveform, getG
    from Configure_Istruments.Configure_LecroyOsc import configure_oscilloscope
    import threading
    import ctypes
    
    from Configure_Istruments.Configure_AWG import Generate_waveform
    
    # Parameters for waveform generation on AT_AWG to read
    
    #Amplitude = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
    Amplitude = 0.1#  Voltage for read on AWG
    #Offset = Amplitude/2
   #TimePeriod = 200e-06
    Frequency = 5# in khz
    NoPulses = 1
    #Measurement_duration = NoPulses * TimePeriod    
   

    # Parameters
    R = 9860
    # Resistance in ohms for current calculation
    
    #configure Lecroy
    configure_oscilloscope(oscilloscope, Frequency,  AnalogCompute=False)
    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude,Frequency, NoPulses, channel)
    time.sleep(0.1) # wait for waveform to be generated
    
    #Time and voltage data from scope
    #Acquire waveform from LeCroy Oscilloscope
    time_axis, voltage_data = acquire_waveform(oscilloscope, AnalogCompute= False)
    
    # Calculate current assuming a 10000Ω shunt resistor
    G = getG(voltage_data.mean(), R, Amplitude, AnalogCompute= False)
          
    return G
  