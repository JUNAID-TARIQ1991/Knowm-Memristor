import numpy as np
import matplotlib.pyplot as plt

# Load data
data = np.loadtxt('Memristor.csv', delimiter=',')
voltages = data[:, 0]
currents = data[:, 1]

# Find positive and negative peaks
pos_max_idx = np.argmax(currents)
neg_min_idx = np.argmin(currents)

# Function to find zero crossing index
def find_zero_crossing(start_idx, direction):
    for i in range(start_idx, len(currents) if direction == 'forward' else -1, 1 if direction == 'forward' else -1):
        if (direction == 'forward' and currents[i] <= 0) or (direction == 'backward' and currents[i] >= 0):
            return i
    return start_idx  # Fallback if no crossing found

# Extract positive range (from max to first zero crossing)
end_pos = find_zero_crossing(pos_max_idx, 'forward')
positive_range = data[pos_max_idx:end_pos+1]

# Extract negative range (from min to first zero crossing)
end_neg = find_zero_crossing(neg_min_idx, 'forward')
negative_range = data[neg_min_idx:end_neg+1]

# Perform linear fits
def linear_fit(range_data):
    v = range_data[:, 0]
    i = range_data[:, 1]
    coeffs = np.polyfit(v, i, 1)
    return coeffs[0], coeffs

# Calculate conductances
G_pos, pos_coeffs = linear_fit(positive_range)
G_neg, neg_coeffs = linear_fit(negative_range)

print(f"Positive conductance (G₁): {G_pos:.2f} S")
print(f"Negative conductance (G₂): {G_neg:.2f} S")

# Plot results
plt.figure(figsize=(10, 6))
plt.scatter(voltages, currents, s=5, label='Original Data')
plt.plot(positive_range[:, 0], np.polyval(pos_coeffs, positive_range[:, 0]), 
         'r', label=f'Positive Fit (G = {G_pos:.1f} S)')
plt.plot(negative_range[:, 0], np.polyval(neg_coeffs, negative_range[:, 0]), 
         'b', label=f'Negative Fit (G = {G_neg:.1f} S)')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
plt.title('Memristor I-V Characteristics with Linear Fits')
plt.legend()
plt.grid(True)
plt.show()