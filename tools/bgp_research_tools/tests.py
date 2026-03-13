import unittest
import logging
import tempfile

from src.data_download.clients.ripe_client import RIPEClient

class RIPEClientUnitTest(unittest.TestCase):

    tempdir = tempfile.gettempdir() + "/ripe"

    logging.basicConfig(
        filename='ripe.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    #TIMESTAMPS_TEST1 =

    def test_instantiation_without_parameters(self):
        try:
            self.client = RIPEClient()
        except Exception as err:
            self.fail(f"Raised {type(err)=} exception during instantiation without parameters {err=}, ")

    def test_instantiation_with_invalid_logging(self):
        with self.assertRaises(Exception):
            self.client = RIPEClient(logging=1)
            self.assertFalse(hasattr(logging.basicConfig, '__call__'))
    
    def test_instantiation_with_logging(self):
        try:
            self.client = RIPEClient(logging=logging)
            self.assertTrue(hasattr(self.client.logging.basicConfig, '__call__'))
        except Exception as err:
            self.fail(f"Raised {type(err)=} exception during instantiation with logging {err=}, ")

    def test_instantiation_with_cache_location(self):
        try:
            self.client = RIPEClient(cacheLocation=self.tempdir)
        except Exception as err:
            self.fail(f"Raised {type(err)=} exception during instantiation with cacheLocation {err=}, ")

    def test_instantiation_with_cache_location_and_logging(self):
        try:
            self.client = RIPEClient(logging=logging,cacheLocation=self.tempdir)
            self.assertTrue(hasattr(self.client.logging.basicConfig, '__call__'))
        except Exception as err:
            self.fail(f"Raised {type(err)=} exception during instantiation with logging and cacheLocation {err=}, ")
            
    #client.download_updates_interval_files(datetime(2022, 12, 25, 10, 0), datetime(2022, 12, 25, 11, 37))
    #To do: prepare tests evaluating the dates
    # def test_time_rounding_1(self):

if __name__ == '__main__':
    unittest.main()
