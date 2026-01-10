import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def linear_fit(x, G):
    return G * x

def plot_iv():
    file = "Memristor.csv"
    data = np.loadtxt(file, delimiter=",")
    voltage, current = data[:, 0], data[:, 1]
    
    # Find indices of the maximum and minimum current
    I_max_index = np.argmax(current)
    I_min_index = np.argmin(current)
    
    V_max_H, I_max = voltage[I_max_index], current[I_max_index]
    V_min_L, I_min = voltage[I_min_index], current[I_min_index]
    
    # First mask: from maximum positive current to 0.0 current
    mask_1 = ((current >= 0) & (current <= I_max))
    V_combined_1, I_combined_1 = voltage[mask_1], current[mask_1]
    
    # Fit for first region
    popt_1, _ = curve_fit(linear_fit, V_combined_1, I_combined_1)
    G_1 = popt_1[0]
    
    # Second mask: from maximum negative current to 0.0 current
    mask_2 = ((current <= 0) & (current >= I_min))
    V_combined_2, I_combined_2 = voltage[mask_2], current[mask_2]
    
    # Fit for second region
    popt_2, _ = curve_fit(linear_fit, V_combined_2, I_combined_2)
    G_2 = popt_2[0]
    
    # Plotting the data
    plt.figure(figsize=(8, 6))
    
    # Plot the full IV curve (blue)
    plt.plot(voltage, current, 'b-', label="Memristor IV")
    
    # Highlight the mask ranges (positive region in green and negative region in red)
    plt.fill_between(V_combined_1, I_combined_1, color='green', alpha=0.3, label="Positive Region (Mask)")
    plt.fill_between(V_combined_2, I_combined_2, color='red', alpha=0.3, label="Negative Region (Mask)")
    
    # Plot the fits for both regions, extended to the full voltage range
    plt.plot(voltage, linear_fit(voltage, G_1), 'g-', label=f"Fit (Positive): G = {G_1:.2f} μS")
    plt.plot(voltage, linear_fit(voltage, G_2), 'r-', label=f"Fit (Negative): G = {G_2:.2f} μS")
    
    # Adding labels, legend, and grid
    plt.xlabel("Applied Voltage (V)")
    plt.ylabel("Current (μA)")
    plt.legend()
    plt.grid()
    plt.show()

plot_iv()
