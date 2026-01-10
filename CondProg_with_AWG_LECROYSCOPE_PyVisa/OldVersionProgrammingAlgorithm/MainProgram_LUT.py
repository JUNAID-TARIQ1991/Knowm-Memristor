
"""
Written by Prof. Raffaele and J. Tariq
This Module generate pulses on Multiple channels for read and set memristor conductance
Read Conductance :  ModuleName read 1
To set the conductance on memristor
    usage:  ModuleName set 1 100 1 
    Arg2:set: operation to perform on memristor
    Arg3 1: channel 
    Arg4 100: Intended G value


    LUT - Look Up Table based approach to set the conductance
    Arg5 1: Number of iterations to repeat the operation
    Arg6 1: Amplitude in volts for each channel to increase G
    Arg7 -0.3: Amplitude in volts for each channel to decrease G
    Arg8 0: Offset in volts
    Arg9 200e-06: Time period of the wave
    Arg10 5: Frequency in kHz

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
import os
import sys
import time
import csv
from datetime import datetime
import argparse

import dwfpy as dwf
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

# ---- simple per-iteration CSV logger ----
class ProgLogger:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self._f = None
        self._w = None
        self._header_written = False

    def add(self, **row):
        if self._f is None:
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            self._f = open(self.csv_path, "w", newline="")
            self._w = csv.DictWriter(self._f, fieldnames=[
                "timestamp", "scenario", "channel", "attempt",
                "mode",
                "G_prev_uS", "G_uS", "G_target_uS",
                "err_uS", "rel_err",
                "alpha", "beta", "scaling_factor",
                "K", "pw_scale", "np_scale", "stuck_counter", "flip_damped",
                "PW_s", "NP", "Amplitude_V"
            ])
        if not self._header_written:
            self._w.writeheader()
            self._header_written = True
        if "timestamp" not in row:
            row["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for k in self._w.fieldnames:
            row.setdefault(k, "")
        self._w.writerow(row)
        self._f.flush()

    def close(self):
        if self._f:
            self._f.close()
            self._f = None

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
        if action not in ["set", "reset", "read", "compute"]:
            print("Invalid operation! Please provide one of: set, reset, read, compute.")
            sys.exit(1)

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Set up the AWG and the oscilloscope
        awg_handle, oscilloscope = initialize_instrument(AWG_Addr, LeCroy_Address)

        # Helper to write SCPI commands
        def write_cmd(cmd: str):
            awg_handle.write(cmd)

        # Create a new CSV log per run
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if action == "set":
            logname = f"SET_Target{int(sys.argv[3])}uS_{timestamp}.csv"
        else:
            logname = f"LOG_{timestamp}.csv"

        log = ProgLogger(f"logs/{logname}")

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
            try: log.close()
            except: pass
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
            try: log.close()
            except: pass
            return

        # ------------------ READ ------------------
        if action == "read":
            G = ReadMemristor(awg_handle, oscilloscope, channel)
            print("Reading...")
            print(f'Conductance of channel: {channel} =  {G *1e6:.3e} µS Corresponding to {1/G/1e3:.3e} kΩ')
            write_cmd(f"OUTPut{channel}:STATe 0")
            close_awg_connection(awg_handle)
            try: log.close()
            except: pass
            return

        # ------------------ SET ------------------
        if action == "set":
            Amplitude = 1.0        # V (increase G)
            Amplitude_dec = -0.3  # V (decrease G)
            Offset = 0
            Num_Pulses = 100
            Num_Pulses_dec = 100
            Time_Period = 100e-06  # s
            Frequency = 5          # kHz (unused here but preserved)
            max_conductance = 400e-06  #  (400 µS)
            max_attempts = 20
            total_np_increase = 0


            # Intended G (µS -> S)
            if len(sys.argv) >= 4:
                try:
                    intended_g_value = float(sys.argv[3]) * 1e-06
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

            for it in range(iterations):
                print(f"Iteration {it + 1}/{iterations}")
                # --- Pre-reset before each attempt ---
                for r in range(1):
                    print("Pre-reset before each attempt")
                    ResetMemristor(awg_handle, channel)
                    time.sleep(0.1)

                # Initial conductance
                ReadGValue = ReadMemristor(awg_handle, oscilloscope, channel)
                print(f"Initial conductance value: {ReadGValue * 1e6:.3e},  Corresponding to {1/ReadGValue/1e3:.3e} kΩ")
                current_g_value = ReadGValue

                # Tolerance (5-10%)
                tolerance = 0.08 * intended_g_value
                lower_bound = intended_g_value - tolerance
                upper_bound = intended_g_value + tolerance
                attempts = 0

                # History for adaptive scaling
                conductance_values = []

                # Initial scaling parameters, LUT table based on target and initial value
                alpha, beta = 1.0, 1.0

                # Stability check after reaching target, or No check
                additional_reads = 5
                target_reached = False
                DO_STABILITY_CHECK = True   # <-- change to True if you want stability enforced
                
                # Initial scaling parameters
                def init_alpha_beta(intended_g_value, max_conductance, is_increasing=True):
                    """
                    Initialize alpha and beta:
                    """
                    if is_increasing:

                        if ReadGValue < 50e-6:
                            if intended_g_value <= 50e-6:
                                alpha, beta = 1.0, 1.0
                            elif intended_g_value <= 100e-6:
                                alpha, beta = 1.5, 1.5
                            elif intended_g_value <= 200e-6:
                                alpha, beta = 2.0, 2.0
                            else:
                                alpha, beta = 3.0, 3.0

                        elif 50e-6 <= ReadGValue < 150e-6:
                            if intended_g_value <= 150e-6:
                                alpha, beta = 1.0, 1.0
                            elif intended_g_value <= 250e-6:
                                alpha, beta = 1.5, 1.5
                            else:
                                alpha, beta = 2.0, 2.0

                        elif 150e-6 <= ReadGValue < 250e-6:
                            if intended_g_value <= 250e-6:
                                alpha, beta = 1.0, 1.0
                            elif intended_g_value <= 350e-6:
                                alpha, beta = 1.5, 1.5
                            else:
                                alpha, beta = 2.0, 2.0

                        else:  # ReadGValue >= 250 µS
                            if intended_g_value > ReadGValue:
                                alpha, beta = 1.2, 1.2
                            else:
                                alpha, beta = 1.0, 1.0

                    else:
                        alpha, beta = 1.0, 1.0  # decreasing case

                    return alpha, beta
                # check is_increasing is true or false
                if current_g_value < intended_g_value:
                    is_increasing = True
                else:
                    is_increasing = False

                alpha, beta = init_alpha_beta(intended_g_value, max_conductance, is_increasing)

                def calculate_scaling_factor(intended_g_value, ReadGValue, max_conductance, alpha, beta, is_increasing=True):

                    # If little change, gently increase alpha/beta
                    if  len(conductance_values) >= 2 and abs(conductance_values[attempts] - conductance_values[attempts-1]) < 20.0 * 1e-06:
                        alpha = alpha + 0.2 + (attempts / max_attempts)
                        beta  = beta  + 0.2 + (attempts / max_attempts)
                    # Compute scaling factor
                    if is_increasing:
                        difference_ratio = (intended_g_value - ReadGValue) / max(intended_g_value, 1e-30)
                    else:
                        difference_ratio = (ReadGValue - intended_g_value) / max(ReadGValue, 1e-30)

                    absolute_difference = abs(intended_g_value - ReadGValue)
                    scaling_factor = round(alpha * difference_ratio + beta * (absolute_difference / max_conductance), 2)

                    # Clamp ranges
                    if is_increasing and intended_g_value >= 150e-06:
                        return min(3.0, max(0.1, scaling_factor))
                    elif is_increasing and intended_g_value >= 100e-06:
                        return min(3.0, max(0.1, scaling_factor))
                    elif is_increasing and intended_g_value < 100e-06:
                        return min(3.0, max(0.1, scaling_factor))
                    else:
                        return min(3.0, max(0.1, scaling_factor))

                while attempts <= max_attempts:
                    conductance_values.append(current_g_value)

                    # Increase
                    if current_g_value < intended_g_value:
                        print(f"Increasing the conductance..... attempt {attempts}")
                        scaling_factor = calculate_scaling_factor(intended_g_value, current_g_value, max_conductance, alpha, beta, True)
                        PW_used = Time_Period/2
                        NP_used = int(max(1, round(Num_Pulses * scaling_factor)))
                        total_np_increase += NP_used
                        Amp_used = Amplitude
                        log.add(
                            scenario="set", channel=channel, attempt=attempts, mode="inc",
                            G_prev_uS=current_g_value*1e6, G_uS="",
                            G_target_uS=intended_g_value*1e6,
                            err_uS=(intended_g_value-current_g_value)*1e6,
                            rel_err=(intended_g_value-current_g_value)/max(intended_g_value,1e-30),
                            alpha=alpha, beta=beta, scaling_factor=scaling_factor,
                            PW_s=PW_used, NP=NP_used, Amplitude_V=Amp_used
                        )
                        SendWritePulse(awg_handle, Amp_used, PW_used, NP_used, channel)
                        

                    # Decrease
                    elif current_g_value > intended_g_value:
                        print(f"Decreasing the conductance..... attempt {attempts}")
                        scaling_factor = calculate_scaling_factor(intended_g_value, current_g_value, max_conductance, alpha, beta, False)
                        PW_used = Time_Period/2
                        NP_used = int(max(1, round(Num_Pulses_dec * scaling_factor)))
                        Amp_used = Amplitude_dec
                        log.add(
                            scenario="set", channel=channel, attempt=attempts, mode="dec",
                            G_prev_uS=current_g_value*1e6, G_uS="",
                            G_target_uS=intended_g_value*1e6,
                            err_uS=(intended_g_value-current_g_value)*1e6,
                            rel_err=(intended_g_value-current_g_value)/max(intended_g_value,1e-30),
                            alpha=alpha, beta=beta, scaling_factor=scaling_factor,
                            PW_s=PW_used, NP=NP_used, Amplitude_V=Amp_used
                        )
                        SendWritePulse(awg_handle, Amp_used, PW_used, NP_used, channel)
                    else:
                        # Exactly equal (rare)
                        target_reached = True

                    time.sleep(0.2)

                    # Readback
                    previous_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
                    log.add(
                        scenario="set", channel=channel, attempt=attempts, mode="read",
                        G_prev_uS=current_g_value*1e6, G_uS=previous_g_value*1e6,
                        G_target_uS=intended_g_value*1e6,
                        err_uS=(intended_g_value-previous_g_value)*1e6,
                        rel_err=(intended_g_value-previous_g_value)/max(intended_g_value,1e-30),
                        PW_s=0.0, NP=0, Amplitude_V=0.0
                    )
                    print(f"Previous Conductance: { current_g_value * 1e6:.3e} µS, (R={1/current_g_value/1e3:.3e} kΩ)")
                    print(f"Current  Conductance: { previous_g_value * 1e6:.3e} µS, (R={1/previous_g_value/1e3:.3e} kΩ) ")

                    current_g_value = previous_g_value

                    #  Apply stability check
                    if lower_bound <= current_g_value <= upper_bound:
                        target_reached = True
                        # ----Always  Store successful programming result, without stability 
                        append_success_result(target_uS=intended_g_value * 1e6, programmed_uS=current_g_value * 1e6) 
                        
                        print(f"Memristor conductance within target range: { current_g_value * 1e6:.3e} µS.")
                        # ---- Skip stability check if not enabled ----
                        if not DO_STABILITY_CHECK:
                            print("Target reached, No stability check, exit()")
                            time.sleep(0.01)
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

                if not target_reached:
                    print(f"Target not reached after {max_attempts} attempts.")
            print("\n======================================")
            print(f"Total pulses used to INCREASE conductance: {total_np_increase}")
            print("======================================")

            print("Closing the device......")
            for i in range(1, 5):
                write_cmd(f"OUTPut{i}:STATe 0")
            close_awg_connection(awg_handle)
            try: log.close()
            except: pass
            return

    except ValueError:
        print("Invalid input. Unable to establish connection.")
        sys.exit(1)


if __name__ == "__main__":
    main()
