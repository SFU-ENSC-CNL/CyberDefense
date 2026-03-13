import fileinput
import os
from feature_extraction.cli import append_suffix_on_filename
from datetime import datetime

def read_multiple_files(files_in):
    return list(fileinput.input(files_in))

def merge_files(files_in, file_out, header_line=False):

    lines = read_multiple_files(files_in)
    
    check_datapoints_continuity(lines)

    with open(file_out, 'w') as file:
        if (header_line):
            file.write(f"{header_line}\n")
        file.writelines(lines)
        print(f"{len(files_in)} files were merged on {file_out} containing {len(lines):,.0f} data points.")

def check_datapoints_continuity(file_input, interval_seconds=60):

    i=0
    discontinuities=[]
    for line in file_input:
        i+=1

        columns = line.split(" ")
        if (not len(columns)>1):
            print(f"A empty line (n. {i}) was found. {line}")

        ts = int(columns[0])

        actual_dt = datetime.utcfromtimestamp(ts)

        if (i==1):
            begin_dt = actual_dt
            print(f"Starting continuity analysis from {begin_dt}.")            
        
        if (i>1):

            if (previous_dt == actual_dt):
                print(f" * REPEATED timestamp was found. The timestamp {previous_dt} was found repeated.")
            
            if (previous_dt > actual_dt):
                print(f" * INVERSE order was found. The timestamp {previous_dt} was found before than {actual_dt}.")

            if ((actual_dt - previous_dt).total_seconds() > interval_seconds):
                discontinuities.append({"from": previous_dt, "to": actual_dt, "duration": actual_dt - previous_dt})
                print(f" * DISCONTINUITY was found from {previous_dt} to {actual_dt}.")
            
        previous_dt = datetime.utcfromtimestamp(ts)
        last_dt = actual_dt

    print()
    print(f"The dataset was processed from {begin_dt} to {last_dt} with {len(discontinuities)} discontinuities detected.")