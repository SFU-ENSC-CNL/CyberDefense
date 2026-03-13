import argparse
import os
import sys
import time
from natsort import natsorted

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from data_merging.merge_files import *

HEADER_LINE = "POSIXTIME DATETIME HOUR MINUTE SECOND F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 F13 F14 F15 F16 F17 F18 F19 F20 F21 F22 F23 F24 F25 F26 F27 F28 F29 F30 F31 F32 F33 F34 F35 F36 F37 F38 F39 F40 F41"

if __name__ == "__main__":

    parser = argparse.ArgumentParser('CLI for Data Merging module of BGP Research Software')

    parser.add_argument('files_in', nargs='*', help='Type a list with files_in')
    parser.add_argument('-o', '--output', dest='output_filename', type=str, required=True, help='Choose the file output location.')
    parser.add_argument('--header-line', dest='header_line', default=HEADER_LINE, type=str, help='Choose the content of the header line to the CSV file.')
    
    args = parser.parse_args()

    files_in = args.files_in
    files_in = natsorted(files_in)

    print(f"Merging the following files:")
    for file in files_in:
        print(f" * {file}")
    
    print()
    
    merge_files(files_in, args.output_filename, args.header_line)

    print(f"Data merging finished. File written in {args.output_filename}.")


