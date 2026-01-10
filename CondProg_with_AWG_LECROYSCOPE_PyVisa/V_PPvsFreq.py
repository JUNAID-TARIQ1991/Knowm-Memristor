import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Load CSV without header and assign column names
file_path = "vpp_vs_frequency_AMP.csv"
df = pd.read_csv(file_path, header=None, names=["Frequency_kHz", "Vpp_Volts"])

# Convert columns to numeric
df["Frequency_kHz"] = pd.to_numeric(df["Frequency_kHz"], errors='coerce')
df["Vpp_Volts"] = pd.to_numeric(df["Vpp_Volts"], errors='coerce')
df.dropna(inplace=True)

# Dummy conductance and resistance values
conductances = [100e-6, 95e-6,194e-6, 300e-6]  # Siemens (S)
resistances_kohm = [1.0/g/1e3 for g in conductances]
# Convert frequency from kHz to MHz
res_text = "R = [" + ", ".join(f"{R:.1f} kΩ" for R in resistances_kohm) + "]"
df["Frequency_MHz"] = df["Frequency_kHz"]

# Create plot
plt.figure(figsize=(8, 6), dpi=150)  # More balanced aspect ratio

plt.plot(
    df["Frequency_MHz"],
    df["Vpp_Volts"],
    marker='o',
    markersize=6,
    linewidth=2,
    label="Passive setup with  TIA ($V_{pp}$)"
)

plt.xscale('log')
plt.xlabel('Frequency (Hz)', fontsize=16)
plt.ylabel('Peak-to-Peak Voltage (V)', fontsize=16)
plt.title('Peak-to-Peak Voltage vs Frequency (4 Memristors)', fontsize=18)

plt.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.7)
plt.tick_params(axis='both', which='major', labelsize=14)
# Build a nice text line like: G = [60, 140, 200, 150] µS
handles, labels = plt.gca().get_legend_handles_labels()
handles.append(Line2D([], [], linestyle='None', label=res_text))
plt.legend(handles=handles, fontsize=14)
plt.tight_layout()
plt.show()
