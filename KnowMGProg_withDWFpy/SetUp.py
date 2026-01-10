import dwfpy as dwf
import time  

def SetUp(device):
    import dwfpy as dwf
    import time
    import ctypes
    
    """
    Initializes the device, sets up power supplies, and selects the memristor.

    Arguments:
    device -- the AnalogDiscovery2 device handle.
    Returns:
    
    0 if no error
    -1 if error
    """
    
    

    # 25.10.2024
    #
    # Add code to disable autoconfigure 
    #device.reset()
    #device.auto_reset = True #reset on exit 
    device.auto_configure = True
 
    #ret = dwf.api.dwf_enum_config_info( index, dwf.api.DECI_ANALOG_IN_BUFFER_SIZE       )
    
    ret = dwf.bindings.dwf_enum_config(0)
 
    #print ( f'ret = {ret}' )

    # Drives logical level low to the DIO pins (digital output)
    # deselect all memristors    
    pattern = device.digital_output
    #pattern.trigger.source = dwf.TriggerSource.PC
    #pattern.reset()
    #time.sleep(0.05)
    for i in range(16):  # Use the length of pattern to avoid out of range
        pattern[i].setup_constant('low', start=True)
        time.sleep(0.05)   
    # Set the power supplies to ±5V    
    device.supplies.positive.setup(voltage=5.0)
    device.supplies.negative.setup(voltage=-5.0)
    device.supplies.master_enable = True
    time.sleep(0.1)
    # Trigger source
    device.analog_output[1].setup(start=False) # channel 1 Disabled
    device.analog_output[0].limitation = -1.0 # Set the voltage limitation to -1V or the maximum allowed
    device.analog_output[0].trigger.source = dwf.TriggerSource.PC #Set Trigger source to PC 
    
    device.analog_input.trigger.source = dwf.TriggerSource.PC
    


    return None


# # # Attempt to open the AnalogDiscovery2 device
# with dwf.AnalogDiscovery2() as device:
#     print(f'Found device: {device.name} ({device.serial_number})')
#     print(f'DWF Version: {dwf.Application.get_version()}')
#     #SetUp(device)
#     device.analog_output[0].setup(enabled=False)
#     device.analog_output[1].setup(enabled=False)
    
#     while True:
#         user_input = input("Type 'quit' to stop: ")
#         if user_input.lower() == 'quit':
#             print("Exiting loop.")
#             break
#         else:
#             print("You typed:", user_input)
#             time.sleep(2)  # Wait for 2 seconds before asking again
            
# #     SelectMemristor(device, 5)