from data_download.clients.ripe_client import RIPEClient
import tempfile
import os
from pathlib import Path
import subprocess
import sys
import concurrent.futures
import time

class PythonMRTParser:

    def __init__(self,
                 mrt_client,
                 ascii_cache_location=False,
                 logging=False,
                 debug=False,
                 max_concurrent_threads=1,
                 ):
        
        if ( not isinstance(mrt_client, RIPEClient)):
            raise Exception(f"The argument mrt_client is mandatory and must to be RIPEClient type. Instead {type(mrt_client)} was provided.")
        self.client = mrt_client

        self.logging = logging
        self.debug = debug
        self.max_concurrent_threads = int(max_concurrent_threads)

        #Checking if logging has a valid value
        if not (self.logging==False or (hasattr(self.logging, 'basicConfig') and hasattr(self.logging.basicConfig, '__call__'))):
            raise Exception('The logging parameters need to be a valid logging object or False')

        # This attribute stores the tmp_object
        self.tmp = False

        # Mapping possible cache location passed
        if (ascii_cache_location):
            #To-do: check if the location exists and it is writeable
            self.work_dir = ascii_cache_location
        else:
            #Creating a unique temp dir (when cache feature is disabled)
            with tempfile.TemporaryDirectory(prefix=f"bgptools_") as tmp_dirname:
                # If a tmp directory will be used it will be linked 
                # in this attribute to be cleaned at the end of the execution
                self.tmp = tmp_dirname
                self.work_dir = tmp_dirname
                self.log_info(f"created temporary directory: {tmp_dirname}")
                
        self.work_dir += f"/{self.client.TYPE}"

        # Creating the work directory if not exists
        if not os.path.exists(self.work_dir):
            self.log_info("Creating the ASCII directory: " + self.work_dir)
            self.create_path_if_not_exists(self.work_dir)

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

    # def cleanup(self):
    #     if self.tmp:
    #         self.log_info(f"Cleanup the tmp dir at {self.tmp}")
    #         self.tmp.cleanup()

    def create_path_if_not_exists(self,path):
        try:
            if not os.path.exists(path):
                self.log_info('Creating dir: ' + path)
                path = Path(path)
                path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            self.log_error('Failure when creating the dir: ' + path)
            return False

    def parse_file(self, file_dict):

        if not file_dict['internal_path']:
            raise Exception('File dict need to have the internal_path index')

        file_path = file_dict['file_path']
        internal_path_out = file_dict['internal_path'].replace('.gz', '.parse')
        file_path_out = self.work_dir + internal_path_out

        #Creating dir if not exists
        head, tail = os.path.split(file_path_out)
        self.create_path_if_not_exists(head)

        path_zebra = os.path.dirname(os.path.abspath(__file__))
        cmd = f"zcat < {file_path} | {path_zebra}/zebra-dump-parser-modified.pl > {file_path_out}"
        #print(f"executing the command: {cmd}")
        
        try:
            start_parse_time = time.perf_counter()
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)
        except subprocess.CalledProcessError as e:
            self.log_error(
                'Error during parse file: {}. return code: {}. stderr: {}. stdout: {}.'.format(
                    file_path,
                    e.returncode,
                    e.stderr.decode(sys.getfilesystemencoding()),
                    e.output.decode(sys.getfilesystemencoding()),
                    )
            )
            return False
            # print('stdout: {}'.format())
            
        #Checking if the path exists
        if os.path.exists(file_path_out):
            finish_parse_time = time.perf_counter()
            file_stats = os.stat(file_path_out)
            # return file_path_out
            return {"parsed_file_path": file_path_out, "parsed_internal_path": internal_path_out, "parsing_time": finish_parse_time-start_parse_time, "parsed_file_size_in_bytes": file_stats.st_size }
        else:
            self.log_error('Parsed file was not found in: ' + file_path_out)            

    def parse_files(self, file_dicts):

        if self.max_concurrent_threads > 0:
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_threads) as executor:
                    for result in executor.map(self.parse_file, file_dicts):
                        yield result
            except Exception as err:
                self.log_error(f"Error during parser err={err}, {type(err)=}")

        
        
