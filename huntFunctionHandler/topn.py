import json
from Modules.basicUtils import getJsonDirPath,setParamsInJson
import pandas as pd
from Modules.comparator import comparator
def getMainFunction():
    return applytopN
def getDevAPIFunction():
    return devQuery

def getComparator():
    return comp

def applytopN(testObj,parms):
    print "=========================== Running QA logic for topN group by ==========================="
    data = testObj.data_list
    df = pd.DataFrame(data)
    #df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
    #df = df.set_index("ts")
    #df = df.sort_index()
    groupby_fields = parms['groupByFields'].split(',')
    #groupby_fields = set( list(groupby_fields) + ['gsi_ts'])
    groupby_fields = list(groupby_fields)
    aggregateon = parms['aggregates'].split(':')[-1].split('(')[-1].rstrip(')')
    dfFinal = df.groupby(groupby_fields).agg(aggregateon)
    aggdf = getattr(dfFinal,parms['field'])().reset_index(drop=False)
    dfFinal = aggdf.sort_values(by=aggregateon)
    dfFinal.columns = groupby_fields + [parms['field']]
    dfFinal = dfFinal.head(int(parms['size']))
    return dfFinal


def devQuery(devObject,huntAttributes):
    print "=========================== Running Dev call for topN group by ==========================="
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'groupbytopn.json'
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


def comp(df1,df2):
    return comparator(df1,df2,excludeList=['gsi_ts'])
