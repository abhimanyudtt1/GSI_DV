from Modules.metadataservice import Metadataservice

testobj = Metadataservice()

# Sample TC :: Compare All the dataset properties

dev_properties = testobj.get_datasource_properties
qa_properties = testobj.calculate_datasource_properties

print ("Dataset :: Dev properties->[ST, ET, AverageKfps, PeakKfps] :: QA properties->[ST, ET, AverageFps, PeakFps]")
for key in dev_properties.keys():
    print(key, "::", dev_properties[key], "::", qa_properties[key])
