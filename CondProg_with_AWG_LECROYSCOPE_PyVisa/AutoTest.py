import subprocess
import sys
import re
MAIN_PROGRAM = "MainProgram_Mod16_02_2026.py"
# This script runs a series of automated tests on the MainProgram_Mod13_02_2026A.py, covering set, read, and compute operations.
def run_command(args, capture_output=False): # build the command list and run it, return success status and output if captured
    cmd = ["python", MAIN_PROGRAM] + args
    print(f"\n[AutoTest] Running: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True
    )

    if result.returncode != 0:
        print(f"[AutoTest]  Command failed (code={result.returncode})")
        return False, None

    return True, result.stdout


# ---------------- USER CONFIG ----------------
exit_mode = "after-stability"        # early | after-stability | none, by default after-stability, but for faster testing you can set it to early to exit immediately 
#after reaching target without waiting for stability reads.
# # Set to "none" to disable auto-exit and always wait for all stability reads (useful for debugging stability behavior).
plot_live = True
max_attempts = 10
# ---------------- TEST VECTORS ----------------
conductance_values = [90, 130, 160, 200] # in µS, for set phase
voltage_sets = [
[0.04,   0.06,   0.08,  0.10 ],		
[0.05,   0.075,  0.110,  0.140 ],		
[0.065,   0.095,  0.120,  0.150 ],		
[0.040,   0.090,  0.130,  0.135 ],		
[0.055,   0.070,  0.100,  0.125 ],		
[0.085,   0.045,  0.140,  0.150 ],		
[0.120,  0.150,   0.060,   0.040 ],		
[0.100,  0.130,  0.150,  0.110 ],		
[0.150,  0.100,   0.070,   0.045 ],		
[0.140,  0.120,   0.090,   0.060 ],		

]


# ---------------- SET PHASE ----------------
print("\n========== AUTO TEST: SET PHASE ==========")

for idx, G in enumerate(conductance_values, start=1): # python MainProgram_Mod06_02_2026.py set <channel> <target_G> <max_attempts> --exit early --plot-live

    args = [
        "set",
        str(idx),
        str(G),
        str(max_attempts),
        "--exit", exit_mode,
        
    ]

    if plot_live:
        args.append("--plot-live")

    ok = run_command(args)

    if not ok:
        print(f"[AutoTest]  SET failed at row {idx}, G={G} µS")
        sys.exit(1)

print("\n[AutoTest]  All SET operations completed")

#---------------- READ PHASE ----------------
print("\n========== AUTO TEST: READ PHASE ==========")

G_read = []

for ch in range(1, 5):
    ok, output = run_command(["read", str(ch)], capture_output=True)

    if not ok:
        print(f"[AutoTest]  READ failed on channel {ch}")
        sys.exit(1)

    for line in output.splitlines(): # print each line to debug
        print(line)

        if "Conductance of channel" in line:
            # Example line:
            # Conductance of channel: 1 =  123.45 µS Corresponding to ...
            import re

            line = line.strip() # remove leading/trailing whitespace for safety
            val = float(re.search(r"([\d.]+)", line).group(1)) # extract the first number (conductance value) from the line, 
            #val = float(line.split("=")[1].split("µS")[0])
            G_read.append(val)

if len(G_read) != 4:
    print("[AutoTest]  ERROR: Did not read 4 conductance values")
    sys.exit(1)


# ---------------- COMPUTE PHASE ----------------
print("\n========== AUTO TEST: COMPUTE PHASE ==========")

for i, V in enumerate(voltage_sets, start=1):
    print(f"\n[AutoTest] Compute {i}/{len(voltage_sets)}") 

    args = ["compute"] + list(map(str, V)) # 

    ok = run_command(args)

    if not ok:
        print("[AutoTest]  COMPUTE failed")
        sys.exit(1)

print("\n[AutoTest]  All COMPUTE tests completed")
