from dotenv import dotenv_values
import json
import os
import utils
from datetime import datetime
from math import floor, ceil
import json
import sys
import time
import logging
import shutil
import multiprocessing
import humanize
import socket
import re

#Configuração de LOGGING
logging.basicConfig(
    filename=f"bgpresearch.log",
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

app_path = f"{os.path.dirname(__file__)}"

# lib_path = f"{os.path.dirname(__file__)}/../"
# print(lib_path)
# sys.path.append(lib_path)
# print(sys.path)

from data_download.clients.ripe_client import RIPEClient
from data_parse.python_mrt_parser import PythonMRTParser
from feature_extraction.bgp_csharp_feature_extraction import BGPCSharpFeatureExtraction
from feature_extraction.bgp_cplusplus_feature_extraction import BGPCPlusPlusFeatureExtraction
from data_merging.merge_files import merge_files
from data_labeling.anomalous_and_regular_data_labeling import AnomalousAndRegularDataLabeling

# LOADING ENV FILE
netscience_path = f"{app_path}/../netscience.env"
if not os.path.exists(netscience_path):
    msg=f"ABORTING: were not found the netscience environment file at: {netscience_path}"
    logging.error(msg)
    sys.exit(msg)

uname = os.uname()
print(f" 🖥️ Node Hostname: {uname.nodename}")
print(f"    Sysname: {uname.sysname}")
print(f"    Release: {uname.release}")
print(f"    Version: {uname.version}")
print(f"    Arch: {uname.machine}")

number_of_cores = multiprocessing.cpu_count()
print(f" 🧠 Detected number of CPU cores: {number_of_cores}")

netscience_config = dotenv_values(netscience_path)
print(f" 💼 Netscience User: {netscience_config['USERNAME']}")

task_working_dir = os.getcwd()
print(f" 📂 Starting dataset task on CWD: {task_working_dir}")

today = datetime.today()
print(f" 🕣 Starting time: {today}")

file = open('task.json')
task = json.load(file)

print(f" 🔑 Task key: {task['id']}")
print(f" ⚙️ Task parameters (before parsing):")
utils.print_task_parameters(task)

p = task['parameters']

date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

# Preparing the parameters
collection_site = p['collection_site']
ripe_ris_rrc = p['ripe_ris_rrc']

date_start = p['date_start']
time_start = p['time_start']
date_end = p['date_end']
time_end = p['time_end']

anomalous_date_start = p['anomalous_date_start']
anomalous_date_end = p['anomalous_date_end']

anomalous_time_start = p['anomalous_time_start']
anomalous_time_end = p['anomalous_time_end']

fe_system = p['fe_system']

filter_asn = False if ('filter_asn' not in p or p['filter_asn'] is None) else p['filter_asn']
filter_ipv4 = False if ('filter_ipv4' not in p or p['filter_ipv4'] is None) else p['filter_ipv4']
filter_ipv6 = False if ('filter_ipv6' not in p or p['filter_ipv6'] is None) else p['filter_ipv6']

filter_asn = str(filter_asn).split(":") if filter_asn else []
filter_ipv4 = str(filter_ipv4).split(",") if filter_ipv4 else []
filter_ipv6 = str(filter_ipv6).split(",") if filter_ipv6 else []

cache_path = netscience_config['CACHE_BASE_PATH'] if p['cache'] == 'activated' else False
debug = True if p['debug'] == 'activated' else False

print('')

datetime_start = datetime.strptime(f"{date_start}T{time_start}00", "%Y%m%dT%H%M%S")
datetime_end = datetime.strptime(f"{date_end}T{time_end}59", "%Y%m%dT%H%M%S")

anomalous_datetime_start = datetime.strptime(f"{anomalous_date_start}T{anomalous_time_start}00", "%Y%m%dT%H%M%S")
anomalous_datetime_end = datetime.strptime(f"{anomalous_date_end}T{anomalous_time_end}59", "%Y%m%dT%H%M%S")

params = {
    'collection_site': collection_site,
    'ripe_ris_rrc': ripe_ris_rrc,
    'datetime_start': datetime_start,
    'datetime_end': datetime_end,
    'anomalous_datetime_start': anomalous_datetime_start,
    'anomalous_datetime_end': anomalous_datetime_end,
    'fe_system': fe_system,
    'filter_asn': filter_asn,
    'filter_ipv4': filter_ipv4,
    'filter_ipv6': filter_ipv6,
    'cache_path': cache_path,
    'debug': debug

}

print(f" ⚙️ Task parameters (after parsing):")
utils.print_generic_parameters(params)

print('')

print(f" 📂 Cache path on: {cache_path}")

print('')

if os.path.exists(cache_path):
    #shutil.rmtree(cache_path)
    ascii_path = f"{cache_path}/ascii"
    if os.path.exists(ascii_path): shutil.rmtree(ascii_path)
    features_path = f"{cache_path}/features"
    if os.path.exists(features_path): shutil.rmtree(features_path)

client = RIPEClient(cacheLocation=f"{cache_path}/mrt",
                    logging=logging,
                    debug=False,
                    max_concurrent_requests=64)

# Downloading Files

start_download_time = time.perf_counter()
# Generator
files = client.download_updates_interval_files(datetime_start,
                                            datetime_end, int(ripe_ris_rrc))
# The files are returned as they are being generated using yield
t = 0
from_download=0
from_cache=0
download_error=0
bytes_from_remote=0
bytes_from_cache=0
downloaded_files = []
for file in files:
    t+=1
    if file:
        # filename = os.path.basename(file)
        #print(f"File ready: {filename}")
        if file['source']=='remote':
            from_download+=1
            bytes_from_remote+=file['file_size_in_bytes']
            print(f"File {file['file_path']} of {humanize.naturalsize(file['file_size_in_bytes'])} were downloaded in {file['download_time_in_seconds']} seconds.")
        else:
            from_cache+=1
            bytes_from_cache+=file['file_size_in_bytes']
            print(f"File {file['file_path']} of {humanize.naturalsize(file['file_size_in_bytes'])} were retrieved from cache in no time.")
        
        downloaded_files.append(file)        

print('')

finish_download_time = time.perf_counter()
print(f"Were obtained {from_download+from_cache} of {t} files totaling {humanize.naturalsize(bytes_from_remote+bytes_from_cache)}  in {finish_download_time-start_download_time:.2f} seconds using {client.max_concurrent_requests} concurrent requests.")
print(f"{from_download} files were downloaded ({humanize.naturalsize(bytes_from_remote)}) and {from_cache} were obtained from cache, avoiding download {humanize.naturalsize(bytes_from_cache)}.")

if fe_system == 'c_sharp':

    #When using CSharp Tool are required two separated steps: parsing and feature extraction
    #Parsing using CSharp Tool

    parser = PythonMRTParser(ascii_cache_location=f"{cache_path}/ascii",
                    logging=logging,
                    mrt_client=client,
                    debug=False,
                    max_concurrent_threads=number_of_cores)

    start_parse_time = time.perf_counter()

    # Generator
    files_parsed = parser.parse_files(downloaded_files)

    # The files are returned as they are being generated using yield
    parse_i = 0
    parse_t = 0
    bytes_parsed=0
    parsed_files = []
    for file_parsed in files_parsed:
        parse_t+=1
        if file_parsed:
            # filename = os.path.basename(file)
            #print(f"File ready: {filename}")
            bytes_parsed+=file_parsed['parsed_file_size_in_bytes']
            print(f"ASCII file created at {file_parsed['parsed_file_path']} with {humanize.naturalsize(file_parsed['parsed_file_size_in_bytes'])} in {file_parsed['parsing_time']} seconds.")
            parsed_files.append(file_parsed)
            parse_i+=1

    finish_parse_time = time.perf_counter()
    print(f"Were parsed {parse_i} of {parse_t} files totaling {humanize.naturalsize(bytes_parsed)} in {finish_parse_time-start_parse_time:.2f} seconds using {parser.max_concurrent_threads} threads.")

    # Extracting Features
    extractor = BGPCSharpFeatureExtraction(features_cache_location=f"{cache_path}/features",
                        logging=logging,
                        debug=True,
                        max_concurrent_threads=number_of_cores
    )

    start_extract_time = time.perf_counter()

    files_extract = extractor.extract_features_from_files(parsed_files)

    # The files are returned as they are being generated using yield
    extract_i = 0
    extract_t = 0
    bytes_extracted=0
    extracted_files = []
    for file_extract in files_extract:
        extract_t+=1
        if file_extract:
            # filename = os.path.basename(file)
            #print(f"File ready: {filename}")
            bytes_extracted+=file_extract['extraction_fileout_size_in_bytes']
            print(f"Features file created at {file_extract['file_path']} with (Input: {humanize.naturalsize(file_extract['extraction_filein_size_in_bytes'])} / Output: {humanize.naturalsize(file_extract['extraction_fileout_size_in_bytes'])}) in {file_extract['extraction_time_in_seconds']} seconds.")
            extracted_files.append(file_extract)
            extract_i+=1

    finish_extract_time = time.perf_counter()
    print(f"Were extracted {extract_i} of {extract_t} files totaling {humanize.naturalsize(bytes_extracted)}  in {finish_extract_time-start_extract_time:.2f} seconds using {extractor.max_concurrent_threads} threads.")
    #Finished feature extraction using CSharp Tool

elif fe_system == 'c_plusplus':
    #When using CPlusplus Tool are required just one step to parse and extract features
    
    # Extracting Features
    extractor = BGPCPlusPlusFeatureExtraction(features_cache_location=f"{cache_path}/features",
                        logging=logging,
                        debug=True,
                        max_concurrent_threads=number_of_cores
    )

    start_extract_time = time.perf_counter()

    print(f"Splitting the downloaded files in chunks per day")
    buckets = client.split_downloaded_files_in_buckets_per_day(downloaded_files)
    extracted_files = []
    extract_i=0
    extract_t=len(buckets.items())
    for key, bucket in buckets.items():
        file_path_out = bucket[0]['file_path']
        file_path_out = file_path_out.replace('mrt', 'features')
        file_path_out = re.sub('\.\d{4}\.gz', '.features', file_path_out)
        print(f"Extracting {len(bucket)} files of the bucket {key} and writing in {file_path_out}")
        file_extract = extractor.extract_features_from_files(bucket, file_path_out, filter_asn, filter_ipv4, filter_ipv6)
        if file_extract:
            extracted_files.append(file_extract)
            extract_i+=1

        finish_extract_time = time.perf_counter()
        print(f"Were extracted bucket {extract_i}/{extract_t} in {finish_extract_time-start_extract_time:.2f} seconds")
    #Finished feature extraction using CSharp Tool

# extracted_files.sort()
extracted_files.sort(key=lambda x: x['file_path'])

print(f"Starting merge files.")

dataset_path_tmp = './DATASET.tmp'
dataset_path_with_labels = './DATASET.csv'

if fe_system == 'c_sharp':
    headerLine = "DATETIME HOUR MINUTE SECOND F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 F13 F14 F15 F16 F17 F18 F19 F20 F21 F22 F23 F24 F25 F26 F27 F28 F29 F30 F31 F32 F33 F34 F35 F36 F37"
elif fe_system == 'c_plusplus':
    headerLine = "POSIXTIME DATETIME HOUR MINUTE SECOND F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 F13 F14 F15 F16 F17 F18 F19 F20 F21 F22 F23 F24 F25 F26 F27 F28 F29 F30 F31 F32 F33 F34 F35 F36 F37"

extracted_files_path = [f['file_path'] for f in extracted_files]
merge_files(extracted_files_path, dataset_path_tmp, headerLine)

print(f"Features files merge finished.")
print(f"Starting data labeling.")

data_labeler = AnomalousAndRegularDataLabeling(logging=logging)

data_labeler.new_dataset_with_labels(dataset_path_tmp,dataset_path_with_labels, anomalous_datetime_start, anomalous_datetime_end)
# os.remove(dataset_path_tmp)

print(f"Data labeling finished.")
print(f"The dataset is ready available at {dataset_path_with_labels}")