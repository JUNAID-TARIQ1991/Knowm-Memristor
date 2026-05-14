import os
from urllib import response
import pyvisa
import numpy as np
import time
import matplotlib.pyplot as plt
import struct
import re
def read_lecroy_waveform(osc):
    # optionally read the oscilloscope waveform template to get the descriptor format, but not strictly necessary if we know the format in advance
    #osc.write(f"TMPL?")
    #raw = osc.read_raw()

    #osc.write("COMM_HEADER OFF") # Disable header in waveform data
    #osc.write("COMM_FORMAT DEF9,WORD,BIN") # Set communication format to binary with 16-bit words

    # Read complete waveform block: descriptor + data
    osc.write("STOP") # Stop acquisition to ensure stable data
    osc.write("C4:WF?") # Request waveform data from channel 4
    raw = osc.read_raw() #  Read raw binary data from the oscilloscope

    hash_index = raw.find(b"#") # Find the index of the binary block start
    if hash_index == -1: 
        raise RuntimeError(f"Binary block (#) not found. Reply starts: {raw[:100]!r}")

    raw = raw[hash_index:] # Trim data to start from the binary block

    nd = int(raw[1:2]) # Number of digits that specify the length of the binary block
    total_len = int(raw[2:2 + nd]) # Total length of the binary block (descriptor + data)
    payload = raw[2 + nd:2 + nd + total_len] # Extract the payload containing descriptor and waveform data

    if payload[0:8] != b"WAVEDESC":
        raise RuntimeError("WAVEDESC not found at beginning of payload")

    def i16(off):
        return struct.unpack("<h", payload[off:off + 2])[0]

    def i32(off):
        return struct.unpack("<i", payload[off:off + 4])[0]

    def f32(off):
        return struct.unpack("<f", payload[off:off + 4])[0]

    def f64(off):
        return struct.unpack("<d", payload[off:off + 8])[0]

    COMM_TYPE = i16(32)       # 0 = BYTE, 1 = WORD
    COMM_ORDER = i16(34)      # 0 = HIFIRST, 1 = LOFIRST

    DESC_LEN = i32(36)
    USER_LEN = i32(40)
    TRIG_LEN = i32(48)
    WAVEARRAY_1 = i32(60)     # bytes, not samples

    WAVE_ARRAY_COUNT = i32(116)

    VERT_GAIN = f32(156)
    VERT_OFFSET = f32(160)
    HORIZ_INT = f32(176)
    HORIZ_OFF = f64(180)

    WAVE_SOURCE = i16(344)


    #VERT_GAIN = struct.unpack("<f", payload[156:160])[0] # volts per ADC unit
    #VERT_OFFSET = struct.unpack("<f", payload[160:164])[0] # vertical offset in volts
    #HORIZ_INTERVAL = struct.unpack("<f", payload[176:180])[0]   # time interval between samples in seconds
    #HORIZ_OFFSET = struct.unpack("<d", payload[180:188])[0] # horizontal offset in seconds

    DATA_START = DESC_LEN + USER_LEN + TRIG_LEN # Starting index of waveform data in the payload
    DATA_END = DATA_START + WAVEARRAY_1  # Ending index of waveform data in the payload

    data = payload[DATA_START:DATA_END] # Extract the waveform data bytes

    if len(data) != WAVEARRAY_1:
        raise ValueError(
            f"Data length mismatch: len(data)={len(data)}, WAVEARRAY_1={WAVEARRAY_1}"
        )

    if COMM_TYPE == 0:
        adc = np.frombuffer(data, dtype=np.int8).astype(np.float64)
        #print("Detected BYTE / 8-bit waveform")

    elif COMM_TYPE == 1:
        if COMM_ORDER == 0:
            adc = np.frombuffer(data, dtype=">i2").astype(np.float64)
            #print("Detected WORD / 16-bit waveform, big-endian")
        else:
            adc = np.frombuffer(data, dtype="<i2").astype(np.float64)
            #print("Detected WORD / 16-bit waveform, little-endian")

    else:
        raise ValueError(f"Unknown COMM_TYPE = {COMM_TYPE}")
    

    if adc.size == 0:
        raise ValueError("ADC array is empty")

    voltage = adc * VERT_GAIN - VERT_OFFSET # Convert ADC counts to voltage using gain and offset
    time_axis = HORIZ_OFF + np.arange(adc.size) * HORIZ_INT # Generate time axis based on horizontal offset and interval

    return time_axis, voltage 


def acquire_waveform(oscilloscope,  AnalogCompute=False):
    if AnalogCompute:
        vdiv = float(oscilloscope.query("C4:VDIV?").split()[1])
        offset = float(oscilloscope.query("C4:OFFSET?").split()[1])
        tdiv = float(oscilloscope.query("TIME_DIV?").split()[1])
        
        # Call the descriptor function to get voltage
        Voltage =  read_lecroy_waveform(oscilloscope)
        
        # Generate time array
        num_samples = len(Voltage)

        time_axis = np.linspace(-5*tdiv, -5*tdiv + tdiv * 10, num_samples)
        # Extract data for the specific time duration (100 µs to 200 µs)
        # Boolean mask for the time range
        time_range_mask = (time_axis >= 0.52*tdiv) & (time_axis <= tdiv*0.99)
        voltage_array = Voltage[time_range_mask] # in case of square pulse i/p return this array
        time_filtered = time_axis[time_range_mask]
        
        #Square Pulse case
        """Return the mean of the top 10% highest values in the voltage array."""
        v = np.asarray(voltage_array, dtype=float)
        v = v[np.isfinite(v)]
        n = v.size
        if n == 0:
            raise ValueError("Voltage array is empty!")
        
        # Number of samples in the top 5%
        k = max(1, int(0.7 * n))
        
        # Sort and take the top k samples
        v_sorted = np.sort(v)
        top_vals = v_sorted[-k:]
        
        #voltage_filtered= float(np.mean(top_vals))
        voltage_filtered= top_vals
        
        
        # # For sine wave to get Vpp
        # vf = np.asarray(voltage_array, dtype=float)
        # vf = vf[np.isfinite(vf)]
        # n = vf.size
        # if n == 0:
        #     raise ValueError("Empty selection after time_range_mask.")

        # # top/bottom 2% means 2% in each tail
        # tail= max(1, int(np.ceil(0.02 * n)))
        # tail = min(tail, n // 2)  # don't exceed half the samples

        # sv = np.sort(vf)
        # min_avg = float(np.mean(sv[:tail]))
        # max_avg = float(np.mean(sv[-tail:]))
        # vpp = max_avg - min_avg
        # Ipp = vpp / 9860   #SineWave Case
        # #print(f"{max_avg}, {min_avg}, Vpp={vpp}, Ipp={Ipp}")


        # # Append frequency and Vpp to file
        # with open("vpp_vs_frequency_AMP.csv", "a") as f:
        #     f.write(f"{1/tdiv:.5e},{vpp:.6f}\n")  
        
        # Print the waveform
        do_plot = 0
        if do_plot == 1:
            # Plot the full waveform
            plt.figure(figsize=(12, 6))
            plt.subplot(2, 1, 1)
            plt.plot(time_axis, Voltage)
            plt.title("Full Waveform from Channel 4")
            plt.xlabel("Time (s)")
            plt.ylabel("Voltage (V)")
            # plt.ylim(-vdiv * 5, vdiv * 5)
            plt.grid(True)

            # Plot the filtered waveform (100 µs to 200 µs)
            plt.subplot(2, 1, 2)
            plt.plot(time_filtered, voltage_array)
            plt.title("Filtered Waveform ")
            plt.xlabel("Time (s)")
            plt.ylabel("Voltage (V)")
            plt.grid(True)

            plt.tight_layout()
            plt.show()
        # Save waveform data to a CSV file
        # np.savetxt("waveform_data.csv", np.column_stack((time_axis, voltage)), delimiter=",  ", header="Time (s),Voltage (V)", comments="")
        # print("Waveform data saved to waveform_data.csv")

        return time_axis, voltage_filtered
    
    # If only read No Scaler Product with Square pulse
    else:
        response = oscilloscope.query("TIME_DIV?").strip() # Query the oscilloscope for the current time division setting
        #print("DEBUG TIME_DIV response:", repr(response)) # Check if response is valid and contains expected data, if not response or "TIME_DIV" not in response:
        try:
            tdiv = float(response) # if response is a simple number 
        except ValueError:
            tdiv = float(response.split()[1]) # if response is like "TIME_DIV 1e-3"

        #print(f"tdiv = {tdiv:.3e} seconds")
        
        #vdiv = float(oscilloscope.query("C4:VDIV?").split()[1])
        #offset = float(oscilloscope.query("C4:OFFSET?").split()[1])

        # Call the descriptor function to get voltage
        time_axis, Voltage = read_lecroy_waveform(oscilloscope)

        # Generate time array
        #num_samples = len( Voltage)
        #time_axis = np.linspace(-5*tdiv, -5*tdiv + tdiv * 10, num_samples) 

        # Extract data for the specific time duration (100 µs to 200 µs)
        # Boolean mask for the time range
        time_range_mask = (time_axis >= 0.60 * tdiv) & (time_axis <= 0.90*tdiv)
        time_filtered = time_axis[time_range_mask]
        voltage_array = Voltage[time_range_mask]
        
        """Return the mean of the top 60%highest values in the voltage array."""
        v = np.asarray(voltage_array, dtype=float)
        v = v[np.isfinite(v)]
        n = v.size
        if n == 0:
            raise ValueError("Voltage array is empty!")
        
        # Number of samples in the top % of array
        k = max(1, int(0.6 * n))
        
        # Sort and take the top k samples
        v_sorted = np.sort(v)
        top_vals = v_sorted[-k:]
        voltage_filtered= top_vals # in case of square pulse i/p return this array
        

        do_plot = 0

        if do_plot == 1:
            # Plot the full waveform
            plt.figure(figsize=(12, 6))
            plt.subplot(2, 1, 1)
            #plt.plot(time_axis * 1e06, voltage)
            plt.plot(time_axis * 1e06, Voltage)
            plt.title("Full Waveform from Channel 4")
            plt.xlabel("Time (mus)")
            plt.ylabel("Voltage (V)")
            # plt.ylim(-vdiv * 5, vdiv * 5)
            plt.grid(True)

            # Plot the filtered waveform (100 µs to 200 µs)
            plt.subplot(2, 1, 2)
            plt.plot(time_filtered * 1e06, voltage_array)
            plt.title("Filtered Waveform ")
            plt.xlabel("Time (mus)")
            plt.ylabel("Voltage (V)")
            plt.grid(True)

            plt.tight_layout()
            plt.show(block=True)
        # Save waveform data to a CSV file
        # np.savetxt("waveform_data.csv", np.column_stack((time_axis, voltage)), delimiter=",  ", header="Time (s),Voltage (V)", comments="")
        # print("Waveform data saved to waveform_data.csv")

        return time_axis, voltage_filtered
    
        

    
    

# Calculate the current through 10k Resistor 
def getG(voltage_mean, series_resistor, Amplitude, AnalogCompute=False):
    if AnalogCompute:

        I = voltage_mean / series_resistor  # Current (Ohm's law)
        """Calculate current using Ohm's Law (I = V/R)."""
        print(f'Average Computed Current: {I}')
        return I

    else:
        
        I_mean = voltage_mean/ series_resistor  # Current (Ohm's law)
        V_diff = Amplitude - voltage_mean
        
        G_mean = I_mean / V_diff  # Conductance

        #print (f'Voltage across memristor-resistor series {Amplitude:.3e} V and current through {I_mean:.3e} A')
        #print (f"Voltage across series resistor {voltage_mean:.3e} V")
        #print (f'Voltage across memristor {V_diff:.3e}V and current through {I_mean:.3e} A')
        
        

        return G_mean