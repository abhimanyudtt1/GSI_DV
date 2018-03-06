from Modules.launch_hunt_jobs import HuntApi
testobj = HuntApi()
testobj.requestSource('rdpsuccess',"Automation_Hunt120")
testobj.waitTillFinishedOrFailed("1")
print(testobj.requestDriverStatus())
print("First", testobj.outputdataset)

testobj.requestEnrichment("blacklist1","resp_h")

testobj.waitTillFinishedOrFailed("1")

print(testobj.requestDriverStatus())

print("Second", testobj.outputdataset)

testobj.requestpPipelineLive()
testobj.waitTillFinishedOrFailed("1")

print(testobj.requestDriverStatus())
print("Third---LiveHunt", testobj.outputdataset)



