import struct
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import re

def extract_number_from_raw(raw_bytes):
    """Extracts a scientific-notation number from LeCroy raw bytes."""
    text = raw_bytes.decode(errors="ignore")  # convert bytes → string
    m = re.search(r'[-+]?\d*\.?\d+E[-+]?\d+', text)
    return float(m.group()) if m else None


def read_lecroy_waveform(osc):
    # -------------------------------------------------------------
    # 1. Read Descriptor (WAVEDESC 2.3)
    # -------------------------------------------------------------
    osc.write("C4:WF? DESC")
    desc = osc.read_raw()
    print(f"\nDescriptor received ({len(desc)} bytes)\n")

    # Locate block header "#"
    i = desc.find(b"#")
    ndig = int(desc[i+1:i+2])
    blen = int(desc[i+2:i+2+ndig])
    start = i + 2 + ndig

    wavedesc = desc[start:start + blen]

    # ---- Extract WAVEDESC values ----
    # Verified for LeCroy WAVEDESC 2.3 (WaveRunner series)
    VERT_GAIN      = struct.unpack("<f", wavedesc[156:160])[0]
    VERT_OFFSET    = struct.unpack("<f", wavedesc[160:164])[0]
    ADC_OFFSET     = struct.unpack("<h", wavedesc[164:166])[0]   # TRUE ADC offset
    HORIZ_INTERVAL = struct.unpack("<f", wavedesc[176:180])[0]
    HORIZ_OFFSET   = struct.unpack("<d", wavedesc[180:188])[0]
    N_SAMPLES      = struct.unpack("<i", wavedesc[60:64])[0]

    print("VERT_GAIN      =", VERT_GAIN)
    print("VERT_OFFSET    =", VERT_OFFSET)
    print("ADC_OFFSET     =", ADC_OFFSET)      # <-- Correct field
    print("HORIZ_INTERVAL =", HORIZ_INTERVAL)
    print("HORIZ_OFFSET   =", HORIZ_OFFSET)
    print("N_SAMPLES      =", N_SAMPLES)

    # -------------------------------------------------------------
    # 2. Read waveform ADC data (DAT1 block)
    # -------------------------------------------------------------
    osc.write("C4:WF? DAT1")
    data = osc.read_raw()

    print("\nRaw data header:", data[:40])
    print("Raw data preview (500 bytes):", data[:500])

    # Locate # block
    j = data.find(b"#")
    nd = int(data[j+1:j+2])
    dlen = int(data[j+2:j+2+nd])
    st = j + 2 + nd

    raw = data[st:st+dlen]
    print("Waveform raw extracted:", raw[:40])
    print("Raw length =", len(raw))

    # -------------------------------------------------------------
    # 3. Determine ADC width (8-bit or 16-bit)
    # -------------------------------------------------------------
    if dlen == N_SAMPLES:
        adc = np.frombuffer(raw, dtype=np.int8)
    elif dlen == 2 * N_SAMPLES:
        adc = np.frombuffer(raw, dtype="<i2")
    else:
        raise ValueError(f"Unexpected raw length: dlen={dlen}, expected {N_SAMPLES} or {2*N_SAMPLES}")

    # -------------------------------------------------------------
    # 4. Correct LeCroy voltage reconstruction formula
    # -------------------------------------------------------------
    # Official: voltage = (adc - ADC_OFFSET) * VERT_GAIN - VERT_OFFSET
    voltage = (adc - ADC_OFFSET) * VERT_GAIN - VERT_OFFSET

    return voltage


# ----------------------------------------------------
# Example usage
# ----------------------------------------------------
rm = pyvisa.ResourceManager()
scope = rm.open_resource("TCPIP0::172.16.13.144::INSTR")
scope.timeout = 5000

voltage = read_lecroy_waveform(scope)

# ---- Plot waveform ----
plt.figure(figsize=(12, 6))
plt.plot(voltage)
plt.title("Waveform from Channel 4")
plt.xlabel("Sample index")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.show()
