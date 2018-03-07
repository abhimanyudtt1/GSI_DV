import os
import yaml
import json

def getJsonDirPath():
    return '/'.join(os.getcwd().split('/')[:-1])+'/Test_Data/json_folder/'



def configParsed(configFile='Config/huntInputParams.yml'):
    stream = file(configFile)
    return yaml.safe_load(stream)

def getConfigFlow(configFile="Config/huntInputParams.yml"):
    config = configParsed(configFile)
    pipeLine = config['pipeLine']


def setParamsInJson(jsonFile,devObject,huntAttributes):
    jsonFile = json.loads('\n'.join(open(jsonFile).readlines()))
    jsonFile["input"] = devObject.outputdataset
    jsonFile["huntName"] = devObject.enrichment_name
    functionProperties = json.loads(jsonFile["functionProperties"])
    tempFunctionProperties = []
    for k, v in huntAttributes.items():
        for eachItem in functionProperties:
            if eachItem['name'] == k:
                eachItem['value'] = v
            tempFunctionProperties.append(eachItem)
    functionProperties = json.dumps(tempFunctionProperties, separators=(',', ':')).replace('"', '\\"')
    jsonFile["functionProperties"] = functionProperties
    return jsonFile


def findKey(key, dictionary):
    for k, v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in findKey(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d,dict):
                    for result in findKey(key, d):
                        yield result
