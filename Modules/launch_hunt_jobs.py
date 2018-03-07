from __future__ import print_function
from __future__ import print_function
import json
import os
import time
import re
import sys
from rest_utils import REST
import imp
from Modules.basicUtils import configParsed


class HuntApi (REST):

    def __init__(self, ip='192.168.133.53', port='6773', json_folder=None):
        super (HuntApi, self).__init__ ()
        self.tooldir = os.getcwd()
        if json_folder is None:
            self.json_folder = self.tooldir + "/Test_Data/json_folder/"
        self.headers = {"Content-Type": "application/json"}
        conf = configParsed()
        ip_port = conf['interactivehunt']['url']
        self.url = ip_port
        self.current_request = None
        self.current_response = {}
        self.outputdataset = None
        self.driverId = None
        self.enrichment_name = None
        self.liveJson = []

    def _set_url(self, ip, port):
        return "http://" + ip + ':' + str (port)

    def createDir(self, directory):
        if not os.path.exists (directory):
            os.makedirs (directory)

    def returnOutputDatasetName(self):
        self.outputdataset = self.current_response["output"]
        return self.outputdataset

    def returndriverId(self):
        self.driverId = self.current_response["identifier"]
        return self.driverId

    def update_dict(self, obj, key, replace_value, search=None, myindex=None):
        for k, v in obj.items ():
            if isinstance (v, dict):
                obj[k] = self.update_dict (self, v, key, replace_value)
            elif isinstance (v, list):
                for index, i in enumerate (v):
                    self.update_dict (i, key, replace_value, search, index)
        if key in obj:
            if myindex == search:
                obj[key] = replace_value
        return obj

    def requestSource(self, input_=None, huntName=None, json_template='get_source.json', startTime=None, endTime=None,
                      api=None):
        json_template_path = self.json_folder + json_template

        if api is None:
            api = '/interactiveservice/rest/elasticservice/interactivelaunch'
        else:
            api = api
        dictObj = json.load (open (json_template_path))
        to_update = {"input": input_, "huntName": huntName, "startTime": startTime, "endTime": endTime}
        dictObj.update ((k, v) for k, v in to_update.iteritems () if v is not None)
        print(self.url+ api,self.headers,dictObj)

        response = self.execute_request ("post", self.url + api, data=json.dumps (dictObj), headers=self.headers)
        if response.status_code == 200:
            try:
                self.current_response = json.loads (response.content)
            except:
                self.current_response = response.content
        else:
            print ("Launching get Source failed!!!")
        self.enrichment_name = huntName
        self.returnOutputDatasetName ()
        self.returndriverId ()
        self.requestDriverStatus ()

    def requestDriverStatus(self, api=None):
        if api is None:
            api = '/interactiveservice/rest/elasticservice/getstatus'
        response = self.execute_request ("get", self.url + api + "/" + self.driverId)
        if response.status_code == 200:
            output = response.content
            try:
                driver_response = json.loads (output)
            except:
                driver_response = output
        return driver_response['status']

    def returnLiveCall(self,huntName,dataset,freeq):
        data_json = {}
        data_json['outputDatasetName'] = huntName
        data_json['dag'] = {}
        data_json['dag']['functionset'] = self.liveJson
        data_json['inputDatasetName'] = dataset
        data_json['start'] = True
        data_json['huntName'] = huntName
        data_json['frequency'] = freeq
        data_json['user'] = "admin"
        data_json['description'] = "adsfasd"
        data_json['dag'] = json.dumps(data_json['dag'])
        return json.dumps(data_json)

    def genericDevRequest(self,huntName,params):
        try :
            params.pop('huntName')
        except KeyError:
            pass
        huntAttributes = params
        f, filename, description = imp.find_module(huntName,
                                                   [os.getcwd() + '/huntFunctionHandler'])
        handle = imp.load_module(huntName, f, filename, description)
        function = handle.getDevAPIFunction()
        api_body = function(self,huntAttributes)
        if api_body == 0 :
            return False
        else:
            api,body = api_body
        self.liveJson.append(json.loads(json.loads(body)['dag'])['functionset'][0])
        response = self.execute_request("post", self.url + api, data=body, headers=self.headers)
        if response.status_code == 200:
            try:
                self.current_response = json.loads (response.content)
            except:
                self.current_response = response.content
        else:
            print ("Response not 200 Exiting ")
            allAttrs = vars(response)
            print (', '.join("%s: %s" % item for item in allAttrs.items()))
            exit(1)
        self.returnOutputDatasetName ()
        self.returndriverId ()
        return True
    def requestEnrichment(self, ibname=None, enrichment_fields=None, json_template='blacklist.json', api=None):
        json_template_path = self.json_folder + json_template
        if api is None:
            api = '/interactiveservice/rest/elasticservice/interactivelaunch'
        dictObj = json.load (open (json_template_path))
        dictObj["input"] = self.outputdataset
        dictObj["huntName"] = self.enrichment_name

        '''If blacklist.json file is a Pure JSOn fields then update the ibname and Fields to enrich this way'''
        if enrichment_fields is not None:
            dictObj = self.update_dict (dictObj, "value", enrichment_fields, 1, None)
        if ibname is not None:
            dictObj = self.update_dict (dictObj, "value", ibname, 0, None)

        '''If blacklist.json file properties field is a string not a JSON fields then update the ibname and Fields to 
        enrich this way Work Around till it gets fixed.'''
        try:
            dictObj["functionProperties"] = re.sub ('[A-Za-z0-9]+?referenceib', ibname, dictObj["functionProperties"])
            dictObj["functionProperties"] = re.sub ('[a-zA-Z0-9,_]+(\"[ \t]*?}])', enrichment_fields + r"\1",
                                                    dictObj["functionProperties"])
        except TypeError:
            pass
        #print (self.outputdataset)
        #print (enrichment_fields)
        #print (dictObj["functionProperties"])
        response = self.execute_request ("post", self.url + api, data=json.dumps (dictObj), headers=self.headers)
        if response.status_code == 200:
            try:
                self.current_response = json.loads (response.content)
            except:
                self.current_response = response.content
        self.returnOutputDatasetName ()
        self.returndriverId ()

    def request_filter(self, json_template='filter.json', conditions=None, api=None):
        json_template_path = self.json_folder + json_template
        if api is None:
            api = '/interactiveservice/rest/elasticservice/interactivelaunch'
        dictObj = json.load (open (json_template_path))
        dictObj["input"] = self.outputdataset
        dictObj["huntName"] = self.enrichment_name
        if conditions is None:
            conditions = "WHERE ("+conditions+")"
            try:
                dictObj["functionProperties"] = re.sub ('[a-zA-Z0-9,_]+(\"[ \t]*?}])', conditions + r"\1", dictObj["functionProperties"])
            except:
                pass
        print (self.outputdataset)
        print (dictObj["functionProperties"])

        response = self.execute_request ("post", self.url + api, data=json.dumps (dictObj), headers=self.headers)
        if response.status_code == 200:
            try:
                self.current_response = json.loads (response.content)
            except:
                self.current_response = response.content
        self.returnOutputDatasetName ()
        self.returndriverId ()

    def request_topngroupby(self, json_template='filter.json', conditions=None, api=None):
        json_template_path = self.json_folder + json_template
        if api is None:
            api = '/interactiveservice/rest/elasticservice/interactivelaunch'
        dictObj = json.load (open (json_template_path))
        dictObj["input"] = self.outputdataset
        dictObj["huntName"] = self.enrichment_name
        if conditions is None:
            conditions = "WHERE (" + conditions + ")"
            try:
                dictObj["functionProperties"] = re.sub ('[a-zA-Z0-9,_]+(\"[ \t]*?}])', conditions + r"\1",
                                                        dictObj["functionProperties"])
            except:
                pass
        print (self.outputdataset)
        print (dictObj["functionProperties"])

        response = self.execute_request ("post", self.url + api, data=json.dumps (dictObj), headers=self.headers)
        if response.status_code == 200:
            try:
                self.current_response = json.loads (response.content)
            except:
                self.current_response = response.content
        self.returnOutputDatasetName ()
        self.returndriverId ()


    def requestpPipelineLive(self, frequency="3600", json_template="live_hunt.json", api=None):
        if api is None:
            api = '/interactiveservice/rest/elasticservice/livelaunch'
        json_file = self.json_folder + json_template
        dictObj = json.load (open (json_file))
        dictObj["huntName"] = self.enrichment_name
        dictObj["freq"] = frequency.strip ()
        response = self.execute_request ("post", self.url + api, data=json.dumps (dictObj), headers=self.headers)
        if response.status_code == 200:
            try:
                self.current_response = json.loads (response.content)
            except:
                self.current_response = response.content
        else:
            print ("Launching Request Live Pipe failed!!!")
        print (self.current_response)
        self.returnOutputDatasetName ()
        self.returndriverId ()
        print (self.driverId)

    def waitTillFinishedOrFailed(self, monitor_time=15):
        counter = 0
        time.sleep (1)
        while self.requestDriverStatus () != "FINISHED":
            print("In monitoring, response: " + str(self.requestDriverStatus()))
            time.sleep (60)
            #print ("In monitoring, response: " + str (self.requestDriverStatus ()))
            counter = counter + 1
            if counter >= int (monitor_time):
                return self.requestDriverStatus ()
        return self.requestDriverStatus ()
