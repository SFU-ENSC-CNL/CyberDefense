import os
import pandas as pd
import numpy as np
import datetime
from datetime import timezone

class AnomalousAndRegularDataLabeling:

    def __init__(self,
                 logging=False,
                 debug=False,
                 ):
        self.logging = logging
        self.debug = debug
        
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

    def new_dataset_with_labels(self,dataset_path_in, dataset_path_out, anomalous_datetime_start, anomalous_datetime_end, delimiter_in=' ', delimiter_out=',', regular_label=0, anomalous_label=1):

        if not os.path.exists(dataset_path_in):
            raise IOError(f"Dataset file not found in {dataset_path_in}.")
        
        df = pd.read_csv(dataset_path_in, delimiter=delimiter_in)

        df = self.put_labels(df, anomalous_datetime_start, anomalous_datetime_end, regular_label, anomalous_label)

        df.to_csv(dataset_path_out, sep=delimiter_out, index=False, date_format='%Y-%m-%dT%H:%M:%S')

        return df

    def put_labels(self,df, anomalous_datetime_start, anomalous_datetime_end, regular_label=0, anomalous_label=1):

        # In case of CPlusPLus will use the column POSIXTIME
        # In case of CSharp will be use column DATETIME
        # Todo: change errors to raise and put the stack on LOG file.
        if 'POSIXTIME' in df.columns:
            df['DATETIME'] = pd.to_datetime(df['POSIXTIME'], unit='s', errors='coerce')
        if 'timestamp' in df.columns:
            df['DATETIME'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
        elif 'DATETIME' in df.columns: 
            df['DATETIME'] = pd.to_datetime(df['DATETIME'], errors='coerce')
        else:
            raise Exception(f"The timestamp column was not found.")

        #Adding a new column to put the LABEL
        df = df.assign(LABEL=0)

        #Updating values conditionally
        df['LABEL'] = np.where(( (df['DATETIME'] >= anomalous_datetime_start) & (df['DATETIME'] <= anomalous_datetime_end) ), anomalous_label, regular_label)

        return df

    def put_labels_multiple_periods(self,df, anomalous_periods, regular_label=0, anomalous_label=1):
        # In case of CPlusPLus will use the column POSIXTIME
        # In case of CSharp will be use column DATETIME
        # Todo: change errors to raise and put the stack on LOG file.
        if 'POSIXTIME' in df.columns:
            df['DATETIME'] = pd.to_datetime(df['POSIXTIME'], unit='s', errors='coerce')
        elif 'timestamp' in df.columns:
            df['DATETIME'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
        elif 'DATETIME' in df.columns: 
            df['DATETIME'] = pd.to_datetime(df['DATETIME'], errors='coerce')
        elif 'datetime' in df.columns: 
            df['DATETIME'] = pd.to_datetime(df['datetime'], errors='coerce')
        else:
            raise Exception(f"The timestamp column was not found.")
        
        df['LABEL'] = df.apply(lambda x: anomalous_label if self.is_inside_period(x['DATETIME'], anomalous_periods) else regular_label, axis=1)

        return df

    def is_inside_period(self,dt, anomalous_periods):

        if not isinstance(dt, datetime.datetime):
            raise Exception(f"The dr parameter has to be a datetime type. Instead {type(dt)} was provided.")

        for ann_period in anomalous_periods:
                       
            if not (isinstance(ann_period['start'], datetime.datetime) and isinstance(ann_period['end'], datetime.datetime)):
                raise Exception(f"The anomaly period start and end parameters has to be a datetime type. Instead {type(ann_period['start'])} and {type(ann_period['end'])} were provided.")

            if dt.replace(tzinfo=timezone.utc) >= ann_period['start'] and dt.replace(tzinfo=timezone.utc) <= ann_period['end']:
                # Anomaly label
                return True
        # Regular Label
        return False

    