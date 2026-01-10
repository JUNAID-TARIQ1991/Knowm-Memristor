import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Load the CSV file
file_path = r'c:\Users\Junaid\Desktop\Memristor.csv'  

data = pd.read_csv(file_path)

data.columns = ['Voltage', 'Current']

# Extract voltage and current data
voltage = data['Voltage']
current = data['Current']

# Plot the IV curve
plt.figure(figsize=(10, 6))
plt.plot(voltage, current, 'o', label='Data')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (µA)')
plt.title('IV Curve')
plt.grid(True)

# Perform linear regression
slope, intercept, r_value, p_value, std_err = linregress(voltage, current)

# Plot the linear fit
fit_line = slope * voltage + intercept
plt.plot(voltage, fit_line, 'r', label=f'Fit: I = {slope:.3f} µS * V + {intercept:.3f} µA')

# Add legend
plt.legend()

# Show plot
plt.show()
#plt.savefig('IV_curve.png')  

# Print the slope and intercept
print(f'Slope (Conductance): {slope:.3f} µS')
print(f'Intercept: {intercept:.3f} µA')

# Append the conductance value to a file
conductance_file_path = 'Conductance_valuesM91Level.dat'
with open(conductance_file_path, 'a') as file:
    file.write(f'{slope:.3f}\n')

print(f'Conductance value {slope:.3f} µS, R = {1e06/slope }, Error = {std_err}, R_Value= {r_value}, P_value={p_value}')
