import os
import pandas as pd
from dataset.dataset import Dataset
from feature_selection.feature_selection import ExtraTreesFeatureSelection
import json

DATASET_FILENAME = 'DATASET.csv'
IMPORTANCES_FILENAME = 'fs_importances.json'

def execute_feature_selection_single_task(task_path, train_size, top_n_features=10, save_file=True):
    if not os.path.isdir(task_path):
        raise Exception(f"Aborting: You have to pass a valid task folder absolute path.")        
    
    dataset_path = os.path.join(task_path, DATASET_FILENAME)
    if not os.path.isfile(dataset_path):
        raise Exception(f"Aborting: The task path provided must to have a {DATASET_FILENAME} file.")

    print(f"###############################")
    print(f"* Train size (proportion): {train_size}")
    print()

    #Dataset object
    dataset = Dataset(dataset_path)
    #Dataset DataFrame
    df = dataset.df

    print(f"###############################")
    print(f"Looking for NaN values")
    nan_rows = df[df.isna().any(axis=1)]
    if (len(nan_rows)> 0):
        print(nan_rows)
    else: print(f"No NaN value were found.")

    print(f"###############################")
    print(f"* Stats of the original dataset")
    print(f"    Regular: {len(df.loc[df['LABEL'] == 0])}")
    print(f"    Anomalous: {len(df.loc[df['LABEL'] == 1])}")
    print(f"    Total: {len(df)}")
    print(f"    NaN lines: {len(nan_rows)}")
    df = df.dropna()
    print(f"    Total after remove NaN lines: {len(df)}")
    print()

    #Train Dataset
    tr_dataset = dataset.get_training_sample(train_size)
    print(f"###############################")
    print(f"* Stats of the TRAINING sample:")
    print(f"    Regular: {tr_dataset.count_regular_data_points()}")
    print(f"    Anomalous: {tr_dataset.count_anomalous_data_points()}")
    print(f"    Total: {tr_dataset.count_total_data_points()}")
    print()

    #Testing Dataset
    ts_dataset = dataset.get_testing_sample(train_size)
    print(f"###############################")
    print(f"* Stats of the TESTING sample:")
    print(f"    Regular: {ts_dataset.count_regular_data_points()}")
    print(f"    Anomalous: {ts_dataset.count_anomalous_data_points()}")
    print(f"    Total: {ts_dataset.count_total_data_points()}")
    print()

    fs = ExtraTreesFeatureSelection(tr_dataset)

    # Importances Dataframe
    idf = fs.getImportancesDataFrame()
    print(f"###############################")
    print(f"* Features in order of importance:")
    print(idf)
    print()
    fs_importances_path = os.path.join(task_path, IMPORTANCES_FILENAME)
    try:
        with open(fs_importances_path, 'w') as file:
            json_obj = json.loads(idf.to_json())
            file.write(json.dumps(json_obj['importance']))
        print(f"File with features importances saved at: {fs_importances_path}")
    except Exception as e:
        print(f"Failure when saving features importances file at: {fs_importances_path}.")

    print(f"###############################")
    print(f"* Selected (N={top_n_features}) features:")
    print(fs.getSelectedFeatures(top_n_features))
    

def execute_feature_selection_multiple_tasks(tasks_path, train_size, top_n_features=10, save_file=True):
    if not os.path.isdir(tasks_path):
        print(f"Aborting: You have to pass a valid task folder absolute path.")
        return False
    
    for root, dirs, files in os.walk(tasks_path):
        for d in dirs:
            task_path = os.path.join(root, d)
            print(f"Executing Feature Selection for {task_path}")
            try:
                execute_feature_selection_single_task(task_path, train_size, top_n_features, save_file)
            except Exception as e:
                print(e)
