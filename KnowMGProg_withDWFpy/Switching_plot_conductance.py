import matplotlib.pyplot as plt
import numpy as np

# Data for each memristor and state
states = ['Initial Read with AD2', 'Power cycle AD2', 'Plug Out and In', 'KeySight Plug in and Out']

# Conductance values for each state and memristor
conductance_values = {
    'Memristor 1': [9.242e-05, 9.2072e-05, 2.8092e-04, 1.3257e-05],
    'Memristor 2': [1.0134e-05, 7.8412e-05, 7.5434e-05, 2.7384e-06],
    'Memristor 3': [3.9917e-03, 3.9698e-03, 4.0243e-03, 3.1648e-03],
    'Memristor 4': [1.2352e-04, 1.2106e-04, 8.4373e-05, 2.0031e-03],
    'Memristor 5': [9.6252e-05, 9.7252e-05, 9.8252e-05, 7.5096e-04],
    'Memristor 6': [1.0042e-05, 7.9969e-05, 7.1136e-05, 8.3899e-05],
    'Memristor 7': [9.4805e-05,  9.4801e-05, 8.7336e-05 ,6.0964e-06],
    'Memristor 8': [9.4421e-05 , 8.4014e-05, 1.1060e-04, 6.7821e-06],
    'Memristor 9': [9.9247e-05, 9.3256e-05, 3.0703e-04, 5.8024e-04],
    'Memristor 10': [9.209e-05, 1.0294e-05, 2.7104e-05, 2.3956e-06],
    'Memristor 11': [8.8458e-05, 6.2569e-05, 1.1926e-05, 2.5521e-05],
    'Memristor 12': [9.3173e-05, 8.3973e-05, 2.5187e-06, 2.4375e-06],
    'Memristor 13': [9.5390e-05, 5.4732e-05, 5.8319e-05, 3.0535e-06],
    'Memristor 14': [8.2013e-05, 1.9132e-05, 1.7793e-05, 6.5468e-06],
    'Memristor 15': [8.9806e-05, 6.5857e-05, 6.2497e-05, 1.5580e-05],
    'Memristor 16': [8.0790e-05, 1.5360e-05, 2.6916e-05, 2.9365e-06],
}

# Plotting
memristors = list(conductance_values.keys())
conductances = np.array(list(conductance_values.values()))

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot each memristor's conductance values over different states
for i, memristor in enumerate(memristors):
    ax.plot(states, conductances[i], label=memristor, marker='o')

# Formatting the plot
ax.set_title('Conductance of Memristors at Different States')
ax.set_xlabel('State')
ax.set_ylabel('Conductance (S)')
ax.set_yscale('log')  # Use logarithmic scale for better visibility of small values
ax.legend(loc='upper left', bbox_to_anchor=(1, 1), title='Memristors')

# Rotate x-axis labels for readability
plt.xticks(rotation=45)

plt.tight_layout()  # Adjust layout to prevent clipping
plt.show()
