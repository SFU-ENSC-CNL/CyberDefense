# https://data.ris.ripe.net/rrcXX/YYYY.MM/TYPE.YYYYMMDD.HHmm.gz

# with:

# XX = the RRC number
# YYYY = year
# MM = month
# TYPE = the type of file, which is either bview (dumps) or update (updates)
# DD = day
# HH = hour
# mm = minute
# Currently dumps are created every 8 hours, and updates are created every 5 minutes
#


import tempfile
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
import concurrent.futures
import time
from requests_cache import CachedSession, FileCache
from pathlib import Path

from datetime import date
from dateutil.relativedelta import relativedelta

from bs4 import BeautifulSoup
from urllib.parse import urlparse

class RIPEClient:

    #Datetime of the first update message available on RIPE
    RIPE_DATETIME_BEGIN = datetime(2001, 4, 24, 10, 42)
    TYPE = 'ripe'
        
    def __init__(self,
                 cacheLocation=False,
                 baseURL='https://data.ris.ripe.net',
                 logging=False,
                 debug=False,
                 max_concurrent_requests=1
                 ):
        
        self.baseURL = baseURL
        self.logging = logging
        self.debug = debug
        self.max_concurrent_requests = int(max_concurrent_requests)

        #Checking if logging has a valid value
        if not (self.logging==False or (hasattr(self.logging, 'basicConfig') and hasattr(self.logging.basicConfig, '__call__'))):
            raise Exception('The logging parameters need to be a valid logging object or False')

        # This attribute stores the tmp_object
        self.tmp = False
        self.session=False

        # Mapping possible cache location passed
        if (cacheLocation):
            #To-do: check if the location exists and it is writeable
            self.work_dir = f"{cacheLocation}/ripe"
            # Creating folder if not exists
            Path(self.work_dir).mkdir(parents=True, exist_ok=True)
            # Creating HTML cache to be used by nodes without internet access
            html_cache_dir = os.path.join(self.work_dir, 'html_cache')
            Path(self.work_dir).mkdir(parents=True, exist_ok=True)
            self.session = CachedSession(backend=FileCache(
                cache_name=html_cache_dir,

            ))
        else:
            #Creating a unique temp dir (when cache feature is disabled)
            with tempfile.TemporaryDirectory(prefix="bgptools_") as tmp_dirname:
                self.log_info(f"created temporary directory: {tmp_dirname}")
                self.work_dir = tmp_dirname + "/ripe"
            

        # Creating the work directory if not exists
        if not os.path.exists(self.work_dir):
            self.log_info("Creating the directory: " + self.work_dir)
            os.makedirs(self.work_dir)

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
        
    def check_interval(self,number, min, max):
        return min <= number <= max
    
    def datetime_start_is_valid(self, datetime_start):
        return datetime_start >= self.RIPE_DATETIME_BEGIN
            
    def validate_ripe_minute(self, minute):
        if not minute in range(0, 60, 5):
            raise Exception('Minute {minute} must be within the range between 0 and 59 and be multiple of 5'.format(minute=minute))
        return True
    
    def filename_from_url(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path
        return os.path.basename(path)
    
    # def date_from_url(self, url):
    #     parsed_url = urlparse(url)
    #     path = parsed_url.path
    #     #Get the substring after ('updates.')
    #     date = path.split('updates.', 1)[1]
    #     #get the substring after the first .
    #     date = path.split('.', 1)[0]
    #     return date

    def create_path_if_not_exists(self,path):
        try:
            if not os.path.exists(path):
                self.log_info('Creating dir: ' + path)
                path = Path(path)
                path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            self.log_error('Failure when creating the dir: ' + path)
            return False
            
        
    def generate_update_url(self, year, month, day, hour, minute, rrc=4):
        
        return "{baseURL}/rrc{rrc}/{year}.{month}/updates.{year}{month}{day}.{hour}{minute}.gz".format(
            baseURL=self.baseURL,
            year=year,
            month="{:02d}".format(month),
            day="{:02d}".format(day),
            hour="{:02d}".format(hour),
            minute="{:02d}".format(minute),
            rrc="{:02d}".format(rrc)
        )
    
    def generate_update_local_path(self, year, month, day, hour, minute, rrc=4):

        return "{work_dir}/rrc{rrc}/{year}.{month}/updates.{year}{month}{day}.{hour}{minute}.gz".format(
            work_dir=self.work_dir,
            year=year,
            month="{:02d}".format(month),
            day="{:02d}".format(day),
            hour="{:02d}".format(hour),
            minute="{:02d}".format(minute),
            rrc="{:02d}".format(rrc)
        )

    def download_update_file(self, url):

        #self.datetime_start_is_valid(ripe_datetime)

        # Setting the local attributes
        internal_path = urlparse(url).path
        filePath = self.work_dir + internal_path
        
        # CACHE: Checking if the file was already downloaded before
        if not os.path.exists(filePath):
        
            # Downloading the file
            self.log_info('Downloading RIPE file: ' + self.filename_from_url(url))
            try:
                download_start_time = time.perf_counter()
                res = requests.get(url, allow_redirects=True)
                res.raise_for_status()
                try:
                    #Checking if the path exists
                    head, tail = os.path.split(filePath)
                    self.create_path_if_not_exists(head)
                    open(filePath, 'wb').write(res.content)
                    #self.log_info('File saved in: ' + url)
                    download_finish_time = time.perf_counter()
                    if os.path.exists(filePath):
                        # return filePath
                        file_stats = os.stat(filePath)
                        return {"file_path": filePath, "internal_path": internal_path, "source": 'remote', "download_time_in_seconds":download_finish_time-download_start_time, "file_size_in_bytes": file_stats.st_size, "date": self.get_date_str_from_url(url)}
                    else:
                        self.log_error('Downloaded file was not found in: ' + filePath)
                except Exception as err:
                    self.log_error(f"Failure when writing file in the filesystem: exception={err} filepath={filePath}")
            except requests.exceptions.HTTPError as errh:
                self.log_error(f"HTTP Error: {errh} during downloading file URL={url}")
            except requests.exceptions.ConnectionError as errc:
                self.log_error(f"Connecting Error: {errc} during downloading file URL={url}")
            except requests.exceptions.Timeout as errt:
                self.log_error(f"Timeout Error: {errt} during downloading file URL={url}")
            except requests.exceptions.RequestException as err:
                self.log_error(f"Something Else Error: {err} during downloading file URL={url}")
        else:
            self.log_info('Download prevented because the file was found in cache: ' + self.filename_from_url(url))
            # return filePath
            file_stats = os.stat(filePath)
            return {"file_path": filePath, "internal_path": internal_path, "source": 'cache', "file_size_in_bytes": file_stats.st_size, "date": self.get_date_str_from_url(url)}

    def generate_years_and_months_interval(self, ripe_datetime_start, ripe_datetime_end):
            
            date_start = ripe_datetime_start.replace(day=1).date()

            #last_day_of_month = calendar.monthrange(ripe_datetime_end.year, ripe_datetime_end.month)[1]
            date_end = ripe_datetime_end.replace(day=1).date()

            d = date_start

            while date_start <= d <= date_end:
                # The timestamps are returned as they are being generated using yield
                yield {'year': d.year, 'month': d.month}
                d += relativedelta(months=+1)

    def get_files_links_from_year_month(self, year, month, rrc=4):

        url = f"{self.baseURL}/rrc{int(rrc):02d}/{int(year)}.{int(month):02d}/"

        # Getting file links from one index page
        self.log_info('Getting file links from one index page: ' + self.filename_from_url(url))
        try:
            # res = requests.get(url, allow_redirects=True)
            res = self.requests_get_with_cache(url)
            res.raise_for_status()
            
            try:
                soup = BeautifulSoup(res.content, "html.parser")
                for a in soup.find_all('a'):
                    href = a['href']
                    if href != '../':
                        yield f"{url}{href}"
                
            except Exception as err:
                self.log_error(f"Failure when parsing HTML index URL={url} exception={err}")
        except requests.exceptions.HTTPError as errh:
            self.log_error(f"HTTP Error: {errh} when scrapping the URL={url}")
        except requests.exceptions.ConnectionError as errc:
            self.log_error(f"Connecting Error: {errc} when scrapping the URL={url}")
        except requests.exceptions.Timeout as errt:
            self.log_error(f"Timeout Error: {errt} when scrapping the URL={url}")
        except requests.exceptions.RequestException as err:
            self.log_error(f"Something Else Error: {err} when scrapping the URL={url}")

    def get_datetime_from_url(self, url):
        
        filename = self.filename_from_url(url)

        file_type, date_str, time_str, extension = filename.split('.')

        return datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M")
    
    def get_date_str_from_url(self, url):
        
        filename = self.filename_from_url(url)

        file_type, date_str, time_str, extension = filename.split('.')

        return date_str
    
    def get_files_links_from_interval(self, ripe_datetime_start, ripe_datetime_end, rrc=4):

        # Generating tuples year/month (periods) from ripe_datetime_start to ripe_datetime_end
        periods = self.generate_years_and_months_interval(ripe_datetime_start, ripe_datetime_end)

        # if self.max_concurrent_requests > 0:
        #     try:
        #         with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
        #             args = ((period['year'], period['month'], rrc) for period in periods)
        #             for arg in args:
        #                 print(arg, type(arg))
        #             for result in executor.map(self.get_files_links_from_year_month, args):
        #                  yield result
        #     except Exception as err:
        #         self.log_error(f"Error during the download err={err}, {type(err)=}")

        for period in periods:
            for file_url in self.get_files_links_from_year_month(period['year'], period['month'], rrc):
                ts = self.get_datetime_from_url(file_url)
                if ripe_datetime_start <= ts <= ripe_datetime_end:
                    yield file_url 


    def get_updates_links_from_interval(self, ripe_datetime_start, ripe_datetime_end, rrc=4):

        files_urls = self.get_files_links_from_interval(ripe_datetime_start, ripe_datetime_end, rrc)

        for file_url in files_urls:

            if 'updates' in file_url:
                yield file_url

        
    def download_updates_interval_files(self, ripe_datetime_start, ripe_datetime_end, rrc=4):
        
        if not (isinstance(ripe_datetime_start, datetime) and isinstance(ripe_datetime_end, datetime)):
            raise Exception(f"The parameter ripe_datetime_start and ripe_datetime_end need to be a datetime type.")    
        
        if not (self.datetime_start_is_valid(ripe_datetime_start)):
            raise Exception(f"The parameter ripe_datetime_start must be from or after than: {self.RIPE_DATETIME_BEGIN}")
            
        urls = self.get_updates_links_from_interval(ripe_datetime_start, ripe_datetime_end, rrc)

        if self.max_concurrent_requests > 0:
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
                    for result in executor.map(self.download_update_file, urls):
                        yield result
            except Exception as err:
                self.log_error(f"Error during the download err={err}, {type(err)=}")

    def split_downloaded_files_in_buckets_per_day(self, downloaded_files):
        buckets = {}
        for file in downloaded_files:
            # Checking if the bucket was not created yet
            date = file['date']
            if  date not in buckets:
                buckets.update({date: []})

            buckets[date].append(file)

        return buckets
    
    def requests_get_with_cache(self, url):
        if self.session:
            return self.session.get(url, allow_redirects=True)
        else:
            return requests.get(url, allow_redirects=True)
            


        
