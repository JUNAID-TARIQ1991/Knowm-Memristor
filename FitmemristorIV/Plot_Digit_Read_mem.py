import numpy as np
import matplotlib.pyplot as plt
import sys

# Dummy function to simulate reading conductance values from memristors
# Replace this with your actual code for reading conductance values
def read_conductance_values():
    # Simulating 16 conductance values for now
    conductance_values = np.linspace(10, 250, 16)  # Replace with actual read logic
    return conductance_values

# Function to draw a grayscale digit based on conductance values
def draw_digit(digit, conductance_values):
    # Normalize and scale conductance values for gray levels
    target_max = 250
    conductance_normalized = (conductance_values - min(conductance_values)) / (max(conductance_values) - min(conductance_values))
    gray_levels = (conductance_normalized * target_max).astype(np.uint8)

    # Define indices for digits
    digit_indices = {
        "1": [
            (0, 2), (1, 2), (2, 2), (3, 2),  # Vertical line of "1"
            (0, 1), (0, 3),                  # Top of "1"
        ],
        "2": [
            (0, 0), (0, 1), (0, 2), (0, 3),  # Top horizontal line of "2"
            (1, 3),                         # Top-right vertical line of "2"
            (2, 2),                         # Middle horizontal line of "2"
            (3, 1), (3, 2), (3, 3)          # Bottom horizontal line of "2"
        ]
    }

    # Check if the digit is valid
    if digit not in digit_indices:
        print(f"Digit {digit} is not supported. Supported digits: {list(digit_indices.keys())}")
        return

    # Create a blank 4x4 grid with a light background
    gray_grid = np.full((4, 4), 240, dtype=np.uint8)  # Light gray for the background

    # Assign gray levels to the digit shape
    indices = digit_indices[digit]
    for idx, (i, j) in enumerate(indices):
        gray_grid[i, j] = gray_levels[idx % len(gray_levels)]  # Cycle through gray levels

    # Plot the digit
    plt.figure(figsize=(4, 4))
    plt.imshow(gray_grid, cmap='gray', vmin=0, vmax=255)
    plt.colorbar(label='Grayscale Level')
    plt.title(f"Digit {digit} with Lighter Shades")
    plt.axis('off')
    plt.show()

# Main function
def main():
    # Simulate reading conductance values
    conductance_values = read_conductance_values()

    # Check for user input
    if len(sys.argv) < 2:
        print("Usage: python modulename.py <digit>")
        sys.exit(1)

    # Get the digit from user input
    digit = sys.argv[1]
    
    # Draw the digit
    draw_digit(digit, conductance_values)

# Entry point
if __name__ == "__main__":
    main()
