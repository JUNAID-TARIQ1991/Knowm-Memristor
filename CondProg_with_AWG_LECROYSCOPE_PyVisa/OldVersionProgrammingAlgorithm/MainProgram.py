"""
Written by Prof. Raffaele and J. Tariq
This Module generate pulses on Multiple channels for read and set memristor conductance
Read Conductance :  ModuleName read 1
To set the conductance on memristor
    usage:  ModuleName set 1 100 1 
    Arg2:set: operation to perform on memristor
    Arg3 1: channel 
    Arg4 100: Intended G value

"""

# Main function to handle the operation based on input arguments
def main():
    import os
    import sys
    import time

    import dwfpy as dwf
    from SetUp import SetUp
    import argparse
    from ReadMemristor import ReadMemristor
    from ResetMemristor import ResetMemristor
    from Set_G_Channel import SendWritePulse
    from SetUp_AWG import initialize_instrument
    #from SetUp_LeCroy import initialize_Oscilloscope
    from Configure_AWG import Generate_waveform
    from Configure_LecroyOsc import configure_oscilloscope
    from datetime import datetime
    from DriveInputs_AWG import AnalogCompute
    from SetUp_AWG import close_awg_connection
    AWG_Addr = "TCPIP0::172.16.9.59::inst0::INSTR"
    LeCroy_Address = "TCPIP0::172.16.13.144::INSTR"

    #AWG_Addr = "TCPIP0::172.16.0.3::inst0::INSTR"
    #LeCroy_Address = "TCPIP0::172.16.13.43::INSTR"
    


    #try:
    # Ensure the correct number of arguments are passed
    if len(sys.argv) <2:
        print("Please provide the operation <set, reset, read, compute>.")
        sys.exit(1)

    # Get the operation (set, reset, read)
    action = sys.argv[1].lower()

    # Check if the action is valid
    if action not in ["set", "reset", "read", "compute"]:
        print("Invalid operation! Please provide one of the following: set, reset, read or compute.")
        sys.exit(1)

    timestamp = datetime.now()
    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_timestamp)  # Example: 2025-02-17 12:34:5


    # Set up the AT_AWG, #setup the Lecroy Oscilloscope
    awg_handle, oscilloscope = initialize_instrument(AWG_Addr, LeCroy_Address)


    def write_cmd(cmd):
        awg_handle.write(cmd)
    # Perform the action based on the input argument for AWG

    # Handle the `compute` action
    if action == "compute":
    # Parse the voltages from terminal arguments (starting from the second argument)
        if len(sys.argv) < 6:
            print("Please provide 4 voltage values for compute action.")
            sys.exit(1)

        # Parse the voltages (the arguments after 'compute')
        v1, v2, v3, v4 = map(float, sys.argv[2:6])

        print("Performing compute action...")

        I = AnalogCompute(awg_handle,oscilloscope, v1, v2, v3, v4)
        print(f'Average I = {I:.2e} A')
        time.sleep(0.2)
        print(f"Closing the AD2 device......")
            
        for i in range(1, 5):      
            write_cmd(f"OUTPut{i}:STATe 0")
        close_awg_connection(awg_handle)
        sys.exit(0)

    # For reset, read and set we need, Get the Channel number
    input_value = sys.argv[2]
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

    # perform reset operation on memristor
    if action == "reset":             
        # Check if a reset count is provided as the third argument, if none then reset only once
        if len(sys.argv) == 4:
            if sys.argv[3].isdigit():
                reset_count = int(sys.argv[3])
            else:
                print("Invalid reset count! Please enter a valid number.")
                sys.exit(1)
        else:
            reset_count = 5

        # Perform reset for the specified number of times
        for i in range(reset_count):
            ResetMemristor(awg_handle, channel)
            #time.sleep(0.1)
            g = ReadMemristor(awg_handle,oscilloscope, channel)
            print(f"conductance value for attempt {i}: {g * 1e6:.3e} µS")
            print(f"Resetting... (Attempt {i + 1})")
        print(
            f"Memristor on channel  {channel} reset {reset_count} time(s).")
        # Check if a reset count is provided as the third argument, if none then reset only once
        ResetMemristor(awg_handle, channel)
        print(f"Reset pulses generated on channel: {channel}")
        #Closing the connection
        write_cmd(f"OUTPut{channel}:STATe 0")
        close_awg_connection(awg_handle)

    #Reading the Conductance
    elif action == "read":

        G = ReadMemristor(awg_handle,oscilloscope, channel)          
        print("Reading...")
        print (f'Conductance of channel: {channel} =  {G *1e6:.3e} µS Corresponding to {1/G/1e3:.3e} kΩ')                 
        # print(f"Conductance of memristor {selected_memristor} is {g:.3e} µS corresponding to {1/g/1e3:.3e} kΩ")rint(f"Read pulses generated on channel {channel}.")
                
        write_cmd(f"OUTPut{channel}:STATe 0")
        close_awg_connection(awg_handle)

    # Read and increase or decrease the conductance
    elif action == "set":
        Amplitude = 1.0 # Amplitude in volts for each channel to increase G
        Amplitude_dec =-0.25 # Amplitude in volts for each channel to decrease G
        
        Offset = 0  # Offset in volts  
        Num_Pulses = 50 # Number of pulses to generate for increase the G
        Num_Pulses_dec = 100 # Number of pulses to generate for decreaae the G
        pulses_applied=0
        Time_Period = 200e-06 # Time period of the wave
        Frequency = 5 # Frequency in kHz                    
        max_conductance = 400e-06
        
        max_attempts = 20
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
            
                for i in range(iterations):
                    print(f"Iteration {i + 1}/{iterations}")

                    # Initial conductance value of memristor
                    ReadGValue = ReadMemristor(awg_handle,oscilloscope, channel)
                
                    print(
                        f"Initial conductance value: {ReadGValue * 1e6:.3e},  Corresponding to {1/ReadGValue/1e3:.3e} kΩ")
                    current_g_value = ReadGValue  # Set previous value initially to the first read

                    # Set tolerance (10%) 0r 15%
                    tolerance = 0.1 * intended_g_value
                    lower_bound = intended_g_value - tolerance
                    upper_bound = intended_g_value + tolerance
                    attempts = 0
                    conductance_values = []  # Initialize an empty list to store conductance values

                    # Initial scaling parameter
                    alpha, beta = 1.0, 1.0  # Initial values Dynamic Scaling factor
                    # print(f"{alpha},{beta}")
                    
                    # Initialize a flag to check if target range is reached
                    target_reached = False
                    additional_reads = 5  # Counter for extra reads after reaching target

                    while attempts <= max_attempts:
                        # Append the read value to the conductance_values list
                        conductance_values.append(current_g_value)

                        # Generalized scaling factor function to calculate scaling factor
                        def calculate_scaling_factor(intended_g_value, ReadGValue, max_conductance, alpha, beta, is_increasing=True):

                            #  You can also fixed these parameter or initialize alpha and beta depends how far you are from target ! You can update these parameter based on memristor behaviour
                            #This is first version of code
                            
                            if is_increasing and ReadGValue < 50 and intended_g_value <= 50 * 1e-06:
                                alpha, beta = 1.0, 1.0
                            elif is_increasing and ReadGValue < 50 and intended_g_value < 100 * 1e-06:
                                alpha, beta = 1.5, 1.5
                            elif is_increasing and ReadGValue < 50 and intended_g_value <= 150 * 1e-06:
                                alpha, beta = 1.75, 1.75
                            elif is_increasing and ReadGValue < 50 and intended_g_value > 150 * 1e-06:
                                alpha, beta = 2.0, 2.0
                            else:  # Decreasing
                                alpha, beta = 1.0, 1.0

                            # update the alpha value if there is no significanr change in G! or fine tunning in each attempt  
                            
                            if attempts > 0 and abs(conductance_values[attempts] - conductance_values[attempts-1]) < 10.0 * 1e-06:
                                print(
                                    "No significant change detected.")
                                alpha = max(
                                    alpha, (alpha + 0.5 + (attempts/max_attempts)))
                                beta = max(
                                    beta, (beta + 0.5 + (attempts/max_attempts)))

                            # Main  Calculation of scaling factor
                            if is_increasing:
                                difference_ratio = (intended_g_value - current_g_value) / intended_g_value
                            else:
                                difference_ratio = (current_g_value - intended_g_value) / current_g_value

                            absolute_difference = abs(
                                intended_g_value - current_g_value)

                            scaling_factor = round(
                                alpha * difference_ratio + beta * (absolute_difference / max_conductance), 2)

                            # Ensure the minimum limit of the scaling factor 
                            if is_increasing and intended_g_value >= 150 * 1e-06:
                                # max up to 5.0, min at 1.0
                                return min(5.0, max(0.5, scaling_factor))
                            elif is_increasing and intended_g_value >= 100 * 1e-06:
                                # max up to 5.0, min at 0.5
                                return min(5.0, max(0.3, scaling_factor))
                            elif is_increasing and intended_g_value < 100 * 1e-06:
                                # max up to 5.0, min at 0.1
                                return min(5.0, max(0.1, scaling_factor))

                            else:       # if decreasing
                                return min(3.0, max(0.1, scaling_factor))

                        #****************************************INCREASE CONDUCTANCE ******************************
                        # Case 1 Increase conductance
                        if current_g_value < intended_g_value:
                            print(
                                f"Increasing the conductance..... attempt {attempts}")

                            scaling_factor = calculate_scaling_factor(
                                intended_g_value,  current_g_value, max_conductance, alpha, beta, is_increasing=True)
                            #print(f"Scaling Factor: {scaling_factor}")
                            SendWritePulse(awg_handle, Amplitude, Time_Period * scaling_factor , Num_Pulses* scaling_factor,channel )
                            #pulses_applied += Num_Pulses*scaling_factor
                            #print(f"Pulses applied {pulses_applied}")

                        #****************************************DECREASE CONDUCTANCE*********************************
                        # Case 2 Decrease conductance
                        elif current_g_value > intended_g_value:
                            print(
                                f"Decreasing the conductance..... attempt {attempts}")

                            scaling_factor = calculate_scaling_factor(
                                intended_g_value,  current_g_value, max_conductance, alpha, beta, is_increasing=False)
                            #print(
                                #f"Scaling Factor: {scaling_factor}")
                            
                            SendWritePulse(awg_handle, Amplitude_dec, Time_Period , Num_Pulses_dec* scaling_factor,channel )

                        # Slight slower attemp, increase stability of g value
                        time.sleep(0.05)

                        # Read the new conductance value
                        previous_g_value = ReadMemristor(awg_handle,oscilloscope, channel)

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

                            for i in range(additional_reads):
                                stable_value =ReadMemristor(awg_handle,oscilloscope, channel)
                                time.sleep(2)
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
                            if stable_reads >= additional_reads:
                                print(
                                    f"Conductance stable within target range for {additional_reads} reads. Process complete.")
                                return True
                                break
                                # sys.exit()
                            else:
                                print(
                                    "Stability check failed. Reapplying pulses.")
                                # attempts = 0

                        
                        # Increment attempt counter
                        attempts += 1
                    
                    # If the loop ends, it means max attempts reached without success (Close all connection and return False)
                    if not target_reached:
                        print(f"Stability check failed after {max_attempts} attempts.")
                        print(f"Closing the device......")
                        #Close AWG 
                        for i in range(1, 5):      
                            write_cmd(f"OUTPut{i}:STATe 0")
                        close_awg_connection(awg_handle)
                        #device.close()

                        return False  # Return False if stability wasn't reached

                    print(
                        f"All {iterations} iterations completed.")

            except ValueError:
                print(
                    "Invalid iteration count! Please provide a valid number.")
                sys.exit(1)
        # if  repeat is none, this loop will execute
        else:
            print(
                "Invalid iteration count! Please provide a valid number as afourth argument .")
            sys.exit(1)
        print(f"Closing the device......")
        write_cmd(f"OUTPut{channel}:STATe 0")
        close_awg_connection(awg_handle)


    #except ValueError:
        #print("Invalid input. Unable to eastablish connection.")
       # sys.exit()
    
if __name__ == "__main__":
    main()
