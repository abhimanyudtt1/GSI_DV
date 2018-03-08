import json
from Modules.basicUtils import getJsonDirPath,setParamsInJson
import pandas as pd
import pandasql as ps
import numpy as np
from Modules.metadataservice import Metadataservice
def getMainFunction():
    return applyFilter
def getDevAPIFunction():
    return devQuery


def returnLable(row,trueVal,falseVal,ib,dataField):
    if row[dataField] in ib:
        return trueVal
    else:
        return falseVal

def applyFilter(testObj,parms):
    print "===========================Running QA Compute logic for AD==========================="
    #print ("Calculating the data for filter function ")
    #data = testObj.data_list
    #df = pd.DataFrame(data)
    #ib = Metadataservice().get_static_dataset(parms['ibName'])
    #ib = pd.DataFrame(ib)
    #dataField,ibField = parms['userFields'].split(':')
    #df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
    #df = df.set_index("ts")
    #df = df.sort_index()
    #ib = ib[ibField].to_dict().values()
    #df[parms['labelField']] = df.apply(lambda row : returnLable(row,parms['labelValue'],parms['unknownLabelValue'],ib,dataField),axis=1)
    #reducedIB = ps.sqldf("" % (ibField), locals())
    #groupby_fields = parms['groupByFields']
    #aggregateon = parms['aggregates'].split(':')[-1].split('(')[-1].rstrip(')')
    #queries = parms['whereClause']
    #queries = 'SELECT * FROM df ' + queries
    #df = ps.sqldf(queries, locals())
    #df = df.query(queries, inplace=False)
    return pd.DataFrame()
    return df


def devQuery(devObject,huntAttributes):
    print "===========================Running Dev call for AD==========================="
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'ad.json'
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