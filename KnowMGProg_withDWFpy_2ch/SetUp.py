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
      
    device.analog_input.trigger.source = dwf.TriggerSource.PC
 
    return None


# # Attempt to open the AnalogDiscovery2 device
# with dwf.AnalogDiscovery2() as device:
#     print(f'Found device: {device.name} ({device.serial_number})')
#     print(f'DWF Version: {dwf.Application.get_version()}')
#     SetUp(device)
#     SelectMemristor(device, 5)