import numpy as np
import matplotlib.pyplot as plt

# Load data
data = np.loadtxt(r'c:\Users\Tariq\Desktop\Memristor.csv', delimiter=',')
voltages = data[:, 0]
currents = data[:, 1]

# Find positive and negative peaks
pos_max_idx = np.argmax(currents)
neg_min_idx = np.argmin(currents)

# Corrected zero-crossing detection function
def find_zero_crossing(start_idx, target_sign):
    if target_sign == "positive_to_zero":
        # Find first zero crossing (current <= 0) moving forward
        for i in range(start_idx, len(currents)):
            if currents[i] <= 0:
                return i
    elif target_sign == "negative_to_zero":
        # Find first zero crossing (current >= 0) moving forward
        for i in range(start_idx, len(currents)):
            if currents[i] >= 0:
                return i
    return start_idx  # Fallback

# Extract ranges with corrected logic
end_pos = find_zero_crossing(pos_max_idx, "positive_to_zero")
positive_range = data[pos_max_idx:end_pos+1]

end_neg = find_zero_crossing(neg_min_idx, "negative_to_zero")
negative_range = data[neg_min_idx:end_neg+1]

# Linear fitting function
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

# Plot with thicker lines for visibility
plt.figure(figsize=(10, 6))
plt.scatter(voltages, currents, s=5, label='Original Data', color='gray', alpha=0.6)

# Plot fits with distinct styles
plt.plot(positive_range[:, 0], np.polyval(pos_coeffs, positive_range[:, 0]), 
        'r', linewidth=2.5, label=f'Positive Fit (G = {G_pos:.1f} S)')
plt.plot(negative_range[:, 0], np.polyval(neg_coeffs, negative_range[:, 0]), 
        'g--', linewidth=2.5, label=f'Negative Fit (G = {G_neg:.1f} S)')

plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
plt.title('Memristor I-V Characteristics with Corrected Fits')
plt.legend()
plt.grid(True)
plt.show()