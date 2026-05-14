import pyvisa
import numpy as np
import struct
import matplotlib.pyplot as plt
import time

resource = "TCPIP0::172.16.14.23::inst0::INSTR"
channel = "C4"

rm = pyvisa.ResourceManager()
scope = rm.open_resource(resource)
scope.timeout = 20000

scope.clear()

print(scope.query("*IDN?"))

# Important communication setup
scope.write("COMM_HEADER OFF")
scope.write("COMM_FORMAT DEF9,WORD,BIN")

# Make sure C4 is displayed and has acquisition memory
scope.write(f"{channel}:TRACE ON")
time.sleep(0.5)

# Ask for all waveform content: DESC + DAT1
scope.write(f"{channel}:WF? DAT1")
raw = scope.read_raw()

hash_index = raw.find(b"#")
if hash_index < 0:
    raise RuntimeError(f"No binary block found. Reply starts: {raw[:100]!r}")

raw = raw[hash_index:]

nd = int(raw[1:2])
total_len = int(raw[2:2 + nd])
payload = raw[2 + nd:2 + nd + total_len]

if payload[0:8] != b"WAVEDESC":
    raise RuntimeError("WAVEDESC not found at start of payload")

# Descriptor values
DESC_LEN = struct.unpack("<i", payload[36:40])[0]
USER_LEN = struct.unpack("<i", payload[40:44])[0]
TRIG_LEN = struct.unpack("<i", payload[48:52])[0]
WAVE_ARRAY_1 = struct.unpack("<i", payload[60:64])[0]

VERT_GAIN = struct.unpack("<f", payload[156:160])[0]
VERT_OFFSET = struct.unpack("<f", payload[160:164])[0]
HORIZ_INTERVAL = struct.unpack("<f", payload[176:180])[0]
HORIZ_OFFSET = struct.unpack("<d", payload[180:188])[0]

print("DESC_LEN =", DESC_LEN)
print("USER_LEN =", USER_LEN)
print("TRIG_LEN =", TRIG_LEN)
print("WAVE_ARRAY_1 bytes =", WAVE_ARRAY_1)
print("VERT_GAIN =", VERT_GAIN)
print("VERT_OFFSET =", VERT_OFFSET)
print("HORIZ_INTERVAL =", HORIZ_INTERVAL)
print("HORIZ_OFFSET =", HORIZ_OFFSET)

if WAVE_ARRAY_1 == 0:
    raise RuntimeError(
        "WAVE_ARRAY_1 is zero: the scope returned descriptor only, no waveform samples. "
        "Press Run/Stop so a waveform is acquired, or force/acquire a trigger before reading."
    )

# Data starts after descriptor + optional arrays
DATA_START = DESC_LEN + USER_LEN + TRIG_LEN
DATA_END = DATA_START + WAVE_ARRAY_1

data = payload[DATA_START:DATA_END]

print("Data bytes =", len(data))

adc = np.frombuffer(data, dtype="<i2").astype(float)
print("ADC samples =", len(adc))

voltage = adc * VERT_GAIN - VERT_OFFSET
time_axis = HORIZ_OFFSET + np.arange(len(voltage)) * HORIZ_INTERVAL

print("Voltage min =", np.min(voltage))
print("Voltage max =", np.max(voltage))

plt.figure(figsize=(10, 5))
plt.plot(time_axis * 1e6, voltage)
plt.xlabel("Time (us)")
plt.ylabel("Voltage (V)")
plt.title(f"{channel} waveform")
plt.grid(True)
plt.show(block=True)

scope.close()
rm.close()