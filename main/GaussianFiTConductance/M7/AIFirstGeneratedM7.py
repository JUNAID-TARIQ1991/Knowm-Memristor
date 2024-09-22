import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.neighbors import KernelDensity

# Given 30 conductance values
original_values = [37.03, 36.109, 38.044, 38.099, 38.9, 37.00, 38.75, 38.84, 39.00, 39.04, 37, 38, 
                   37.60, 40.40, 38.00, 40.5, 37, 35, 39.24, 36.20, 38, 39, 36.00, 38.00, 37]

# Fit a Kernel Density Estimate (KDE) to model the data distribution
kde = KernelDensity(kernel='gaussian', bandwidth=0.4).fit(np.array(original_values).reshape(-1, 1))

# Generate 70 new values using KDE
new_values = kde.sample(70).flatten()

# Combine original and generated values
combined_values = np.concatenate((original_values, new_values))

# Save the 100 values to a file
with open("conductance_values.txt", "w") as file:
    for value in combined_values:
        file.write(f"{value:.4f}\n")

# Plot histogram of the combined values
plt.figure(figsize=(10, 6))
count, bins, ignored = plt.hist(combined_values, bins=10, density=True, alpha=0.6, color='skyblue', edgecolor='black')

# Fit a Gaussian curve to the data
mu, std = norm.fit(combined_values)
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)

# Plot the Gaussian fit
plt.plot(x, p, 'k', linewidth=2)
plt.title('Histogram of Conductance Values with Gaussian Fit')
plt.xlabel('Conductance (μS)')
plt.ylabel('Probability Density')

# Display the mean and standard deviation
plt.text(xmax - 5, max(count) - 0.05, f'$\mu={mu:.2f}, \ \sigma={std:.2f}$', fontsize=12)

# Show plot
plt.show()

print("Conductance values saved to 'conductance_values.txt'.")

