
def ResetMemristor(device, channel):
    import dwfpy as dwf
    import time
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import threading
    #from SelectMemristor import SelectMemristor  

    """
    Arguments:
    device -- the AnalogDiscovery2 device handle.
    
    Purpose:
    Resets the selected memristor, assuming one and only one is selected.
    """

    
    if device is None :
        print("Failed to initialize device or select memristor.")
        return

    R = 10000  # value (ohm) of the resistor in series to memristor when Knowm Memristor Discovery is mode 1 
    sample_rate = 100000  # Sample rate for the scope in Hz

    def step_seconds_converter(data, sample_rate):
        num_samples = len(data)
        return np.linspace(0, num_samples / sample_rate, num_samples)

    def do_trigger():
        device.trigger_pc()
        #print("Generating a PC trigger...")





    # Set up the waveform generator and trigger
    TimePeriod = 100e-06 # Time Period in seconds
    No_Pulses = 5  # Number of pulses to be applied
    Measurement_duration = TimePeriod * No_Pulses  # Measurement duration in seconds
    Frequency = 1 / TimePeriod  # Frequency of the wave
    voltage = - 2.0
    wavegen = device.analog_output
    
    if channel == 0:
        wavegen[1].setup(start=False)
        wavegen[1].nodes[dwf.AnalogOutputNode.CARRIER].enabled = False 
        wavegen[channel].reset()
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
        wavegen[channel].trigger.source = dwf.TriggerSource.PC
        wavegen[channel].idle = 0
        wavegen[channel].run_length = Measurement_duration  # Added by Prof Rafaele, ! Important for working wavegen
        wavegen[channel].setup(function='pulse', frequency=Frequency, offset=0.00, symmetry=50)
        wavegen[channel].nodes[dwf.AnalogOutputNode.CARRIER].amplitude = voltage
        wavegen[channel].apply()
        wavegen[channel].configure(start=True)    

        
    # Setup oscilloscope for recording
    scope = device.analog_input
    scope.reset()

    # Set up the Oscilloscope
    scope.channels[0].setup(range=2.5, enabled=True)
    scope.channels[1].setup(range=2.5, enabled=True)
    #scope.buffer_size = 16384 #(the maximum )
    scope.configure()
    #Wait for scope status
    scope.wait_for_status(dwf.Status.READY, read_data=False)
    
    timer_thread = threading.Timer(0.1, do_trigger)  # Set a 1-second delay before trigger
    timer_thread.start()
    recorder = scope.record(sample_rate=sample_rate, length=Measurement_duration, configure=True, start=True)
    timer_thread.join()  
    scope.wait_for_status(dwf.Status.DONE, read_data=True)

    # Stop the waveform generator
    wavegen[channel].configure(start=False)
   
    # Extract recorded data
    voltage_memristor_cathode = recorder.channels[0].data_samples   
    t = step_seconds_converter(voltage_memristor_cathode, sample_rate)
    I =  voltage_memristor_cathode / R  # Current (Ohm's law)
    
    return None
    # popt, _ = curve_fit(linear_func, voltage_memristor_cathode, I)
    # fitted_G = popt[0]  # Extract conductance (slope)

    # #plt.figure(figsize=(10, 6))
    do_plot = 0
    if do_plot == 1:
        plt.figure()
        plt.plot(t, I, label='V_Applied ', color='b')
        plt.title('Current ')
        plt.xlabel('Time [s]')
        plt.ylabel('I [A]')
        plt.legend()
        plt.grid()
        plt.show()
    # #print("Memristor Reset")
    
      
    


