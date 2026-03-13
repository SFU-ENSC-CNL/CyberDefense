import requests
import json
import concurrent.futures

class RIPEStatClient:

    def __init__(self,
                 baseURL='https://stat.ripe.net/data',
                 logging=False,
                 debug=False,
                 max_concurrent_requests=8
                 ):
        
        self.baseURL = baseURL
        self.logging = logging
        self.debug = debug
        self.max_concurrent_requests = int(max_concurrent_requests)

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

    def get_url(self, url):
        try:
            print(url)
            res = requests.get(url, allow_redirects=True)
            res.raise_for_status()
            return res.content
        except requests.exceptions.HTTPError as errh:
            self.log_error(f"HTTP Error: {errh} when getting the URL={url}")
        except requests.exceptions.ConnectionError as errc:
            self.log_error(f"Connecting Error: {errc} when getting the URL={url}")
        except requests.exceptions.Timeout as errt:
            self.log_error(f"Timeout Error: {errt} when getting the URL={url}")
        except requests.exceptions.RequestException as err:
            self.log_error(f"Something Else Error: {err} when getting the URL={url}")

    # Example:
    # https://stat.ripe.net/data/ris-prefixes/data.json?resource=6849&list_prefixes=true&query_time=2024-03-14T08:00
    def get_ris_prefixes_for_asn(self, asn, remove_non_cidr_standard=True):
        asn = int(asn)

        url = f"{self.baseURL}/ris-prefixes/data.json?resource={asn}&list_prefixes=true"

        response = self.get_url(url)
        response = json.loads(response)

        if 'data' not in response:
            raise Exception(self.log_error(f"The response for the following URL doesn't returned data. (URL={url})"))
        
        data = response['data']
        v4_originating = data['prefixes']['v4']['originating']
        v4_transiting = data['prefixes']['v4']['transiting']
        
        # Merging the two lists (originating and transiting) on one SET
        v4_prefixes = set(v4_originating)
        v4_prefixes.union(v4_transiting)

        # Removing non CIDR-standard prefixes (example: 31.128.68.0-31.128.95.255)
        if remove_non_cidr_standard:
            v4_prefixes = [v4p for v4p in v4_prefixes if '-' not in v4p]

        v6_originating = data['prefixes']['v6']['originating']
        v6_transiting = data['prefixes']['v6']['transiting']

        # Merging the two lists (originating and transiting) on one SET
        v6_prefixes = set(v6_originating)
        v6_prefixes.union(v6_transiting)

        return v4_prefixes, v6_prefixes
    

    def retrieve_ris_prefixes_for_multiple_asns(self, asns):

        if self.max_concurrent_requests > 0:
                try:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
                        for result in executor.map(self.get_ris_prefixes_for_asn, asns):
                            yield result
                except Exception as err:
                    self.log_error(f"Error during the download err={err}, {type(err)=}")

    def get_ris_prefixes_for_multiple_asns(self, asns):
        ipv4 = ipv6 = set()
        prefixes = self.retrieve_ris_prefixes_for_multiple_asns(asns)
        for p in prefixes:
            ipv4 = ipv4.union(p[0])
            ipv6 = ipv6.union(p[1])

        return ipv4, ipv6
    
    def get_country_resource_list(self, country_code, time, remove_non_cidr_standard=True):

        url = f"{self.baseURL}/country-resource-list/data.json?resource={country_code}&v4_format=prefix&time={time}"

        response = self.get_url(url)
        response = json.loads(response)

        if 'data' not in response:
            raise Exception(self.log_error(f"The response for the following URL doesn't returned data. (URL={url})"))
        
        data = response['data']

        asns = data['resources']['asn']
        ipv4 = data['resources']['ipv4']
        ipv6 = data['resources']['ipv6']

        return asns, ipv4, ipv6

