from dotenv import dotenv_values
import json
import os
import utils
from datetime import datetime
from math import floor, ceil
import json
import sys
import logging
import multiprocessing
from netscience_client import NetScienceClient
from dataset.dataset import Dataset
from feature_selection.feature_selection import ExtraTreesFeatureSelection
from exploratory_data_analysis.cli import execute_eda_single_task
import sweetviz as sv
from dataset.dataset_scatter import save_3d_scatter, save_plotly_scatter, save_3d_datetime_scatter

DATASET_FILENAME = 'DATASET.csv'
DATASET_FILENAME_WITHOUT_NORMALIZATION = 'DATASET-without-normalization.csv'
IMPORTANCES_FILENAME = 'fs_importances.json'

#Configuração de LOGGING
logging.basicConfig(
    filename=f"bgpresearch.log",
    filemode='a',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

app_path = f"{os.path.dirname(__file__)}"

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
print(f" 📂 Starting experiment task on CWD: {task_working_dir}")

today = datetime.today()
print(f" 🕣 Starting time: {today}")

file = open('task.json')
task = json.load(file)

print(f" 🔑 Task key: {task['id']}")

print(f" 🧪 Getting experiment details (TaskId = {task['id']})")
client = NetScienceClient(netscience_config['BASE_URL'], netscience_config['USERNAME'], netscience_config['PASSWORD'],netscience_config['TASKS_BASE_PATH'], logging=logging)

task = client.get_experiment(task['id'])
p = task['parameters']
p['dataset_id'] = task['dataset_id']
dataset_task_path = os.path.join(netscience_config['TASKS_BASE_PATH'], task['dataset_id'])
p['dataset_path'] = os.path.join(dataset_task_path, DATASET_FILENAME)

print(f" ⚙️ Task parameters (before parsing):")
utils.print_task_parameters(task)

# Preparing the parameters
dataset_id = p['dataset_id']
dataset_path = p['dataset_path']

data_partition_training = p['data_partition_training'] / 100
data_partition_reference = p['data_partition_reference']

rnn_length = p['rnn_length']

debug = True if p['debug'] == 'activated' else False

params = {
    'dataset_id': dataset_id,
    'dataset_path': dataset_path,
    'data_partition_training': data_partition_training,
    'data_partition_reference': data_partition_reference,
    'rnn_length': rnn_length,
    'debug': debug,
}

print('')

print(f" ⚙️ Task parameters (after parsing):")
utils.print_generic_parameters(params)

print()

#Dataset object
dataset = Dataset(dataset_path)
#Dataset DataFrame
df = dataset.df

print(f" ⛔️ Looking for NaN values on original dataset")
nan_rows = df[df.isna().any(axis=1)]
if (len(nan_rows)> 0):
    print(f"  → {nan_rows} NaN values were found.")
else: print(f"  → No NaN value were found.")
print()

print(f" 📊 Stats of the original dataset")
print(f"  → Regular: {len(df.loc[df['LABEL'] == 0])}")
print(f"  → Anomalous: {len(df.loc[df['LABEL'] == 1])}")
print(f"  → Total: {len(df)}")
print(f"  → NaN lines: {len(nan_rows)}")
df = df.dropna()
print(f"  → Total after remove NaN lines: {len(df)}")
print()

# df.info(verbose=True, show_counts=True)
print()

#Dataset DataFrame
dataset = dataset.get_normalized_zscore_dataset()
df = dataset.df

print(f" 📊 Stats of the normalized dataset")
print(f"  → Regular: {len(df.loc[df['LABEL'] == 0])}")
print(f"  → Anomalous: {len(df.loc[df['LABEL'] == 1])}")
print(f"  → Total: {len(df)}")

print()

print(f" 🍕 Data partition:")

effective_data_train_percentage = data_partition_training

if (data_partition_reference == 'anomalous'):
    # Anomalous ratio data partitioning
    print(f"  * Data partition referenced only on anomalous samples was detected.")
    print(f"  * This approach is a indirect way to do data partitioning.")

    train_dataset, test_dataset = dataset.get_train_test_datasets_anomalous_ratio(data_partition_training)
    
    effective_data_train_percentage = dataset.get_effective_percentage_from_anomalous_percentage(data_partition_training)
    print(f"  * In order to have {data_partition_training*100}% of anomalous data points in the training partition")
    print(f"    will applied a effective data train of {effective_data_train_percentage}%")          

else:
    # Effective ratio data partitioning
    train_dataset, test_dataset = dataset.get_train_test_datasets_effective_ratio(data_partition_training)

print()

print(f"  → Requested Train size (proportion): {data_partition_training}")
print(f"  ⛔️ Effective Train size (proportion): {effective_data_train_percentage}")
print(f"  ⛔️ Effective Testing size (proportion): {1-effective_data_train_percentage}")
print()

#New Dataset with partition column
print(f" 📊 Stats of the dataset with partition column")
print(f"  → Training: {len(train_dataset)}")
print(f"  → Testing: {len(test_dataset)}")
print(f"  → Training - Regular: {train_dataset.count_regular_data_points()}")
print(f"  → Training - Anomalous: {train_dataset.count_anomalous_data_points()}")
print(f"  → Testing - Regular: {test_dataset.count_regular_data_points()}")
print(f"  → Testing - Anomalous: {test_dataset.count_anomalous_data_points()}")
print(f"  → Total: {len(dataset)}")
print()

print(f" 💾 Saving Zscore normalized dataset")
dataset.df.to_csv(DATASET_FILENAME)

print()

#Train Dataset
print(f" 📊 Stats of the TRAINING sample:")
print(f"  → Regular: {train_dataset.count_regular_data_points()}")
print(f"  → Anomalous: {train_dataset.count_anomalous_data_points()}")
print(f"  → Total: {train_dataset.count_total_data_points()}")
print()

# train_dataset.df.info(verbose=True, show_counts=True)
print()

#Testing Dataset
print(f" 📊 Stats of the TESTING sample:")
print(f"  → Regular: {test_dataset.count_regular_data_points()}")
print(f"  → Anomalous: {test_dataset.count_anomalous_data_points()}")
print(f"  → Total: {test_dataset.count_total_data_points()}")
print()

# test_dataset.df.info(verbose=True, show_counts=True)
print()

print(f" 📉 Executing automatic exploratory data analysis")
# html_path = os.path.join(task_working_dir, 'eda.html')
# report = sv.compare([train_dataset.df, "Trainning"],[test_dataset.df, "Test"], target_feat=dataset.target_column)
# try:
#     report.show_html(html_path, open_browser=False, layout='vertical')
# except Exception as e:
#     print(f"Failure during writing html EDA file. {html_path}")

# print(f" 📉 Executing Feature Selection")

# fs = ExtraTreesFeatureSelection(train_dataset)
fs = ExtraTreesFeatureSelection(dataset)

# Importances Dataframe
idf = fs.getImportancesDataFrame()
print(f"###############################")
print(f"* Features in order of importance:")
print(idf)
print()
fs_importances_path = os.path.join(task_working_dir, IMPORTANCES_FILENAME)
try:
    with open(fs_importances_path, 'w') as file:
        json_obj = json.loads(idf.to_json())
        file.write(json.dumps(json_obj['importance']))
    print(f"File with features importances saved at: {fs_importances_path}")
except Exception as e:
    print(f"Failure when saving features importances file at: {fs_importances_path}.")

top_n_features = 10

print(f"###############################")
print(f"* Selected (N={top_n_features}) features:")
selected_features = fs.getSelectedFeatures(top_n_features)
print(selected_features)

dataset.df.info()

print(f"###############################")
print(f"* Generating 3D scatter plots")
save_3d_scatter('selected_features', dataset, selected_features[0], selected_features[1], selected_features[2])
save_3d_scatter('paper', dataset, 'F8', 'F9', 'F5')
save_3d_scatter('time', dataset,'POSIXTIME', 'F8', 'F9')
# save_3d_datetime_scatter('time', dataset,'F8', 'F9')

print(f"F8 min: {min(dataset.df['F8'])} max: {max(dataset.df['F8'])}")
print(f"F9 min: {min(dataset.df['F9'])} max: {max(dataset.df['F9'])}")

# save_plotly_scatter('plotly_paper_scatter.png', train_dataset, 'F8', 'F9', 'F5')
# save_plotly_scatter('plotly_paper_time_scatter.png', dataset,'POSIXTIME', 'F8', 'F9')
