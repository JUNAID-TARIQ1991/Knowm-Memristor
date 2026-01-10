
def ResetMemristor(awg_handle,  channel):

    """
    Arguments:
    Awg_handle -- The AT_AWG handle
    device -- the AnalogDiscovery2 device handle.
    
    Purpose:
    Reads the conductance of a selected memristor, assuming there is one and only one.
    """
    
    from Configure_AWG import Generate_waveform
   
    
    # Parameters for waveform generation on AT_AWG to read
    
    #Amplitude = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
    Amplitude = -1.0#  Voltage for read on AWG
    #Offset = Amplitude/2
    TimePeriod = 200e-06
    Frequency = 5 # in khz
    NoPulses = 100
    #Measurement_duration = NoPulses * TimePeriod    


 
    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude,Frequency, NoPulses, channel) 
    return None
     