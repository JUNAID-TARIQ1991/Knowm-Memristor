import os
from urllib import response
import pyvisa
import numpy as np
import time
import matplotlib.pyplot as plt
import struct
import re
# Oscilloscope reads by Prof.Raffaele
def read_lecroy_waveform(osc):
    # -------------------------------------------------------------

    osc.write("C4:WF? DESC") # Request waveform descriptor from channel 4
    desc = osc.read_raw() # Read raw binary data containing the descriptor

    pos = desc.find(b"WAVEDESC") # Locate the position of the "WAVEDESC" header in the raw data
    if pos < 0:
        raise RuntimeError("WAVEDESC not found!") 
    #print("Descriptor:",desc )
    # WAVEDESC is always 346 bytes long 
    wavedesc = desc[pos : pos + 346] # Extract the 346-byte descriptor block
    #print("Descriptor:", wavedesc)
    VERT_GAIN      = struct.unpack("<f", wavedesc[156:160])[0]
    VERT_OFFSET    = struct.unpack("<f", wavedesc[160:164])[0]
    ADC_OFFSET     = struct.unpack("<h", wavedesc[164:166])[0]
    HORIZ_INTERVAL = struct.unpack("<f", wavedesc[176:180])[0]
    HORIZ_OFFSET   = struct.unpack("<d", wavedesc[180:188])[0]
    N_SAMPLES      = struct.unpack("<i", wavedesc[60:64])[0]
    Time_div      = struct.unpack("<h", wavedesc[324:326])[0]


    #print("VERT_GAIN =", VERT_GAIN)
    #print("VERT_OFFSET =", VERT_OFFSET)
    #print("ADC_OFFSET =", ADC_OFFSET)
    #print("HORIZ_INTERVAL =", HORIZ_INTERVAL)
    #print("HORIZ_OFFSET =", HORIZ_OFFSET)
    #print("N_SAMPLES =", N_SAMPLES)
    #print("Time_div =", Time_div)

    # -------------------------------------------------------------
    # 2. Read waveform ADC data (DAT1 block)
    # -------------------------------------------------------------
    #osc.write("COMM_HEADER OFF")
    #osc.write("COMM_FORMAT DEF9,WORD,BIN")
    osc.write("C4:WF? DAT1") # Request waveform data from channel 4
    data = osc.read_raw() # Read raw binary data containing the waveform data

    #print("\nRaw data header:", data[:22])
    #print("Raw data preview (500 bytes):", data[:500])

    # Locate # block
    j = data.find(b"#") # Find the index of the binary block start
    nd = int(data[j+1:j+2]) # Number of digits that specify the length of the binary block
    dlen = int(data[j+2:j+2+nd])    # Total length of the binary block (descriptor + data)
    st = j + 2 + nd     # Starting index of the actual data in the raw response

    raw = data[st:st+dlen] # Extract the raw waveform data based on the length specified in the header
    #print("Waveform raw extracted:", raw[:40])
    #print("Raw length =", len(raw))

    #3. Determine ADC width (8-bit or 16-bit)
    
    if dlen == N_SAMPLES:
        adc = np.frombuffer(raw, dtype=np.int8) # 8-bit signed integers (LeCroy can use 8-bit or 16-bit ADC depending on settings)
    elif dlen == 2 * N_SAMPLES:
        adc = np.frombuffer(raw, dtype="<i2") # little ending 16-bit signed integers
    else:
        raise ValueError(f"Unexpected raw length: dlen={dlen}, expected {N_SAMPLES} or {2*N_SAMPLES}")
    
    
    #  Correct LeCroy voltage reconstruction formula
    adc = adc.astype(np.float64) # ADC convert to float 
    if adc.size == 0:
        raise ValueError("ADC array is empty")
    #print(f"ADC values: {adc}")
    #voltage = (adc - ADC_OFFSET) * VERT_GAIN - VERT_OFFSET # Offset is already given
    voltage = adc  * VERT_GAIN - VERT_OFFSET 
    time_axis = HORIZ_OFFSET + np.arange(adc.size) * HORIZ_INTERVAL 
    #voltage = (adc  *  VERT_GAIN) + VERT_OFFSET
    

    return voltage
    

def plot_waveform(time_axis, voltage_data):
    """Plot the voltage and current waveform."""
    plt.figure(figsize=(10, 5))
    plt.plot(time_axis, voltage_data, label="Voltage (V)", color='b')
    # plt.plot(time_axis, current_data, label="Current (A)", color='r', linestyle='dashed')
    plt.xlabel("Time (mus)")
    plt.ylabel("Voltage (V) ")
    plt.title("Pulse Waveform")
    plt.legend()
    plt.grid()
    plt.show()


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
        response = oscilloscope.query("TIME_DIV?").strip()
        print("DEBUG TIME_DIV response:", repr(response)) # Check if response is valid and contains expected data, if not response or "TIME_DIV" not in response:
        try:
            tdiv = float(response) # if response is a simple number 
        except ValueError:
            tdiv = float(response.split()[1]) # if response is like "TIME_DIV 1e-3"

        print(f"tdiv = {tdiv:.3e} seconds")
        
        #vdiv = float(oscilloscope.query("C4:VDIV?").split()[1])
        #offset = float(oscilloscope.query("C4:OFFSET?").split()[1])

        # Call the descriptor function to get voltage
        Voltage =  read_lecroy_waveform(oscilloscope)

        # Generate time array
        num_samples = len( Voltage)
        time_axis = np.linspace(-5*tdiv, -5*tdiv + tdiv * 10, num_samples) # Generate time axis based on tdiv and number of samples, centered around the trigger point (0 to 10*tdiv) 
        # It s useful if you get the axix information from the scope. 

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
        k = max(1, int(0.60 * n))
        
        # Sort and take the top k samples
        v_sorted = np.sort(v)
        top_vals = v_sorted[-k:]
        
        #voltage_filtered= float(np.mean(top_vals))
        voltage_filtered= top_vals
        

        do_plot = 1

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
