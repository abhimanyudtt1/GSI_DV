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
    print "===========================Running QA Compute logic for blackList==========================="
    data = testObj.data_list
    df = pd.DataFrame(data)
    ib = Metadataservice().get_static_dataset(parms['blacklistIBName'])
    ib = map(lambda x : x['URL/IP'],ib)
    df['Blacklist_%s' % parms['inputFields']] = df.apply(lambda row :
                returnBlackList(row,False,True,ib,parms['inputFields']),axis=1)
    print "BlackList calculation done"
    dfCols = df.columns.tolist()
    dfCols = [dfCols[-1]] + dfCols[:-1]
    df = df[dfCols]
    return df

def devQuery(devObject,huntAttributes):
    print "===========================Running Dev Call for blackList==========================="
    api = '/interactiveservice/rest/elasticservice/interactivelaunch'
    jsonFile = getJsonDirPath() + 'blacklist.json'
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