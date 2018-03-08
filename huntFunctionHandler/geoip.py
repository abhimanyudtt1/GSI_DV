from Modules.ip_utils import IpUtils
import re
from Modules.basicUtils import getJsonDirPath
import json
import pandas as pd

def getMainFunction():
    return applygeoip
def getDevAPIFunction():
    return devQuery


def applygeoip(self, params):
    print "=========================== Running QA Compute logic for GeoIP ==========================="
    geoipib = params['geoIBName']
    data_columns=params['inputFields'].split(',')
    print "This is GeoFilter Application"
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
    return pd.DataFrame(self.data_list)


def devQuery(devObject,huntAttributes):
    print "=========================== Running Dev Call for GeoIP ==========================="
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'prefix.json'
    jsonFile = json.loads('\n'.join(open(jsonFile).readlines()))
    jsonFile["input"] = devObject.outputdataset
    jsonFile["huntName"] = devObject.enrichment_name
    dag = json.loads(jsonFile["dag"])
    functionProperties = dag['functionset'][0]['functionProperties']
    functionProperties = json.loads(functionProperties)
    tempFunctionProperties = []
    for eachItem in functionProperties:
        if eachItem['name'] in huntAttributes.keys():
            eachItem['value'] = huntAttributes[eachItem['name']]
            tempFunctionProperties.append(eachItem)
    functionProperties = json.dumps(tempFunctionProperties, separators=(',', ':')) #.replace('"', '\\"')
    dag['functionset'][0]['functionProperties'] = functionProperties
    jsonFile["dag"] = json.dumps(dag)
    #jsonFile["functionProperties"] = functionProperties
    #jsonFile = setParamsInJson(jsonFile,devObject,huntAttributes)
    #print api,json.dumps(jsonFile)
    return api,json.dumps(jsonFile)