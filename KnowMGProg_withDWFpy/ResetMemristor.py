
def ResetMemristor(device):
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

    def linear_func(V, G, intercept):
        return G * V + intercept

    TimePeriod = 200e-06  # Time Period in seconds
    No_Pulses = 10  # Number of pulses to be applied
    Measurement_duration = TimePeriod * No_Pulses  # Measurement duration in seconds
    Frequency = 1 / TimePeriod  # Frequency of the wave

    wavegen = device.analog_output
    wavegen[0].reset()
    time.sleep(0.05)
    #wavegen[0].trigger.source = dwf.TriggerSource.PC
    V_reset = 2.0 # Reset voltage for the memristor
    amplitude_ch1 = 0.0  # Set amplitude for channel 1 (disabled)

    # Setup waveform generator and trigger
    wavegen[0].run_length = Measurement_duration  # Set run length
    
    # Set the wavegen output idle to 0
    wavegen[0].idle = 0
    #time.sleep(0.1)
    #wavegen parameters
    wavegen[0].setup(function='pulse', frequency=Frequency, amplitude=V_reset, offset=0.00, symmetry=50.00)  
    wavegen[0].apply()
    #time.sleep(0.1)
    wavegen[0].configure( start= True)
    wavegen[1].setup(start=False)  # Disable wavegen channel 1

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
    wavegen[0].configure(start=False)
   
    # Extract recorded data
    voltage_memristor_cathode = recorder.channels[0].data_samples
    voltage_generator_output = recorder.channels[1].data_samples
    t = step_seconds_converter(voltage_memristor_cathode, sample_rate)

    voltage_diff = voltage_generator_output - voltage_memristor_cathode
    I = voltage_diff / R  # Current (Ohm's law)

    # popt, _ = curve_fit(linear_func, voltage_memristor_cathode, I)
    # fitted_G = popt[0]  # Extract conductance (slope)

    # #plt.figure(figsize=(10, 6))
    do_plot = 0
    if do_plot == 1:
        plt.figure()
        plt.plot(t, voltage_memristor_cathode, label='V_Applied ', color='b')
        plt.title('Voltage Applied Over Time')
        plt.xlabel('Time [s]')
        plt.ylabel('Voltage [V]')
        plt.legend()
        plt.grid()
        plt.show()
    # #print("Memristor Reset")
    
      
    return None


