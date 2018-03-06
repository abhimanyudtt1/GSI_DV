import glob
import re
from date_utils import DateUtils


class LogParser (object):
    def __init__(self, log_type, log_dir, dataset, timeformat, ts_col=0, field_seperator='\t'):
        self.log_type = log_type
        self.log_dir = log_dir
        self.files = self._get_files ()
        self.timeformat = timeformat
        self.ts_col = ts_col
        self.field_seperator = field_seperator
        self.dataset = dataset

    def _get_files(self):
        return glob.glob (self.log_dir)

    def parse_ib(self):
        binning_index = {}
        for FILE in self.files:
            for line in open (FILE):
                if re.match (r'^#', line):
                    continue
                if self.dataset not in binning_index:
                    binning_index[self.dataset] = 1
                else:
                    binning_index[self.dataset] = binning_index[self.dataset] + 1
        return binning_index

    def parse_log(self):
        binning_index = {}
        for FILE in self.files:
            for line in open (FILE):
                if re.match (r'^#', line):
                    continue
                ts = line.split (self.field_seperator)[self.ts_col]
                try:
                    current_index = self.dataset + '-' + DateUtils (ts, self.timeformat).get_binning_index ()
                except:
                    current_index = ''
                if current_index:
                    if current_index not in binning_index:
                        binning_index[current_index] = 1
                    else:
                        binning_index[current_index] = binning_index[current_index] + 1

        return binning_index
