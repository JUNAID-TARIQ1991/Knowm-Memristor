"This module generate the pulse waveform on all channel of AT_AWG"

import dwfpy as dwf
from Configure_Istruments.SetUp_AWG import initialize_instrument
from Voltage_Data_Osc import acquire_waveform, plot_waveform, getG
from Configure_Istruments.Configure_LecroyOsc import configure_oscilloscope
# add another function


def AnalogCompute(awg_handle, oscilloscope, V1, V2, V3, V4):
    import time
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import threading
    from Configure_Istruments.Configure_AWG import Generate_waveform

    # Parameters for waveform generation
    # Amplitude in volts for each channel
    Amplitude = [V1, V2, V3, V4, 0.1, 0.1, 0.1, 0.1]
    Channel = [1, 2, 3, 4]
    Offset = [0, 0, 0, 0, 0, 0, 0, 0]  # Offset in volts
    Num_Pulses = 1 # Number of pulses to generate

    Frequency = 5# in kHz


    R = 9860  # Resistance in ohms for current calculation
    # sample_rate = 1e7 # Sample rate for the scope in Hz

    # Configure Lecroy
    configure_oscilloscope(oscilloscope, Frequency, AnalogCompute=True)

    # Generate waveform on the AT_AWG generator
    Generate_waveform(awg_handle, Amplitude, Frequency,
                      Num_Pulses, Channel, AnalogComp=True)

    # time and voltage data from scope
    # Acquire waveform from LeCroy Oscilloscope
    time_axis, voltage_data = acquire_waveform(
        oscilloscope, AnalogCompute=True)

    # Calculate current assuming a 10000Ω shunt resistor
    I = getG(voltage_data.mean(), R, Amplitude, AnalogCompute=True)
    return I
