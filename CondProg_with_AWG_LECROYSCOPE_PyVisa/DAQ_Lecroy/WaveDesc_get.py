import pyvisa
import numpy as np
import struct
import matplotlib.pyplot as plt


resource = "TCPIP0::172.16.14.23::inst0::INSTR"
channel = "C4"

rm = pyvisa.ResourceManager()
scope = rm.open_resource(resource)
scope.timeout = 20000


scope.clear()    # empty VISA buffer (very important!)

# richiedi waveform (include descriptor + data)
scope.write(f"TMPL?")
raw = scope.read_raw()

# parse waveform descriptor
# (see LeCroy 64-bit binary format for details) 
descriptor = raw[:346]
# parse data
data = raw[346:] 

with open("descriptor.txt", "w") as f:
    f.write(raw.decode("ascii")) 

