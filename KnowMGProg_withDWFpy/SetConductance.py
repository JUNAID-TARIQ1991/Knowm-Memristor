# SendWriteErasePulses function definition
def SendWriteErasePulses(device, voltage, time_period, no_pulses, duty_cycle):
    import time
    import dwfpy as dwf
    import numpy as np
    import matplotlib.pyplot as plt
    import threading

    R = 10000  # 10 kohm Resistance in ohms for current calculation
    sample_rate = 100000  # 1 MHz Sample rate for the scope in Hz

    def step_seconds_converter(data, sample_rate):
        num_samples = len(data)
        return np.linspace(0, num_samples / sample_rate, num_samples)

    def do_trigger():
        device.trigger_pc()
    

    #pulse parameters
    Measurement_duration = time_period * no_pulses
    Frequency = 1 / time_period
    
    # Set up the waveform generator 
    wavegen = device.analog_output
    wavegen[0].reset()
    wavegen[0].trigger.source = dwf.TriggerSource.PC
    time.sleep(0.05)
    amplitude_ch1 = 0.0  # Set amplitude for channel 1 (disabled)          
    #wavegen[0].limitation = -1.0 # Set the voltage limitation to -1V or the maximum allowed
    # Check if the requested voltage exceeds the limitation
    if abs(voltage) > abs(2):
        print(f"Voltage {voltage}v exceeds the set limitation of 2.00 V.")
        exit()    
    
    #set the wavegen ouput idle to 0
    wavegen[0].idle = 0
    #time.sleep(0.05) 
    
    # Setup the waveform generator trigger
    wavegen[0].run_length = Measurement_duration   # Added by Prof Rafaele, ! Important for working wavegen
    wavegen[0].setup(function='pulse', frequency=Frequency,amplitude=voltage, offset=0.00, symmetry=duty_cycle)
    wavegen[0].apply()
    wavegen[0].configure(start=True)
    wavegen[1].setup(start=False)

    #Scope Setting
    scope = device.analog_input
    scope.reset()
    #scope.buffer_size = 16384
    scope.configure()
    scope.wait_for_status(dwf.Status.READY, read_data=False) # wait for scope ready
    
    timer_thread = threading.Timer(Measurement_duration +0.1, do_trigger) #Delay time for each trigger
    
    timer_thread.start()    
    #Start the voltage recording
    recorder = scope.record(sample_rate=sample_rate, length=Measurement_duration,buffer_size=8192,  configure=True, start=True)
    timer_thread.join()

    # Wait for scope done 
    #scope.wait_for_status(dwf.Status.DONE, read_data=True)
    
    #Stopping the wavegen
    wavegen[0].configure(start=False)
    
    # voltage_memristor_cathode = recorder.channels[0].data_samples
    # voltage_generator_output = recorder.channels[1].data_samples
    # t = step_seconds_converter(voltage_memristor_cathode, sample_rate)

    # voltage_diff = voltage_generator_output - voltage_memristor_cathode
    # I = voltage_diff / R  # Current (Ohm's law)
    # G = -I / voltage_memristor_cathode  # Conductance

    # plt.figure(figsize=(10, 6))
    # plt.plot(t, voltage_generator_output, color='b')
    # plt.title(f'Memristor Voltage Over Time', fontsize=10)
    # plt.xlabel('Time [s]', fontsize=8)
    # plt.ylabel('Voltage [V]', fontsize=8)
    # # #plt.legend(fontsize=8)
    # plt.grid(True)
    # plt.tight_layout()
    # plt.draw()
    # plt.show()
        
