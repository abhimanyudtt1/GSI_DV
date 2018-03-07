#from __future__ import print_function
from calculate_hunt_functions import Enrichment
from launch_hunt_jobs import HuntApi as LaunchHunt
from Modules.comparator import comparator
from metadataservice import Metadataservice
import json
import time
import csv
import subprocess
from ingestion import Ingestion
from Modules import basicUtils
from random import randint
def write_to_file(filename, my_list):
    print(len(my_list))
    with open (filename, 'w') as FH:
        if not any(my_list):
            return
        writer = csv.DictWriter (FH, my_list[0].keys ())
        writer.writeheader ()
        writer.writerow (my_list[0])
        for i in my_list[1:]:
            writer.writerow (i)
        FH.close ()
        return


class Interactivehunt (Enrichment, LaunchHunt):

    def __init__(self, conf='Config/security_dv.ini'):
        pass
        #super (Interactivehunt, self).__init__ ()
        self.ingested_logs = Ingestion ().query_dict
        loadconfig = self.get_section (conf, 'interactivehunt')
        #self.huntname_prefix = loadconfig['huntname_prefix']
        #self.pipelines = loadconfig['pipelines']
        #self.enrichment_map = json.loads (loadconfig['enrichment_map'])
        #self.staticib = Ingestion ().staticib
        self.count = 0
        #self.frequency = loadconfig['frequency']
        #self.iterations = int (loadconfig['iterations'])




    def runLivePipe(self,pipe,params):
        #self.runValidPipeline(pipe,params)
        current_huntname = pipe['prefix'] + pipe['log'] + str(self.count) + "_" + "%05d" % randint(1,99999)
        liveCallBody = self.runValidPipeline(pipe,params)
        dataset = pipe['log'] + pipe['prefix']
        api = basicUtils.configParsed()['liveHunt']['url'] + basicUtils.configParsed()['liveHunt']['api']
        testObj = Enrichment()
        headers = basicUtils.configParsed()['liveHunt']['header']
        result = testObj.execute_request("post", api, data=liveCallBody, headers=headers)
        outputDataSet = result.json()['output']
        devobj = LaunchHunt()
        dataSetMetaInfo = Metadataservice().calculate_datasource_properties
        try :
            ST, ET = dataSetMetaInfo[outputDataSet][0:2]
        except KeyError:
            ST,ET = (-1,-1)
        print ("Pushing the Logs:")
        config = basicUtils.configParsed()
        ingestionConfig = config['ingestion']
        logPathServer = ingestionConfig['inputlogspath']
        logPathLocal = ingestionConfig['localdatapath']
        logType = pipe['log']
        logPathLocal += '/' + logType
        output = subprocess.Popen('ls %s ' % logPathLocal,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()
        output = output[0].split('\n')
        output = map(lambda x: x.split('_'), output)
        output = map(lambda x: map(lambda y: y.split('.')[0], x), output)
        output = map(lambda x: x[1:], output)
        output = map(lambda x: ':'.join(x), output)
        pattern = '%d:%m:%Y:%H:%M'
        import time
        output = filter(lambda x : not x == '',output)
        epochOutput = map(lambda x: int(time.mktime(time.strptime(x, pattern))), output)
        output = map(lambda x: (int(time.mktime(time.strptime(x, pattern))), logType.upper()+'_' + '_'.join(x.split(':')) + '.log'), output)
        epochOutput = filter(lambda x : x > ET,epochOutput )
        output = filter(lambda (x,y) : x in epochOutput,output)
        output = map(lambda (x, y): y, output)
        if len(output) == 0 :
            raise Exception("No futher logs present for this")
        else:
            Ingestion().push_logs()
        while True :
            dataSetMetaInfo = Metadataservice().calculate_datasource_properties
            newET = dataSetMetaInfo[dataset][1]
            if newET > ET :
                break
            print "New Data Not yet injested Waiting for 60 sec"
            time.sleep(60)


        jsonBody = json.dumps(basicUtils.configParsed()['liveHunt']['pause']['jsonBody'])
        jsonBody['huntName'] = outputDataSet
        testObj.getsource(dataset, ST, ET)
        #Pause
        testObj.execute_request('post',basicUtils.configParsed()['liveHunt']['pause']['api']
                                ,basicUtils.configParsed()['liveHunt']['header']
                                ,data=jsonBody)
        devData = Metadataservice().get_static_dataset(outputDataSet)

        #Play
        jsonBody = json.dumps(basicUtils.configParsed()['liveHunt']['pause']['jsonBody'])
        jsonBody['huntName'] = outputDataSet
        testObj.execute_request('post', basicUtils.configParsed()['liveHunt']['play']['api']
                                , basicUtils.configParsed()['liveHunt']['header']
                                , data=jsonBody)
        for k, v in pipe['flow'].items():
            qa_result = testObj.getHuntFunction(v['huntName'])(testObj, params[v['huntName']][pipe['log']])
        comparator(devData,qa_result)

    def validate_livepipeline(self, dataset, pipeline, huntName, frequency, iteration, enrichment_fields):
        frequency = int (frequency)
        if iteration < 1:
            return
        qa_results = []
        testobj = Enrichment ()
        ST, ET = Metadataservice ().calculate_datasource_properties[dataset][0:2]
        ST = frequency * (int (ET) // frequency)
        ET = ST + frequency
        # Ingest New Logs <--> Logic
        print ("Pushing the Logs:")
        Ingestion ().push_logs ()
        time.sleep (60)
        testobj.getsource (dataset, ST, ET)
        for huntfunction in pipeline.split (':'):
            ibname = self.ingested_logs[huntfunction][0]
            function = testobj.getHuntFunction(huntfunction)
            qa_results = function(testobj, ibname, enrichment_fields)

            '''
            if huntfunction == "blacklist":
                ibname = self.ingested_logs[huntfunction][0]
                function = testobj.getHuntFunction(huntfunction)
                qa_results = function (testobj,ibname, enrichment_fields)
            if huntfunction == "geoip":
                ibname = self.ingested_logs['geoip'][0]
                qa_results = testobj.applygeoip (ibname, enrichment_fields)
            ##### XXXX #####'''
        # TBD  -> Monitor the Completion of HuntJobs before taking the Dev Dumps
        time.sleep (180)
        dev_results = Metadataservice ().get_dataset_timerange (huntName, ST, ET)
        print (
            'LiveHunt QA Results and Dev Results for HuntName: {}, having pipeLine: {} on datset :{} & ST & ET : {}'.format (
                huntName, pipeline, dataset, str (ST) + ':' + str (ET)))
        print (qa_results, dev_results)
        self.validate_livepipeline (dataset, pipeline, huntName, frequency, iteration - 1, enrichment_fields)


    def runValidPipeline(self,pipe,params):
        current_huntname = pipe['prefix'] + pipe['log'] + str(self.count)
        dataset = pipe['log'] + pipe['prefix']
        devobj = LaunchHunt()
        testobj = Enrichment()
        ST, ET = Metadataservice().calculate_datasource_properties[dataset][0:2]
        print ("GetSource call being sent for Dev object")
        devobj.requestSource(dataset, huntName=current_huntname, json_template="get_source.json", startTime=ST,
                             endTime=ET)
        devobj.waitTillFinishedOrFailed("1")
        print ("GetSource got Completed for dataset: {} and pipeline-id: {}".format(dataset, self.count))
        print ("GetSource Call being sent for Test Object")
        testobj.getsource(dataset, ST, ET)
        print ("GetSource Call being completed for Test Object")
        for k,v in pipe['flow'].items():

            result = devobj.genericDevRequest(v['huntName'],params[v['huntName']][pipe['log']])
            if not result:
                continue
            devobj.waitTillFinishedOrFailed("5")
            print("Apply enrichment {} got Completed with  for pipeline-id: {} and dataset: {}"
                  .format(v['huntName'],self.count,dataset))
            es_dataset_name = devobj.outputdataset
            try:
                dev_result =  Metadataservice().get_static_dataset(es_dataset_name)
            except:
                dev_result = []
            ibname = dataset
            qa_result = testobj.getHuntFunction(v['huntName'])(testobj,params[v['huntName']][pipe['log']])
            testobj.data_list = qa_result
            # = function(testobj, v)
            comparator(dev_result,qa_result)
        return devobj.returnLiveCall(current_huntname+'_'+"%05d" % randint(1,99999),devobj.outputdataset,"3600")

    def _run_validate_pipeline(self, pipeline, dataset, enrichment_fields):
        current_huntname = self.huntname_prefix + dataset + '_' + str (self.count)
        devobj = LaunchHunt ()
        testobj = Enrichment ()
        ST, ET = Metadataservice ().calculate_datasource_properties[dataset][0:2]
        devobj.requestSource (dataset, huntName=current_huntname, json_template="get_source.json", startTime=ST,
                              endTime=ET)
        devobj.waitTillFinishedOrFailed ("1")
        print ("GetSource got Completed for dataset: {} and pipeline-id: {}".format (dataset, self.count))
        #testobj.getsource (dataset, ST, ET)
        for huntfunction in pipeline.split (':'):
            ibname = 0
            #self.ingested_logs[dataset][0]
            result = devobj.genericDevRequest(huntfunction)
            if not result:
                continue

            devobj.requestEnrichment(ibname, enrichment_fields, huntfunction + ".json")
            devobj.waitTillFinishedOrFailed("5")
            print(
                "Apply enrichment {} got Completed with  for pipeline-id: {} and dataset: {}".format(huntfunction,
                                                                                                     self.count,
                                                                                                     dataset))
            es_dataset_name = devobj.outputdataset
            try:
                dev_result = [] # Metadataservice().get_static_dataset(es_dataset_name)
            except:
                dev_result = []
            ibname = dataset
            function = testobj.getHuntFunction(huntfunction)
            qa_result = function(testobj, ibname, enrichment_fields)
            # qa_result = testobj.applyblacklist (ibname, enrichment_fields)
            # print ("First dev & QA results: {}, {}".format (dev_result, qa_result))
            # write_to_file(current_huntname+huntfunction+'_qa', qa_result)
            # write_to_file (current_huntname + huntfunction + '_dev', dev_result)
            '''
            if huntfunction == "blacklist":
                ibname = self.ingested_logs['blacklist'][0]
                devobj.requestEnrichment (ibname, enrichment_fields, huntfunction + ".json")
                devobj.waitTillFinishedOrFailed ("5")
                print (
                    "Apply enrichment {} got Completed with  for pipeline-id: {} and dataset: {}".format (huntfunction,
                                                                                                          self.count,
                                                                                                          dataset))
                es_dataset_name = devobj.outputdataset
                try:
                    dev_result = Metadataservice ().get_static_dataset (es_dataset_name)
                except:
                    dev_result = []
                ibname = self.ingested_logs['blacklist'][0]
                function = testobj.getHuntFunction(huntfunction)
                qa_result = function(testobj, ibname, enrichment_fields)
                

            if huntfunction == "geoip":
                ibname = self.ingested_logs['geoip'][0]
                devobj.requestEnrichment (ibname, enrichment_fields, huntfunction + ".json")
                devobj.waitTillFinishedOrFailed ("5")
                print ("Apply enrichment {} got Completed  for pipeline-id: {} and dataset {}".format (huntfunction,
                                                                                                       self.count,
                                                                                                       dataset))
                es_dataset_name = devobj.outputdataset
                try:
                    dev_result = Metadataservice ().get_static_dataset (es_dataset_name)
                except:
                    dev_result = []
                qa_result = testobj.applygeoip (ibname, enrichment_fields)

                write_to_file(current_huntname+huntfunction+'_qa', qa_result)
                write_to_file (current_huntname + huntfunction + '_dev', dev_result)
                #print ("Dev & QA results: {}, {}".format (dev_result, qa_result))
        #print ("InteractiveHunt Completed for: {}, Going Live now".format (current_huntname))
        #devobj.requestpPipelineLive (self.frequency)
        #self.validate_livepipeline (dataset, pipeline, current_huntname, self.frequency, self.iterations,enrichment_fields)
        NO NEED FOR THIS PART AS ITS NOT HANDLED WITH HELPERS '''

    def startinteractivehunt(self):
        for log_type in self.ingested_logs.keys ():
            if log_type in self.staticib:
                continue
            dataset = self.ingested_logs[log_type][0]
            enrichment_json = json.dumps (self.enrichment_map)
            enrichment_dict = json.loads (enrichment_json)
            if log_type not in enrichment_dict:
                print("Not Applying Enrichment map for log : {}".format(log_type))
                continue
            else:
                enrichment_fields = enrichment_dict[log_type]
            for pipeline in self.pipelines.split (','):
                self.count = self.count + 1
                print ("Starting Interactive Hunt for : {} with dataset: {} & pipeline: {}".format (log_type, dataset,
                                                                                                    pipeline))
                self._run_validate_pipeline (pipeline, dataset, enrichment_fields)

    def startInteractiveHunt(self):
        config = basicUtils.configParsed()

        #huntInputParams = config['defaultInputParams']
        pipeLine = config['pipeLine']
        pipeline = ''
        defaults = config['defaultInputParams']
        for pipe,val in pipeLine.items():
            self.count = self.count + 1
            print ("Working on pipeLine : %s " % pipe)
            print ("Pipe Line Type : %s " % val['type'])
            print ("Log to be taken : %s " % val['log'])
            print("")
            pipeline = map(lambda (x,y) : y['huntName'],val['flow'].items())
            for k,v in val['flow'].items():
                try :
                    defaults[v['huntName']][val['log']].update(v)
                except KeyError:
                    raise Exception("Default Params Not present for %s for hunt type : %s " % (val['log'], v['huntName']))

            #pipeline = ':'.join(pipeline)
            if  val['type'].lower() == 'interactive':
                print "Interactive Type of request made for the log : %s " % val['log']+val['prefix']
                #val['flow']
                #defaults[val['log']]
                self.runValidPipeline(val,defaults)
            elif val['type'].lower() == 'live' :
                print "Live Type of request made for log : %s " % val['log']+val['prefix']
                self.runLivePipe(val,defaults)



