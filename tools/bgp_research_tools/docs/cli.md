The Command Line Interface (CLI) provided in this repository offers the following modules:

#### [Dataset creation](#dataset-creation)
* [Data Download](#data-downloading)
* [Feature Extraction](#feature-extraction)
* [Data merging](#data-merging)
* [Data labeling](#data-labeling)

#### Exploratory data analysis and Feature selection
* Exploratory data analysis
* Feature selection
  
#### Machine Learning
* Data normalization
* Data partition
* Batch model training
* Performance evaluation

# Dataset creation

## Data downloading

#### Choosing site collection, RRC, and time interval
```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 
```
* Download MRT BGP files from RIPE RIS RRC04 from 2023-01-01T00:00:00 to 2024-01-28T23:59:59.
* A list with the path of the downloaded files will be printed at stdout.
* The files will be downloaded in a temporary folder provided by the operational system.

#### Choosing a cache location
```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache
```
* Uses the path `~/cache` to store the downloaded files.
* The same directory is also used as a cache source that allows avoid downloading repeated files. 

#### Choosing the max number of concurrent requests

```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache
--max-concurrent-requests 32
```
* Specify that the connection pool will use a maximum number of 32 concurrent HTTP requests at the same time.

### Data downloading using distributed processing
This CLI offers valuable resources when distributing the data download into several nodes. In this way, it is possible to specify that each node will download a chunk of the total period requested. This chunk corresponds to some interval of hours. The default value is 24 hours.

#### Specifying a chunk number
```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1
```
* In the example above, the data download will execute only chunk number 1 of a total of 393 chunks.
* Passing `--chunk 1` returns: "The datetime_start and datetime_end were adjusted to 2023-01-01 00:00:00 and 2023-01-01 23:59:59, respectively. Considering chunk_number=1 and chunk_duration_hours=24."
* Passing `--chunk 2` returns: "The datetime_start and datetime_end were adjusted to 2023-01-02 00:00:00 and 2023-01-02 23:59:59, respectively. Considering chunk_number=2 and chunk_duration_hours=24."
* A useful resource is to pass `--chunk 0` to force the CLI to return an error message that displays the range of chunk numbers that is valid: "ABORTING: For the datetime interval provided the chunk_number must be between 1 and 393. Instead, 0 was provided."

#### Specifying the chunk duration

```console
python src/data_download/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--chunk-duration-hours 4
```
* Passing `--chunk 1` returns: "The datetime_start and datetime_end were adjusted to 2023-01-01 00:00:00 and 2023-01-01 03:59:59, respectively. Considering chunk_number=1 and chunk_duration_hours=4."
* Passing `--chunk 0` returns: "ABORTING: For the datetime interval provided, the chunk_number must be between 1 and 2358. Instead, 0 was provided."

Additional information is available through `--help` switch.
```console
python src/data_download/cli.py --help                                                
```

## Feature extraction

Feature extraction is a step done after data downloading or during the download when using pipelining.

To make it easy to use this CLI, the data download step was totally integrated with the feature extraction step. This means that the users can execute commands for feature extraction, and the CLI will automatically and transparently take care of the data downloading.

This CLI runs the MRTprocessor in the background, which has to be installed to perform feature extraction.

#### Extracting features from a specific site collection, RRC, and time interval
```console
python src/feature_extraction/cli.py --rrc 0 \
--from 20230101T000000 --to 20230102T235959 \
--mrt-cache-directory ~/cache \
--output ~/datasets/dataset.csv
```
* In the example above, the feature extraction will be performed by downloading MRT files or getting them from the cache when available.
* The MRTprocessor will be called passing parameter a list of files according to the parameters `--rrc`, `--from`, and `--to`.
* The matrix having the 37 features and one line for each 1-minute interval will be saved at `~/datasets/dataset.csv`.

### Feature extraction using distributed processing

#### Specifying a chunk number
```console
python src/feature_extraction/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--output ~/datasets/dataset.csv
```
* Feature extraction using distributed processing will generate several output files. For every chunk will be added a suffix, for example `~/datasets/dataset-1.csv` for chunk number 1.

#### Specifying the chunk duration
```console
python src/feature_extraction/cli.py --rrc 4 \
--from 20230101T000000 --to 20240128T235959 \
--mrt-cache-directory ~/cache \
--chunk 1 \
--chunk-duration-hour 4 \
--output ~/datasets/dataset.csv
```

Additional information is available through `--help` switch.
```console
python src/feature_extraction/cli.py --help                                                
```

## Data merging

Data merging allows the merging of several output files, which is especially useful when the processing is distributed by several nodes.

```console
python src/data_merging/cli.py ~/datasets/ripe_dataset_westrock_rrc14_* \
-o ~/datasets/DATASET-unlabeled.csv
```
* The CLI command receives a list of files to do data merging.
* The parameter `-o` or `--output` specifies the destination of the file resulting from the data merging process.
* Before reading, the list of files will be sorted using the natural sort algorithm.
* The sorted list will be displayed.
* During data merging, the CLI will do some verifications displaying alerts when:
  * some empty line is found.
  * some data points are out of order, based on the value found in the first column (POSIXTIME).
  * some repeated data points' timestamps are found.
  * some temporal discontinuity is found between two data points.

In the case above, the CLI will display the following output:
```
Merging the following files:
 * ~/datasets/ripe_dataset_westrock_rrc14_1.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_2.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_3.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_4.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_5.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_6.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_7.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_8.csv
 * ~/datasets/ripe_dataset_westrock_rrc14_9.csv

Starting continuity analysis from 2021-01-21 00:00:00.

The dataset was processed from 2021-01-21 00:00:00 to 2021-01-29 23:59:00 with 0 discontinuities detected.
9 files were merged on ~/datasets/DATASET.csv containing 12,960 data points.
Data labeling finished.
Finished.
```
Additional information is available through `--help` switch.
```console
python src/data_merging/cli.py --help
```

## Data labeling

```console
python src/data_labeling/cli.py \
-i ~/datasets/DATASET-unlabeled.csv \
-o ~/datasets/DATASET.csv \
--anomaly-from 20210123T011200 \
--anomaly-to 20210129T235900
```
Additional information is available through `--help` switch.
```console
python src/data_labeling/cli.py --help
```