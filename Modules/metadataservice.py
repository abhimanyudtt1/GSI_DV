from __future__ import print_function

import json
import logging

from elastic_utility import ElasticsearchUtils
from rest_utils import REST
from security_ini_configparser import SecurityConfigParser
from Modules.basicUtils import configParsed
max_wait = 180


class Metadataservice (SecurityConfigParser, REST):
    ignore_field = ["sads", "type", "tags", "beat", "input_type", "@timestamp", "source", "host", "offset", "message",
                    "@version"]

    def __init__(self, conf='../Config/security_dv.ini'):
        super (Metadataservice, self).__init__ ()
        self.logger = logging.getLogger (__name__)
        loadconfig = self.get_section (conf, 'metadataservice')
        self.api = loadconfig['api']
        self.url = loadconfig['url']
        self.headers = loadconfig['headers']
        self.get_response = self._request_get
        self.response_list = self.parse_response

    @property
    def _request_get(self):
        rest = self.url + self.api
        headers = self.headers
        response = self.execute_request ('GET', rest, headers=headers)
        #print (rest,headers,response)
        if response.status_code == 200:
            return response.content
        else:
            return None

    @property
    def parse_response(self):
        resp = self.get_response
        #print (resp)
        return json.loads (resp)

    @property
    def get_permanent_datasources(self):
        mylist = []
        config = configParsed()
        config = config['pipeLine']
        config = map(lambda (x,y) : y['log']+y['prefix'],config.items())

        for line in self.response_list:
            if 'averageKfps' in line['properties']:
                if line['name'] in config or True :
                    mylist.append (line['name'])
        return mylist

    @property
    def get_datasources_count(self):
        return len (self.get_permanent_datasources)

    def exists(self, dataset):
        for ds in self.response_list:
            if ds['name'] == dataset.lower ():
                return True
        return False

    def get_datasource_property(self, dataset):
        for ds in self.response_list:
            if ds['name'] == dataset.lower ():
                return ds['properties']
        return []

    @property
    def get_datasource_properties(self):
        mydict = {}
        for line in self.response_list:
            if 'averageKfps' in line['properties']:
                dataset = line['name']
                average = line['properties']['averageKfps']
                peak = line['properties']['peakKfps']
                startTime = line['properties']['startTime']
                endTime = line['properties']['endTime']
                mydict[dataset] = [startTime, endTime, average, peak]
        return mydict

    @property
    def get_datasources_without_stats(self):
        datasets = []
        for line in self.response_list:
            if not line['properties'].get ('averageKfps'):
                dataset = line['name']
                datasets.append (dataset)

        return datasets

    def get_static_dataset(self, ib, fields=ignore_field, ignore_fields=True):
        return ElasticsearchUtils ().dump_index (ib, fields, ignore_fields)

    @staticmethod
    def get_dataset_records_counts(dataset):
        return ElasticsearchUtils ().es_index_pattern_count (dataset + '-*')

    @staticmethod
    def get_mints_dataset(dataset):
        retsult =  ElasticsearchUtils ().get_mints_index_pattern (dataset + '-*')
        return retsult
    @staticmethod
    def get_maxts_dataset(dataset):
        return ElasticsearchUtils ().get_maxts_index_pattern (dataset + '-*')

    def get_ST_ET_dataset(self, dataset):

        ST = self.get_mints_dataset (dataset)
        ET = self.get_maxts_dataset (dataset)
        return ST / 1000.0, ET / 1000.0

    @staticmethod
    def get_dataset_timerange(dataset, ts1=0, ts2=1956528000, fields=ignore_field, timefield="gsi_ts"):
        return ElasticsearchUtils ().get_dataset_dump_timerange (dataset + '-*', ts1, ts2, fields, timefield)

    @staticmethod
    def get_peak_of_dataset(dataset):
        peak_per_index = []
        indices = ElasticsearchUtils ().es_index_pattern_list (dataset + '-')
        if any (indices):
            for index in indices:
                peak = ElasticsearchUtils ().get_peak_of_index (index)
                peak_per_index.append (peak)
        return max (peak_per_index)

    @property
    def calculate_datasource_properties(self):
        mydict = {}
        all_datasets = self.get_permanent_datasources
        for dataset in all_datasets:
            try:
                startTime = self.get_mints_dataset (dataset) / 1000.0
                endTime = self.get_maxts_dataset (dataset) / 1000.0
            except:
                startTime=0.0
                endTime=0.0
            avg_count = self.get_dataset_records_counts (dataset)
            if (endTime - startTime) < 1.0:
                average = avg_count
            else:
                average = avg_count * 1.0 / (endTime - startTime + 1.0)
            average = '{:.20f}'.format (average)
            try:
                peak = self.get_peak_of_dataset (dataset)
            except:
                peak = 0.0
            mydict[dataset] = [int (startTime), int (endTime), average, peak]
        return mydict
