import dwfpy as dwf

# add another function
def SendWritePulse(device, voltage, time_period, NoPulses, channel):
    import time
    import dwfpy as dwf
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import threading
   
    print("Driving inputs")
   
    # Parameters
    R = 10000  # Resistance in ohms for current calculation
    sample_rate = 1000000 # Sample rate for the scope in Hz

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
    scope.trigger.source = dwf.TriggerSource.PC

    scope.channels[0].setup(range=2.5, enabled=True)  # Voltage across memristor
    scope.channels[1].setup(range=2.5, enabled=True)  # Voltage generator output
    #scope.buffer_size = 16384 #(the maximum )
    scope.configure()
       
    # Set up the waveform generator and trigger

    Measurement_duration = time_period * NoPulses  # Measurement duration in seconds
    Frequency = 1 / (time_period)# Frequency of the wave

    
    wavegen = device.analog_output
    if channel == 0:
        wavegen[1].setup(start=False)
        wavegen[1].nodes[dwf.AnalogOutputNode.CARRIER].enabled = False  
        wavegen[channel].reset()
        #print("Plot")
        wavegen[channel].trigger.source = dwf.TriggerSource.PC
        wavegen[channel].idle = 0
        wavegen[channel].run_length = Measurement_duration  # Added by Prof Rafaele, ! Important for working wavegen
        wavegen[channel].setup(function='pulse', frequency=Frequency, offset=0.00, symmetry=50)
        wavegen[channel].nodes[dwf.AnalogOutputNode.CARRIER].amplitude = voltage
        wavegen[channel].apply()
        wavegen[channel].configure(start=True)
    else:
        wavegen[0].setup(start=False)
        wavegen[0].nodes[dwf.AnalogOutputNode.CARRIER].enabled = False 
        wavegen[channel].reset()
        #print("Plot")
        wavegen[channel].trigger.source = dwf.TriggerSource.PC
        wavegen[channel].idle = 0
        wavegen[channel].run_length = Measurement_duration  # Added by Prof Rafaele, ! Important for working wavegen
        wavegen[channel].setup(function='pulse', frequency=Frequency, offset=0.00, symmetry=50)
        wavegen[channel].nodes[dwf.AnalogOutputNode.CARRIER].amplitude = voltage
        wavegen[channel].apply()
        wavegen[channel].configure(start=True)
        
    
    
    timer_thread = threading.Timer(0.1, do_trigger)  # Set a 100 m-second delay before trigger or desired
    timer_thread.start()
    
    recorder = scope.record(sample_rate=sample_rate, length=Measurement_duration, buffer_size=8192, configure=True, start=True) 
    timer_thread.join()
    scope.wait_for_status(dwf.Status.DONE, read_data=True)

    wavegen[channel].configure(start=False)
    #wavegen[1].configure(start=False)    
    
    # Extract recorded data
    #voltage_memristor_cathode = recorder.channels[0].data_samples
    #t = step_seconds_converter(voltage_memristor_cathode, sample_rate)
    
    # Calculate voltage difference, current, and conductance
    #I = voltage_memristor_cathode / R  # Current (Ohm's law)
    #print("Plot")
  
    # do_plot = 0
    # if do_plot == 1:         
    #     # Plot the results
    #     plt.figure(figsize=(10, 6))
    #     plt.plot(t, voltage_memristor_cathode, label='Vout ', color='b')
    #     plt.xlabel('Time (s)', fontsize=8)
    #     plt.ylabel('I [A]', fontsize=8)
    #     plt.legend(fontsize=8)
    #     plt.grid(True)
    #     plt.tight_layout()
    #     plt.draw()
    #     plt.show()
        
     
    #return I
        

#  #Open the AnalogDiscovery2 device
# with dwf.AnalogDiscovery2() as device:
    
#      print(f'Found device: {device.name} ({device.serial_number})')
#      print(f'DWF Version: {dwf.Application.get_version()}')

#      device.auto_configure = True
#      device.analog_input.trigger.source = dwf.TriggerSource.PC
# #     
# #     #for i in range(1000):
    
#      SendWritePulse(device, -2.0,200e-06, 10, 1)
# #     print (f'Average I =  {I*1e6:.2f} microA') 
    