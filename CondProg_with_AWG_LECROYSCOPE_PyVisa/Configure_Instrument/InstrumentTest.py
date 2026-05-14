# import pyvisa

# rm = pyvisa.ResourceManager()
# resources = rm.list_resources()
# print("Resources:", resources)

# print("\n--- Testing AWG ---")
# awg = rm.open_resource("TCPIP::172.16.9.59::INSTR")
# print(awg.query("*IDN?"))

# print("\n--- Testing LeCroy ---")
# scope = rm.open_resource("TCPIP::172.16.5.178::INSTR")
# print(scope.query("*IDN?"))
# for r in resources:
#     try:
#         inst = rm.open_resource(r)
#         print(r, "->", inst.query("*IDN?").strip())
#     except:
#         pass