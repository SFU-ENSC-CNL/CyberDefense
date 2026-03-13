import argparse
import os
import sys

src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(src_dir)

from data_labeling.anomalous_and_regular_data_labeling import AnomalousAndRegularDataLabeling
from data_download.cli import convert_datetime

if __name__ == "__main__":

    parser = argparse.ArgumentParser('CLI for Data labeling module of BGP Research Software')

    parser.add_argument('-i', '--input', dest='input_filename', type=str, required=True, help='Choose the file input location.')
    parser.add_argument('-o', '--output', dest='output_filename', type=str, required=True, help='Choose the file output location.')
    parser.add_argument('--anomaly-from', dest='anomaly_datetime_start', type=str, required=True, help='Choose the datetime to that started the anomalous data points. Format: yyyymmddThhmmss. Example: 20030521T080100')
    parser.add_argument('--anomaly-to', dest='anomaly_datetime_end', type=str, required=True, help='Choose the datetime to that ended the anomalous data points. Format: yyyymmddThhmmss. Example: 20030521T080100')
    parser.add_argument('--delimiter-input', dest='delimiter_input', type=str, required=False, default=" ", help='Choose the field character delimiter that will be used to parse the input file.')
    parser.add_argument('--delimiter-output', dest='delimiter_output', type=str, required=False, default=",", help='Choose the field character delimiter that will be used to write the output file.')
    
    args = parser.parse_args()

    anomaly_datetime_start = convert_datetime(args.anomaly_datetime_start)
    anomaly_datetime_end = convert_datetime(args.anomaly_datetime_end)

    data_labeler = AnomalousAndRegularDataLabeling()

    data_labeler.new_dataset_with_labels(args.input_filename,args.output_filename, anomaly_datetime_start, anomaly_datetime_end, delimiter_in=args.delimiter_input, delimiter_out=args.delimiter_output)
    print(f"Data labeling finished. File written in {args.output_filename}.")


