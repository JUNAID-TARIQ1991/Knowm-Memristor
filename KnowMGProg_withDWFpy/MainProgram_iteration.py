"""
Written by Prof. Raffaele and J.Tariq
Arguments:
Arg0: ModuleName
Arg1: Operation to perform on memristor (read, reset, set) 
       in case of reset:
        Arg3: you can optionally pass the number of reset 
       in case of set you must pass:
            Arg3: required g value 
            Arg4: number of iteration 
Arg2: Select memristor

Purpose:
Reads, Resets, and Set the conductance of a selected memristor, assuming there is one and only one.
"""


# Main function to handle the operation based on input arguments

def main():
    import os
    import sys
    import time
    import csv
    # path = r'C:\Users\Tariq\Data\Analog_Discovery2_Python\Reset_Set_Read\SetCode'
    # sys.path.append(path)  # Add the module path to sys.path

    import dwfpy as dwf
    from SetUp import SetUp
    from SelectMemristor import SelectMemristor
    from ReadMemristor import ReadMemristor
    from ResetMemristor import ResetMemristor
    from SetConductance import SendWriteErasePulses
    from MemristorTest import MemristorCheck
    # from GetMemristorData import get_memristor_data
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
    
    try:
        # Ensure the right number of arguments are passed
        if len(sys.argv) < 3:
            print(
                "Please provide the operation (set, reset, read) and the memristor number.")
            sys.exit(1)

        # Get the operation (set, reset, read)
        action = sys.argv[1].lower()
        # Check if the action is valid
        if action not in ["set", "reset", "read", "check"]:
            print(
                "Invalid operation! Please provide one of the following: set, reset, read.")
            sys.exit(1)

        # Get the memristor number
        input_value = sys.argv[2]
        if input_value.isdigit():
            Memristor = int(input_value)
            if 1 <= Memristor <= 16:
                print(f"Memristor Selected: {Memristor}")
            else:
                print("Input is out of range! Please enter a number between 1 and 16.")
                sys.exit(1)
        else:
            print("Invalid input! Please enter a valid number.")
            sys.exit(1)

        # Open the AnalogDiscovery2 device
        with dwf.AnalogDiscovery2() as device:
            print(f'Found device: {device.name} ({device.serial_number})')
            print(f'DWF Version: {dwf.Application.get_version()}')

            # Set up the AD2
            SetUp(device)

            # Select the desired memristor
            selected_memristor = SelectMemristor(device, Memristor)

            # Load the memristor info from the data file
            # memristor_info = get_memristor_data(file_path, number)

            # Perform the action based on the input argument
            if action == "reset":
                # Check if a reset count is provided as the third argument, if none then reset only once
                if len(sys.argv) == 4:
                    if sys.argv[3].isdigit():
                        reset_count = int(sys.argv[3])
                    else:
                        print("Invalid reset count! Please enter a valid number.")
                        sys.exit(1)
                else:
                    reset_count = 1

                # Perform reset for the specified number of times
                for i in range(reset_count):
                    ResetMemristor(device)
                    # time.sleep(0.1)
                    g = ReadMemristor(device)
                    print(
                        f"conductance value for attempt {i}: {g * 1e6:.3e} µS")
                    print(f"Resetting... (Attempt {i + 1})")
                print(
                    f"Memristor {selected_memristor} reset {reset_count} time(s).")

            elif action == "read":
                g = ReadMemristor(device)
                print("Reading...")
                print(
                    f"Conductance of memristor {selected_memristor} is {g *1e6:.3e} µS corresponding to {1/g/1e3:.3e} kΩ")
                # print(f"Conductance of memristor {selected_memristor} is {g:.3e} µS corresponding to {1/g/1e3:.3e} kΩ")
            
            elif action == "check":
                print("Performing Memristor check and Reset")
                MemristorCheck(device)
                 
                
                
            elif action == "set":
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
                # Check if an intended_g_value is provided as the third argument
                if len(sys.argv) >= 4:
                    try:
                        intended_g_value = float(
                            sys.argv[3]) * 1e-06  # Convert µS to S
                        print(
                            f"Intended conductance value: {intended_g_value * 1e6:.3e} µS")
                    except ValueError:
                        print(
                            "Invalid intended conductance value! Please provide a valid number.")
                        sys.exit(1)
                else:
                    # If no value is passed, raise error
                    print(f"Provide intended g value as a Argument")
                    sys.exit(1)

                # Check if a fourth argument is passed for iterations (interpreted as repeat) value after each repeat store in a file
                if len(sys.argv) == 5:
                    try:
                        # Number of iterations for repeat
                        iterations = int(sys.argv[4])
                    except ValueError:
                        print("Invalid iteration count! Please provide a valid number.")
                        sys.exit(1)
                else:
                    print("Invalid iteration count! Please provide a valid number as a fourth argument.")
                    sys.exit(1)
            

                
                log_directory = r"C:\Users\Tariq\Data\CondProg_with_AD2_Dwfpy\Memristor_Conductance_data"
                log_file = f'{log_directory}\\Memristor_{selected_memristor}_{intended_g_value*1e6:.0f}.txt'
                
                # --- Tolerance (± ?%) ---
                tolerance = 0.08 * intended_g_value
                lower_bound = intended_g_value - tolerance
                upper_bound = intended_g_value + tolerance
                
                # Stability check after reaching target, or No check
                additional_reads = 5
                target_reached = False # Flag
                DO_STABILITY_CHECK = True   # <-- change to True if you want stability enforced

                # ===================== SCALING LOGIC =====================
                def init_alpha_beta(G_init, G_target, G_max, is_increasing):
                    """
                    Smooth gain scheduling:
                    Choose K_des that is linear in G_target, then solve alpha so that
                    K = alpha*(er + gt*ea) matches K_des. Keep beta = alpha*gt.
                    """
                    g0 = G_init / max(G_max, 1e-12) # initial normalized conductance
                    gt = G_target / max(G_max, 1e-12) # target normalized conductance

                    # For now, apply the same K shaping in both directions:
                    dG = abs(G_target - G_init)

                    # Errors at initialization (same definitions used later)
                    if is_increasing:
                        er = (G_target - G_init) / max(G_target, 1e-12) # relative error
                    else:
                        er = (G_init - G_target) / max(G_init, 1e-12) # relative error

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

                    # ---- Linear mapping of target K ----
                    t = (min(max(G_target, Gmin), Gmax_lin) - Gmin) / (Gmax_lin - Gmin)  # [0, 1] clipped factor. 
                    K_des = Kmin + (Kmax - Kmin) * t # desired K, what we want to achieve

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

                                    # --- Scaling factor ---
                    K = alpha * er + beta * ea # combined effect Define K (scaling factor) ********

                    # --- Safety clamps ---
                    K = max(0.1, min(5.0, K))
                    alpha = min(alpha, 5.0)
                    beta  = min(beta, 5.0)

                    return K, alpha, beta, stuck
                        
                        
                for i in range(iterations):
                    print(f"Iteration {i + 1}/{iterations}")
                    
                    # ---- Per-iteration traces for plotting ----
                    attempt_trace = []
                    G_trace_uS = [] 
                    K_trace = []
                    # ======================================================
                    # # --- Pre-reset before each attempt ---, Initial memristor diagnostic check (once per iteration)
                    # ======================================================
                    print("[INIT] Running initial MemristorCheck and reset...")
                    MemristorCheck(device)
                    time.sleep(0.2)

                    # Initial conductance value of memristor
                    current_g_value = ReadMemristor(device)
                    print(
                        f"Initial conductance value: {current_g_value * 1e6:.3e},  Corresponding to {1/current_g_value/1e3:.3e} kΩ")
                        # Set previous value initially to the first read
                    
                    # Continue normally
                    is_increasing = current_g_value < intended_g_value
                    attempts = 0
                    G_history = []  # Initialize an empty list to store conductance values
                    # Initialize a flag to check if target range is reached
                    target_reached = False
                    additional_reads = 5  # Counter for extra reads after reaching target

                    # Initial scaling parameter
                    alpha, beta = init_alpha_beta(G_init=current_g_value,G_target=intended_g_value,G_max=max_conductance,is_increasing=is_increasing)
                    
                    while attempts <= max_attempts:
                        # Append the read value to the conductance_values list
                        G_history.append(current_g_value)
                        # Initial scaling parameters
                        is_increasing = current_g_value < intended_g_value

                            
                        # Generalized scaling factor function to calculate scaling factor
                        K, alpha, beta, stuck = update_scaling(G_current=current_g_value,G_target=intended_g_value,G_max=max_conductance,
                                                           alpha=alpha,beta=beta,G_history=G_history,attempt=attempts,max_attempts=max_attempts,
                                                           is_increasing=is_increasing)
                        # ---- Store values for plotting (before pulse) ----
                        attempt_trace.append(attempts)
                        G_trace_uS.append(current_g_value * 1e6)
                        K_trace.append(K)
                        
                        cfg = INC if is_increasing else DEC # select INC/DEC config
                        base_np = cfg["Num_pulses"] # default
                        # ---- Target-dependent base pulse count override for very log G values only for increase case----
                        if intended_g_value <= 50e-6:
                            base_np = 10
                        elif intended_g_value <= 100e-6:
                            base_np = 25
                        elif intended_g_value <= 200e-6:
                            base_np = 50                 
                        # ---- Make DEC slightly safer ----
                        if not is_increasing:
                            base_np = min(base_np, cfg["Num_pulses"])
                        # Low, MID / HIGH target NO limit
                        NP_used = int(max(1, round(base_np * K))) # no limit on NP

                        PW_used = cfg["pw"]
                        #PW_used = max(10.0e-6, min(1.0, cfg["pw"] * K))
                        Amp_used = cfg["amplitude"]
                        # Determine amplitude based on increase/decrease (Veriable amplitude programming (Not recommended))
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
                        # ---- Send pulse to memritor ---   

                        SendWriteErasePulses(
                                device, Amp_used, PW_used , NP_used, duty_cycle=50.00)

                        
                        time.sleep(0.1)

                        # Read the new conductance value
                        previous_g_value = ReadMemristor(device)
                        # time.sleep(0.1)
                        # Update alpha and beta values based on change in conductance
                        # alpha, beta = update_alpha_beta(alpha, beta, attempts,  current_g_value, previous_g_value, intended_g_value)

                        # Log the updated values
                        print(
                            f"Previous Conductance: { current_g_value * 1e6:.3e} µS, (R={1/current_g_value/1e3:.3e} kΩ)")
                        print(
                            f"Current Conductance: {previous_g_value * 1e6:.3e} µS, (R={1/previous_g_value/1e3:.3e} kΩ) ")

                        # Update  current_g_value for the next iteration

                        current_g_value = previous_g_value
                        # Check range and apply additional read loop
                        if lower_bound <= current_g_value <= upper_bound:
                            target_reached = True
                            stable_reads = 0
                            print(
                                f"Memristor conductance within target range: { current_g_value * 1e6:.3e} µS.")
                            # ----Always  Store successful programming result, without stability 
                            append_success_result(target_uS=intended_g_value * 1e6, programmed_uS=current_g_value * 1e6) 
                             # ---- Skip stability check if not enabled ----
                            if not DO_STABILITY_CHECK:
                                print("Target reached, No stability check, exit()")
                                break   # move directly to next iteration
                            # ---- Optional stability check ----

                            for i in range(additional_reads):
                                stable_value = ReadMemristor(
                                    device)
                                time.sleep(1)
                                if lower_bound <= stable_value <= upper_bound:
                                    stable_reads += 1
                                    print(
                                        f"Stability Check {i + 1}: {stable_value * 1e6:.3e} µS within target range")
                                else:
                                    print(
                                        f"Deviation detected in Stability Check {i + 1}: {stable_value * 1e6:.3e} µS outside target range")
                                    target_reached = False
                                    break  # Exit stability check if deviation occurs
                                # If stable reads are confirmed, break main loop
                            if target_reached and stable_reads >= additional_reads:
                                print(
                                    f"Conductance stable within target range for {additional_reads} reads. Process complete.")
                                break
                                
                                # sys.exit()
                            else:
                                print(
                                    "Stability check failed. Reapplying pulses.")
                                # attempts = 0

                        # Increment attempt counter
                        attempts += 1
                    if not target_reached:
                        print("[FAILURE] Target not reached  ")

            print(f"Closing the device......")
            device.close()
            return

    except ValueError:
        print("Invalid input. Please enter a number.")
        sys.exit(1)


if __name__ == "__main__":
    main()


"""def calculate_scaling_factor(intended_g_value, current_g_value, max_conductance, alpha, beta, is_increasing=True, attempt_history=None):
    # Initialize attempt history if None is provided
    if attempt_history is None:
        attempt_history = []

    # Calculate relative and absolute differences
    if is_increasing:
        difference_ratio = (intended_g_value - current_g_value) / intended_g_value
    else:
        difference_ratio = (current_g_value - intended_g_value) / current_g_value

    absolute_difference = abs(intended_g_value - current_g_value)

    # Adjust scaling factor based on relative and absolute differences
    scaling_factor = alpha * difference_ratio + beta * (absolute_difference / max_conductance)

    # Ensure scaling factor stays within a reasonable range
    scaling_factor = min(5.0, max(0.2, scaling_factor))  # max up to 5.0, min at 0.2

    # Track recent attempts to adjust alpha and beta if no progress
    attempt_history.append(current_g_value)
    if len(attempt_history) > 5:
        attempt_history.pop(0)

    # Check for significant change over last 5 attempts
    if len(attempt_history) == 5:
        avg_change = abs(attempt_history[0] - attempt_history[-1]) / intended_g_value
        if avg_change < 0.01:  # No significant change (e.g., <1% of intended value)
            # Increase alpha and beta adaptively based on current position relative to target
            proximity_ratio = absolute_difference / max_conductance

            # Increase alpha and beta proportionally, more aggressively if farther from target
            alpha += 0.1 * (1 + proximity_ratio)
            beta += 0.05 * (1 + proximity_ratio)
            print(f"Adjusted alpha to {alpha:.2f}, beta to {beta:.2f} due to slow progress.")

    return scaling_factor, alpha, beta, attempt_history
"""
