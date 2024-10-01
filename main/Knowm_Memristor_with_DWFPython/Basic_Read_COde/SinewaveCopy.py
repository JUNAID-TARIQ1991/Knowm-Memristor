import time
import dwfpy as dwf
import numpy as np
import matplotlib.pyplot as plt

# Parameters
R = 10000  # Resistance in ohms for current calculation
sample_rate = 100000  # Sample rate for the scope in Hz
measurement_duration = 0.0002  # Measurement duration in seconds


# Function to convert step indices to time
def step_seconds_converter(data, sample_rate):
    num_samples = len(data)
    return np.linspace(0, num_samples / sample_rate, num_samples)

# Initialize device
print(f'DWF Version: {dwf.Application.get_version()}')

with dwf.AnalogDiscovery2() as device:
    print(f'Found device: {device.name} ({device.serial_number})')

    # Set the positive power supply to 3.3V and enable it. This enables switches, without these voltage we will encounter an error while reading voltage.
    device.supplies.positive.setup(voltage=5.0) #this step seems give a spike of 0.004V (negligible)
    device.supplies.negative.setup(voltage=-5.0)
    device.supplies.master_enable = True

    pattern = device.digital_output
    # Output a high level on pin DIO-0 to select the righ Memristor.
    for i in range(6,6):
        pattern[i].setup_constant('low', start=True)
    
    time.sleep(1)
   

    # Setup the oscilloscope (analog input)
    scope = device.analog_input
    scope.channels[0].setup(range=5.0, enabled=True)  # Measure voltage across memristor at Channel 0 (IO 0)
    scope.channels[1].setup(range=5.0, enabled=True)  #  Measure voltage at another point (e.g., voltage generator)
    #It is important to keep the sleep before
    for selected_memristor in(0,16):
        pattern[selected_memristor].setup_constant('high', start=True) #It is important to keep the sleep before
        
        # Start waveform generation
        # Setup the waveform generator to produce a sine wave on Wavegen 1 (Channel 0)
        wavegen = device.analog_output
        wavegen[0].setup(
            function='square',   # Sine wave
            frequency=5000,     # 1 kHz frequency
            amplitude=1,     # 1 V peak-to-peak
            offset=0.0,        # set offset 
            start=True
        )
        wavegen[1].setup(enabled=False)



        print('Waveform generation started...')

        # Start oscilloscope recording
        recorder = scope.record(sample_rate=sample_rate, length=measurement_duration, configure=True, start=True)
        print('Recording voltage data across memristor...')

        # Wait for the recording to complete
        time.sleep(measurement_duration)
        # Stop waveform generation
        wavegen[0].configure(start=False)
        print('Waveform generation stopped.')


        # Check for lost or corrupted samples
        if recorder.lost_samples > 0:
            print('Samples lost, reduce sample rate.')
        if recorder.corrupted_samples > 0:
            print('Samples corrupted, reduce sample rate.')

        # Extract recorded data
        voltage_memristor_cathode = recorder.channels[0].data_samples # voltage on memristor cathode
        voltage_generator_output = recorder.channels[1].data_samples # voltage at the output of thw AnalogWaveGenerator
        t = step_seconds_converter(voltage_memristor_cathode, sample_rate)

        plt.show(block=False)

        # Plot Voltage vs Time
        plt.figure(figsize=(10, 6))
        plt.plot(t, voltage_generator_output, label='V_genout', color='b')
        plt.plot(t, voltage_memristor_cathode,  label='V_memcathode',color='r')
        #plt.title('Voltage at the generator output')
        plt.xlabel('Time [s]')
        plt.ylabel('Voltage [V]')
        plt.legend()
        plt.grid()
        plt.draw()
        plt.pause(0.001)
        #exit()


        # Calculate voltage difference, current, and conductance
    
        voltage_diff =  voltage_generator_output - voltage_memristor_cathode # Voltage diff is the voltage accross series resistor

        
        
        I = voltage_diff / R  # Current through the resistor (which is also through the memristor) (Ohm's law)
        G = - I / voltage_memristor_cathode  # Conductance of the memristor

        # Plot Voltage vs Time
        plt.figure(figsize=(10, 6))
        plt.plot(t, voltage_diff, label='V_resistor ', color='b')
        plt.title('Voltage Across Resistor Over Time')
        plt.xlabel('Time [s]')
        plt.ylabel('Voltage [V]')
        plt.legend()
        plt.grid()
        plt.draw()
        plt.pause(0.001)


        # Plot I-V Curve
        plt.figure(figsize=(10, 6))
        plt.plot(voltage_memristor_cathode, I, label='I-V Curve', color='g')
        plt.title('Current vs Voltage (I-V Curve)')
        plt.xlabel('Voltage [V]')
        plt.ylabel('Current [A]')
        plt.legend()
        plt.grid()
        plt.draw()
        plt.pause(0.001)


        # Plot Conductance vs Voltage
        plt.figure(figsize=(10, 6))
        plt.plot(voltage_memristor_cathode, G, label='Conductance vs Voltage', color='r')
        plt.title('Conductance vs Voltage (G-V Curve)')
        plt.xlabel('Voltage [V]')
        plt.ylabel('Conductance [S]')
        plt.legend()
        plt.grid()
        plt.draw()
        plt.pause(0.001)
        
        
        plt.show()

        # Save data to CSV file
        data = np.column_stack((t, voltage_memristor_cathode, I, G))
        np.savetxt("voltage_current_conductance.csv", data, delimiter=",", header="Time [s], Voltage [V], Current [A], Conductance [S]", comments='')
        print('Data saved to "voltage_current_conductance.csv".')
        
        time.sleep(1)
        pattern[selected_memristor].setup_constant('low', start=True) #It is important to keep the sleep 
