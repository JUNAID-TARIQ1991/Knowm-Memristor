
import dwfpy as dwf
from SetUp_AWG import initialize_instrument 

def SendWritePulse(awg_handle, Amplitude, Time_Period ,Num_Pulses,Channel):
    #import AWG_Module
    import time
    import dwfpy as dwf
    import numpy as np
    import matplotlib.pyplot as plt
    import threading
    from Configure_AWG import Generate_waveform
     


    # Calculate frequency in Hz
    frequency_hz = 1 / Time_Period

    # Convert frequency to kHz
    frequency_khz = frequency_hz / 1000

    # Format frequency to avoid scientific notation
    formatted_frequency = "{:.1f}".format(frequency_khz)  # Rounded to 1 decimal place
        
    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude,formatted_frequency, Num_Pulses, Channel) 
   

    return None
    
 
        
    