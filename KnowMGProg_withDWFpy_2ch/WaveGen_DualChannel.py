"""
This Program is to simplt test the waveform generation on both channels
run with Modulename, and pass the required arguments on the terminal
"""

def is_float(value):
    
    try:
        float(value)
        return True
    except ValueError:
        return False



# Main function to handle the operation based on input arguments
def main():
    import sys
    import dwfpy as dwf
    from SetUp import SetUp
    from DriveInputs import AnalogCompute

    try:
        # Ensure the right number of arguments are passed
        if len(sys.argv) < 4:
            print("Usage: <script_name> <v1> <v2>   <time_period>  ")
            sys.exit(1)
        
        # Get inputs from command line arguments
        V1, V2, time_period = sys.argv[1:4]

        if is_float(V1):
            voltage1 = float(V1)
        else:
            print("Wavegen 1 input voltage is out of range!")
            sys.exit(1)
        
        if is_float(V2):
            voltage2 = float(V2)
        else:
            print("Wavegen 2 input voltage is out of range!")
            sys.exit(1)
            
        if is_float(time_period):
            time_period = float(time_period)
        else:
            print("Time period is out of range!")
            sys.exit(1)
     

        # Open the AnalogDiscovery2 device
        with dwf.AnalogDiscovery2() as device:
            print(f"Found device: {device.name} ({device.serial_number})")
            print(f"DWF Version: {dwf.Application.get_version()}")

            # Set up the AD2
            SetUp(device)

            # Generate waveform on both wavegen channels
            print("Generating the waveform on both wavegen channels...")
            AnalogCompute(device, voltage1,voltage2, time_period)

        print(f"Waveform generation completed on both channel.")

    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
