"""
Written by Prof. Raffaele and J. Tariq
This Module generate pulses on both channels for read and set memristor conductance
usage:  ModuleName set 1 100 1 
Arg2:set: operation to perform on memristor
Arg3 1: channel 
Arg4 100: Intended G value
Arg5: iteration (must be atleat one)
"""

# Main function to handle the operation based on input arguments
def main():
    import os
    import sys
    import time

    import dwfpy as dwf
    from SetUp import SetUp
    from SelectMemristor import SelectMemristor
    from ReadMemristor import ReadMemristor
    from ResetMemristor import ResetMemristor
    from Set_G_Dual import SendWritePulse

    try:
        # Ensure the correct number of arguments are passed
        if len(sys.argv) <= 2:
            print("Please provide the operation <set, reset, read> <channel> .")
            sys.exit(1)

        # Get the operation (set, reset, read)
        action = sys.argv[1].lower()

        # Check if the action is valid
        if action not in ["set", "reset", "read"]:
            print("Invalid operation! Please provide one of the following: set, reset, read.")
            sys.exit(1)

        # Get the Channel number
        input_value = sys.argv[2]
        if input_value.isdigit():
            channel = int(input_value)
            if 0 <= channel <= 1:
                print(f"Channel Selected: {channel}")
            else:
                print("Input is out of range! Please enter channel number between 0 and 1.")
                sys.exit(1)
        else:
            print("Invalid input! Please enter a valid Channel number.")
            sys.exit(1)

        # Open the AnalogDiscovery2 device
        with dwf.AnalogDiscovery2() as device:
            print(f"Found device: {device.name} ({device.serial_number})")
            print(f"DWF Version: {dwf.Application.get_version()}")

            # Set up the Analog Discovery 2 device
            SetUp(device)

            # Perform the action based on the input argument
            if action == "reset":
                # Check if a reset count is provided as the third argument, if none then reset only once
            
                ResetMemristor(device, channel)
                print(f"Reset pulses generated on channel {channel}")
            
            #Reading the Conductance
            elif action == "read":
                g = ReadMemristor(device, channel)
                print("Reading...")
                print(f"Conductance of memristor on channel  {channel} is {g *1e6:.3e} µS corresponding to {1/g/1e3:.3e} kΩ")
                # print(f"Conductance of memristor {selected_memristor} is {g:.3e} µS corresponding to {1/g/1e3:.3e} kΩ")rint(f"Read pulses generated on channel {channel}.")

            elif action == "set":
                voltage_inc = 1.0 #Driving the memristor Anode
                voltage_dec = -0.3
                time_period = 200e-06
                no_pulses = 200.00  # You can change the no. of pulses based on memristor behaviour
                duty_cycle = 50.00
                max_attempts = 40  # number of attempts to achieve intended value
                max_conductance = 250e-06  # The maximum value of g we want to achieve
                
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
                            ReadGValue = ReadMemristor(device, channel)
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

                                    # initialize alpha nad beta depends how far you are from target ! You can update these parameter based on memristor behaviour
                                    #This is first version of code
                                    if is_increasing and ReadGValue < 50 and intended_g_value <= 50 * 1e-06:
                                        alpha, beta = 0.5, 0.5
                                    elif is_increasing and ReadGValue < 50 and intended_g_value < 100 * 1e-06:
                                        alpha, beta = 1.0, 1.0
                                    elif is_increasing and ReadGValue < 50 and intended_g_value <= 150 * 1e-06:
                                        alpha, beta = 1.0, 1.5
                                    elif is_increasing and ReadGValue < 50 and intended_g_value > 150 * 1e-06:
                                        alpha, beta = 1.0, 2.0
                                    else:  # Decreasing
                                        alpha, beta = 1.0, 2.0

                                    # update the alpha value if there is no significanr change! or fine tunning in each attempt
                                    if attempts > 0 and abs(conductance_values[attempts] - conductance_values[attempts-1]) < 10.0 * 1e-06:
                                        print(
                                            "No significant change detected.")
                                        alpha = max(
                                            alpha, (alpha + 0.5 + (attempts/max_attempts)))
                                        beta = max(
                                            beta, (beta + 0.5 + (attempts/max_attempts)))

                                    # Calculate scaling factor
                                    if is_increasing:
                                        difference_ratio = (intended_g_value - current_g_value) / intended_g_value
                                    else:
                                        difference_ratio = (current_g_value - intended_g_value) / current_g_value

                                    absolute_difference = abs(
                                        intended_g_value - current_g_value)

                                    scaling_factor = round(
                                        alpha * difference_ratio + beta * (absolute_difference / max_conductance), 2)

                                    # Ensure scaling factor stays within a reasonable range
                                    if is_increasing and intended_g_value >= 150 * 1e-06:
                                        # max up to 3.0, min at 1.0
                                        return min(3.0, max(0.5, scaling_factor))
                                    elif is_increasing and intended_g_value >= 100 * 1e-06:
                                        # max up to 3.0, min at 0.5
                                        return min(3.0, max(0.3, scaling_factor))
                                    elif is_increasing and intended_g_value < 100 * 1e-06:
                                        # max up to 3.0, min at 0.1
                                        return min(3.0, max(0.05, scaling_factor))

                                    else:       # if decreasing
                                        return min(5.0, max(0.1, scaling_factor))

                                # Case 1 Increase conductance
                                if current_g_value < intended_g_value:
                                    print(
                                        f"Increasing the conductance..... attempt {attempts}")

                                    scaling_factor = calculate_scaling_factor(
                                        intended_g_value,  current_g_value, max_conductance, alpha, beta, is_increasing=True)
                                    print(
                                        f"Scaling Factor: {scaling_factor}")
                                    SendWritePulse(device,voltage_inc ,time_period * scaling_factor,no_pulses* scaling_factor,channel )

                                # Case 2 Decrease conductance
                                elif current_g_value > intended_g_value:
                                    print(
                                        f"Decreasing the conductance..... attempt {attempts}")

                                    scaling_factor = calculate_scaling_factor(
                                        intended_g_value,  current_g_value, max_conductance, alpha, beta, is_increasing=False)
                                    print(
                                        f"Scaling Factor: {scaling_factor}")
                                    SendWritePulse(
                                        device, voltage_dec, time_period * scaling_factor, no_pulses * scaling_factor, channel)

                                # Slight slower attemp, increase stability of g value
                                time.sleep(0.5)

                                # Read the new conductance value
                                previous_g_value = ReadMemristor(device,channel)

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
                                        stable_value = ReadMemristor(
                                            device,channel)
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
                                        break
                                        # sys.exit()
                                    else:
                                        print(
                                            "Stability check failed. Reapplying pulses.")
                                        # attempts = 0

                                # Increment attempt counter
                                attempts += 1

                            

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
            device.close()


    except ValueError:
        print("Invalid input. Please enter a number.")
        sys.exit(1)


if __name__ == "__main__":
    main()
