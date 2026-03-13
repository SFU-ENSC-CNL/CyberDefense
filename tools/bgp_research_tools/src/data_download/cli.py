import argparse
import os
import sys
import datetime
import math

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from data_download.clients.ripe_client import RIPEClient

def convert_datetime(date_time_input):
    format="%Y%m%dT%H%M%S"
    try:
        return datetime.datetime.strptime(date_time_input, format)
    except ValueError:
        sys.exit(f"ABORTING: ERROR. The input \"{date_time_input}\" does not match format {format}.")

def split_interval_into_chunks(datetime_start, datetime_end, chunk_number, chunk_duration_hours=24):

    if (datetime_end <= datetime_start):
        sys.exit(f"ABORTING: The datetime_end must be greater than datetime_start. Instead, a bigger datetime_start was provided.")

    # Calculate the total period in hours and split by the chunk_duration_hours 
    max_chunks = math.ceil(((datetime_end - datetime_start).total_seconds()/3600) / chunk_duration_hours)
    
    # print(chunk_number)
    if (chunk_number < 1 or chunk_number > max_chunks):
        sys.exit(f"ABORTING: For the datetime interval provided the chunk_number must be between 1 and {max_chunks}. Instead, {chunk_number} was provided.")

    # Beginning of the desired chunk
    new_datetime_start = datetime_start + datetime.timedelta(hours=((chunk_number - 1) * chunk_duration_hours))
    
    # Ending of the desired chunk
    new_datetime_end = datetime_start + datetime.timedelta(hours=((chunk_number) * chunk_duration_hours), seconds=-1)
    # In case of the last chunk, use the time provided by the parameter datetime_end
    new_datetime_end = min(new_datetime_end, datetime_end)

    return new_datetime_start, new_datetime_end

def data_download(datetime_start, datetime_end, rrc=4, site_collection='ripe', max_concurrent_requests=32, cacheLocation=False):
    client = RIPEClient(max_concurrent_requests=32, debug=True, cacheLocation=cacheLocation)
    return client.download_updates_interval_files(datetime_start,
                                            datetime_end, int(rrc))
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser('CLI for Download module of BGP Research Software')

    parser.add_argument('--site-collection', dest='site_collection', default='ripe', choices=['ripe'], help='Choose a site collection that can be ripe or route-views (not available yet)')
    parser.add_argument('--from', dest='datetime_start', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--to', dest='datetime_end', type=str, required=True, help='Choose a datetime to start download in the format: yyyymmddThhmmss. Example: 20030521T080100 ')
    parser.add_argument('--rrc', dest='rrc', type=int, default=4, help='Choose a RRC')
    parser.add_argument('--max-concurrent-requests', dest='max_concurrent_requests', type=int, default=32, help='Choose a number of max concurrent requests')
    parser.add_argument('--mrt-cache-directory', dest='mrt_cache_directory', type=str, default=False, help='Directory location to save and retrieve (cache) the downloaded MRT files.')
    parser.add_argument('--chunk', dest='chunk_number', type=int, required=False, default=False, help='In case of distributed processing, choose the chunk number of the total period that will be processed.')
    parser.add_argument('--chunk-duration-hours', dest='chunk_duration_hours', type=int, required=False, default=24, help='In case of distributed processing, choose the duration in HOURS of each chunk that will be considered in the split step.')

    args = parser.parse_args()

    datetime_start = convert_datetime(args.datetime_start)
    datetime_end = convert_datetime(args.datetime_end)

    # is not False is different from True. Example chunk_number=0
    if (args.chunk_number is not False):
        datetime_start, datetime_end = split_interval_into_chunks(datetime_start, datetime_end, args.chunk_number, args.chunk_duration_hours)
        print(f"The datetime_start and datetime_end were adjusted to {datetime_start} and {datetime_end}, respectively. Considering chunk_number={args.chunk_number} and chunk_duration_hours={args.chunk_duration_hours}.")

    for file in data_download(datetime_start, datetime_end, rrc=args.rrc, site_collection=args.site_collection, max_concurrent_requests=args.max_concurrent_requests, cacheLocation=args.mrt_cache_directory):
        print(file['file_path'])
    