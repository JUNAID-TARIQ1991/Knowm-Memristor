import time
import dwfpy as dwf
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import threading
import ctypes

def ReadMemristor(device, channel):

    """
    Arguments:
    device -- the AnalogDiscovery2 device handle.
    
    Purpose:
    Reads the conductance of a selected memristor, assuming there is one and only one.
    """
    
    # Parameters
    R = 10000  # Resistance in ohms for current calculation
    sample_rate = 1E7 # Sample rate for the scope in Hz

    # Function to convert step indices to time
    def step_seconds_converter(data, sample_rate):
        num_samples = len(data)
        return np.linspace(0, num_samples / sample_rate, num_samples)
    
    # Trigger function
    def do_trigger():
        device.trigger_pc()
    
    # Linear function for fitting
    def linear_func(V, G, intercept):
        return G * V + intercept

    # Setup the oscilloscope (analog input)
    scope = device.analog_input
    scope.reset()
    scope.trigger.source = dwf.TriggerSource.PC
    scope.channels[0].setup(range=2.5, enabled=True)  # Voltage across memristor
    scope.channels[1].setup(range=2.5, enabled=True)  # Voltage generator output
    scope.configure()
       
    # Set up the waveform generator and trigger
    TimePeriod = 200e-06 # Time Period in seconds
    No_Pulses = 1  # Number of pulses to be applied
    Measurement_duration = TimePeriod * No_Pulses  # Measurement duration in seconds
    Frequency = 1 / TimePeriod  # Frequency of the wave
    voltage = 0.1
    wavegen = device.analog_output
    
    if channel == 0:
        wavegen[1].setup(start=False, enabled = False)
        #wavegen[1].nodes[dwf.AnalogOutputNode.CARRIER].enabled = False    
        wavegen[channel].reset()
        wavegen[channel].trigger.source = dwf.TriggerSource.PC
        wavegen[channel].idle = 0
        wavegen[channel].run_length = Measurement_duration  # Added by Prof Rafaele, ! Important for working wavegen
        wavegen[channel].setup(function='pulse', frequency=Frequency, offset=0.00, symmetry=50)
        wavegen[channel].nodes[dwf.AnalogOutputNode.CARRIER].amplitude = voltage
        wavegen[channel].apply()
        wavegen[channel].configure(start=True)
    else:
        wavegen[0].setup(start=False, enabled= False)
        #wavegen[0].nodes[dwf.AnalogOutputNode.CARRIER].enabled = False    
        wavegen[channel].reset()
        wavegen[channel].trigger.source = dwf.TriggerSource.PC
        wavegen[channel].idle = 0
        wavegen[channel].run_length = Measurement_duration  # Added by Prof Rafaele, ! Important for working wavegen
        wavegen[channel].setup(function='pulse', frequency=Frequency, offset=0.00, symmetry=50)
        wavegen[channel].nodes[dwf.AnalogOutputNode.CARRIER].amplitude = voltage
        wavegen[channel].apply()
        wavegen[channel].configure(start=True)    
    
    # Setup oscilloscope for recording
    timer_thread = threading.Timer(0.1, do_trigger)  # Set a 100 m-second delay before trigger or desired
    timer_thread.start()
    recorder = scope.record(sample_rate=sample_rate, length=Measurement_duration, buffer_size=8192, configure=True, start=True) 
    timer_thread.join()
    scope.wait_for_status(dwf.Status.DONE, read_data=True)
    wavegen[channel].configure(start=False)    
    
    # Extract recorded data
    voltage_memristor_cathode = recorder.channels[0].data_samples
    t = step_seconds_converter(voltage_memristor_cathode, sample_rate)
    
    # Calculate voltage difference, current, and conductance
    I = voltage_memristor_cathode/ R  # Current (Ohm's law)
    V_diff = voltage - voltage_memristor_cathode
    
    # Calculate the indices for 15% and 50% of the array length    
    start_index = int(len(voltage_memristor_cathode) * 0.05)
    end_index = int(len(voltage_memristor_cathode) * 0.5)
           
    # Fit the I-V data with a linear function to find conductance
    popt, _ = curve_fit(linear_func, V_diff, I)
    fitted_G = popt[0]  # Extract conductance (slope)0
    #print(f"conductance {fitted_G}")   

    G = I[start_index:end_index] / V_diff[start_index:end_index]  # Conductance 
    averageG = sum(G) / len(G)    
    
    do_plot = 1
    if do_plot == 1:         
        # Plot the results
        plt.figure(figsize=(10, 6))
        #plt.plot(voltage_memristor_cathode, I, label='I-V Curve', color='g')
        #plt.plot(voltage_memristor_cathode, linear_func(voltage_memristor_cathode, *popt), 'r--', label=f'Fit: G={fitted_G:.4e}')
        plt.plot(t, voltage_memristor_cathode, label='V_applied ', color='b')
        plt.plot(t[start_index:end_index] , voltage_memristor_cathode[start_index:end_index] , label='V_averaged ', color='r')
        plt.xlabel('Time [s]', fontsize=8)
        plt.ylabel('Voltage [V]', fontsize=8)
        plt.legend(fontsize=8)
        plt.grid(True)
        plt.tight_layout()
        plt.draw()
        #plt.show(block=False)
        plt.show()
    return averageG
# #  #Open the AnalogDiscovery2 device
# with dwf.AnalogDiscovery2() as device:
    
#     print(f'Found device: {device.name} ({device.serial_number})')
#     print(f'DWF Version: {dwf.Application.get_version()}')

#     device.auto_configure = True
#     #device.analog_output[0].source = dwf.TriggerSource.PC
#     #for i in range(1000):
    
    
#     G = ReadMemristor(device, 1)
#     print (f'Average  G =  {G} S') 
 