## RIPE Client

Client to facilitate downloading MRT files from the RIPE repository.

### Usage

#### Simple usage without cache, logging, and debug

```python
client = RIPEClient()
# Example datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

**Expected output:**

```bash
(...)/ripe/rrc04/2022.12/updates.20221225.1000.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1005.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1010.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1015.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1020.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1025.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1030.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1035.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1040.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1045.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1050.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1055.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1100.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1105.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1110.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1115.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1120.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1125.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1130.gz
(...)/ripe/rrc04/2022.12/updates.20221225.1135.gz
```

#### Passing a cache location

```python
client = RIPEClient(cacheLocation='./cache/ripe')
# Returns a array with the location of the downloaded files respecting the datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

Passing a cache location, the client will check the previous existence of the file before doing the download.
When the file is found in the cache, the client will return the cached file.
When a cache location is not provided, the client will choose a temp directory and will use this for cache purposes.

#### Passing a logging object

```python
#LOGGING configuration
logging.basicConfig(
    filename='ripe.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


client = RIPEClient(logging=logging, cacheLocation='./cache/ripe')
# Returns a array with the location of the downloaded files respecting the datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

In this way, some messages will be written in the log file in according to the log object configuration.

#### Enabling debug messages

```python
client = RIPEClient(debug=True)
# Returns a array with the location of the downloaded files respecting the datetime range
files = client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))

# The files are immediately returned as they are being downloaded
for file in files:
    print(file)
```

With debug=True some messages will be printed on the screen during the client downloading proccess. 