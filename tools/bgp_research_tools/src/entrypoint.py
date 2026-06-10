from dotenv import dotenv_values
from netscience_client import NetScienceClient
import logging
import time
import subprocess
import sys
import os
import utils

# LOADING ENV FILE
netscience_path = './netscience.env'
if not os.path.exists(netscience_path):
    msg=f"ABORTING: were not found the netscience environment file at: {netscience_path}"
    logging.error(msg)
    sys.exit(msg)

netscience_config = dotenv_values(netscience_path)

INTERVAL_DURING_TASK_CATCHING=10

# LOGGING setup
logging.basicConfig(
    filename='netscience.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

client = NetScienceClient(netscience_config['BASE_URL'], netscience_config['USERNAME'], netscience_config['PASSWORD'],netscience_config['TASKS_BASE_PATH'], logging=logging)
counter=0

print(" 🚚 Task catcher service started. ")

while True:
    task = client.catch_task('BGPAnomaly')
    
    if (task):
        print(f" ✅ New {task['pipeline']} task found.")
        task_working_dir = f"{netscience_config['TASKS_BASE_PATH']}/{task['id']}"
        #Preparing TASKS folder
        if utils.create_path_if_not_exists(task_working_dir):
            logging.info(f"Was created the filesystem structure at {task_working_dir}")

        stdout_path = f"{task_working_dir}/stdout.log"
        print(f" ✅ Writing output in: {stdout_path}")

        # Executing python script without stdout buffer
        if task['pipeline'] == 'dataset':
            command = f"python3 -u {os.getcwd()}/src/dataset_runner.py"
        
        elif task['pipeline'] == 'experiment':
            command = f"python3 -u {os.getcwd()}/src/experiment_runner.py"
        
        # Specify the file where you want to redirect the output
        output_file = f"{task_working_dir}/stdout.log"

        # Open the file in write mode (overwriting previous content if exists)
        with open(output_file, "w") as file:
            # Create a subprocess with stdout redirected to a file and tee'd to the console
            process = subprocess.Popen(
                f"{command} | tee -a {output_file}",
                shell=True,
                stdout=subprocess.PIPE,
                # stderr=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=task_working_dir
            )

            # Read and print the output in real-time
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                print(line, end="")

        # Wait for the subprocess to complete
        process.wait()

        # Optionally, you can check the return code of the subprocess
        return_code = process.returncode
        print(f"Subprocess exited with return code {return_code}")
        updated = client.update_task_finished(task, return_code)
        if updated:
            print(f"Task {updated['id']} finished_at attribute updated {updated['finished_at']}")

    #else:
    #    print(f" 🕣  No pending tasks found. Checking again in {INTERVAL_DURING_TASK_CATCHING} seconds.")
    
    time.sleep(INTERVAL_DURING_TASK_CATCHING)
    






