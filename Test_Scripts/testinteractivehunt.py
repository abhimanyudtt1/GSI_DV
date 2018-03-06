from Modules.interactivehunt import Interactivehunt
from Modules.launch_hunt_jobs import HuntApi


#obj = HuntApi()
#obj.genericDevRequest('filter',{'huntName' : 'sdf', 'whereClause' : "WHERE (cert_count =  '1'  AND gsi_ts > 0 AND (orig_p LIKE( '%22%' ) AND requested_color_depth =  '24bit' ))"})
#obj.genericDevRequest('label',{'huntName' : 'sdf', 'userFields' : "orig_h:src_ip",'ibName' : "assetenrichment",'labelField' : "name",'labelValue' : "found", 'unknownLabelValue' : "false"})

#print obj.liveJson
testobj = Interactivehunt ()
#print testobj.liveJson
#exit()
testobj.startInteractiveHunt()
#testobj.startinteractivehunt ()

#testobj.startInteractiveHunt()

# testobj.validate_livepipeline('rdpds5','blacklist:geoip', 'hunt5rdpds5_1','3600',1,'orig_h,resp_h')
