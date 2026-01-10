import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import curve_fit

# Define the Gaussian function for fitting
def gaussian(x, mu, sigma, amplitude):
    return amplitude * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

# Load the CSV file containing the conductance data
file_path = 'conductance_valuesM1Min.csv'
data = pd.read_csv(file_path, header=None)  # No header row in the CSV file

# Assume the data is in the first column (index 0)
conductance = data.iloc[:, 0]

# Plot histogram of conductance values
plt.figure(figsize=(10, 6))
hist, bins, _ = plt.hist(conductance, bins=50, alpha=0.6, color='b', density=True)

# Fit a Gaussian curve to the histogram
bin_centers = (bins[:-1] + bins[1:]) / 2
popt, _ = curve_fit(gaussian, bin_centers, hist, p0=[np.mean(conductance), np.std(conductance), max(hist)])

mu, sigma, amplitude = popt

# Plot the fitted Gaussian curve
x_fit = np.linspace(min(conductance), max(conductance), 100)
y_fit = gaussian(x_fit, *popt)
plt.plot(x_fit, y_fit, 'r--', label=f'Fit: $\mu$ = {mu:.3f}, $\sigma$ = {sigma:.3f}')

# Add labels and legend
plt.xlabel('Conductance (S)')
plt.ylabel('Frequency')
plt.title('Histogram of Conductance Values')
plt.legend()

# Show plot
plt.show()

# Print the mean and standard deviation
print(f'Mean Conductance: {mu:.3f} S')
print(f'Standard Deviation: {sigma:.3f} S')
