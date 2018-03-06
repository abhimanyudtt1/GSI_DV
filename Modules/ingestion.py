from __future__ import print_function
from __future__ import print_function
from __future__ import print_function
import json
import re
import sys
import time

from elastic_utility import ElasticsearchUtils
from logs_parser import LogParser
from rest_utils import REST
import pexpect
from security_ini_configparser import SecurityConfigParser

max_wait = 1


class Ingestion (SecurityConfigParser, REST):
    def __init__(self, conf='../Config/security_dv.ini'):
        """

        :rtype: object
        """
        super (Ingestion, self).__init__ ()
        loadconfig = self.get_section (conf, 'ingestion')
        self.api = loadconfig['api']
        self.url = loadconfig['url']
        print (loadconfig)
        self.parserconf_type = loadconfig['parserconf_type']
        self.headers = loadconfig['headers']
        self.dataset_suffix = loadconfig['dataset_suffix']
        self.inputlogspath = loadconfig['inputlogspath']
        self.inputconffile = loadconfig['inputconffile']
        self.tempflag = loadconfig['tempflag']
        self.timedict = loadconfig['timedict']
        self.default_timeformat = loadconfig['default_timeformat']
        self.localdatadir = loadconfig['localdatapath']
        self.staticib = loadconfig['staticib'].split (',')
        self.query_dict = self._generate_rest

    @property
    def _generate_rest(self):
        query_dict = {}
        parserconf_type_map = self.parserconf_type
        for i,v in parserconf_type_map.items():
            for j in v.split(','):

                conf, logs_extention = j,i
                log_type = re.findall ('[a-zA-Z]+_(.*?)\.conf', conf)[0]
                dataset = log_type + self.dataset_suffix
                rest = self.url + self.api + dataset
                log_dir = self.inputlogspath + 'logs/' + log_type + '/*.' + logs_extention
                body = {"inputlogspath": log_dir, "inputconffile": self.inputconffile + conf, "tempflag": self.tempflag}
                if log_type in self.timedict:
                    timeformat = self.timedict[log_type]
                else:
                    timeformat = self.default_timeformat
                local_logdir = self.localdatadir + '/' + log_type + '/*.' + logs_extention
                query_dict[log_type] = [dataset, rest, body, timeformat, local_logdir]
        return query_dict

    def fire_ingestion_api(self):
        for key in self.query_dict.keys ():
            print ("Triggering Ingestion for: %s \n" % key)
            rest = self.query_dict[key][1]
            body = self.query_dict[key][2]
            body = json.dumps (body)
            headers = self.headers
            print(rest, headers,body)
            response = self.execute_request ('POST', rest, headers=headers, data=body)

            if response.status_code == 200:
                print ("Ingestion successfully triggered for {} ".format (key))
            time.sleep (1)

    @staticmethod
    def scpSendToSever(file_path, scp_location, ip_address, username, password='guavus@123'):
        scp_cmd = "scp -r %s %s@%s:%s" % (file_path, username, ip_address, scp_location)
        connect_handle = pexpect.spawn (scp_cmd)
        connect_handle.setwinsize (400, 400)
        connect_handle.logfile_read = sys.stdout
        i = 0
        ssh_newkey = r'(?i)Are you sure you want to continue connecting'
        while True:
            i = connect_handle.expect ([ssh_newkey, 'assword: ', pexpect.EOF, pexpect.TIMEOUT])
            if i == 0:
                connect_handle.sendline ('yes')
                continue
            elif i == 1:
                print ("Password supplied")
                connect_handle.sendline (password)
                continue
            elif i == 2:
                print ("Scp complete")
                break
            elif i == 3:
                raise ValueError ("Unable to establish connection")
        return True

    def push_logs(self, server="192.168.133.54"):
        try:
            self.scpSendToSever (self.localdatadir, self.inputlogspath, server, 'root', 'guavus@123')
        except:
            pass
    @property
    def take_indices_backup(self):
        backup_log_type = {}
        for log in self.query_dict.keys ():
            indices_current_dataset = []
            backup_indices = {}
            dataset = self.query_dict[log][0]
            if log in self.staticib:
                if ElasticsearchUtils ().es_index_exists (dataset):
                    indices_current_dataset = [dataset]
            else:
                if ElasticsearchUtils ().es_index_pattern_exists (dataset):
                    indices_current_dataset = ElasticsearchUtils ().es_index_pattern_list (dataset)

            if any (indices_current_dataset):
                for index in indices_current_dataset:
                    backup_indices[index] = ElasticsearchUtils ().es_index_count (index)
            backup_log_type[log] = backup_indices

        return backup_log_type

    @property
    def calculate_indices(self):
        calculated_log_type = {}
        for log in self.query_dict.keys ():
            dataset = self.query_dict[log][0]
            timeformat = self.query_dict[log][3]
            log_dir = self.query_dict[log][4]
            if log in self.staticib:
                calculated_indices = LogParser (log, log_dir, dataset, timeformat).parse_ib ()
            else:
                calculated_indices = LogParser (log, log_dir, dataset, timeformat).parse_log ()
            calculated_log_type[log] = calculated_indices
        return calculated_log_type

    def check_ingestion_status(self):
        for log in self.query_dict.keys ():
            dataset = self.query_dict[log][0]
            if log in self.staticib:
                status = ElasticsearchUtils ().es_index_exists (dataset)
            else:
                status = ElasticsearchUtils ().es_index_pattern_exists (dataset + '-')
            if status:
                print ('%s Indices are created in ES; Logs ingested successfully' % log)
            else:
                print ('%s Indices arenot created in ES; Logs didnt get ingested successfully' % log)

    def actual_bined_newlogs(self, x, y):
        if isinstance (x, dict) and isinstance (y, dict):
            return {key: self.actual_bined_newlogs (x[key], y[key]) for key in x if key in y}
        else:
            return str (int (x) - int (y))
