import pyvisa
import numpy as np
import struct
import matplotlib.pyplot as plt


def parse_lecroy_waveform(raw):
    
    #raw = binary response of C1:WAVEFORM? DAT1 read with read_raw()
    #returns: time[], voltage[]


    
    
    # --------------------------
    # 1) Parsing header SCPI "#"
    # --------------------------
    if raw[0:1] != b"#":
        raise ValueError("Response is not an SCPI binary block")


    nd = int(raw[1:2])                       # number of digits length
    total_len = int(raw[2:2+nd])             # payload length
    payload = raw[2+nd : 2+nd+total_len]     # WAVEDESC + data

    if payload[0:8] != b"WAVEDESC":
        raise ValueError("WAVEDESC not found at beginning of payload")
    print(payload[0:8])
    
    # helper for big-endian reads
    #def i32(off): return int.from_bytes(payload[off:off+4], byteorder='little', signed = False)
  # Helper functions
    def i16(off):
        return struct.unpack("<h", payload[off:off + 2])[0]

    def i32(off):
        return struct.unpack("<i", payload[off:off + 4])[0]

    def f32(off):
        return struct.unpack("<f", payload[off:off + 4])[0]

    def f64(off):
        return struct.unpack("<d", payload[off:off + 8])[0]

   
    
    DESC_LEN     = i32(36)
    USER_LEN     = i32(40)
    TRIG_LEN     = i32(48)     # durata blocco trig time
    WAVEARRAY_1  = i32(60)     # numero campioni

    print(f"DESC_LEN raw = {payload[36:40]}")
    print(f"USER_LEN raw = {payload[40:44]}")
    print(f"TRIG_LEN raw = {payload[44:48]}")
    print(f"WAVEARRAY_1 raw = {payload[60:64]}")
    print(f"DESC_LEN = {DESC_LEN}, USER_LEN = {USER_LEN}, TRIG_LEN = {TRIG_LEN}, WAVEARRAY_1 = {WAVEARRAY_1} ")

    VERT_GAIN    = f32(156)
    VERT_OFFSET  = f32(160)
    HORIZ_INT    = f32(176)
    HORIZ_OFF    = f32(180)
    
    print(f"VERT_GAIN raw = {payload[156:160]}")
    print(f"VERT_OFFSET raw = {payload[160:164]}")
    print(f"HORIZ_INT raw = {payload[176:180]}")
    print(f"HORIZ_OFF raw = {payload[180:184]}")
    print(f"VERT_GAIN = {VERT_GAIN}, VERT_OFFSET = {VERT_OFFSET}, HORIZ_INT = {HORIZ_INT}, HORIZ_OFF = {HORIZ_OFF} ")

    

    # --------------------------
    # 4) Find beginning of data
    # --------------------------
    # Struttura: WAVEDESC | USERTEXT | TRIGTIME | RISERVATO (4 byte) | DATA
    DATA_START = DESC_LEN + USER_LEN + TRIG_LEN + 4
    DATA_END   = DATA_START + 2 * WAVEARRAY_1   # WORD = 2 byte per campione
    
    print(f" DATA_START = {DATA_START}, DATA_END = {DATA_END}")
    data = payload[DATA_START:DATA_END]
    #return 0,0 
    print(data[:16])
    # --------------------------
    # 5) Decode ADC samples (16 bit signed, little-endian)

    # --------------------------
    #adc = np.frombuffer(data, dtype="<i2")  # > = big-endian, i2 = int16, 16 bit
    adc = np.frombuffer(data, dtype=np.int8) # 8 bit
    print(f"len of adc = {len(adc)}")
    
    # --------------------------
    # 6) # 6) Conversion to real time and voltage

    # --------------------------
    #time = HORIZ_OFF + np.arange(WAVEARRAY_1) * HORIZ_INT
    #time_axis = np.linspace(-5*tdiv, -5*tdiv + tdiv * 10, num_samples)
    voltage = VERT_GAIN * adc - VERT_OFFSET
    
    #voltage = VERT_GAIN * (adc/256) - VERT_OFFSET
    time_axis = HORIZ_OFF + np.arange(adc.size) * HORIZ_INT

    return time_axis, voltage


resource = "TCPIP0::172.16.14.23::INSTR"
channel = "C4"

rm = pyvisa.ResourceManager()
scope = rm.open_resource(resource)
scope.timeout = 20000

# imposta formato binario 16 bit
scope.write("COMM_HEADER OFF")
scope.write("COMM_FORMAT DEF9,WORD,BIN")

scope.clear()    # empty VISA buffer (very important!)
#scope.write("ARM")         # Arm the Trigger
#scope.write("FRTRIG")      # Force trigger

#time.sleep(0.2)            # piccolo delay per sicurezza

# richiedi waveform (include descriptor + data)
scope.write(f"{channel}:WF?")
raw = scope.read_raw()


hash_index = raw.find(b"#")
if hash_index == -1:
    raise ValueError("Binary block (#) not found in waveform response")
#raw = raw[hash_index:]
print (f"hash_index = {hash_index}")
print(raw[0:255])
time, volt_arr  = parse_lecroy_waveform(raw[hash_index:])

plt.figure(figsize=(10,5))
plt.plot(time*1e06, volt_arr)
plt.xlabel("Tempo (s)")
plt.ylabel("Tensione (V)")
plt.title("Forma d'onda LeCroy")
plt.grid(True)
plt.show() 
