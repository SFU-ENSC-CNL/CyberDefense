import argparse
import os
import sys
import time

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from data_download.cli import data_download, convert_datetime, split_interval_into_chunks
from feature_extraction.bgp_cplusplus_feature_extraction import BGPCPlusPlusFeatureExtraction

def append_suffix_on_filename(filename, suffix):
    name, ext = os.path.splitext(filename)
    return f"{name}_{suffix}{ext}"

def convert_parameter_list(input, separator=":"):
    if (input and len(input) > 0):
        # input = input.strip('"')
        return input.split(separator)
    else:
        return []

def data_download_and_extract(output_file, datetime_start, datetime_end, rrc=4, site_collection='ripe', max_concurrent_requests=32, cacheLocation=False, asnfilt=[], nlriv4filt=[], nlriv6filt=[]):
    
    extractor = BGPCPlusPlusFeatureExtraction()
    downloaded_files = []

    start_download_time = time.perf_counter()
    
    for file in data_download(datetime_start, datetime_end, rrc=rrc, site_collection=site_collection, max_concurrent_requests=max_concurrent_requests, cacheLocation=cacheLocation):
        if (file and file is not None):
            # print(f"File downloaded: {file['file_path']}")
            downloaded_files.append(file)
        else:
            print(file)
            sys.exit(f"Unexpected value returned from download.")

    finish_download_time = time.perf_counter()
    print(f"Were obtained {len(downloaded_files)} files in {finish_download_time-start_download_time:.2f} seconds.")

    start_parse_time = time.perf_counter()

    file_extract = extractor.extract_features_from_files(
            downloaded_files,
            output_file,
            filter_by_asn=asnfilt,
            filter_by_ipv4=nlriv4filt,
            filter_by_ipv6=nlriv6filt
    )
    
    if file_extract:
        finish_parse_time = time.perf_counter()
        print(f"Were parsed one file in {finish_parse_time-start_parse_time:.2f} seconds.")
        return file_extract
    else:
        sys.exit(f"Error during extracting file: {output_file} ")

if __name__ == "__main__":

    parser = argparse.ArgumentParser('CLI for Feature Extraction module of BGP Research Tool')

    #Download arguments
    parser.add_argument('--site-collection', dest='site_collection', default='ripe', choices=['ripe'], help='Choose a site collection that can be ripe or route-views (not available yet)')
    parser.add_argument('--from', dest='datetime_start', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--to', dest='datetime_end', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--rrc', dest='rrc', type=int, default=4, help='Choose a RRC')
    parser.add_argument('--max-concurrent-requests', dest='max_concurrent_requests', type=int, default=16, help='Choose a number of max concurrent requests')
    parser.add_argument('--mrt-cache-directory', dest='mrt_cache_directory', type=str, default=False, help='Directory location to save and retrieve (cache) the downloaded MRT files.')
    parser.add_argument('--chunk', dest='chunk_number', type=int, required=False, default=False, help='In case of distributed processing, choose the chunk number of the total period that will be processed.')
    parser.add_argument('--chunk-duration-hours', dest='chunk_duration_hours', type=int, required=False, default=24, help='In case of distributed processing, choose the duration in HOURS of each chunk that will be considered in the split step.')

    #Extraction arguments
    parser.add_argument('--output', dest='output_file', type=str, required=True, help='Choose the file output location.')
    parser.add_argument('--asnfilt', dest='asnfilt', type=str, required=False, default=False, help='Choose list of Autonomous System Numbers (ASNs) to be used to filter the BGP update messages.')
    parser.add_argument('--nlriv4filt', dest='nlriv4filt', type=str, required=False, default=False, help='Choose list of Network Layer Reachability Information (NLRI) IPv4 to be used to filter the BGP update messages.')
    parser.add_argument('--nlriv6filt', dest='nlriv6filt', type=str, required=False, default=False, help='Choose list of Network Layer Reachability Information (NLRI) IPv6 to be used to filter the BGP update messages.')
    
    
    args = parser.parse_args()

    datetime_start = convert_datetime(args.datetime_start)
    datetime_end = convert_datetime(args.datetime_end)

    output_file = args.output_file

    asnfilt = convert_parameter_list(args.asnfilt)
    nlriv4filt = convert_parameter_list(args.nlriv4filt, ",")
    nlriv6filt = convert_parameter_list(args.nlriv6filt, ",")
    
    # is not False is different from True. Example chunk_number=0
    if (args.chunk_number is not False):
        datetime_start, datetime_end = split_interval_into_chunks(datetime_start, datetime_end, args.chunk_number, args.chunk_duration_hours)
        print(f"The datetime_start and datetime_end were adjusted to {datetime_start} and {datetime_end}, respectively. Considering chunk_number={args.chunk_number} and chunk_duration_hours={args.chunk_duration_hours}.")
        
        output_file = append_suffix_on_filename(output_file, args.chunk_number)
        print(f"The output_file name was adjusted to \"{output_file}\".")

    # print(datetime_start, datetime_end)
    file_extract = data_download_and_extract(output_file, datetime_start, datetime_end, rrc=args.rrc, site_collection=args.site_collection, max_concurrent_requests=args.max_concurrent_requests, cacheLocation=args.mrt_cache_directory, asnfilt=asnfilt, nlriv4filt=nlriv4filt, nlriv6filt=nlriv6filt)
    print(file_extract)