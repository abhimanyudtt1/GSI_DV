from __future__ import print_function
from metadataservice import Metadataservice
from annotation_utils import Annotation
from ip_utils import IpUtils
import pandas as pd
import re
import imp
import os

class Enrichment (Metadataservice, Annotation):

    def __init__(self):
        super (Enrichment, self).__init__ ()
        self.data_list = []

    def getsource(self, source_dataset=None, ts1=0, ts2=956528000):
        self.ts1 = ts1
        self.ts2 = ts2
        print ("Getting data from dataset : %s " % source_dataset)
        try:
            self.data_list = self.get_dataset_timerange (source_dataset, ts1, ts2)

        except:
            self.data_list = []
        return self.data_list
        ##### XXX #####

    def getHuntFunction(self,name):
        f, filename, description = imp.find_module(name, [os.getcwd()+'/huntFunctionHandler'])
        handle = imp.load_module(name, f, filename, description)
        return handle.getMainFunction()

    '''def applyblacklist(self, blacklistib='blacklist1', data_columns="srcIp"):
        dump = self.get_static_dataset (blacklistib)
        ib_dict = {}
        for item in dump:
            for value in item.values ():
                ib_dict[value] = "True"
        ib_columns = "Blacklist"
        default_ib_columns = "False"
        self.data_list = self.applyenrichment (self.data_list, data_columns, ib_dict, ib_columns, default_ib_columns)
        return self.data_list'''

    '''def applygeoip(self, geoipib="geoip1", data_columns="srcIp"):
        ib_dict = {}
        dump = self.get_static_dataset (geoipib)
        try:
            ib_columns = [column for column in dump[0].keys () if not re.match ('ip_*', column)]
            default_ib_columns = ['', 0.0, 0.0, '']
        except IndexError:
            ib_columns = None
        for item in dump:
            ips = IpUtils ().ips_in_range (item['ip_start_range'], item['ip_end_range'])
            for ip in ips:
                ib_dict[ip] = []
                for ib_column in ib_columns:
                    ib_dict[ip].append (item[ib_column])
        self.data_list = self.applyenrichment (self.data_list, data_columns, ib_dict, ib_columns, default_ib_columns)
        return self.data_list'''


class Compute (Enrichment):
    def __init__(self):
        super (Compute, self).__init__ ()

    def _index_sort(self):
        df = pd.DataFrame (self.data_list)
        df['ts'] = pd.to_datetime (df['ts'], unit='s', errors='coerce')
        df = df.set_index ("ts")
        df = df.sort_index ()
        return df

    def groupby_sum(self, groupby_fields, aggregateon, N):
        df = self._index_sort ()
        df = df.groupby (groupby_fields.split (',')).agg (aggregateon).sum ().reset_index (drop=False)
        df = df.sort_values (by=aggregateon)
        return df.head (N)

    def groupby_max(self, groupby_fields, aggregateon, N):
        df = self._index_sort ()
        df = df.groupby (groupby_fields.split (',')).agg (aggregateon).max ().reset_index (drop=False)
        df = df.sort_values (by=aggregateon)
        df.to_dict()
        return df.head (N)


    def groupby_min(self, groupby_fields, aggregateon, N):
        df = self._index_sort ()
        df = df.groupby (groupby_fields.split (',')).agg (aggregateon).min ().reset_index (drop=False)
        df = df.sort_values (by=aggregateon)
        return df.head (N)

    def groupby_last(self, groupby_fields, aggregateon, N):
        df = self._index_sort ()
        df = df.groupby (groupby_fields.split (',')).agg (aggregateon).last ().reset_index (drop=False)
        df = df.sort_values (by=aggregateon)
        return df.head (N)

    def groupby_first(self, groupby_fields, aggregateon, N):
        df = self._index_sort ()
        df = df.groupby (groupby_fields.split (',')).agg (aggregateon).first ().reset_index (drop=False)
        df = df.sort_values (by=aggregateon)
        return df.head (N)

    def groupby_std(self, groupby_fields, aggregateon, N):
        df = self._index_sort ()
        df = df.groupby (groupby_fields.split (',')).agg (aggregateon).std ().reset_index (drop=False)
        df = df.sort_values (by=aggregateon)
        return df.head (N)

    def groupby_avg(self, groupby_fields, aggregateon, N):
        df = self._index_sort ()
        df = df.groupby (groupby_fields.split (',')).agg (aggregateon).mean ().reset_index (drop=False)
        df = df.sort_values (by=aggregateon)
        return df.head (N)

    def filter(self, queries, N):
        df = self._index_sort ()
        df = df.query (queries, inplace=False)
        return df.head (N)
