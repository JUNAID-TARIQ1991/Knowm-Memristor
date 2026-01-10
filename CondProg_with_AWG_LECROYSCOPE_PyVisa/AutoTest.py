import subprocess

# Function to run the command with given arguments
def run_command(action, *args):
    command = ["python", "./MainProgram_LUT_alphaonly.py", action] + list(map(str, args))
    subprocess.run(command)

# Define the list of conductance values
conductance_values = [50, 60, 100, 120]
voltages1 = [0.02, 0.025, 0.055, 0.06]
voltages2 = [0.025, 0.030, 0.060, 0.065]
voltages3 = [0.030, 0.035, 0.065, 0.070]
voltages4 = [0.035, 0.040, 0.070, 0.075]
voltages5 = [0.040, 0.045, 0.075, 0.080]
voltages6 = [0.045, 0.050, 0.080, 0.090]
voltages7 = [0.050, 0.055, 0.085, 0.1]
voltages8 = [0.1, 0.090, 0.05, 0.02]
voltages9 = [0.09, 0.080, 0.06, 0.03]
voltages10 = [0.08, 0.070, 0.075, 0.04]
# Loop through each conductance value and execute the "set" command
for i, conductance in enumerate(conductance_values, start=1):
    run_command("set", i, conductance, 1)

# After setting conductance values, run the "compute" action with the given voltages

run_command("compute", *voltages1)
run_command("compute", *voltages2)
run_command("compute", *voltages3)
run_command("compute", *voltages4)
run_command("compute", *voltages5)
run_command("compute", *voltages6)
run_command("compute", *voltages7)
run_command("compute", *voltages8)
run_command("compute", *voltages9)
run_command("compute", *voltages10)