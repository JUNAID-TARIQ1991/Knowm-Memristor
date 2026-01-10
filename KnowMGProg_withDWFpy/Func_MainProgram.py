# """
# Arguments:
# Arg0: ModuleName
# Arg1: Operation to perform on memristor (read, reset, set) 
#        in case of reset:
#         Arg3: you can optionally pass the number of reset 
#        in case of set you must pass:
#             Arg3: required g value 
#             Arg4: number of iteration 
# Arg2: Select memristor

# Purpose:
# Reads, resets, and sets the conductance of a selected memristor, assuming there is one and only one.
# """
# # Main function to handle the operation based on input arguments
# def main():
#     import os
#     import sys
#     import time
#     path = r'C:\Users\Tariq\Data\Analog_Discovery2_Python\Reset_Set_Read\SetCode'    
#     sys.path.append(path)  # Add the module path to sys.path

#     import dwfpy as dwf
#     from SetUp import SetUp
#     from SelectMemristor import SelectMemristor
#     from ReadMemristor import ReadMemristor
#     from ResetMemristor import ResetMemristor
#     from SetConductance import SendWriteErasePulses
#     from GetMemristorData import get_memristor_data


#     try:
#         # Ensure the right number of arguments are passed
#         if len(sys.argv) < 3:
#             print("Please provide the operation (set, reset, read) and the memristor number.")
#             sys.exit(1)

#         # Get the operation (set, reset, read)
#         action = sys.argv[1].lower()
#         # Check if the action is valid
#         if action not in ["set", "reset", "read"]:
#             print("Invalid operation! Please provide one of the following: set, reset, read.")
#             sys.exit(1)

#         # Get the memristor number
#         input_value = sys.argv[2]
#         if input_value.isdigit():
#             Memristor = int(input_value)
#             if 1 <= Memristor <= 16:
#                 print(f"Memristor Selected: {Memristor}")
#             else:
#                 print("Input is out of range! Please enter a number between 1 and 16.")
#                 sys.exit(1)
#         else:
#             print("Invalid input! Please enter a valid number.")
#             sys.exit(1)

#         # Open the AnalogDiscovery2 device
#         with dwf.AnalogDiscovery2() as device:
#             print(f'Found device: {device.name} ({device.serial_number})')
#             print(f'DWF Version: {dwf.Application.get_version()}')

#             # Set up the AD2
#             SetUp(device)

#             # Select the desired memristor
#             selected_memristor = SelectMemristor(device, Memristor)
            
#             # Load the memristor info from the data file
#             #memristor_info = get_memristor_data(file_path, number)

#             # Perform the action based on the input argument
#             if action == "reset":
#                 # Check if a reset count is provided as the third argument, if none then reset only once
#                 if len(sys.argv) == 4:
#                     if sys.argv[3].isdigit():
#                         reset_count = int(sys.argv[3])
#                     else:
#                         print("Invalid reset count! Please enter a valid number.")
#                         sys.exit(1)
#                 else:
#                     reset_count = 1

#                 # Perform reset for the specified number of times
#                 for i in range(reset_count):
#                     ResetMemristor(device)
#                     time.sleep(0.1)
#                     g = ReadMemristor(device)
#                     print(f"conductance value for attempt {i}: {g * 1e6:.3e} µS")
#                 print(f"Memristor {selected_memristor} reset {reset_count} time(s).")

#             elif action == "read":
#                 g = ReadMemristor(device)
#                 print("Reading...")
#                 print(f"Conductance of memristor {selected_memristor} is {g *1e6:.3e} µS corresponding to {1/g/1e3:.3e} kΩ")
#                 #print(f"Conductance of memristor {selected_memristor} is {g:.3e} µS corresponding to {1/g/1e3:.3e} kΩ")
#             elif action == "set":
#                 voltage_inc= -1.00
#                 voltage_dec= 0.25
#                 time_period=300e-06
#                 no_pulses=500.00
#                 duty_cycle=50.00
#                 max_attempts = 10 # number of attempts to achieve intended value
#                 max_conductance = 200e-06 # The maximum value of g we want to achieve
#                 # Check if an intended_g_value is provided as the third argument
#                 if len(sys.argv) >= 4:
#                     try:
#                         intended_g_value = float(sys.argv[3]) * 1e-06  # Convert µS to S
#                         print(f"Intended conductance value: {intended_g_value * 1e6:.3e} µS")
#                     except ValueError:
#                         print("Invalid intended conductance value! Please provide a valid number.")
#                         sys.exit(1)
#                 else:
#                     #If no value is passed, raise error
#                     print(f"Provide intended g value as a Argument")
#                     sys.exit(1)

   
#                 # Attempt to set conductance value
#                 ReadGValue = ReadMemristor(device) #inital g value of memristor
#                 print(f"Initially, memristor has {ReadGValue*1e6:.3e} µS.")
#                 tolerance = 0.15 * intended_g_value  # Set a 10% tolerance
#                 lower_bound = intended_g_value - tolerance
#                 upper_bound = intended_g_value + tolerance
                
#                 attempts = 0

#                 while attempts <= max_attempts:
#                     print(f"conductance value for attempt {attempts}: {ReadGValue * 1e6:.3e} µS")
                    
#                     if ReadGValue < intended_g_value:
#                         print(f"Increasing the conductance..... attempt {attempts}")
#                         if lower_bound <= ReadGValue <= upper_bound:
#                             print(f"Memristor conductance within target range: {ReadGValue * 1e6:.3e} µS.")
#                             break

#                         # We should implement more dynamic approach
#                         # alpha and beta are scaling factor, csn be adjusted on each repeatation
#                         def calculate_scaling_factor_increase(intended_g_value, ReadGValue, max_conductance, alpha=0.8, beta=0.8):
#                             # Calculate the relative and absolute differences
#                             difference_ratio = (intended_g_value - ReadGValue) / intended_g_value
#                             absolute_difference = abs(intended_g_value - ReadGValue)
    
#                             # Adjust the scaling factor based on both relative and absolute differences
#                             scaling_factor = alpha * difference_ratio + beta * (absolute_difference / max_conductance)
    
#                             # Ensure scaling factor stays within a reasonable range (0, 1) or (0, 2)?
#                             return min(3, max(0.1, scaling_factor))  # Ensuring the scaling factor isn't too small or too large 
                        
#                         # Calculate the scaling factor for each attempt
#                         scaling_factor_inc = calculate_scaling_factor_increase(intended_g_value, ReadGValue, max_conductance) 
                        
#                         #Increase train of pulse  
#                         SendWriteErasePulses(device, voltage_inc , time_period , no_pulses*scaling_factor_inc  , duty_cycle* 1.5 )  
                                              
#                         time.sleep(0.1) 
#                         ReadGValue = ReadMemristor(device)
#                         time.sleep(0.1)
#                         attempts += 1 
                        
#                     elif ReadGValue > intended_g_value:
#                         print(f"Decreasing the conductance.....{attempts}")
#                         if lower_bound <= ReadGValue <= upper_bound:
#                             print(f"Memristor conductance within target range: {ReadGValue * 1e6:.3e} µS.")
#                             break
#                         # Calculate the scaling factor for each attempt
#                         def calculate_scaling_factor_decrease(intended_g_value, ReadGValue, max_conductance, alpha=0.4, beta=0.4):
#                             # Calculate the relative and absolute differences
#                             difference_ratio = (ReadGValue - intended_g_value) / ReadGValue
#                             absolute_difference = abs(intended_g_value - ReadGValue)
    
#                             # Adjust the scaling factor based on both relative and absolute differences
#                             scaling_factor = alpha * difference_ratio + beta * (absolute_difference / max_conductance)
    
#                             # Ensure scaling factor stays within a reasonable range (0, 1]
#                             return min(0.5, max(0.1, scaling_factor))  # Ensuring the scaling factor isn't too small or too large
                        
#                         scaling_factor_dec = calculate_scaling_factor_decrease(intended_g_value, ReadGValue, max_conductance) 
#                         # decrease train of pulse
#                         SendWriteErasePulses(device, voltage_dec ,time_period, no_pulses*scaling_factor_dec, duty_cycle )    
                         
#                         time.sleep(0.1)
#                         ReadGValue = ReadMemristor(device)
#                         attempts += 1 
#                 print(f"conductance value after final  attempt {attempts}: {ReadGValue * 1e6:.3e} µS")
#                 print(f"All {attempts}  attempts completed.")
#             #close the device
#             print("Closing the device........")
#             device.close()
                

#     except ValueError:
#         print("Invalid input. Please enter a number.")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()


