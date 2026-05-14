
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

To compute the analog sum of current on memristor
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
    Arg6 4.0: voltage on channel 4      """

# --- Imports ---
from cmath import log
import os
import sys
import io
import time
import csv
from datetime import datetime
import argparse 
import matplotlib.pyplot as plt

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
plt.ion()
import dwfpy as dwf
from Read_write_reset.Stuck_low_check import Pulse4StuckLow
from Read_write_reset.Stuck_High_check import Pulse4StuckHigh
from Configure_Instrument.SetUp_AD2 import SetUp
from Read_write_reset.ReadMemristor import ReadMemristor
from Read_write_reset.ResetMemristor import ResetMemristor
from Read_write_reset.Set_G_Channel import SendWritePulse
from Configure_Instrument.SetUp_AWG import initialize_instrument, close_awg_connection
from Read_write_reset.Handle_Runaway import handle_runaway
from DriveInputs_AWG import AnalogCompute
from Scaling_Factor.Stuck_Check import Stuck_Check
from Scaling_Factor.init_alpha_beta import init_alpha_beta
from Scaling_Factor.update_scaling import update_scaling
from Scaling_Factor.LivePlot import LivePlot
from Scaling_Factor.Adaptive_PW import stepped_pw_inc_dec
from Scaling_Factor.Init_NP import init_base_np, refine_np_near_target
from Scaling_Factor.Init_mode import detect_init_mode
from Scaling_Factor.Initial_Reset import InitialReset
from Scaling_Factor.Stuck_Monitor import StuckMonitor
from Scaling_Factor.AdaptiveResponseMonitor import  DirectionalResponseMonitor


AWG_Addr = "TCPIP0::172.16.9.59::inst0::INSTR"
LeCroy_Address = "TCPIP0::172.16.14.23::inst0::INSTR"

# to store log into a file
class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


logfile = open("log.txt", "a", encoding="utf-8")
sys.stdout = Tee(sys.stdout, logfile)
sys.stderr = Tee(sys.stderr, logfile)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Memristor Conductance Programming Tool"
    )

    sub = parser.add_subparsers(dest="action", required=True)

    # ---------- SET ----------
    set_p = sub.add_parser("set", help="Program memristor conductance")
    set_p.add_argument("channel", type=int)
    set_p.add_argument("target_uS", type=float)
    set_p.add_argument(
    "iterations",
    nargs="?",
    type=int,
    default=10,
    help="Number of programming iterations (default: 10)")

    set_p.add_argument("--plot-live", action="store_true")
    # ---exit policy -----
    set_p.add_argument(
    "--exit",
    choices=["early", "after-stability", "full-iterations"],
    default="after-stability",
    help=(
        "early: exit immediately when target reached\n"
        "after-stability: perform stability check (if enabled) then exit\n"
        "full-iterations: complete all iterations even if target reached"
    )
)


    # ---------- READ ----------
    read_p = sub.add_parser("read", help="Read memristor conductance")
    read_p.add_argument("channel", type=int)

    # ---------- RESET ----------
    reset_p = sub.add_parser("reset", help="Reset memristor")
    reset_p.add_argument("channel", type=int)

    # ---------- CHECK ----------
    check_p = sub.add_parser("check", help="Diagnostic memristor check")
    check_p.add_argument("channel", type=int)

    # ---------- COMPUTE ----------
    compute_p = sub.add_parser("compute", help="Analog current compute")
    compute_p.add_argument(
        "voltages",
        nargs=4,
        type=float,
        help="Four input voltages"
    )
    parser.add_argument(
        "--plot-live",
        action="store_true",
        help="Enable live programming plot"
    )


    return parser.parse_args()



# Main function to handle the operation based on input arguments
def main():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        args = parse_args()
        # Get the operation (set, reset, read, compute)
        action = args.action

        # Check if the action is valid
        if action in ["set", "reset", "read", "check"] and args.channel is None:
            raise ValueError("Channel is required for this action")

        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Set up the AWG and the oscilloscope
        awg_handle, oscilloscope = initialize_instrument(AWG_Addr, LeCroy_Address)

        # Helper to write SCPI commands
        def write_cmd(cmd: str):
            awg_handle.write(cmd)

        # ------------------- COMPUTE ------------------
        if action == "compute":
            if len(args.voltages) != 4:
                raise ValueError("Compute requires exactly 4 voltage values")

            v1, v2, v3, v4 = args.voltages

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
        channel = args.channel
        if not (1 <= channel <= 8):
            raise ValueError("Channel must be between 1 and 8")


        # ------------------ RESET ------------------
        if action == "reset":
            MAX_ATTEMPTS = 5
            BASE_PULSES  = 10
            PULSE_STEP   = 50       # how much to increase if ineffective
            MIN_DG_RATIO = 0.05      # 5% change threshold
            g_prev = ReadMemristor(awg_handle, oscilloscope, channel)
            time.sleep(0.2)
            pulses = BASE_PULSES
            for attempt in range(1, MAX_ATTEMPTS + 1):

                print(f"[RESET] Attempt {attempt} → Pulses = {pulses}")

                ResetMemristor(awg_handle, channel, No_Pulses=pulses)
                time.sleep(0.5)
                g = ReadMemristor(awg_handle, oscilloscope, channel, 0.1)
                time.sleep(0.2)

                print(f"[RESET] G = {g * 1e6:.2f} µS")

                delta_g = g - g_prev
                dg_ratio = abs(delta_g) / g_prev if g_prev > 0 else 1.0

                if delta_g >= 0:
                    print("[RESET] G increased → escalating reset")
                    pulses += PULSE_STEP

                elif dg_ratio < MIN_DG_RATIO:
                    print("[RESET]  Weak reset → escalating pulses")
                    pulses += PULSE_STEP

                else:
                    print("[RESET]  Reset effective")

                g_prev = g
                if g <= 20e-06: # Reset target
                    print("[RESET] Target low-G reached--> stopping early")
                    break

            print(f"[RESET] Reset sequence finished on channel {channel}")

            write_cmd(f"OUTPut{channel}:STATe 0")
            close_awg_connection(awg_handle)
            return

        # ------------------ READ ------------------
        if action == "read":
            G = ReadMemristor(awg_handle, oscilloscope, channel)
            print("Reading...")
            print(f'Conductance of channel: {channel} =  {G *1e6:.2f} µS Corresponding to {1/G/1e3:.2f} kΩ')
            write_cmd(f"OUTPut{channel}:STATe 0")
            close_awg_connection(awg_handle)
            return

        # ------------------ MemristorCheck------------------
        if action == "check":
            print("Performing Memristor Check...")
            State= Stuck_Check(awg_handle=awg_handle,oscilloscope=oscilloscope, Voltage_Inc=1.5,Time_Period=200e-6, No_Pulses_inc=10, Max_Conductance=250e-06, channel=channel)
            print(f"Memrsitor on channel {channel} is (Stuck_Low, Stuck_High) = {State}")
            #print(f'Conductance of memristor on channel: {channel} =  {G *1e6:.3e} µS Corresponding to {1/G/1e3:.3e} kΩ')
            write_cmd(f"OUTPut{channel}:STATe 0")
            close_awg_connection(awg_handle)
            return
        # ------------------ SET ------------------
        if action == "set":
            Amplitude_inc = 1.0# V (increase G)
            Amplitude_dec = -0.20 # V (decrease G)
            Offset = 0
            Num_Pulses_inc = 20 # Default, later become adaptive
            Num_Pulses_dec = 5 # Default
            Time_Period = 100e-06  # s
            Frequency = 5          # kHz 
            max_conductance = 250e-06  #  (250 µS)
            max_attempts = 20 # importatnt to define attempts in each trial of programming, fewer attempts memristor not responsive, large cause more programming time
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
                "pw":         Time_Period/2
            }
            #=====================Flags=======================================
            Target_reached = False # Flag
            Stability_reads = 3 # Number of reads to confirm stability
            DO_STABILITY_CHECK = True  # <-- change to True if you want stability enforced
            DO_Initial_Reset = True # <-- change to True if you want initial reset before programming
            Do_Initial_check = True # This check is useful if meristor is stuck
            no_progress_counter = 0 
            consecutive_iteration_failures = 0
            NO_PROGRESS_LIMIT = 1   # if not converging for consective 2 iteration
            iteration_np_boost = 1.0 # multiplier for initial NP in each iteration, boosted if iteration failure detected
            exit_policy = args.exit
            EXIT_EARLY = exit_policy == "early" # As the target reached
            EXIT_AFTER_STABILITY = exit_policy == "after-stability" # with stability check
            COMPLETE_ALL_ITERATIONS = exit_policy == "full-iterations" # Complete all iterations
            ENABLE_ADAPTIVE_MONITOR = True   # <-- plug-in switch

            
            # =========================Target/Intended G value ===========================================
            intended_g_value = args.target_uS* 1e-06 # convert µS to S 
            if intended_g_value is None:
                print("Please provide an intended G value in µS for set action.")
                sys.exit(1)
            
            iterations = int(args.iterations)
            if iterations < 1:
                print("Iterations must be at least 1.")
                sys.exit(1)
            
            # ===============================Initail Check==================================
            # This check is very helpful if mersitor is stuck LOW Aso help for fast convergence. 
            if Do_Initial_check:
                print("[PRE-CHECK] Running one-time MemristorCheck()")
                Pulse4StuckLow(awg_handle, channel, 500e-03, 1.0, 10)
                time.sleep(2) # shoer pause after initial check

            
            # =========================== TOLERANCE ===========================
            # Relative tolerance defines the SPEC
            # Absolute floor protects PROGRAMMING only

            # -------- Relative tolerance (depends on G) --------
            if intended_g_value <= 120e-6:
                tol_frac = 0.10          # 10% for low-G
            else:
                tol_frac = 0.08          # 8% for high-G

            # -------- Stability window (UNCHANGED, symmetric) --------
            stability_tol = tol_frac * intended_g_value
            stability_lower = intended_g_value - stability_tol
            stability_upper = intended_g_value + stability_tol

            # -------- Absolute uncertainty floor (PROGRAMMING only) --------
            if intended_g_value < 150e-6:
                g_uncertainty_floor = 10e-6   # larger floor at low-G
            else:
                g_uncertainty_floor = 15e-6    # smaller floor at high-G

            # -------- Programming tolerance width --------
            prog_tol_abs = max(stability_tol, g_uncertainty_floor)

            # -------- Programming window (biased high, For higher stability ) --------
            prog_lower = intended_g_value # - prog_tol_abs,
            if intended_g_value>=150e-6:
                prog_lower = intended_g_value-prog_tol_abs 
                #prog_lower = intended_g_value 

            prog_upper = intended_g_value + prog_tol_abs
            
            # =========================== TOLERANCE BLOCK END ===========================

            print(f"Intended conductance value: {intended_g_value * 1e6:.2f} uS")
            #print(f"Target range: {lower_bound * 1e6:.3e} µS to {upper_bound * 1e6:.3e} µS")   

            # ==============================StuckMonitor =================================== 
            # Initialize before iteration start,object of stuck class (If memristor is stuck perform reset and start again and check hard stuck High/Low)
            stuck_monitor = StuckMonitor(min_effective_dG=20e-6,min_error_reduction=0.5, max_hard_stuck_iter=3 )                    
            stuck_monitor.iteration_fail_count = 0 # to count consecutive iteration failures
            stuck_monitor.iteration_final_G.clear() # to store final G of each iteration for plateau detection

            #================================MAIN LOOP================================
            #====================Here is the main Programming Loop over number of iteration, normally one====================

            for it in range(iterations):
                time.sleep(0.2)  # small delay between iterations
                print(f"Iteration {it + 1}/{iterations}")
                            
                plotter = None # Initialize plotter to None
                # --------- Live plotter ----------
                if args.plot_live:
                    plotter = LivePlot(target_uS=intended_g_value * 1e6,lower_uS=stability_lower * 1e6,upper_uS=stability_upper * 1e6,max_attempts=max_attempts,
                    iteration=it + 1)
                                          
                # ====================Initial reset and stuck high check====================
                stuck_handler = InitialReset(reset_pulses=5,stuck_high_g=600e-06,reset_attempts=1,stuck_attempts = 5) 
                current_g_value, stuck_high = stuck_handler.initial_reset_check(awg_handle=awg_handle,oscilloscope=oscilloscope,channel=channel,do_initial_reset=DO_Initial_Reset)
                if stuck_high:
                    print("[FATAL] Aborting programming due to STUCK HIGH device.")
                    close_awg_connection(awg_handle)
                    sys.exit(1)
   
                # ==================== Detect initial programming mode (Slow/Agressive) ====================
                init_mode, current_g_value  = detect_init_mode(awg_handle=awg_handle,oscilloscope=oscilloscope,channel=channel,current_g_value=current_g_value)
                time.sleep(0.1)
                print(f"[INIT] Initial Conductance: {current_g_value * 1e6:.2f} µS, (R={1/current_g_value/1e3:.2f} kΩ) ")
                is_increasing = current_g_value < intended_g_value
                # ==================== Initialize adaptive response monitor ====================
                if ENABLE_ADAPTIVE_MONITOR:
                    response_monitor = DirectionalResponseMonitor(target_G=intended_g_value,max_wrong_direction=3,max_weak_response=5)
                    response_monitor.reset()
                    response_monitor.prev_G = current_g_value

                #=================== Initialize scaling factors ====================
                alpha, beta = init_alpha_beta(G_init=current_g_value,G_target=intended_g_value,G_max=max_conductance, mode=init_mode,is_increasing=is_increasing)
                G_init = current_g_value # store initial G 
                G_history = [] # to store conductance history
                G_history_inc = [] # to store increase history
                G_history_dec = [] # to store decrease history
                attempts = 0
                target_reached = False # Flag  
                runaway_counter = 0
                RUNAWAY_LIMIT = 3   # How many reset attempts in case of runaway occurs

                #======================= Programming attempts loop ======================
                while attempts < max_attempts:
                    
                    G_history.append(current_g_value) # for plotting
                    stuck_monitor.update(current_g_value) # For stuck check, after each attempt update G value 
                    is_increasing = current_g_value < intended_g_value # increase or decrease
                    # -------- Update scaling factor -----------
                    K, alpha, beta, stuck = update_scaling(IntendedG_value=intended_g_value,G_current=current_g_value,G_target=intended_g_value,G_max=max_conductance,
                        alpha=alpha, beta=beta,G_history=G_history,attempt=attempts,max_attempts=max_attempts,is_increasing=is_increasing)
                    
                    # --------- live update G ----------
                    if plotter:
                        plotter.update(current_g_value * 1e6, K)
                    if plotter and plotter.closed():
                        print("Live plot closed by user — stopping")
                        break

                    # -------Pulse parameters -------
                    # Determine pulse parameters based on increase/decrease
                    cfg = INC if is_increasing else DEC # select INC/DEC config               

                    # -------- Initialize base NP ----------
                    if is_increasing:
                        base_np = init_base_np(target_g=intended_g_value, current_g=current_g_value, is_increasing=is_increasing, mode=init_mode) 
                        base_np = refine_np_near_target(base_np, current_g_value, intended_g_value) # Optional only for increse G(with in 20 % of the target) 
                        # comment out the following line if you don't want iteration-level NP boost even in the beginning iterations 
                        # (can help faster convergence but risk of overshoot if too aggressive) 
                        base_np = int(base_np * iteration_np_boost) # apply iteration-level NP boost if needed

                    else:
                        base_np = init_base_np(target_g=intended_g_value, current_g=current_g_value, is_increasing=is_increasing, mode=init_mode)
                    # round and ensure at least 1 pulse
                    NP_used = int(max(1, round(base_np * K))) 

                    # --------- Determine pulse width --------
                    #PW_used = cfg["pw"] # default fixed PW (not adaptive here)
                    if is_increasing: 
                        PW_used = stepped_pw_inc_dec(current_g_value,intended_g_value,Time_Period,min_pw=10e-6,is_increasing=is_increasing, mode=init_mode,G_history=G_history, G_history_dec=G_history_dec)  
                    else:
                        PW_used = stepped_pw_inc_dec(current_g_value,intended_g_value,Time_Period, min_pw=10e-6,is_increasing=is_increasing,mode=init_mode,G_history=G_history, G_history_dec=G_history_dec)  
                        #PW_used = cfg["pw"] # fixed PW for DEC as well
                    
                    # --------- Determine amplitude --------
                    Amp_used = cfg["amplitude"] # Fixed  
                    # # for fixed amplitude, i.e., 1V just remove the following if else block
                    if is_increasing:
                        if init_mode == "very slow":
                            Amp_used = 0.7
                        elif init_mode == "slow":
                            Amp_used =0.8 if intended_g_value <= 100e-6 else 1.0
                        else:
                            Amp_used = 0.8 if intended_g_value <= 50e-6 else 1.0
                    # if intended_g_value <= 40e-6:
                    #         Amp_used = 1.0
                    #     elif intended_g_value <= 100e-6:
                    #         Amp_used = 1.0
                    #     else:
                    #         Amp_used = 1.0          
                    # else:
                    #     Amp_used = cfg["amplitude"]                         

                    total_np_increase += NP_used if is_increasing else 0 # count only increases 

                    print(f"Attempt {attempts + 1}: Applying {'INC' if is_increasing else 'DEC'} pulse - "
                          f"Amp: {Amp_used} V, PW: {PW_used * 1e6:.2f} µs, NP: {NP_used}, K: {K:.3f}")
                    
                    # --- Send write pulse ----
                    SendWritePulse(awg_handle, Amp_used, PW_used, NP_used, channel)
                     # small settle time    
                    time.sleep(0.2)
                    # Readback, get new conductance
                    previous_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
                    #time.sleep(0.1)
                    
                    print(f"Previous Conductance: { current_g_value * 1e6:.2f} µS, (R={1/current_g_value/1e3:.2f} kΩ)")
                    print(f"Current Conductance: { previous_g_value * 1e6:.2f} µS, (R={1/previous_g_value/1e3:.2f} kΩ) ")

                    current_g_value = previous_g_value # update for next iteration
                    attempts += 1  # increment attempt count
                    # ==================== ADAPTIVE RESPONSE MONITOR ====================
                    if ENABLE_ADAPTIVE_MONITOR:
                        restart_iteration = response_monitor.check(
                            G_current=current_g_value,
                            is_increasing=is_increasing
                        )
                    if restart_iteration:
                        print("[ADAPTIVE] Per-attempt response ineffective --> restarting iteration")
                        break

                    if is_increasing:
                        G_history_inc.append(current_g_value)
                    else:
                        G_history_dec.append(current_g_value)
                    
                    # ===============================Ruaway handling======================================
                    runaway = False
                    # Absolute ceiling protection
                    if current_g_value >= 350e-6:
                        runaway = True
                    # Overshoot protection (INC direction)
                    elif is_increasing and current_g_value > intended_g_value + max_conductance:
                        runaway = True
                    if runaway:
                        runaway_happened = True
                        recovered, abort, current_g_value, runaway_counter = handle_runaway(
                            current_g_value=current_g_value,
                            is_increasing=is_increasing,
                            intended_g_value=intended_g_value,
                            max_conductance=max_conductance,
                            awg_handle=awg_handle,
                            oscilloscope=oscilloscope,
                            channel=channel,
                            runaway_counter=runaway_counter,
                            RUNAWAY_LIMIT=RUNAWAY_LIMIT
                        )
                        if abort:
                            print("[PROGRAM ABORT] Stopping programming due to persistent runaway.")
                            return
                        # runaway but not recovered --> retry
                        if not recovered:
                            continue
                        # runaway recovered → RESET CONTROLLER (same as old code)
                        alpha, beta = init_alpha_beta(
                            G_init=current_g_value,
                            G_target=intended_g_value,
                            G_max=max_conductance, mode=init_mode,
                            is_increasing=current_g_value < intended_g_value
                        )
                        G_history.clear()
                        G_history_dec.clear()
                        G_history_inc.clear()
                        stuck_monitor.reset()
                        if ENABLE_ADAPTIVE_MONITOR:
                            response_monitor.reset()
                            response_monitor.prev_G = current_g_value
                        continue
                  
                   
                    # =============Stability Check Block, Early exit or Exit after stability verified ==========
                    if stability_lower  <= current_g_value <= stability_upper: # if within stability range (with some margin)
                        print(f"[TARGET] G within target range: {current_g_value*1e6:.2f} µS")
                        if ENABLE_ADAPTIVE_MONITOR: # reset monitor if target reached to avoid false trigger on noise in stability reads
                            response_monitor.reset()
                            response_monitor.prev_G = current_g_value

                        if plotter:
                            plotter.update(current_g_value * 1e6, K)
                        # ========== EARLY EXIT ==========
                        if EXIT_EARLY:
                            target_reached = True
                            print("[EXIT] Early exit requested")
                            break
                        
                        # ========== AFTER-STABILITY (but stability disabled, continue to next iteration untill finished) ==========
                        if EXIT_AFTER_STABILITY and not DO_STABILITY_CHECK:
                            target_reached = True
                            print("[EXIT] Stability disabled--> exiting on target")
                            break

                        # ==================== STABILITY-CONTROLLED EXIT ==============
                        if EXIT_AFTER_STABILITY and DO_STABILITY_CHECK and not COMPLETE_ALL_ITERATIONS:
                            stable_reads = 0
                            for j in range(Stability_reads):
                                stable_value = ReadMemristor(awg_handle, oscilloscope, channel, Amplitude=0.15)
                                time.sleep(0.1)
                                # UPDATE CONTROLLER STATE
                                current_g_value = stable_value 
                                if plotter:
                                    plotter.update(stable_value * 1e6, K)
                                if stability_lower <= stable_value <= stability_upper +0.5*prog_tol_abs: # allow some asymmetric margin on upper side for better stability pass, can be removed for stricter stability
                                    stable_reads += 1
                                    print(f"[STABILITY] {j+1}/{Stability_reads}: OK")
                                    print(f"[STABILITY] Stable Conductance: {stable_value * 1e6:.2f} µS, (R={1/stable_value/1e3:.2f} kΩ) ")
                                else:
                                    print("[STABILITY] Failed")
                                    current_g_value = stable_value # update current G for better next iteration (if needed)
                                    break
                                time.sleep(3)  # delay between stability reads
                            if stable_reads == Stability_reads:
                                target_reached = True
                                stable_value_last = ReadMemristor(awg_handle, oscilloscope, channel, Amplitude=0.10)
                                print(f"Final Conductance: { stable_value_last * 1e6:.2f} µS, (R={1/stable_value_last/1e3:.2f} kΩ)")
                                print("[EXIT] Stable target reached")
                                break
                            if attempts == max_attempts - 1:
                                print("[FAILURE] Stability failed on final attempt")
                                target_reached = False
                                break

                            print("[INFO] Stability failed --> retrying")
                            continue

                        # ========== FULL ITERATIONS ==========
                        if COMPLETE_ALL_ITERATIONS:
                            target_reached = True
                            iteration_np_boost = 1.0 # reset any iteration-level NP boost if target reached to avoid excessive pulsing in later iterations
                            print("[INFO] Target reached, continuing iterations as requested")
                            break
   
                # ==================== PLOTTING ====================
                if plotter:
                    plotter.finalize(
                    os.path.join(PLOT_DIR, f"{timestamp}_{intended_g_value * 1e6:.2f}GvsK_Ch{channel}_Iter{it+1}.png"))  
                    print(f"Live plot saved for Iteration {it + 1}.")     
                
                # Target acquired and exit()
                if target_reached and not COMPLETE_ALL_ITERATIONS:

                    print("[PROGRAM EXIT] Target reached")
                    time.sleep(0.5)
                    return

                
                # ====================Stuck Monitor Block! Important=========================
                # If meristor shows stuck behaviour across all attempts, or cosective two iteration
                stuck, reason = stuck_monitor.is_stuck(intended_g_value)
                is_last_iteration = (it == iterations - 1)
                if stuck and not target_reached:
                    print(f"[STUCK] Detected: {reason}")
                    # If this is the final iteration --> exit WITHOUT conditioning 
                    if is_last_iteration:
                        print("[FINAL EXIT] Last iteration reached.")
                        break
                    if reason == "STUCK_LOW":
                        print("[STUCK_LOW] Device unresponsive at low-G running MemristorCheck)")
                        Pulse4StuckLow(awg_handle, channel, 500e-03, 1.0, 10) # 
                        no_progress_counter = 0   # reset counter
                        time.sleep(0.2)
                    elif reason == "HARD_STUCK_LOW":
                        print("[HARD STUCK_LOW] Device unresponsive at low-G running MemristorCheck)")
                        Pulse4StuckLow(awg_handle, channel, 500e-03, 1.5, 20) # 
                        time.sleep(0.2)
                        SendWritePulse(awg_handle,1.5,100e-06,100,channel)
                        time.sleep(0.2)
                        current_g_value = ReadMemristor(awg_handle, oscilloscope, channel)
                        print(f"[HARD_STUCK_LOW] G after recovery: "f"{current_g_value*1e6:.2f} µS")
                        no_progress_counter = 0   # reset counter
                        time.sleep(0.5)
                    elif reason == "PERMANENT_HARD_STUCK":
                        print("[FATAL] Device permanently stuck low — aborting programming")
                        break   # or return / skip channel
                    elif reason == "STUCK_HIGH":
                        print("[FATAL] Device stuck at high conductance.")
                        print("[FATAL] Reset attempts exhausted.") 
                        print("[FATAL] This memristor is not programmable.")
                        print("[ACTION] Mark device as FAILED and stop experiment (Required Hardware reset).")
                        return   # or sys.exit(1)
                    elif reason in  ("NO_PROGRESS_TOWARD_TARGET"):
                        no_progress_counter += 1
                        if no_progress_counter >= NO_PROGRESS_LIMIT:
                            print("[NO_PROGRESS] Consecutive failures ---> conditioning device") 
                            iteration_np_boost = min(iteration_np_boost * 1.25 ,3) # boost NP by 25% for next iteration, cap at 3x to avoid excessive pulsing
                            print(f"[ITERATION BOOST] Increasing initial NP boost to {iteration_np_boost:.2f}")
                            Pulse4StuckLow(awg_handle, channel, 500e-03, 1.0, 20)
                            no_progress_counter = 0
                            time.sleep(0.1)
                        else:
                            print("[NO_PROGRESS] Restarting next iteration without conditioning")
                    else:
                        print("[WARNING STUCK] Ineffective programming (soft reset only)")
                        no_progress_counter = 0

                    stuck_monitor.reset()
                    continue
                # --------------------- If not globally stuck but current iteration shows no progress, count it and condition if needed
                iter_stuck, iter_reason = stuck_monitor.register_iteration_result(
                    target_reached,
                    current_g_value
                )

                if iter_stuck:
                    print(f"[ITERATION_MONITOR] {iter_reason}")
                    ResetMemristor(awg_handle, channel, No_Pulses=10, Amplitude=-0.5) # soft reset for iteration failure
                    time.sleep(0.1)
                    Pulse4StuckLow(awg_handle, channel, 500e-03, 1.0, 20)
                    time.sleep(0.2)
                    stuck_monitor.iteration_fail_count = 0
                    continue
                    


                                                
            print("\n======================================")
            print(f"Total pulses used to INCREASE conductance in {attempts} attempts : {total_np_increase}")
            print("======================================")

            print("Closing the device......")
            for i in range(1, 6):
                write_cmd(f"OUTPut{i}:STATe 0")
            close_awg_connection(awg_handle)
            return

    #except ValueError:
        #print("Invalid input. Unable to establish connection.")
        #sys.exit(1)
    except ValueError as e:
        print("ValueError occurred:")
        print(e)
        raise

if __name__ == "__main__":
    main()
