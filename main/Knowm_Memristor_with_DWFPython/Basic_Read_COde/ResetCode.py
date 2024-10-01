import time
import dwfpy as dwf

# Parameters for the triangular pulse
pulse_frequency = 100  # Frequency for 10ms pulse width (1/10ms = 100 Hz)
pulse_amplitude = 1.0  # Peak-to-peak voltage (1V means 0V to +1V)
pulse_offset = 0.0  # Offset to make the pulse go from 0V to +1V
pulse_count = 5  # Number of pulses to apply
symmetry = 50.0  # Duty cycle as a percentage (50% symmetry for triangular wave)
output_file = "oscilloscope_data.txt"  # File to store oscilloscope data

print(f'DWF Version: {dwf.Application.get_version()}')

with dwf.Device() as device:
    print(f'Found device: {device.name} ({device.serial_number})')

    # Configure the waveform generator (channel 0) for a triangular wave
    wavegen = device.analog_output
    wavegen[0].setup(function='triangle', frequency=pulse_frequency, amplitude=pulse_amplitude, offset=pulse_offset)
    wavegen[0].symmetry = symmetry  # 50% symmetry for the triangular wave

    # Configure the oscilloscope (channel 1) to read the memristor output
    scope = device.analog_input
    scope[0].setup(range=5)  # Set range to 5V (adjust as necessary)
    scope[0].enable = True  # Enable channel 1
    scope.frequency = 1e6  # 1 MHz sampling frequency
    scope[0].buffer_size = 8192  # Set buffer size (can be adjusted as needed)
    scope.configure()

    print('Applying triangular pulses to memristor...')

    # Start the waveform generator
    wavegen[0].configure(start=True)
    time.sleep(pulse_count / pulse_frequency)  # Wait for the pulses to be applied

    # Stop the waveform generator
    wavegen[0].configure(start=False)

    # Read data from oscilloscope channel 1
    print('Reading data from oscilloscope...')
    scope.read_status()
    voltage_data = scope[0].get_data()  # Get voltage data from the buffer

    # Store the voltage data in the output file
    with open(output_file, 'w') as file:
        for sample in voltage_data:
            file.write(f"{sample}\n")

    print(f'Acquisition complete. Data stored in {output_file}')
