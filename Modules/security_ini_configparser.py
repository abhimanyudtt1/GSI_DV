import ConfigParser
import logging
from Modules.basicUtils import configParsed


class SecurityConfigParser (object):
    def __init__(self):
        self._logger = logging.getLogger (__name__)

    @staticmethod
    def get_section(file, mysection='ingestion'):
        config = configParsed()
        return config[mysection]
        '''parser = ConfigParser.ConfigParser ()
        parser.readfp (open (file))
        return {section: dict (parser.items (section)) for section in parser.sections ()}[mysection]'''
