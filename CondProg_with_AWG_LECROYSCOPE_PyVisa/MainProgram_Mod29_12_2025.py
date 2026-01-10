
"""
Written by Prof. Raffaele and J. Tariq
This Module generate pulses on Multiple channels for read and set memristor conductance
Read Conductance :  ModuleName read 1
To set the conductance on memristor
    usage:  ModuleName set 1 100 1 
    Arg2:set: operation to perform on memristor
    Arg3 1: channel 
    Arg4 100: Intended G value in µS
    Arg5 1: Number of iterations

To reset the conductance on memristor
    usage: ModuleName reset 1 5
    Arg2: reset: operation to perform on memristor
    Arg3 1: channel 
    Arg4 5: Number of times to reset the memristor

To compute the current on memristor
    usage: ModuleName compute 1.0 2.0 3.0 4.0
    Arg2 compute: operation to perform on memristor
    Arg3 1.0: voltage on channel 1
    Arg4 2.0: voltage on channel 2
    Arg5 3.0: voltage on channel 3
    Arg6 4.0: voltage on channel 4

To compute the current on memristor using AnalogCompute function
    usage: ModuleName compute 1.0 2.0 3.0 4.0
    Arg2 compute: operation to perform on memristor
    Arg3 1.0: voltage on channel 1
    Arg4 2.0: voltage on channel 2
    Arg5 3.0: voltage on channel 3
    Arg6 4.0: voltage on channel 4

LUT - Look Up Table based approach to set the conductance
    usage: ModuleName set <channel> <intended_g_value> <iterations>
    Arg2 set: operation to perform on memristor
    Arg3 1: channel 
    Arg4 100: Intended G value in µS        """

# --- Imports ---
from cmath import log
import os
import sys
import time
import csv
from datetime import datetime
import argparse
import matplotlib.pyplot as plt


import dwfpy as dwf
from MemristorTest import MemristorCheck
from SetUp import SetUp
from ReadMemristor import ReadMemristor
from ResetMemristor import ResetMemristor
from Set_G_Channel import SendWritePulse
from SetUp_AWG import initialize_instrument, close_awg_connection
from Configure_AWG import Generate_waveform
from Configure_LecroyOsc import configure_oscilloscope
from DriveInputs_AWG import AnalogCompute

AWG_Addr = "TCPIP0::172.16.9.59::inst0::INSTR"
LeCroy_Address = "TCPIP0::172.16.13.144::INSTR"

# Store results into a file, if successful 
RESULTS_CSV = r"C:\Users\Junaid\Data\Experimental_data\VMM_and_Con_Programming\ConductanceBoxPlot\programmed_G_results5.csv"
# Helper to store results
def append_success_result(target_uS, programmed_uS):
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    file_exists = os.path.isfile(RESULTS_CSV)

    with open(RESULTS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["G_target_uS", "G_programmed_uS"])
        writer.writerow([f"{target_uS:.6e}", f"{programmed_uS:.6e}"])


# Main function to handle the operation based on input arguments
def main():
    try:
        # Ensure the correct number of arguments are passed
        if len(sys.argv) < 2:
            print("Please provide the operation <set, reset, read, compute>.")
            sys.exit(1)

        # Get the operation (set, reset, read, compute)
        action = sys.argv[1].lower()

        # Check if the action is valid
        if action not in ["set", "reset", "read", "check", "compute"]:
            print("Invalid operation! Please provide one of: set, reset, read, check, compute.")
            sys.exit(1)

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Set up the AWG and the oscilloscope
        awg_handle, oscilloscope = initialize_instrument(AWG_Addr, LeCroy_Address)

        # Helper to write SCPI commands
        def write_cmd(cmd: str):
            awg_handle.write(cmd)


        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


        # Handle the `compute` action (early exit path)
        if action == "compute":
            if len(sys.argv) < 6:
                print("Please provide 4 voltage values for compute action.")
                sys.exit(1)

            v1, v2, v3, v4 = map(float, sys.argv[2:6])
            print("Performing compute action...")
            I = AnalogCompute(awg_handle, oscilloscope, v1, v2, v3, v4)
            print(f'Average I = {I:.2e} A')
            time.sleep(0.2)
            print("Closing the AD2 device......")
            for i in range(1, 5):
                write_cmd(f"OUTPut{i}:STATe 0")
            close_awg_connection(awg_handle)
            sys.exit(0)

        # For reset, read and set we need a channel number
        input_value = sys.argv[2] if len(sys.argv) >= 3 else ""
        if input_value.isdigit():
            channel = int(input_value)
            if 1 <= channel <= 8:
                print(f"Channel Selected: {channel} ")
            else:
                print("Input is out of range! Please enter channel number between 1 and 8.")
                sys.exit(1)
        else:
            print("Invalid input! Please enter a valid Channel number.")
            sys.exit(1)

        # ------------------ RESET ------------------
        if action == "reset":
            # Optional 4th arg = reset count, default 5
            if len(sys.argv) >= 4 and sys.argv[3].isdigit():
                reset_count = int(sys.argv[3])
            else:
                reset_count = 5

            for i in range(reset_count):
                ResetMemristor(awg_handle, channel)
                g = ReadMemristor(awg_handle, oscilloscope, channel)
                print(f"conductance value for attempt {i}: {g * 1e6:.3e} µS")
                print(f"Resetting... (Attempt {i + 1})")
            print(f"Memristor on channel  {channel} reset {reset_count} time(s).")
            write_cmd(f"OUTPut{channel}:STATe 0")
            close_awg_connection(awg_handle)
            return

        # ------------------ READ ------------------
        if action == "read":
            G = ReadMemristor(awg_handle, oscilloscope, channel)
            print("Reading...")
            print(f'Conductance of channel: {channel} =  {G *1e6:.3e} µS Corresponding to {1/G/1e3:.3e} kΩ')
            write_cmd(f"OUTPut{channel}:STATe 0")
            close_awg_connection(awg_handle)
            return

        # ------------------ MemristorCheck------------------
        if action == "check":
            MemristorCheck(awg_handle, channel)
            print("Performing Memristor Check...")
            time.sleep(0.2)
            #G = ReadMemristor(awg_handle, oscilloscope, channel)
            #print(f'Conductance of memristor on channel: {channel} =  {G *1e6:.3e} µS Corresponding to {1/G/1e3:.3e} kΩ')
            write_cmd(f"OUTPut{channel}:STATe 0")
            close_awg_connection(awg_handle)
            return
        # ------------------ SET ------------------
        if action == "set":
            Amplitude_inc = 1.0      # V (increase G)
            Amplitude_dec = -0.20  # V (decrease G)
            Offset = 0
            Num_Pulses_inc = 100
            Num_Pulses_dec = 20
            Time_Period = 200e-06  # s
            Frequency = 5          # kHz (unused here but preserved)
            max_conductance = 250e-06  #  (200 µS)
            max_attempts = 25
            total_np_increase = 0
            # ---- Plot directory ----
            PLOT_DIR = os.path.join(os.path.dirname(__file__), "Plots")
            os.makedirs(PLOT_DIR, exist_ok=True)

            # ===================== PULSE PARAMETERS =====================

            # --- Increase conductance ---
            INC = {
                "amplitude":  Amplitude_inc,        # V
                "Num_pulses": Num_Pulses_inc,
                "pw":         Time_Period / 2
            }

            # --- Decrease conductance ---
            DEC = {
                "amplitude":  Amplitude_dec,       # V
                "Num_pulses": Num_Pulses_dec,         # <-- can be different
                "pw":         Time_Period / 2
            }
            
            if len(sys.argv) >= 4: # Intended g value from the terminal
                try:
                    intended_g_value = float(sys.argv[3]) * 1e-06 # convert µS to S 
                    print(f"Intended conductance value: {intended_g_value * 1e6:.3e} µS")
                except ValueError:
                    print("Invalid intended conductance value! Please provide a valid number.")
                    sys.exit(1)
            else:
                print("Provide intended g value as an argument.")
                sys.exit(1)

            # Iterations (repeat)
            if len(sys.argv) == 5:
                try:
                    iterations = int(sys.argv[4])
                except ValueError:
                    print("Invalid iteration count! Please provide a valid number.")
                    sys.exit(1)
            else:
                print("Invalid iteration count! Please provide a valid number as a fourth argument.")
                sys.exit(1)
            
            # --- Tolerance (± ?%) ---
            tolerance = 0.08 * intended_g_value
            lower_bound = intended_g_value - tolerance
            upper_bound = intended_g_value + tolerance
            
            # Stability check after reaching target, or No check
            additional_reads = 5
            target_reached = False # Flag
            DO_STABILITY_CHECK = True   # <-- change to True if you want stability enforced
            DO_INITIAL_MEMRISTOR_CHECK = True  # set False to skip MemristorCheck at iteration start
            MAX_FAILURE_RECOVERIES = 1       # how many auto-recoveries after max_attempts failure
            
            # ===================== SCALING LOGIC =====================
            def init_alpha_beta(G_init, G_target, G_max, is_increasing):
                """
                Smooth gain scheduling:
                Choose K_des that is linear in G_target, then solve alpha so that
                K = alpha*(er + gt*ea) matches K_des. Keep beta = alpha*gt.
                """
                g0 = G_init / max(G_max, 1e-12) # Current normalized conductance or current G value
                gt = G_target / max(G_max, 1e-12) # target normalized conductance

                # apply the same K shaping in both directions, for absolute error:
                dG = abs(G_target - G_init)

                # Errors at initialization (same definitions used later) # relative error
                if is_increasing:
                    er = (G_target - G_init) / max(G_target, 1e-12)
                else:
                    er = (G_init - G_target) / max(G_init, 1e-12) 

                ea = dG / max(G_max, 1e-12)

                # ----- Desired linear K vs target (tune these 4 numbers, Gmin, Gmax, Kmin, Kmax) -----
                Gmin = 40e-6 #  Minimum target conductance
                Gmax_lin = 250e-6 # Maximum target conductance
                # ---- Direction-aware K range, Constarint on scaling factor, and it should be linear in this range----
                if is_increasing:
                    Kmin = 0.10
                    Kmax = 2.0
                else:
                    Kmin = 0.10
                    Kmax = 1.00

                # ---- Linear mapping of target K, t is just a factor b/w 0 and 1, k_des is the desired factor i.e., 
                # 0.1 and 2.0 or 3.0 ----
                if is_increasing:
                    t = (min(max(G_target, Gmin), Gmax_lin) - Gmin) / (Gmax_lin - Gmin)
                else:
                    # Use distance to go for RESET
                    dGmax = max(1e-12, (G_max - Gmin))   # scale reference
                    t = min(1.0, max(0.0, dG / dGmax))   # larger drop => larger K_des      
                K_des = Kmin + (Kmax - Kmin) * t # desired K, what we want to achieve, 
                                                 #K is decided before looking at error magnitude

                # ---- Solve alpha to hit K_desired smoothly ----
                denom = er + gt * ea #
                if abs(denom) < 1e-9:   # Very rare case, avoid div by zero 
                    alpha = 1.0 # arbitrary
                else:
                    alpha = K_des / denom # solve for alpha, real definition of K

                # ---- Safety limits ----
                alpha = max(0.1, min(3.0, alpha)) # alpha non-negative
                beta  = alpha * gt
                beta  = max(0.0, min(3.0, beta)) # beta non-negative
                return alpha, beta


            def update_scaling(G_current,G_target,G_max,alpha,beta,G_history,attempt,max_attempts,is_increasing):
                """
                Compute scaling factor K and update alpha/beta.
                Fully symmetric increasing/decreasing logic.
                """

                # --- Relative error (asymmetric, IMPORTANT) ---
                if is_increasing:
                    er = (G_target - G_current) / max(G_target, 1e-12)
                else:
                    er = (G_current - G_target) / max(G_current, 1e-12)

                # --- Absolute error ---
                ea = abs(G_target - G_current) / G_max

                # --- Stuck detection ---
                stuck = False
                if len(G_history) >= 2:
                    dG = abs(G_history[-1] - G_history[-2])
                    if dG < 0.1 * G_current:  # less than 5% change
                        stuck = True
                # --- Adaptive update in case of stuck ---
                if stuck:
                    # Very mild gain, slowly increases with attempts
                    gain = 0.05 + 0.20 * (attempt / max_attempts)
                    alpha *= (1.0 + gain)  
                    beta  *= (1.0 + 0.5 * gain)

                # --- Real Scaling factor ---
                K = alpha * er + beta * ea # combined effect Define K (scaling factor) ********

                # --- Safety clamps ---
                K = max(0.1, min(3.0, K))
                alpha = min(alpha, 5.0)
                beta  = min(beta, 5.0)

                return K, alpha, beta, stuck

            # ********Here is the main Programming Loop over number of iteration, noramly one*******
            for it in range(iterations):
                print(f"Iteration {it + 1}/{iterations}")

                # ---- Per-iteration traces for plotting ----
                attempt_trace = []
                G_trace_uS = [] 
                K_trace = []
                # ======================================================
                # Initial memristor diagnostic check (once per iteration)
                # ======================================================
                current_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
                time.sleep(0.1)

                if DO_INITIAL_MEMRISTOR_CHECK:
                    print("[INIT] DO_INITIAL_MEMRISTOR_CHECK=True -> Running MemristorCheck...")
                    MemristorCheck(awg_handle, channel)
                    time.sleep(0.2)
                    # Re-read after check/reset since the state may have changed
                    current_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
                    time.sleep(0.1)
                else:
                    print("[INIT] DO_INITIAL_MEMRISTOR_CHECK=False -> Skipping MemristorCheck (using current device state).")
                
                print(f"Initial Conductance: { current_g_value * 1e6:.3e} µS, (R={1/current_g_value/1e3:.3e} kΩ) ")

                # Continue normally
                is_increasing = current_g_value < intended_g_value

                alpha, beta = init_alpha_beta(G_init=current_g_value,G_target=intended_g_value,G_max=max_conductance,is_increasing=is_increasing)
                G_history = []
                attempts = 0
                target_reached = False
                
                # Main Loop
                while attempts < max_attempts:

                    G_history.append(current_g_value)
                    is_increasing = current_g_value < intended_g_value
                    K, alpha, beta, stuck = update_scaling(G_current=current_g_value,G_target=intended_g_value,G_max=max_conductance,
                                                           alpha=alpha,beta=beta,G_history=G_history,attempt=attempts,max_attempts=max_attempts,
                                                           is_increasing=is_increasing)
                    # ---- Store values for plotting (before pulse) ----
                    attempt_trace.append(attempts)
                    G_trace_uS.append(current_g_value * 1e6)
                    K_trace.append(K)
                    
                    # --- Pulse parameters ---
                    # Determine pulse parameters based on increase/decrease
                    cfg = INC if is_increasing else DEC # select INC/DEC config
                    base_np = cfg["Num_pulses"] # default
                    # ---- Target-dependent base pulse count override for very log G values only for increase case, for fixed Number of pulse
                    # initialization just remove the following if else block----
                    if is_increasing:
                        if intended_g_value <= 50e-6:
                            base_np = 10
                        elif intended_g_value <= 100e-6:
                            base_np = 25
                        elif intended_g_value <= 200e-6:
                            base_np = 50                 
                    # Low, MID / HIGH target NO limit
                    NP_used = int(max(1, round(base_np * K))) # no limit on NP

                    PW_used = cfg["pw"] 
                    #PW_used = max(10.0e-6, min(1.0, cfg["pw"] * K))
                
                    Amp_used = cfg["amplitude"]
                    # Determine amplitude based on increase/decrease (Veriable amplitude programming (Not recommended))
                    # for fixed amplitude, i.e., 1V just remove the following if else block
                    if is_increasing:
                        # Target-dependent INC amplitude
                        if intended_g_value <= 50e-6:
                            Amp_used = 0.60
                        elif intended_g_value <= 150e-6:
                            Amp_used = 0.80
                        else:
                            Amp_used = 1.20
                    else:
                        # Keep your DEC amplitude (negative)
                        Amp_used = DEC["amplitude"]   # e.g., -0.25                    

                    total_np_increase += NP_used if is_increasing else 0 # count only increases

                    print(f"Attempt {attempts + 1}: Applying {'INC' if is_increasing else 'DEC'} pulse - "
                          f"Amp: {Amp_used} V, PW: {PW_used * 1e6:.2f} µs, NP: {NP_used}, K: {K:.3f}")
                    # ---- Send pulse to memritor ----
                    SendWritePulse(awg_handle, Amp_used, PW_used, NP_used, channel)
                    #time.sleep(0.1)  # small settle time    

                    # Readback, get new conductance
                    previous_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
                    time.sleep(0.1)
                    
                    print(f"Previous Conductance: { current_g_value * 1e6:.3e} µS, (R={1/current_g_value/1e3:.3e} kΩ)")
                    print(f"Current  Conductance: { previous_g_value * 1e6:.3e} µS, (R={1/previous_g_value/1e3:.3e} kΩ) ")

                    current_g_value = previous_g_value # update for next iteration
                    
                    # HARD SAFETY CHECK (direction-aware)
                    # ======================================================
                    runaway = False
                    # Absolute ceiling protection
                    if current_g_value >= 350e-6:
                        runaway = True

                    # If Overshootand also wrong direction only
                    elif is_increasing and current_g_value > intended_g_value + 100e-6:
                        runaway = True

                    #elif (not is_increasing) and current_g_value < intended_g_value - 100e-6:
                        #runaway = False

                    if runaway:
                        print(f"[SAFETY] Runaway conductance detected: {current_g_value*1e6:.2f} µS")
                        print("[SAFETY] Performing MemristorCheck + and restarting programming")
                        MemristorCheck(awg_handle, channel)
                        time.sleep(0.1)
                        current_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
                        alpha, beta = init_alpha_beta(G_init=current_g_value,G_target=intended_g_value,G_max=max_conductance,is_increasing=current_g_value < intended_g_value)
                        G_history.clear()
                        attempts = 0
                        continue
                    
                    #  Here, Apply stability check
                    if lower_bound <= current_g_value <= upper_bound:
                        target_reached = True
                        # ----Always  Store successful programming result, without stability 
                        append_success_result(target_uS=intended_g_value * 1e6, programmed_uS=current_g_value * 1e6) 
                        # ---- Store FINAL successful point for plotting ----
                        attempt_trace.append(attempts + 1)
                        G_trace_uS.append(current_g_value * 1e6)
                        K_trace.append(K)

                        print(f"Memristor conductance within target range: { current_g_value * 1e6:.3e} µS.")
                        # ---- Skip stability check if not enabled ----
                        if not DO_STABILITY_CHECK:
                            print("Target reached, No stability check, exit()")
                            break   # move directly to next iteration
                        # ---- Optional stability check ----
                        stable_reads = 0
                        for j in range(additional_reads):
                                    
                            stable_value = ReadMemristor(awg_handle, oscilloscope, channel)
                            time.sleep(1)
                            if lower_bound <= stable_value <= upper_bound:
                                stable_reads += 1
                                print(f"Stability Check {j + 1}: {stable_value * 1e6:.3e} µS within target range")
                            else:
                                print(f"Deviation detected in Stability Check {j + 1}: {stable_value * 1e6:.3e} µS outside target range")
                                target_reached = False
                                break

                        if target_reached and stable_reads >= additional_reads:
                            print(f"Conductance stable within target range for {additional_reads} reads. Process complete.")
                            break
                        else:
                            print("Target not reached, Stability check failed. Reapplying pulses.")
                    attempts += 1

                # Perform another iteration if not programmed
                if not target_reached:
                    print("[FAILURE] Target not reached  ")
                    
                # ---- Plotting per iteration ----      
                # ==================== PLOTTING ====================
                # --- G vs Attempts ---
                plt.figure(figsize=(7, 5))
                plt.plot(attempt_trace, G_trace_uS, marker="o")
                plt.axhline(intended_g_value * 1e6, linestyle="--", label="Target G")
                plt.xlabel("Attempt")
                plt.ylabel("Conductance (µS)")
                plt.title(f"G vs Attempts | Ch {channel} | Iter {it+1}")
                plt.grid(True)
                plt.legend()

                g_plot_name = f"G_vs_Attempts_Ch{channel}_Iter{it+1}_{timestamp}.png"
                plt.savefig(os.path.join(PLOT_DIR, g_plot_name), dpi=300)
                plt.close()

                # --- Scaling Factor vs Attempts ---
                plt.figure(figsize=(7, 5))
                plt.plot(attempt_trace, K_trace, marker="s")
                plt.xlabel("Attempt")
                plt.ylabel("Scaling Factor K")
                plt.title(f"K vs Attempts | Ch {channel} | Iter {it+1}")
                plt.grid(True)

                k_plot_name = f"K_vs_Attempts_Ch{channel}_Iter{it+1}_{timestamp}.png"
                plt.savefig(os.path.join(PLOT_DIR, k_plot_name), dpi=300)
                plt.close()

                print(f"Plots saved in {PLOT_DIR}")
                            
            print("\n======================================")
            print(f"Total pulses used to INCREASE conductance: {total_np_increase}")
            print("======================================")

            print("Closing the device......")
            for i in range(1, 5):
                write_cmd(f"OUTPut{i}:STATe 0")
            close_awg_connection(awg_handle)
            return

    except ValueError:
        print("Invalid input. Unable to establish connection.")
        sys.exit(1)


if __name__ == "__main__":
    main()
