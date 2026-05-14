import pyvisa
import numpy as np
import struct
import matplotlib.pyplot as plt
import time


resource = "TCPIP0::172.16.14.23::inst0::INSTR"


def read_lecroy_waveform(osc, channel):
    """
    Read waveform from one LeCroy channel.

    Parameters
    ----------
    osc : pyvisa resource
        Oscilloscope object.
    channel : str
        Channel name: "C1", "C2", "C3", or "C4".

    Returns
    -------
    time_axis : np.ndarray
        Time values in seconds.
    voltage : np.ndarray
        Voltage values in volts.
    """

    # Request waveform from selected channel
    osc.write(f"{channel}:WF?")
    raw = osc.read_raw()

    # Find binary block
    hash_index = raw.find(b"#")
    if hash_index == -1:
        raise RuntimeError(
            f"Binary block (#) not found for {channel}. "
            f"Reply starts: {raw[:100]!r}"
        )

    raw = raw[hash_index:]

    # Parse SCPI binary block header
    nd = int(raw[1:2])
    total_len = int(raw[2:2 + nd])
    payload = raw[2 + nd:2 + nd + total_len]

    if payload[0:8] != b"WAVEDESC":
        raise RuntimeError(f"WAVEDESC not found for {channel}")

    # Helper functions
    def i16(off):
        return struct.unpack("<h", payload[off:off + 2])[0]

    def i32(off):
        return struct.unpack("<i", payload[off:off + 4])[0]

    def f32(off):
        return struct.unpack("<f", payload[off:off + 4])[0]

    def f64(off):
        return struct.unpack("<d", payload[off:off + 8])[0]

    # Read waveform descriptor values
    COMM_TYPE = i16(32)       # 0 = BYTE, 1 = WORD
    COMM_ORDER = i16(34)      # 0 = HIFIRST, 1 = LOFIRST

    DESC_LEN = i32(36)
    USER_LEN = i32(40)
    TRIG_LEN = i32(48)
    WAVEARRAY_1 = i32(60)     # bytes

    VERT_GAIN = f32(156)
    VERT_OFFSET = f32(160)
    HORIZ_INTERVAL = f32(176)
    HORIZ_OFFSET = f64(180)

    # Data location
    DATA_START = DESC_LEN + USER_LEN + TRIG_LEN
    DATA_END = DATA_START + WAVEARRAY_1

    data = payload[DATA_START:DATA_END]

    if len(data) != WAVEARRAY_1:
        raise ValueError(
            f"{channel}: Data length mismatch: "
            f"len(data)={len(data)}, WAVEARRAY_1={WAVEARRAY_1}"
        )

    # Convert ADC data depending on waveform format
    if COMM_TYPE == 0:
        adc = np.frombuffer(data, dtype=np.int8).astype(np.float64)

    elif COMM_TYPE == 1:
        if COMM_ORDER == 0:
            adc = np.frombuffer(data, dtype=">i2").astype(np.float64)
        else:
            adc = np.frombuffer(data, dtype="<i2").astype(np.float64)

    else:
        raise ValueError(f"{channel}: Unknown COMM_TYPE = {COMM_TYPE}")

    if adc.size == 0:
        raise ValueError(f"{channel}: ADC array is empty")

    # Convert ADC counts to voltage
    voltage = adc * VERT_GAIN - VERT_OFFSET

    # Generate time axis
    time_axis = HORIZ_OFFSET + np.arange(adc.size) * HORIZ_INTERVAL

    return time_axis, voltage


# ================= MAIN PROGRAM =================

rm = pyvisa.ResourceManager()
scope = rm.open_resource(resource)
scope.timeout = 20000

scope.clear()

# Force known waveform format
scope.write("COMM_HEADER OFF")
scope.write("COMM_FORMAT DEF9,WORD,BIN")

channels = ["C1", "C2", "C3", "C4"]
channels = ["C4"]

# Turn all four traces ON
for ch in channels:
    scope.write(f"{ch}:TRACE ON")

time.sleep(0.5)

# Optional: stop acquisition before reading
# Use this if you want a frozen waveform from all channels
scope.write("STOP")
# time.sleep(0.5)

waveforms = {}

for ch in channels:
    print(f"Reading {ch}...")
    try:
        t, v = read_lecroy_waveform(scope, ch)
        waveforms[ch] = (t, v)
        print(f"{ch}: {len(v)} samples, Vmin={np.min(v):.3f} V, Vmax={np.max(v):.3f} V")
    except Exception as e:
        print(f"Failed to read {ch}: {e}")
        waveforms[ch] = None


# ================= PLOT =================

fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=False)
axs = axs.flatten()

for ax, ch in zip(axs, channels):
    if waveforms[ch] is not None:
        t, v = waveforms[ch]
        ax.plot(t * 1e6, v)
        ax.set_title(f"LeCroy waveform from {ch}")
        ax.set_xlabel("Time (µs)")
        ax.set_ylabel("Voltage (V)")
        ax.grid(True)
    else:
        ax.set_title(f"{ch} read failed")
        ax.set_xlabel("Time (µs)")
        ax.set_ylabel("Voltage (V)")
        ax.grid(True)

plt.tight_layout()
plt.show(block=True)

scope.close()
rm.close()