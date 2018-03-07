import json
from Modules.basicUtils import getJsonDirPath,setParamsInJson
import pandas as pd
import pandasql as ps
import numpy as np
import ipaddress
from Modules.metadataservice import Metadataservice
def getMainFunction():
    return applyPrefix
def getDevAPIFunction():
    return devQuery


def returnLable(row,falseVal,ib,dataField):
    for prefix in ib :
        if ipaddress.ip_address(row[dataField]) in prefix   :
            return "True"
        else:
            return falseVal

def changeToNetwork(x):
    if '/' in x :
        return ipaddress.ip_network(x)
    else:
        if ':' in x :
            return ipaddress.ip_network(x+'/128')
        else:
            return ipaddress.ip_network(x+'/32')

def applyPrefix(testObj,parms):
    print "Calculating the data for Prefix function "
    data = testObj.data_list
    df = pd.DataFrame(data)
    ib = Metadataservice().get_static_dataset(parms['iBName'])
    ib = map(lambda x : x['URL/IP'],ib)
    ib = [ changeToNetwork(x) for x in ib ]
    #ib = map(changeToNetwork,ib)

    #ib = pd.DataFrame(ib)
    #dataField = parms['inputFields']
    #df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
    df = df.set_index("ts")
    df = df.sort_index()
    #ib = ib.set_index(ibField)[parms['valueField']].to_dict()
    df['Prefix_%s' % parms['inputFields']] = df.apply(lambda row : returnLable(row,'False',ib,parms['inputFields']),axis=1)
    #reducedIB = ps.sqldf("" % (ibField), locals())
    #groupby_fields = parms['groupByFields']
    #aggregateon = parms['aggregates'].split(':')[-1].split('(')[-1].rstrip(')')
    #queries = parms['whereClause']
    #queries = 'SELECT * FROM df ' + queries
    #df = ps.sqldf(queries, locals())
    #df = df.query(queries, inplace=False)
    print "Prefix calculation done"
    return df


def devQuery(devObject,huntAttributes):
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