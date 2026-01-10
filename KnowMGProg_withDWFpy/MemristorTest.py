
def MemristorCheck(device):
    import time
    import dwfpy as dwf
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import threading
    import ctypes
    
    """
    Arguments:
    device -- the AnalogDiscovery2 device handle.
    
    Purpose:
    Reads the conductance of a selected memristor, assuming there is one and only one.
    """
    
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
    TimePeriod = 500e-03 # Time Period in seconds
    No_Pulses = 5  # Number of pulses to be applied
    Measurement_duration = TimePeriod * No_Pulses  # Measurement duration in seconds
    Frequency = 1 / TimePeriod  # Frequency of the wave

    wavegen = device.analog_output
    wavegen[0].reset()
    wavegen[0].trigger.source = dwf.TriggerSource.PC
    time.sleep(0.05)
    amplitude_ch0 = -1.5 # Set amplitude to 0.1v for reading G , for channel 0 ( -0.1v, pulse start from negative)

    #set the wavegen ouput idle to 0
    wavegen[0].idle = 0
    #time.sleep(0.05)
         
    # Setup the waveform generator  
    wavegen[0].run_length = Measurement_duration # ! Important for working wavegen
    wavegen[0].setup(function='triangle', frequency=Frequency, amplitude=amplitude_ch0, offset=0.00) 
    #wavegen[0].setup(function='triangle', frequency=Frequency,offset=0.00) 
    #wavegen[0].nodes[dwf.AnalogOutputNode.CARRIER].amplitude = amplitude_ch0
    #print(f'wavegen[0].nodes[dwf.AnalogOutputNode.CARRIER].amplitude = {wavegen[0].nodes[dwf.AnalogOutputNode.CARRIER].amplitude}')

    wavegen[0].apply()  
    wavegen[0].configure(start = True)
    wavegen[1].setup(start=False)  # Disable wavegen channel 1
    #time.sleep(0.005)     ######### This sleep may cause a problem with the scope????
    
    # Setup oscilloscope for recording
    #scope.trigger.source = dwf.TriggerSource.PC
    timer_thread = threading.Timer(0.5, do_trigger)  # Set a 100 m-second delay before trigger or desired
    timer_thread.start()
    
    recorder = scope.record(sample_rate=sample_rate, length=Measurement_duration, buffer_size=8192, configure=True, start=True)
    
    #print(f"Scope read status before Record: {scope.read_status()}")
    #print(f"Scope record status before: {scope.record_status}")
    #recorder = scope.record(sample_rate=sample_rate, length=Measurement_duration, configure=True, start=True)

    #print(f"Scope record status After Recoord: {scope.record_status}")
    timer_thread.join()
    scope.wait_for_status(dwf.Status.DONE, read_data=True)
    # print(f"{recorder._process_recording()}")
    #print(f"Total sample: {recorder.total_samples}")
    #print(f"Lost Sample: {recorder.lost_samples}")
    #print(f"Scope read status After: {scope.read_status()}")
    #print(f"Scope record status after: {scope.record_status}")
    # Stop the waveform generator
    wavegen[0].configure(start=False)
    
    # Extract recorded data
    voltage_memristor_cathode = recorder.channels[0].data_samples
    voltage_generator_output = recorder.channels[1].data_samples
    t = step_seconds_converter(voltage_memristor_cathode, sample_rate)
    
    # Calculate voltage difference, current, and conductance
    voltage_diff = voltage_generator_output - voltage_memristor_cathode
    I = voltage_diff / R  # Current (Ohm's law)
    G = -I / voltage_memristor_cathode  # Conductance    
    
    do_plot = 0
    if do_plot == 1:         
        # Plot the results
        plt.figure(figsize=(10, 6))
        #plt.plot(voltage_memristor_cathode, I, label='I-V Curve', color='g')
        #plt.plot(voltage_memristor_cathode, linear_func(voltage_memristor_cathode, *popt), 'r--', label=f'Fit: G={fitted_G:.4e}')
        plt.plot(t, voltage_generator_output, label='V_applied ', color='b')
        plt.xlabel('Voltage [V]', fontsize=8)
        plt.ylabel('Current [I]', fontsize=8)
        plt.legend(fontsize=8)
        plt.grid(True)
        plt.tight_layout()
        plt.draw()
        #plt.show(block=False)
        plt.show()
           
    return None
        
# This is custom waveform generation
    
    # def generate_pulse_waveform(num_pulses, pulse_period, pulse_width, sample_rate):
    #     # Define the parameters
    #     samples_high = int(pulse_width * sample_rate)
    #     samples_low = int((pulse_period - pulse_width) * sample_rate)
    #     pulse_signal = []
    #     pulse_signal.extend([0.1] * samples_high)
    #     pulse_signal.extend([0.0] * samples_low)
    #     full_signal = pulse_signal * num_pulses
    #     ctype_signal = (ctypes.c_double * len(full_signal))(*full_signal)
    #     return ctype_signal
 
    # # Generate the waveform
    # num_pulses = 3
    # pulse_period = 1e-3
    # pulse_width = pulse_period * .2
    # pulse_signal = generate_pulse_waveform(num_pulses, pulse_period, pulse_width, sample_rate )
    
    # wavegen[0].reset()
    # wavegen[0].idle = 0
    # wavegen[0].run_length = pulse_period 
    # wavegen[0].setup(function='custom') 
    # wavegen[0].nodes[dwf.AnalogOutputNode.CARRIER].set_data_samples(pulse_signal)