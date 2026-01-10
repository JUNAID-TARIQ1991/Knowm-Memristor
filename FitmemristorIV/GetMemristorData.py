import pandas as pd

# Function to retrieve memristor data
def get_memristor_data(file_path, memristor_num):
    """
    Retrieves data for a given memristor number from the .dat file.

    Args:
        file_path (str): Path to the .dat file.
        memristor_num (int): The memristor number to retrieve data for.

    Returns:
        dict: A dictionary containing all data for the specified memristor.
    """
    
    # Read the .dat file
    df = pd.read_csv(file_path,  sep='\s+')
    
    # Filter the data for the specific memristor number
    memristor_data = df[df['Memristor'] == memristor_num]
    
    # Check if the memristor number exists in the data
    if memristor_data.empty:
        raise ValueError(f"Memristor number {memristor_num} not found in the data.")
    
    # Extract and return all the required data
    return {
        'Voltage': memristor_data['Voltage'].values[0],
        'TimePeriod': memristor_data['TimePeriod'].values[0],
        'NoPulses': memristor_data['NoPulses'].values[0],
        'DutyCycle': memristor_data['DutyCycle'].values[0],
        'IntendedGValue': memristor_data['IntendedGValue'].values[0],
        'NoTimes': memristor_data['NoTimes'].values[0]
        
    }

# Example usage: Directly using the get_memristor_data function
#file_path = 'MemristorData.dat'
#memristor_num = 6

# Retrieve the data for a specific memristor
#memristor_info = get_memristor_data(file_path, memristor_num)

# Access individual values directly from the returned dictionary
# voltage = memristor_info['Voltage']
# time_period = memristor_info['TimePeriod']
# no_pulses = memristor_info['NoPulses']
# duty_cycle = memristor_info['DutyCycle']
# intended_g_value = memristor_info['IntendedGValue']
# no_times = memristor_info['NoTimes']

# # Use the variables directly in your script
# print(f"Memristor {memristor_num} Voltage: {voltage}")
# print(f"Time Period: {time_period}")
# print(f"No Pulses: {no_pulses}")
# print(f"Duty Cycle: {duty_cycle}")
# print(f"Intended G Value: {intended_g_value}")


