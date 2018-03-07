import json
from Modules.basicUtils import getJsonDirPath
import pandas as pd
from Modules.metadataservice import Metadataservice

def getMainFunction():
    return applyBlackList
def getDevAPIFunction():
    return devQuery


def returnBlackList(row,falseVal,trueVal,ib,field):
    if row[field] in ib :
        return trueVal
    else:
        return falseVal


def applyBlackList(testObj,parms):
    print "Calculating the data for Prefix function "
    data = testObj.data_list
    df = pd.DataFrame(data)
    ib = Metadataservice().get_static_dataset(parms['blacklistIBName'])
    ib = map(lambda x : x['URL/IP'],ib)
    df['Blacklist_%s' % parms['inputFields']] = df.apply(lambda row :
                returnBlackList(row,'false','true',ib,parms['inputFields']),axis=1)
    print "BlackList calculation done"
    dfCols = df.columns.tolist()
    dfCols = [dfCols[-1]] + dfCols[:-1]
    df = df[dfCols]
    return df

def devQuery(devObject,huntAttributes):
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'blacklist.json'
    jsonFile = json.loads('\n'.join(open(jsonFile).readlines()))
    jsonFile["input"] = devObject.outputdataset
    jsonFile["huntName"] = devObject.enrichment_name
    dag = json.loads(jsonFile["dag"])
    functionProperties = dag['functionset'][0]['functionProperties']
    functionProperties = json.loads(functionProperties)
    tempFunctionProperties = []
    for k, v in huntAttributes.items():
        for eachItem in functionProperties:
            if eachItem['name'] == k:
                eachItem['value'] = v
            tempFunctionProperties.append(eachItem)
    functionProperties = json.dumps(tempFunctionProperties, separators=(',', ':')).replace('"', '\\"')
    dag['functionset'][0]['functionProperties'] = functionProperties
    jsonFile["dag"] = json.dumps(dag)
    #jsonFile["functionProperties"] = functionProperties
    #jsonFile = setParamsInJson(jsonFile,devObject,huntAttributes)
    print api,json.dumps(jsonFile)
    return api,json.dumps(jsonFile)


