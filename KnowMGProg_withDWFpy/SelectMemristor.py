def SelectMemristor(device, memristor_num):
    import dwfpy as dwf
    import time

    """
    Arguments:
    device -- the AnalogDiscovery2 device handle.
    memristor_num -- integer (1 to 16), selects the memristor.

    Purpose:
    Selects one specific memristor, deselects all the others. If an out of range memristor is specified, all are deselected.
    
    Returns:
    The selected memristor or None, if none is selected.
    """
    
    # Setup the DIO pins (digital output) 
    pattern = device.digital_output
    #pattern.trigger.source = dwf.TriggerSource.PC
    for i in range(16):  # Use the length of pattern to avoid out of range
        pattern[i].setup_constant('low', start=True)
        time.sleep(0.05)
    selectedmemristor = memristor_num - 1
    if selectedmemristor < 0 or selectedmemristor > 15:
        print("Invalid memristor number. Please choose a number between 1 and 16.")
        return None, None
    pattern[selectedmemristor].setup_constant('high', start=True)  # Select memristor
    
    return memristor_num
