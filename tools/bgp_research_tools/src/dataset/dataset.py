import pandas as pd
import os
import numpy as np
from scipy.stats import zscore
from sklearn.model_selection import train_test_split
from pathlib import Path
import math

class Dataset:

    def __init__(self,dataset, target_column='LABEL'):

        self.target_column = target_column
        self.file_path = ''
        self.file_name = ''

        if isinstance(dataset, str):
            self.file_path_input = dataset
            self.df = self.openDatasetFromFile(dataset)
        elif isinstance(dataset, pd.DataFrame):
            self.df = dataset

        # Check Dataset
        self.checkDataset()
        # Remove undesired columns
        self.df = self.removeUndesiredColumns(self.df)
        # Casting DATETIME column
        self.parse_datetime_column()

    def openDatasetFromFile(self, dataset_path):
        
        if not os.path.isfile(dataset_path):
            raise Exception(f"Aborting: The task path provided must to have a {dataset_path} file.")            
        
        self.file_path = dataset_path
        self.file_name = Path(dataset_path).name
        
        df = pd.read_csv(dataset_path)

        return df
    
    def checkDataset(self):
        if not self.target_column in self.df.columns:
            raise Exception(f"Aborting: The dataset needs to have a {self.target_column} column (target column)")

    def parse_datetime_column(self, datetime_column='DATETIME'):
        if datetime_column in self.df.columns:
            self.df[datetime_column] = pd.to_datetime(self.df[datetime_column], utc=True)

    def removeUndesiredColumns(self, df):
        # Removing unnamed columns
        df = df.copy(deep=True)
        df.drop(df.columns[df.columns.str.contains(
            'unnamed', case=False)], axis=1, inplace=True)
        return df.drop(['HOUR', 'MINUTE', 'SECOND'], axis=1, errors='ignore')
    
    def removeUndesiredColumnsForTraining(self, df):
        return df.drop(['POSIXTIME','DATETIME','HOUR', 'MINUTE', 'SECOND', 'TRAIN','timestamp', 'datetime'], axis=1, errors='ignore')
    
    # Returns a DataFrame with the Dataset plus a TRAIN column
    # The TRAIN colum is filled according with train_size
    def get_df_with_partition_column(self,train_size):
        # In this kind of dataset, a Time Series
        # is not allowed to change the order of the records
        # Therefore the data is partitioned placing the
        # first TRAIN_SIZE records to training_dataset
        # and the rest for testing dataset 

        if not (train_size >=0 and train_size <=1):
            raise Exception(f"Train size must be >= 0 and <= 1")
        
        df_lines = len(self.df.index)
        train_lines = math.floor(df_lines * train_size)
        test_lines = df_lines - train_lines

        if not (train_lines + test_lines == df_lines):
            raise Exception(f"The sum between number of training lines and testing lines should be equal to total number of lines")

        # # Creating a new and independent copy of the dataframe
        # df = self.df.copy(deep=True)

        df = self.df
        # Creating a new column and setting train = 0 for all values
        df['TRAIN'] = 0
        # Setting train = 1 for the first train_lines
        df.iloc[:train_lines, df.columns.get_loc('TRAIN')] = 1
        # is a training line => TRAIN = 1
        # is a testing line => TRAIN = 0

        #Checking the amount of training and testing lines
        train_lines_found = len(df.loc[df['TRAIN'] == 1])
        test_lines_found = len(df.loc[df['TRAIN'] == 0])

        if not (train_lines_found == train_lines and test_lines_found == test_lines):
            raise Exception(f"The amount of lines for training and testing dit not matched as was planned. Check the code.")

        return df
    
    def get_train_test_datasets_anomalous_ratio(self, anomalous_train_size):
        effective_ratio = self.get_effective_percentage_from_anomalous_percentage(anomalous_train_size)
        print(f"effective_ratio = {effective_ratio}")
        return self.get_train_test_datasets_effective_ratio(effective_ratio)
    
    def get_train_test_datasets_effective_ratio(self, train_size):
        train = self.get_training_dataset_effective_ratio(train_size)
        test = self.get_testing_dataset_effective_ratio(train_size)
        return train, test

    def get_training_dataset_effective_ratio(self, train_size):
        df = self.get_df_with_partition_column(train_size)
        # df = df.dropna()
        # Investigar aqui
        df = df.loc[df['TRAIN'] == 1]
        df = self.removeUndesiredColumns(df)
        return Dataset(df)
    
    def get_testing_dataset_effective_ratio(self, train_size):
        df = self.get_df_with_partition_column(train_size)
        # df = df.dropna()
        df = df.loc[df['TRAIN'] == 0]
        df = self.removeUndesiredColumns(df)
        return Dataset(df)
    
    def get_normalized_zscore_dataset(self, ddof=0, debug=False):
        # Creating a local copy of the dataset
        df = self.df.copy(deep=True)
        # Get all numeric columns
        features_cols = list(self.df.select_dtypes(include=[np.number]).columns)
        # Remove POSIXTIME column
        if 'POSIXTIME' in features_cols: features_cols.remove('POSIXTIME')
        # Remove target column
        if self.target_column in features_cols: features_cols.remove(self.target_column)
        # Removing TRAIN column (if exists)         
        if 'TRAIN' in features_cols: features_cols.remove('TRAIN')
        # # Apply Zscore normalization in all columns (features) except POSIXTIME, TARGET and TRAIN (if exists)
        for column in features_cols:
            if debug: print(f" Applying zscore normalization for column {column} with ddof={ddof}")
            # self.df[column] = zscore(self.df[column], ddof=ddof)
            df[column] = (df[column] - np.mean(df[column])) / np.std(df[column])
            # Filling with zero NaN values.
            # Were found when all values are 0 the zscore result will be nan for all rows
            if (df[column].isna().any()):
                print(f"Were found NaN values on column {column} and these values were replaced to zero.")
                df[column].fillna(0, inplace=True)
        return Dataset(df)
        
    
    def count_regular_data_points(self, regular_value=0):
        return len(self.df.loc[self.df[self.target_column] == regular_value])
    
    def count_anomalous_data_points(self, anomalous_value=1):
        return len(self.df.loc[self.df[self.target_column] == anomalous_value])
    
    def count_total_data_points(self):
        return len(self.df)
    
    # This method was designed for ordered datasets, usually time series dataset
    def get_effective_percentage_from_anomalous_percentage(self, anomalous_percentage, anomalous_value=1):

        if (anomalous_percentage < 0 or anomalous_percentage > 1):
            raise Exception(f"The anomalous_percentage has to be between 0 and 1")
        
        # Total amount of data points
        total_amount = self.count_total_data_points()
        
        # Amount of anomalous data points
        total_anomalous_count = self.count_anomalous_data_points()

        # Amount of anomalous data points in the first partition
        selected_anomalous_count = math.floor(total_anomalous_count * anomalous_percentage)

        # Get the required amount of anomalous data points
        anomalous = self.df.loc[self.df[self.target_column] == anomalous_value].iloc[:selected_anomalous_count]

        # Get the index of the last anomalous data point in the first partition
        separation_idx  = anomalous.tail(1).index.values[0]

        # Get the amount of data points before the separation_idx
        effective_amount = len(self.df.loc[:separation_idx])

        # Effective amount of data points in the first partition splited the total amount of data points
        effective_percentage = effective_amount / total_amount
        return effective_percentage
      
    def get_x_y(self):
        # Separating the dependent and independent variables
        # The use of x and y variables are a convention in ML codes
        df = self.removeUndesiredColumnsForTraining(self.df)
        # y <= just label column
        y = df[self.target_column]
        # x <= just features columns
        x = df.drop(self.target_column, axis = 1)
        return np.array(x), np.array(y)
    
    def get_features_columns(self):
        df = self.removeUndesiredColumnsForTraining(self.df)
        df = df.drop(self.target_column, axis = 1)
        return df.columns
    
    def get_number_of_features(self):
        return len(self.get_features_columns())

    def save_to_file(self, path = './DATASET.CSV'):
        self.df.to_csv(path)

    def __len__(self):
        return len(self.df)
    
    def select_where(self,select_column_name, where_column_name, where_column_value):
        df = self.df[self.df[where_column_name] == where_column_value]
        if select_column_name == 'DATETIME':
            values = df[select_column_name].astype('datetime64[ns, UTC]').values
        else:
            values = df[select_column_name].values
        return list(values)
    
    def print_stats(self):
        print(f"  - Total data points: {self.count_total_data_points()}")
        print(f"  - Regular data points: {self.count_regular_data_points()}")
        print(f"  - Anomaly data points: {self.count_anomalous_data_points()}")



    
    

        
        
        
