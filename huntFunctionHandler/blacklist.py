

def getMainFunction():
    return applyblacklist

def applyblacklist(self,blacklistib='blacklist1', data_columns="srcIp"):
    print "This is BlackList Application"
    dump = self.get_static_dataset (blacklistib)
    ib_dict = {}
    for item in dump:
        for value in item.values ():
            ib_dict[value] = "True"
    ib_columns = "Blacklist"
    default_ib_columns = "False"
    self.data_list = self.applyenrichment (self.data_list, data_columns, ib_dict, ib_columns, default_ib_columns)
    return self.data_list




