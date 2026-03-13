import os
from pathlib import Path
import shutil

def print_task_parameters(task):
        print("  → {:<30} {:<30}".format('Parameter','Value'))
        for param, value in task['parameters'].items():
            if value is None: value = ""
            print("  → {:<30} {:<30}".format(param, value))

def print_generic_parameters(params):
        print("  → {:<30} {}".format('Parameter','Value'))
        for param, value in params.items():
            if value is None: value = ""
            print("  → {:<30} {}".format(param, value))

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def rm_folder_content(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

def create_path_if_not_exists(path):
        try:
            if not os.path.exists(path):
                # self.log_info('Creating dir: ' + path)
                path = Path(path)
                path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            # self.log_error('Failure when creating the dir: ' + path)
            return False