import pyvisa
import numpy as np
import time
import matplotlib.pyplot as plt
from SetUp_LeCroy import initialize_instrument 
from Voltage_Data_copy import acquire_waveform, plot_waveform, calculate_current


def configure_oscilloscope(oscilloscope):
    # """Configure the oscilloscope settings."""
    
    # #oscilloscope.write(r"""vbs 'app.settodefaultsetup' """)
    # oscilloscope.write("vbs 'app.ClearSweeps'")

    # #oscilloscope.write(f"C{4}:VDIV 0.1")  # Set voltage division (20mV/div)
    # #oscilloscope.write(f"C{4}:TDIV 50e-6")  # Set time division (50us/div)
    #   # Set the timebase and trigger settings
    # oscilloscope.write("TRIG_MODE NORM")  # Set trigger mode to Normal
    # oscilloscope.write("TRIG_SELECT EDGE,SR,EXT")  # Set trigger source to external (assuming C4 is the external trigger)
    # oscilloscope.write("C4:TRIG_LEVEL 0.4V")  # Set trigger level to 1.0V (adjust as needed)
    
    # # Set up channel 4
    # oscilloscope.write("C4:VDIV 0.1V")  # Set vertical scale to 1.0V/div (adjust as needed)
    # oscilloscope.write("C4:OFFSET 0.0V")  # Set vertical offset to 0V
    # oscilloscope.write("C4:COUpling DC")  # Set coupling to DC (or AC if needed)
    
    # # Set the timebase
    # oscilloscope.write("TIME_DIV 100.0E-6")  # Set timebase to 1us/div (adjust as needed)
    
    # # Arm the trigger and wait for the acquisition
    # oscilloscope.write("ARM")  # Arm the trigger
    # oscilloscope.write("WAIT")  # Wait for the acquisition to complete
    
    return None
    # Retrieve the waveform data from channel 4
    oscilloscope.write("C4:WF?")  # Request waveform data from channel 4
    waveform_data = oscilloscope.read_raw()  # Read the raw waveform data
    
    # Parse the waveform data
    # The waveform data is typically in binary format, so we need to parse it
    # The first few bytes contain the header information, followed by the actual waveform data
    header_length = int(waveform_data[1:2])  # Get the length of the header
    header = waveform_data[2:2+header_length].decode('ascii')  # Decode the header
    waveform = waveform_data[2+header_length:]  # Extract the waveform data
    
    # Convert the waveform data to a numpy array
    # Assuming the waveform data is in 16-bit signed integer format
    waveform_array = np.frombuffer(waveform, dtype=np.int16)
    
    # Plot the waveform
    plt.plot(waveform_array)
    plt.title("Waveform from Channel 4")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.show()

    return waveform_array
    

    
   



def main():
    resource_str = "TCPIP0::172.16.13.144::INSTR"  # Replace with your oscilloscope's VISA address
    oscilloscope = initialize_instrument(resource_str)
    #configure_oscilloscope(oscilloscope)
    time_axis, voltage_data = acquire_waveform(oscilloscope)
    
    # Calculate current assuming a 10Ω shunt resistor
    current_data = calculate_current(voltage_data, shunt_resistor=10000)
    
    # Plot waveform
    plot_waveform(time_axis, voltage_data)
    
    oscilloscope.close()

if __name__ == "__main__":
    main()
    