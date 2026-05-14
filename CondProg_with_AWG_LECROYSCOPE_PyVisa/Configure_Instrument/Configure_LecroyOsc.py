import pyvisa
import numpy as np
import time
import matplotlib.pyplot as plt
import math

def flush_errors(Oscilloscope):
    """
    Flushes all errors from the AWG.
    """
    def get_err_num(err_string):
        try:
            # Extract substring before the first comma
            substring = err_string.split(',')[0]
            # Convert the substring to a number (float or int)
            number = float(substring) if '.' in substring else int(substring)
            return number
        except ValueError:
            # Handle cases where conversion fails
            return None

    err = Oscilloscope.query('SYST:ERR?')
    print(err)                   
    # Query for errors until receive: "0,No error"
    while get_err_num(err) != 0:
        err = Oscilloscope.query('SYST:ERR?')
        print(err)



def configure_oscilloscope(oscilloscope, Frequency, AnalogCompute=False):
    Frequency_Hz = Frequency * 1e3
    time_period = 1 / Frequency_Hz  # Time period in seconds
    #print(f"{time_period:.3e}")

    if AnalogCompute:
        
        #flush_errors(oscilloscope)
        #oscilloscope.write("CLR")
        oscilloscope.write("vbs 'app.ClearSweeps'")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("CHDR OFF")
        #flush_errors(oscilloscope)

        oscilloscope.write("COMM_FORMAT DEF9,WORD,BIN")    
        #flush_errors(oscilloscope)  
        
        oscilloscope.write("ACQUIRE_NUM_AVG 16")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("TRIG_MODE NORM")
        #flush_errors(oscilloscope)
        
        
        #oscilloscope.write("TRIG_SELECT EDGE,SR,C3,POS")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("C3:TRIG_LEVEL 0.5V")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("C4:VDIV 0.2V")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("C4:OFFSET 0.0V")
        #oscilloscope.write("C4:OFFSET 0.03V")

        #flush_errors(oscilloscope)
        
        oscilloscope.write("C4:TRACE ON")
       # flush_errors(oscilloscope)
        
        oscilloscope.write(f"TIME_DIV {time_period:.6e}")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("ARM")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("WAIT")
        #flush_errors(oscilloscope)

    else:   
     #oscilloscope.write("COMM_FORMAT DEF9,WORD,BIN")
        oscilloscope.write("vbs 'app.ClearSweeps'")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("CHDR OFF")
        #flush_errors(oscilloscope)

        oscilloscope.write("COMM_FORMAT DEF9,WORD,BIN")    
        #flush_errors(oscilloscope)  
        #oscilloscope.write("ACQUIRE_MODE AVERAGE")
        #flush_errors(oscilloscope)
        
        #oscilloscope.write("ACQUIRE_NUM_AVG 16")
        #flush_errors(oscilloscope)

        oscilloscope.write("TRIG_MODE NORM")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("TRIG_SELECT EDGE,SR,C3")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("C3:TRIG_LEVEL 0.5V")
        #flush_errors(oscilloscope)

        #oscilloscope.write("SELECT:CH4 ON")
        oscilloscope.write("C4:TRACE ON")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("C4:VDIV 0.1V")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("C4:OFFSET 0.00V")
        #flush_errors(oscilloscope)
        
        #oscilloscope.write("C4:COUPLING DC")
        #oscilloscope.write("VBS 'app.C4.Coupling = \"DC1M\"'")
        #flush_errors(oscilloscope)
        

        oscilloscope.write(f"TIME_DIV {time_period:.3e}")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("ARM")
        #flush_errors(oscilloscope)
        
        oscilloscope.write("WAIT 5") # Wait for 5 seconds to ensure the oscilloscope is ready and has acquired the waveform
        #flush_errors(oscilloscope)
    #print(f"Oscilloscope Configured for Frequency {Frequency_Hz:.3e} (Time Div: {time_period:.3e} sec)")
   
    return None