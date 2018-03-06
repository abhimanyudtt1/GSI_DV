import json
from Modules.basicUtils import getJsonDirPath,setParamsInJson
import pandas as pd
import pandasql as ps
def getMainFunction():
    return applyFilter
def getDevAPIFunction():
    return devQuery

def applyFilter(testObj,parms):
    print "Calculating the data for filter function "
    data = testObj.data_list
    df = pd.DataFrame(data)
    #df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
    df = df.set_index("ts")
    df = df.sort_index()
    #groupby_fields = parms['groupByFields']
    #aggregateon = parms['aggregates'].split(':')[-1].split('(')[-1].rstrip(')')
    queries = parms['whereClause']
    queries = 'SELECT * FROM df ' + queries
    df = ps.sqldf(queries, locals())
    #df = df.query(queries, inplace=False)
    return df


def devQuery(devObject,huntAttributes):
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'filter.json'
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