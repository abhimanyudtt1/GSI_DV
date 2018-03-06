from Modules.ip_utils import IpUtils
import re

def getMainFunction():
    return applygeoip

def applygeoip(self, geoipib="geoip1", data_columns="srcIp"):
    print "This is GeoFilter Application"
    ib_dict = {}
    dump = self.get_static_dataset (geoipib)
    try:
        ib_columns = [column for column in dump[0].keys () if not re.match ('ip_*', column)]
        default_ib_columns = ['', 0.0, 0.0, '']
    except IndexError:
        ib_columns = None
    for item in dump:
        ips = IpUtils ().ips_in_range (item['ip_start_range'], item['ip_end_range'])
        for ip in ips:
            ib_dict[ip] = []
            for ib_column in ib_columns:
                ib_dict[ip].append (item[ib_column])
    self.data_list = self.applyenrichment (self.data_list, data_columns, ib_dict, ib_columns, default_ib_columns)
    return self.data_list


