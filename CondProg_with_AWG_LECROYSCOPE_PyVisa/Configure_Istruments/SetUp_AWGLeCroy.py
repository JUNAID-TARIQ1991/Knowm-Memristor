import pyvisa
import math
import numpy as np
import matplotlib.pyplot as plt


def initialize_instrument(AWG_addr, LeCroy_address):
    """
    Initializes the AWG instrument and returns the VISA handle.
    
    Parameters:
    - instrument_addr: VISA address of the AWG instrument.
    
    Returns:
    - A VISA resource handle to the AWG.
    """
    try:
        # Initialize VISA resource manager
        rm = pyvisa.ResourceManager()

        # Connect to the AWG
        AWG = rm.open_resource(AWG_addr)
        oscilloscope = rm.open_resource(LeCroy_address)

        # Set the VISA timeout
        AWG.timeout = 60000  # Timeout in milliseconds (60 seconds)

        # Identify the AWG instrument
        print("You are connected to the AWG instrument:\n", AWG.query("*IDN?"))
        # Reset the AWG instrument
        AWG.write("*RST")
        # Set the VISA timeout
        oscilloscope.timeout = 60000  # Timeout in milliseconds (60 seconds)
        #oscilloscope.clear()  # empty VISA buffer (very important!)  

        # Identify the  Oscillocope instrument
        #print("You are connected to the Oscilloscope:\n",
              #oscilloscope.query("*IDN?"))

        # AWG and OSC. handle
        return AWG, oscilloscope
    except Exception as e:
        print("Error: instrument communication: ", e)
        return None


def flush_errors(AWG):
    """
    Flushes all errors from the AWG.
    """
    def get_err_num(err_string):
        try:
            # Extract substring before the first comma
            substring = err_string.split(',')[0]
            # Convert the substring to a number (float or int)
            number = float(substring) if '.' in substring else int(substring)
            return number
        except ValueError:
            # Handle cases where conversion fails
            return None

    err = AWG.query('SYST:ERR?')
    print(err)
    # Query for errors until receive: "0,No error"
    while get_err_num(err) != 0:
        err = AWG.query('SYST:ERR?')
        print(err)


def Reset_Instrument(AWG):
    AWG.write("*RST")
    # print("*RST")


def close_awg_connection(AWG):
    """
    Closes the connection to the AWG.

    Parameters:
    - AWG: VISA resource handle for the AWG.
    """
    if AWG is not None:

        AWG.close()
        pyvisa.ResourceManager().close()

        print("Connection to AWG closed.")
