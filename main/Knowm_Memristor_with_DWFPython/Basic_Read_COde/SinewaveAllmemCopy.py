"""Test Memristor with  dwfpy library
Created : Junaid.Tariq and Prof Raffaele Giardano Sep 2024

Reproduce DC experiment of Mem-Dis
"""
import time
import dwfpy as dwf
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import threading

# Parameters
R = 10000  # Resistance in ohms for current calculation
sample_rate = 100000  # Sample rate for the scope in Hz


# Linear function for fitting
def linear_func(V, G, intercept):
    return G * V + intercept

# Function to convert step indices to time


def step_seconds_converter(data, sample_rate):
    num_samples = len(data)
    return np.linspace(0, num_samples / sample_rate, num_samples)


def do_trigger():
    device.trigger_pc()


# Initialize device
print(f'DWF Version: {dwf.Application.get_version()}')

with dwf.AnalogDiscovery2() as device:
    print(f'Found device: {device.name} ({device.serial_number})')
    # Setup the DIO pins (analog input)
    pattern = device.digital_output
    for i in range(0, 16):
        pattern[i].setup_constant('low', start=True)

    time.sleep(.1)
    # Set the positive power supply to 5V and -5V to enable it.
    device.supplies.positive.setup(voltage=5.0)
    device.supplies.negative.setup(voltage=-5.0)
    device.supplies.master_enable = True

    # Setup the oscilloscope (analog input)
    scope = device.analog_input
    # Voltage across memristor
    scope.channels[0].setup(range=5.0, enabled=True)
    # Voltage generator output
    scope.channels[1].setup(range=5.0, enabled=True)
    # Loop through each memristor

     # Prepare a 4x4 canvas
    fig, axs = plt.subplots(4, 4, figsize=(16, 16))
    axs = axs.flatten()  # Flatten the axis array for easy iteration
    for selected_memristor in range(16):
    #for selected_memristor in [5]:
        

        # Parametrs
        PulseWidth = 0.1  # Pulse wdith in second 100 milli
        No_Pulses = 5  # Number of pulses to be applied
        Measurement_duration = PulseWidth * No_Pulses  # Measurement duration in seconds
        Frequency = 1/PulseWidth  # Frequency of wave

        Amplitude_ch0 = 0.1  # Set amplitude for channel 0
        Amplitude_ch1 = 0.0  # Set amplitude for channel 1 (disabled)
        Offset = 0.0  # Set the waveform offfset

        pattern[selected_memristor].setup_constant(
            'high', start=True)  # Select memristor

        # Setup waveform generator
        wavegen = device.analog_output

        # Check if the amplitude exceeds 1V
        if Amplitude_ch0 > 1 or Amplitude_ch1 > 1:
            print(
                f"Error: Wavegen amplitude exceeds 1V for Memristor {selected_memristor+1}. Terminating program.")
            break
        # Triggring source added by Prof Raffaele
        wavegen[0].trigger.source = dwf.TriggerSource.PC  # PC
        wavegen[0].run_length = Measurement_duration
        wavegen[0].setup(function='sine', frequency=Frequency,
                         amplitude=Amplitude_ch0, offset=Offset, start=True)
        # wavegen[0].run_length = measurement_duration

        wavegen[1].setup(start=False)  # Wave generator 2 Disabled

        print(f'instructed to record data for {Measurement_duration} seconds.')

        # time.sleep(measurement_duration)

        print(scope.read_status())
        scope.trigger.source = dwf.TriggerSource.PC
        print(scope.read_status())

        # Prepares trigger to be generated after 1 second
        timer_thread = threading.Timer(1, do_trigger)
        timer_thread.start()
        recorder = scope.record(
            sample_rate=sample_rate, length=Measurement_duration, configure=True, start=True)
        timer_thread.join()

        print('Waiting for status done')
        scope.wait_for_status(dwf.Status.DONE, read_data=True)
        print(scope.read_status())

        # time.sleep(measurement_duration)
        # print(scope.read_status())

        print('Waiting done')

     #   time.sleep(measurement_duration)

        # Stop the wavegen
        wavegen[0].configure(start=False)
        print('stopping the waveform generation')

        # Extract recorded data
        voltage_memristor_cathode = recorder.channels[0].data_samples
        voltage_generator_output = recorder.channels[1].data_samples
        t = step_seconds_converter(voltage_memristor_cathode, sample_rate)

        # Calculate voltage difference, current, and conductance
        voltage_diff = voltage_generator_output - voltage_memristor_cathode
        I = voltage_diff / R  # Current (Ohm's law)
        G = -I / voltage_memristor_cathode  # Conductance

        
        # Fit the I-V data with a linear function to find conductance
        popt, _ = curve_fit(linear_func, voltage_memristor_cathode, I)
        fitted_G = popt[0]  # Extract conductance (slope)
        

        # Plot I-V curve with linear fit for this memristor
        axs[selected_memristor].plot(
            voltage_memristor_cathode, I, label='I-V Curve', color='g')
        axs[selected_memristor].plot(voltage_memristor_cathode, linear_func(
            voltage_memristor_cathode, *popt), 'r--', label=f'Fit: G={fitted_G:.4e}')
        axs[selected_memristor].set_xlabel('Voltage [V]')
        axs[selected_memristor].set_ylabel('Current [A]')
        # axs[selected_memristor].set_title(f'Memristor {selected_memristor+1} I-V Curve')
        axs[selected_memristor].legend()
        axs[selected_memristor].grid()

        # Save the data to CSV file
        #data = np.column_stack((t, voltage_memristor_cathode, I, G))
        #np.savetxt(f'memristor_{selected_memristor+1}_data.csv', data, delimiter=",", header="Time [s], Voltage [V], Current [A], Conductance [S]", comments='')

        # Log conductance value in a separate file
        #with open('conductance_values.txt', 'a') as f:f.write(f'Memristor {selected_memristor+1}: Conductance = {fitted_G:.4e} S\n')

        Resistance = 1 / fitted_G
        print(
            f'Memristor {selected_memristor+1} : Resistance = {Resistance:.0f} ohm *** Conductance = {fitted_G:.4e} S')
        print(f'Memristor {selected_memristor+1} data saved.')

        # Reset pattern for next memristor
        pattern[selected_memristor].setup_constant('low', start=True)
        time.sleep(.1)  # Delay before next memristor selection

    # Adjust layout and save the 4x4 canvas
    plt.tight_layout()
    plt.savefig('all_memristors_IV_curves.png')
    plt.show() 