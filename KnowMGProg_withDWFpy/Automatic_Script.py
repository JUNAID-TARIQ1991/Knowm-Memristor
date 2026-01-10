import subprocess
import os

# Get the current directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the vector of conductance values
conductance_values = [20, 40, 60, 80]

# Define the set of commands to run
for i, conductance in enumerate(conductance_values, start=1):
    command = ["python3", os.path.join(script_dir, "MainProgram_iteration.py"), "set", str(i), str(conductance), "1"]

    # Try to execute the command once, if it fails, repeat once
    attempt = 0
    success = False
    
    while attempt < 2 and not success:  # Try up to 2 times
        try:
            # Run the command with dynamic values
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            
            # Check the result from the executed command
            if "True" in result.stdout:  # Assuming the main program outputs 'True' when successful
                print(f"Successfully ran: {' '.join(command)}")
                success = True
            else:
                print(f"Failed attempt {attempt + 1}. Retrying...")
                attempt += 1
        except subprocess.CalledProcessError as e:
            print(f"Error running: {' '.join(command)}\n{e}")
            break  # If there's a subprocess error, break out of the loop
