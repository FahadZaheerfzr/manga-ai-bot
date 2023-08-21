import subprocess
import time
import logging

def run_script():
    # Configure logging
    logging.basicConfig(filename='error.log', level=logging.ERROR,
                        format='%(asctime)s %(levelname)s: %(message)s')

    while True:
        # Start the script as a subprocess
        script_process = subprocess.Popen(['python3', 'main.py'],
                                          stderr=subprocess.PIPE)
        
        # Wait for the script to finish
        script_process.wait()
        
        # If the script exited normally (return code 0), break the loop
        if script_process.returncode == 0:
            break
        
        # Log the error
        stderr = script_process.stderr
        if stderr is not None:
            error_message = stderr.read().decode('utf-8').strip()
            logging.error(error_message)
        
        print("Script stopped. Restarting...")
        time.sleep(5)  # Wait for 5 seconds before restarting

run_script()
