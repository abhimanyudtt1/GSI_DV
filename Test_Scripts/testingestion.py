from Modules.ingestion import Ingestion
import time

# Test Cases
testobj = Ingestion ()

# TC_1 : Test Ingestion calls for ALl the Logs

testobj.fire_ingestion_api()

# TC_2 : Check Indices created by Ingestion service

testobj.check_ingestion_status ()

es_stats_before_newLogs = testobj.take_indices_backup

# TC_4 : Push Live, Old & Future  Logs

print ("Pushing Live, Old & Future  Logs:\n")

#testobj.push_logs ()

# TC_5 : Calculate the Indices and records counts of each Logs which are newly pushed.

calculated_stats_of_newLogs = testobj.calculate_indices

# TC_6 : Get the Indicies and records counts of each Logs in ES after Pushing new Logs
es_stats_after_newLogs = testobj.take_indices_backup

Actual_dev_binned = testobj.actual_bined_newlogs (es_stats_after_newLogs, es_stats_before_newLogs)

print ("Es Stats after before Logs {}".format(es_stats_before_newLogs))
print ("Es Stats after New Logs {}".format(es_stats_after_newLogs))


print ("Dev Calculated Binning for new logs:", Actual_dev_binned)
print ("QA Calculated Binning for new logs", calculated_stats_of_newLogs)

# print "Mismatch in Binning", testobj.actual_bined_newlogs(calculated_stats_of_newLogs,Actual_dev_binned)


# TC_7 : Aggregation TC_3 + TC_5 should result into TC_6