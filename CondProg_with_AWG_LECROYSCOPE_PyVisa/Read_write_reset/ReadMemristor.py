
def ReadMemristor(awg_handle, oscilloscope,  channel, Amplitude= 0.10):

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
    from DAQ_Lecroy.Voltage_Data_Osc import acquire_waveform, getG
    from Configure_Instrument.Configure_LecroyOsc import configure_oscilloscope
    import threading
    import ctypes
    
    #from Configure_AWG import Generate_waveform
    from Configure_Instrument.Configure_AWG import Generate_waveform
    
    
    # Parameters for waveform generation on AT_AWG to read
    
    #Amplitude = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
    #Amplitude = 0.10#  Voltage for read on AWG
    #Offset = Amplitude/2
    TimePeriod = 200e-06
    Frequency_hz = 1/TimePeriod
    Frequency = Frequency_hz/1000 # in khz
    NumPulses = 1
    #Measurement_duration = NoPulses * TimePeriod    
   

    # Parameters
    R = 9860
    # Resistance in ohms for current calculation
    
    #configure Lecroy
    configure_oscilloscope(oscilloscope, Frequency,  AnalogCompute=False)
    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude,Frequency, NumPulses, channel)
    time.sleep(0.1)  # Wait for the waveform to complete plus a small buffer time
    oscilloscope.write("STOP") # Iportant for 4104HD to stop acquisition and send data to PC. Otherwise, it will keep acquiring and not send data until acquisition is stopped.
    #Time and voltage data from scope #Acquire waveform from LeCroy Oscilloscope
    time_axis, voltage_data = acquire_waveform(oscilloscope, AnalogCompute= False)
    
    # Calculate current assuming a 10000Ω shunt resistor
    G = getG(voltage_data.mean(), R, Amplitude, AnalogCompute= False)
          
    return G
  