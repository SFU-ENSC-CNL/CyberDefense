import json
import requests
from pathlib import Path
import logging
import os
import utils

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

class NetScienceClient:

    API_AUTH_ENDPOINT = 'rpc/login'
    API_CATCH_TASK_ENDPOINT = 'rpc/catch_task'
    API_TASK_ENDPOINT = 'tasks'
    API_EXPERIMENTS_ENDPOINT = 'experiments'
    TASK_JSON_FILENAME = 'task.json'
    TASK_STDOUT_FILENAME = 'stdout.log'

    def __init__(self,
                 base_url,
                 username,
                 password,
                 task_base_path,
                 logging=False,
                 debug=False
                 ):
        
        self.base_url = base_url
        self.logging = logging
        self.debug = debug
        self.token = False
        self.task_base_path = task_base_path
        self.create_path_if_not_exists(self.task_base_path)

        self.username = username
        self.password = password
        
        #Checking if logging has a valid value
        if not (self.logging==False or (hasattr(self.logging, 'basicConfig') and hasattr(self.logging.basicConfig, '__call__'))):
            raise Exception('The logging parameters need to be a valid logging object or False')

    def log_info(self, msg):
        if self.logging: self.logging.info(msg)
        if self.debug: print(msg)
    
    def log_error(self, msg):
        if self.logging: self.logging.error(msg)
        if self.debug: print(msg)
        
    def log_warning(self, msg):
        if self.logging: self.logging.warning(msg)
        if self.debug: print(msg)

    def log_debug(self, msg):
        if self.logging: self.logging.debug(msg)
        if self.debug: print(msg)

    def do_auth(self):

        headers= {
            'Content-Profile': 'public',
            'Cache-Control': 'no-cache'
        }

        data = {
        "email": self.username,
        "pass": self.password
        }

        # sending post request and saving response as response object
        r = requests.post(url=f"{self.base_url}/{self.API_AUTH_ENDPOINT}", data=data, headers=headers)
        response_data = json.loads(r.text)

        if (r.status_code != 200):
            raise Exception(f"Some problem occurred during the authentication. Code: {r.status_code}. Message: {response_data['message']}.")


        if (response_data['token']):
            self.token = response_data['token']
            return response_data['token']
        else:
            raise Exception(f"The expected token was not present in the response. Instead was received: {response_data['message']}")

    def check_authentication(self):
        # Firstly, check if the instance already has a token
        # If not, try to authenticate
        if not (self.token or self.do_auth()):
            raise Exception(f"Was not possible to authenticate. See the logs.")
        
        return True
    
    def catch_task(self, task_type, allow_retry=True):

        # If dont have a token to the authentication first
        self.check_authentication()

        headers = {
            'Authorization': f"Bearer {self.token}",
            'Cache-Control': 'no-cache'
        }

        data = {
            "tasktype": task_type
        }

        # sending post request and saving response as response object
        r = requests.post(url=f"{self.base_url}/{self.API_CATCH_TASK_ENDPOINT}", data=data, headers=headers)
        response_data = json.loads(r.text)

        if (r.status_code != 200 and r.status_code != 401):
            raise Exception(f"Some unexpected problem occurred during the task catching. Code: {r.status_code}. Message: {response_data['message']}.")

        # Repeating the operation just if: JWT expired and is allowed retry and was possible to authenticate
        if (r.status_code == 401 and allow_retry and self.do_auth()):
            # allow_retry = false => Repeating just one time
            return self.catch_task(task_type, False)
        
        if (len(response_data) > 0):
            task = response_data[0]
            self.initialize_dir(task['id'])
            self.reset_task_json(task['id'])
            self.reset_stdout(task['id'])
            self.write_input_file(task)
            return task
        else:
            return False
    
    def update_task_finished(self, task, return_code, allow_retry=True):

        self.check_authentication()

        headers= {
            'accept': 'application/json',
            'Prefer': 'return=representation',
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.token}",
            'Cache-Control': 'no-cache'
        }

        data = {
            "finished_at": "now()",
            "return_code": return_code
        }

        # sending post request and saving response as response object
        r = requests.patch(url=f"{self.base_url}/{self.API_TASK_ENDPOINT}?id=eq.{task['id']}", json=data, headers=headers)
        response_data = json.loads(r.text)

        if (r.status_code != 200 and r.status_code != 401):
            raise Exception(f"Some unexpected problem occurred during the task catching. Code: {r.status_code}. Message: {response_data['message']}.")

        # Repeating the operation just if: JWT expired and is allowed retry and was possible to authenticate
        if (r.status_code == 401 and allow_retry and self.do_auth()):
            # allow_retry = false => Repeating just one time
            return self.update_task_finished(task, return_code, False)
            
        if (len(response_data) > 0):
            task = response_data[0]
            return task
        else:
            return False
        
    
    def initialize_dir(self, taskId):
        path = f"{self.task_base_path}/{taskId}"
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            utils.rm_folder_content(path)
    
    def reset_task_json(self, taskId):
        path = f"{self.task_base_path}/{taskId}/{self.TASK_JSON_FILENAME}"
        if os.path.exists(path):
            os.remove(path)
    
    def reset_stdout(self, taskId):
        path = f"{self.task_base_path}/{taskId}/{self.TASK_STDOUT_FILENAME}"
        if os.path.exists(path):
            os.remove(path)

    def write_input_file(self, task):
        path = f"{self.task_base_path}/{task['id']}/{self.TASK_JSON_FILENAME}"
        try:
            with open(path, "w") as outfile:
                outfile.write(json.dumps(task, indent=2))
                outfile.close()
            return True
        except IOError:
            raise Exception("Failure while writing file: " + path)
        
    def create_path_if_not_exists(self,path):
        try:
            if not os.path.exists(path):
                self.log_info('Creating dir: ' + path)
                path = Path(path)
                path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            msg='Failure when creating the dir: ' + path
            self.log_error(msg)
            raise Exception(msg)
        
    def get_experiment(self, id):

        # If dont have a token to the authentication first
        self.check_authentication()

        headers = {
            'Authorization': f"Bearer {self.token}",
            'Cache-Control': 'no-cache'
        }

        data = {
            "id": id
        }

        # sending get request and saving response as response object
        r = requests.get(url=f"{self.base_url}/{self.API_EXPERIMENTS_ENDPOINT}", data=data, headers=headers)
        response_data = json.loads(r.text)

        if (r.status_code != 200 and r.status_code != 401):
            raise Exception(f"Some unexpected problem occurred during the task catching. Code: {r.status_code}. Message: {response_data['message']}.")

        # Repeating the operation just if: JWT expired and is allowed retry and was possible to authenticate
        if (r.status_code == 401 and allow_retry and self.do_auth()):
            # allow_retry = false => Repeating just one time
            return self.get_experiment(id)
        
        if (len(response_data) > 0):
            experiment = response_data[0]
            return experiment
        else:
            return False