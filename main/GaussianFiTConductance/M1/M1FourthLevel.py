import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.neighbors import KernelDensity

# Given 30 conductance values
# original_values L4 (1v, 100p,100mu, 10 or 20p) = [110, 112, 113, 111.5, 115, 110.1, 108, 113, 115, 110, 99.1, 98, 116.5, 113.1, 112.1, 110.5, 105, 99, 100, 112, 110, 130, 114]
# 0.5v, 100p -2v 100p
# original_values = [40, 39.15, 42.37, 38, 50, 39.18, 55, 45, 39, 42, 43, 40.15, 35, 33, 50, 35, 32, 38, 42, 37, 39, 35, 38, 39]
# 0.8v 100p -2v 100p
# original_values = [70, 65, 72, 70, 68, 75, 72, 74, 65, 79, 80, 69, 65, 63, 68, 67, 71, 75, 72, 69.4, 71, 74, 66, 61, 63]
original_values = [20, 14, 15, 12, 15, 18, 16, 13, 15,
                   18, 20, 17, 10, 18, 14, 15, 14, 20, 16, 15, 12, 21, 16, 12, 18]
# Fit a Kernel Density Estimate (KDE) to model the data distribution
kde = KernelDensity(kernel='gaussian', bandwidth=0.4).fit(
    np.array(original_values).reshape(-1, 1))

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
count, bins, ignored = plt.hist(
    combined_values, bins=20, density=True, alpha=0.6, color='skyblue', edgecolor='black')

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
plt.text(xmax - 5, max(count) - 0.01,
         f'$\mu={mu:.2f}, \ \sigma={std:.2f}$', fontsize=12)

# Show plot
plt.show()

print("Conductance values saved to 'conductance_values.txt'.")
