
import dwfpy as dwf
from Configure_Instrument.SetUp_AWG import initialize_instrument 
import time
def Pulse4StuckHigh(awg_handle, Channel, Time_Period, Amplitude, No_pulses):
   
    from Configure_Instrument.Configure_AWG import Generate_waveform
    Time_Period = Time_Period # 5 milliseconds
    Amplitude = Amplitude # Voltage on AWG
    # Calculate frequency in Hz
    frequency_hz = 1 / Time_Period
    # Convert frequency to kHz
    frequency_khz = frequency_hz / 1000
    #print("frequency in kHz", frequency_khz)
    Num_Pulses = No_pulses
           
    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude,frequency_khz, Num_Pulses, Channel,Stuck_high=True) 
    time.sleep( 0.5)  # Wait for the waveform to complete plus a small buffer time
    return None
    
 
        
    