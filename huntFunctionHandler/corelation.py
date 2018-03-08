import os
import json
import pandas as pd
from Modules.basicUtils import getJsonDirPath,setParamsInJson
from Modules.elastic_utility import ElasticsearchUtils
def getMainFunction():
    return applyCorelation
def getDevAPIFunction():
    return devQuery

def applyCorelation(self,testObj,parms):

    data = testObj.data_list
    print "=========================== Running QA Compute logic for Corelation ==========================="
    data = testObj.data_list
    df = pd.DataFrame(data)
    #ib = r.getIbFromRedis()
    # ib = pd.DataFrame(ib)
    dataField = parms['userAnnotationFields']
    # df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
    df = df.set_index("ts")
    df = df.sort_index()
    # ib = ib[ibField].to_dict().values()
    df['%s_user_AD' % dataField] = df.apply(lambda row: returnLable(row, ib, dataField), axis=1)
    # reducedIB = ps.sqldf("" % (ibField), locals())
    # groupby_fields = parms['groupByFields']
    # aggregateon = parms['aggregates'].split(':')[-1].split('(')[-1].rstrip(')')
    # queries = parms['whereClause']
    # queries = 'SELECT * FROM df ' + queries
    # df = ps.sqldf(queries, locals())
    # df = df.query(queries, inplace=False)
    # return pd.DataFrame()
    return df



def devQuery(devObject,huntAttributes):
    print "=========================== Running dev call for Corelation ==========================="
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'coreletion.json'
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

