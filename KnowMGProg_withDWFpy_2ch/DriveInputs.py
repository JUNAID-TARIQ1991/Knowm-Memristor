"This module generate the pulse waveform on both channels of AD2"

import dwfpy as dwf

# add another function
def AnalogCompute(device, voltage1,voltage2, pulse_width):
    import time
    import dwfpy as dwf
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import threading
   
    print("Driving inputs")
   
    # Parameters
    R = 10000  # Resistance in ohms for current calculation
    sample_rate = 100/pulse_width # Sample rate for the scope in Hz

    # Function to convert step indices to time
    def step_seconds_converter(data, sample_rate):
        num_samples = len(data)
        return np.linspace(0, num_samples / sample_rate, num_samples)
    
    # Trigger function
    def do_trigger():
        device.trigger_pc()

    # Setup the oscilloscope (analog input)
    scope = device.analog_input
    scope.reset()
    scope.channels[0].setup(range=2.5, enabled=True)  # Voltage across memristor
    scope.channels[1].setup(range=2.5, enabled=True)  # Voltage generator output
    scope.configure()
       
    # Set up the waveform generator and trigger
    Measurement_duration = 2*pulse_width  # Measurement duration in seconds
    Frequency = 1 / (2*pulse_width)# Frequency of the wave  
    wavegen = device.analog_output
    voltages=[voltage1, voltage2]
    
    for i in (0,1):
        wavegen[i].reset()
        wavegen[i].trigger.source = dwf.TriggerSource.PC
        wavegen[i].idle = 0
        wavegen[i].run_length = Measurement_duration  
        wavegen[i].setup(function='pulse', frequency=Frequency,amplitude=voltages[i], offset=0.00, symmetry=50, start=True)
        #wavegen[awg_channel].apply()
        #print( wavegen[awg_channel].nodes[dwf.AnalogOutputNode.CARRIER].phase)
        #print( wavegen[awg_channel].trigger.source)
   
        
    # Setup oscilloscope for recording
    scope.trigger.source = dwf.TriggerSource.PC
    timer_thread = threading.Timer(0.01, do_trigger)  # Set a 100 m-second delay before trigger or desired
    timer_thread.start() 
    recorder = scope.record(sample_rate=sample_rate, length=Measurement_duration, buffer_size=8192, configure=True, start=True)  
    timer_thread.join()
    scope.wait_for_status(dwf.Status.DONE, read_data=True)
    
    # Extract recorded data
    voltage_memristor_cathode = recorder.channels[0].data_samples
    t = step_seconds_converter(voltage_memristor_cathode, sample_rate)
    
    # Calculate voltage difference, current, and conductance
    I = voltage_memristor_cathode / R  # Current (Ohm's law)
    # Calculate the indices for 15% and 45% of the array length
    start_index = int(len(I) * 0.05)
    end_index = int(len(I) * 0.48)
    subset = I[start_index:end_index]
    averageI = sum(subset) / len(subset)    

    do_plot = 0
    if do_plot == 0:         
        print("Plot")
        # Plot the results
        plt.figure(figsize=(10, 6))
        plt.plot(t, voltage_memristor_cathode, label='Vout ', color='b')
        plt.xlabel('Time (s)', fontsize=8)
        plt.ylabel('Memristor Cathode Voltage [V]', fontsize=8)
        plt.legend(fontsize=8)
        plt.grid(True)
        plt.tight_layout()
        plt.draw()
        plt.show()
    
    
    return averageI

 # Open the AnalogDiscovery2 device
with dwf.AnalogDiscovery2() as device:
    
    print(f'Found device: {device.name} ({device.serial_number})')
    print(f'DWF Version: {dwf.Application.get_version()}')

    device.auto_configure = True
    device.analog_input.trigger.source = dwf.TriggerSource.PC
    #device.analog_output[0].source = dwf.TriggerSource.PC
    #for i in range(1000):
    
    
    I = AnalogCompute(device, 0.1, 0.00, 200e-6)
    print (f'Average  I =  {I:.2e} A') 
        
    