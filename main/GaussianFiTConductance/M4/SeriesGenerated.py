import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from scipy.stats import norm
from scipy.optimize import curve_fit

# Given conductance values
conductance_values = np.array([
    7.6, 7.3, 6.7, 5.9, 6.6, 7.2, 5.5, 7.5, 7.5, 6.5,
    7.2, 7.1, 6.5, 6.9, 7.1, 7.2, 6.5, 7.5, 5.6, 5.4,
    5.0, 7.8, 6.5, 5.7, 7.1, 6.8, 5.9, 6.9, 7.1, 5.9
])

# Reshape for fitting the Kernel Density Estimation model
conductance_values = conductance_values.reshape(-1, 1)

# Fit a Kernel Density Estimation model
kde = KernelDensity(kernel='gaussian', bandwidth=0.15).fit(conductance_values)

# Generate 70 new values to add to the original 30
new_conductance_values = kde.sample(70)

# Combine the original and new values
expanded_conductance_values = np.concatenate([conductance_values, new_conductance_values])

# Flatten the array
expanded_conductance_values = expanded_conductance_values.flatten()

# Sort the values for better visualization
expanded_conductance_values.sort()

# Print the 100 values
print("Generated 100 conductance values:\n", expanded_conductance_values)

# Define Gaussian function for fitting
def gaussian(x, mean, amplitude, stddev):
    return amplitude * np.exp(-((x - mean) ** 2 / (2 * stddev ** 2)))

# Fit histogram data to Gaussian
hist, bins = np.histogram(expanded_conductance_values, bins=15, density=True)
bin_centers = (bins[1:] + bins[:-1]) * 0.5

# Initial guess for Gaussian parameters: mean, amplitude, stddev
initial_guess = [np.mean(expanded_conductance_values), 1, np.std(expanded_conductance_values)]

# Fit the histogram data using curve_fit
popt, _ = curve_fit(gaussian, bin_centers, hist, p0=initial_guess)

# Extract the optimized parameters
mean, amplitude, stddev = popt

# Plot histogram
plt.hist(expanded_conductance_values, bins=15, alpha=0.7, color='blue', label='Generated Conductance Values', density=True)

# Plot Gaussian fit
x_fit = np.linspace(min(expanded_conductance_values), max(expanded_conductance_values), 1000)
y_fit = gaussian(x_fit, *popt)
plt.plot(x_fit, y_fit, color='red', linewidth=2, label=f'Gaussian Fit\nMean={mean:.2f}, Stddev={stddev:.2f}')

# Plot mean line
plt.axvline(np.mean(expanded_conductance_values), color='r', linestyle='--', linewidth=1, label=f'Mean: {np.mean(expanded_conductance_values):.2f}')

plt.xlabel('Conductance (uS)')
plt.ylabel('Density')
plt.title('Histogram and Gaussian Fit of Generated Conductance Values')
plt.legend()
plt.show()

