import json
from Modules.basicUtils import getJsonDirPath,setParamsInJson
import pandas as pd
import pandasql as ps
import numpy as np
from Modules.redisUtil import r
from Modules.metadataservice import Metadataservice
def getMainFunction():
    return applyFilter
def getDevAPIFunction():
    return devQuery


def returnLable(row,ib,dataField):
    if row[dataField] in ib.keys():
        if row['gsi_ts'] in ib[row[dataField]] :
            ibVal = ib[row[dataField]].split(',')
            ibVal = filter(lambda x : row['gsi'] in x , ibVal)[0]
            return ibVal.split('_')[0]
        else:
            return ''
    else:
        return ''

def applyFilter(testObj,parms):

    data = testObj.data_list
    print ("Calculating the data for filter function ")
    data = testObj.data_list
    df = pd.DataFrame(data)
    ib = r.zrange()
    ib = map(lambda (m, n): (m, ','.join(n)), ib)
    #ib = pd.DataFrame(ib)
    dataField = parms['userAnnotationFields']
    #df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
    df = df.set_index("ts")
    df = df.sort_index()
    #ib = ib[ibField].to_dict().values()
    df['%s_user_AD' % dataField ] = df.apply(lambda row : returnLable(row,ib,dataField),axis=1)
    #reducedIB = ps.sqldf("" % (ibField), locals())
    #groupby_fields = parms['groupByFields']
    #aggregateon = parms['aggregates'].split(':')[-1].split('(')[-1].rstrip(')')
    #queries = parms['whereClause']
    #queries = 'SELECT * FROM df ' + queries
    #df = ps.sqldf(queries, locals())
    #df = df.query(queries, inplace=False)
    #return pd.DataFrame()
    return df


def devQuery(devObject,huntAttributes):
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'ua.json'
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