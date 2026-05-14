import re
from Read_write_reset.ReadMemristor import ReadMemristor
from Read_write_reset.Set_G_Channel import SendWritePulse
from Read_write_reset.ResetMemristor import ResetMemristor
from Read_write_reset.Stuck_low_check import Pulse4StuckLow
from Read_write_reset.Stuck_High_check import Pulse4StuckHigh



import time

def Stuck_Check(awg_handle, oscilloscope, Voltage_Inc,Time_Period, No_Pulses_inc, Max_Conductance, channel):
    """
    Initializes the memristor to a known conductance state by reading its current conductance.
    
    Arguments:
    awg_handle -- The AT_AWG handle
    oscilloscope -- the AnalogDiscovery2 oscilloscope handle.
    channel -- The AWG channel to use.
    
    Returns:
    G_0 -- The initial conductance of the memristor.
    Purpose:
    Initialize the V_Dec based on memristor behavior. Apply, High voltage pulses to set the memristor to a known or high state, Then apply   
    a decreasing voltage pulses and measure the conductance again. if the difference between the high state and state after applying decrease pulses 
    is significant, i.e., > 100 muS we can use the voltage used in decreasing pulses as V_Dec. If the the conductance ater decrease pulses is still high,
    we can increase the amplitude of decrease pulses and repeat the process until we get a significant change in conductance.
    """
    Stuck_Low = False
    Stuck_High = False
    
    Pulse4StuckHigh(awg_handle,channel,Time_Period=500e-3,Amplitude=1.0,No_pulses=20)
    time.sleep(0.5)
    #Pulse4StuckLow(awg_handle, channel,Time_Period=Time_Period,Amplitude=Voltage_Inc,No_pulses=No_Pulses_inc)

    G_init = ReadMemristor(awg_handle, oscilloscope, channel) # Initial conductance
    print(f"[INIT] Initial conductance G_init: {G_init * 1e6:.2f} µS")
    time.sleep(0.1)
    SendWritePulse(awg_handle, Voltage_Inc, Time_Period, No_Pulses_inc, channel) # Apply increasing pulses
    time.sleep(1)
    G_0 = ReadMemristor(awg_handle, oscilloscope, channel) # Conductance after increase pulses
    print(f"[INIT] Conductance G_0 after increase pulses: {G_0 * 1e6:.2f} µS")
    # If there is no change in G memristor is stuck.
    delta_G = abs(G_0 - G_init)
    if delta_G < 50e-6:
        if G_0 < 50e-6:
            print(f"[INIT] Warning: Memristor stuck Low.")
            Stuck_Low = True
        elif G_0 > 400e-6:
            print(f"[INIT] Warning: Memristor stuck High.")
            Stuck_High = True
    
    if Stuck_Low or Stuck_High:
        print("[INIT] Memristor appears to be stuck. Performing resets...")
        for i in range(5):
            ResetMemristor(awg_handle, channel, 5)
            time.sleep(0.1)
    else:
        print(f"[INIT] Memristor conductance change ΔG: {delta_G * 1e6:.2f} µS after increase pulses.")
        for i in range(3):
            ResetMemristor(awg_handle, channel, 5)
            time.sleep(0.1)
    return Stuck_Low, Stuck_High