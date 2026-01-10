import numpy as np
import matplotlib.pyplot as plt

# Data: Frequency (Hz) and corresponding I_Out (A)
frequencies = np.array([100, 500,1000,5000, 10000, 50000, 100000, 500000, 1000000, 10000000, 100000000])
I_Out = np.array([8.48e-06, 8.51e-06, 8.48e-06, 8.54e-06,8.59e-06,8.50e-06, 8.30e-06, 7.90e-06, 7.70e-06, 4.70e-06, 1.5e-06 ])
I_ideal = 8.68e-06  # Ideal current value

# Compute percentage error
error_percentage = ((I_Out - I_ideal) / I_ideal) * 100

# Dummy conductance and resistance values
conductances = [164e-6, 150e-6,132e-6, 35e-6]  # Siemens (S)
resistances = [6.12e03, 6.6e03,7.6e03, 30.2e03]  # Ohms (Ω)

# Create the figure and axis
plt.figure(figsize=(9, 6))

# Plot measured data with markers
plt.plot(frequencies, I_Out, marker='s', markersize=8, linestyle='--', color='b', label='Measured I_Out')

# Plot the ideal current as a horizontal line
plt.axhline(y=I_ideal, color='r', linestyle='-', linewidth=2, label=f'Ideal I_Out = {I_ideal:.2e} A')

# Annotate the percentage error at each point
for freq, I, err in zip(frequencies, I_Out, error_percentage):
    plt.text(freq, I, f"{err:.1f}%", fontsize=10, verticalalignment="bottom", horizontalalignment="right", color='darkred')

# Configure axes
plt.xscale('log')  # Log scale for frequency
plt.yscale('linear')  # Keep y-axis linear for better comparison

plt.xlabel('Frequency (Hz)', fontsize=12)
plt.ylabel('Computed Current I_Out (A)', fontsize=12)
plt.title('I_Out vs Frequency with Percentage Error', fontsize=14)

plt.xlim(50, 9.5e8)  # Adjust frequency limits
plt.ylim(1.0e-6, 9.5e-6)  # Adjust current limits

plt.grid(True, which="both", linestyle="--", linewidth=0.6)

# Add dummy legend entries for conductance and resistance
for i, (g, r) in enumerate(zip(conductances, resistances), start=1):
    plt.plot([], [], ' ', label=f'G{i} = {g:.2e} S, R{i} = {r:.1f} Ω')

plt.legend()
plt.show()
