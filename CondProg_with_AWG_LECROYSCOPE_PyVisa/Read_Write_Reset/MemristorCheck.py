
import dwfpy as dwf
from Configure_Istruments.SetUp_AWG import initialize_instrument 

def SendTriangularPulse(awg_handle, Channel):
   
    from Configure_Istruments.Configure_AWG import Generate_waveform
    Time_Period = 500e-03  # 200 microseconds
    Amplitude = 1.5  # Voltage for read on AWG
    # Calculate frequency in Hz
    frequency_hz = 1 / Time_Period
    # Convert frequency to kHz
    frequency_khz = frequency_hz / 1000
    Num_Pulses = 5

    # Format frequency to avoid scientific notation
    formatted_frequency = "{:.1f}".format(frequency_khz)  # Rounded to 1 decimal place
        
    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude,formatted_frequency, Num_Pulses, Channel, MemristorCheck=True) 
   

    return None
    
 
        
    