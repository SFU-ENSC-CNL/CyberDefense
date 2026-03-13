from data_download.clients.ripe_client import RIPEClient
import tempfile
import os
from pathlib import Path
import subprocess
import sys
import concurrent.futures
import time

class BGPCPlusPlusFeatureExtraction:

    def __init__(self,
                 logging=False,
                 debug=False,
                 features_cache_location=False,
                 max_concurrent_threads=1,
                 ):
        
        self.logging = logging
        self.debug = debug
        self.max_concurrent_threads = int(max_concurrent_threads)

        #Checking if logging has a valid value
        if not (self.logging==False or (hasattr(self.logging, 'basicConfig') and hasattr(self.logging.basicConfig, '__call__'))):
            raise Exception('The logging parameters need to be a valid logging object or False')

        # This attribute stores the tmp_object
        self.tmp = False

        # Mapping possible cache location passed
        if (features_cache_location):
            #To-do: check if the location exists and it is writeable
            self.work_dir = features_cache_location
        else:
            #Creating a unique temp dir (when cache feature is disabled)
            with tempfile.TemporaryDirectory(prefix=f"features_") as tmp_dirname:
                # If a tmp directory will be used it will be linked 
                # in this attribute to be cleaned at the end of the execution
                self.tmp = tmp_dirname
                self.work_dir = tmp_dirname
                self.log_info(f"created temporary directory: {tmp_dirname}")
                
        # Creating the work directory if not exists
        if not os.path.exists(self.work_dir):
            self.log_info("Creating the Features directory: " + self.work_dir)
            os.makedirs(self.work_dir)

    def log_info(self, msg):
        if self.logging: self.logging.info(msg)
        if self.debug: print(f"{msg}\n")
    
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

    def extract_features_from_file(self, file_dict):

        if not file_dict['internal_path']:
            self.log_warning('To extract features file dict need to have the parsed_internal_path index.')
            return False

        file_path = file_dict['file_path']
        internal_path_out = file_dict['internal_path'].replace('.gz', '.features')
        file_path_out = self.work_dir + internal_path_out

        #Creating dir if not exists
        head, tail = os.path.split(file_path_out)
        self.create_path_if_not_exists(head)

        #export DYLD_LIBRARY_PATH=/opt/bgp_research_tools/src/feature_extraction/mrtprocessor/lib
        #time ./mrtprocessor -T -o DATASET.csv -f /var/netscience/cache/mrt/ripe/rrc00/2005.05/updates.*.gz

        path_cplusplus_tool = os.path.dirname(os.path.abspath(__file__)) + "/mrtprocessor"
        cmd = \
            f"export DYLD_LIBRARY_PATH={path_cplusplus_tool}/lib ; " +\
            f"{path_cplusplus_tool}/bin/mrtprocessor " +\
            f"-np -T -o {file_path_out} -f {file_path}"
        print(f"{cmd}\n")
        try:
            start_extract_time = time.perf_counter()
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)
            # print(cmd)
        except subprocess.CalledProcessError as e:
            print(f"Error output: {output}")
            self.log_error(
                'Error during extracting feature file: {}. return code: {}. stderr: {}. stdout: {}. output: {}'.format(
                    file_path,
                    e.returncode,
                    e.stderr.decode(sys.getfilesystemencoding()),
                    e.output.decode(sys.getfilesystemencoding()),
                    "", #output
                    )
            )
            # self.remove_parse_file(file_path)
            # return False
            # print('stdout: {}'.format())

        # Checking if the file was created
        if os.path.exists(file_path_out):
            finish_extract_time = time.perf_counter()
            # return file_path_out
            file_stats_in = os.stat(file_path)
            file_stats_out = os.stat(file_path_out)
            # self.remove_parse_file(file_path)
            return {"file_path": file_path_out, "internal_file_path": internal_path_out, "extraction_time_in_seconds": finish_extract_time-start_extract_time, "extraction_fileout_size_in_bytes": file_stats_out.st_size, "extraction_filein_size_in_bytes": file_stats_in.st_size}
        else:
            msg='ERROR: File with extracted features was not found in: ' + file_path_out
            print(msg)
            self.log_error(msg)

    def extract_features_from_files(self, files_dict, file_path_out, filter_by_asn=[], filter_by_ipv4=[],filter_by_ipv6=[]):

        input_files = []
        #Checking files_dict and creating input_files
        for file_dict in files_dict:

            if not file_dict['internal_path']:
                self.log_warning('To extract features file dict need to have the parsed_internal_path index.')
                return False

            input_files.append(file_dict['file_path'])
        
        #Creating dir if not exists
        head, tail = os.path.split(file_path_out)
        self.create_path_if_not_exists(head)

        path_cplusplus_tool = os.path.dirname(os.path.abspath(__file__)) + "/mrtprocessor"
        
        cmd = \
            f"export DYLD_LIBRARY_PATH={path_cplusplus_tool}/lib ; " +\
            f"{path_cplusplus_tool}/bin/mrtprocessor " +\
            f"-T -o {file_path_out} " + \
            (f"-asnfilt \"{':'.join(filter_by_asn)}\" " if len(filter_by_asn) > 0 else "")+ \
            (f"-nlriv4filt \"{','.join(filter_by_ipv4)}\" " if len(filter_by_ipv4) > 0 else "")+ \
            (f"-nlriv6filt \"{','.join(filter_by_ipv6)}\" " if len(filter_by_ipv6) > 0 else "")+ \
            f"-f {' '.join(input_files)}"
        
        print(f" ⚡️ MRTprocessor CMD: {cmd}\n")
        try:
            start_extract_time = time.perf_counter()
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)
            # print(cmd)
        except subprocess.CalledProcessError as e:
            self.log_error(
                'Error during extracting feature file: {}. return code: {}. stderr: {}. stdout: {}. output: {}'.format(
                    file_path_out,
                    e.returncode,
                    e.stderr.decode(sys.getfilesystemencoding()),
                    e.output.decode(sys.getfilesystemencoding()),
                    "", #output
                    )
            )
            # self.remove_parse_file(file_path)
            # return False
            # print('stdout: {}'.format())

        # Checking if the file was created
        if os.path.exists(file_path_out):
            finish_extract_time = time.perf_counter()
            # return file_path_out
            file_stats_out = os.stat(file_path_out)
            # self.remove_parse_file(file_path)
            return {"file_path": file_path_out, "extraction_time_in_seconds": finish_extract_time-start_extract_time, "extraction_fileout_size_in_bytes": file_stats_out.st_size}
        else:
            msg='ERROR: File with extracted features was not found in: ' + file_path_out
            print(msg)
            self.log_error(msg)
        

    # Extract features using Python managed parallelism
    def extract_features_from_files_with_external_parallelism(self, file_dicts):

        if self.max_concurrent_threads > 0:
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_threads) as executor:
                    for result in executor.map(self.extract_features_from_file, file_dicts):
                        yield result
            except Exception as err:
                self.log_error(f"Error during extracting features err={err}, {type(err)=}")

    def remove_parse_file(self, parse_filepath):
        #self.log_info(f"Removing parse file {parse_filepath}")
        return os.remove(parse_filepath)  
        
