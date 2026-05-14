import pyvisa
import numpy as np
import matplotlib.pyplot as plt

# Define the IP address of the oscilloscope
OSCILLOSCOPE_IP = '172.16.13.144'  # Replace with your oscilloscope's IP address

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()

# Connect to the oscilloscope
try:
    oscilloscope = rm.open_resource(f'TCPIP::{OSCILLOSCOPE_IP}::INSTR')
    print(f"Connected to: {oscilloscope.query('*IDN?')}")
except Exception as e:
    print(f"Failed to connect to the oscilloscope: {e}")
    exit()

# Configure the oscilloscope for external trigger and channel 4
try:
    # Set the timebase and trigger settings
    oscilloscope.write("TRIG_MODE NORM")  # Set trigger mode to Normal
    oscilloscope.write("TRIG_SELECT EDGE,SR,EXT")  # Set trigger source to external (assuming C4 is the external trigger)
    oscilloscope.write("C4:TRIG_LEVEL 0.4V")  # Set trigger level to 1.0V (adjust as needed)
    
    # Set up channel 4
    oscilloscope.write("C4:VDIV 1.0V")  # Set vertical scale to 1.0V/div (adjust as needed)
    oscilloscope.write("C4:OFFSET 0.0V")  # Set vertical offset to 0V
    oscilloscope.write("C4:COUpling DC")  # Set coupling to DC (or AC if needed)
    
    # Set the timebase
    oscilloscope.write("TIME_DIV 1.0E-6")  # Set timebase to 1us/div (adjust as needed)
    
    # Arm the trigger and wait for the acquisition
    oscilloscope.write("ARM")  # Arm the trigger
    oscilloscope.write("WAIT")  # Wait for the acquisition to complete
    
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

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the connection to the oscilloscope
    oscilloscope.close()
    print("Connection closed.")