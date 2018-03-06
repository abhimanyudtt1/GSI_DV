import redis
from Modules.basicUtils import configParsed,findKey
import collections
class redisConnection(object):
    def __init__(self):
        config = configParsed()
        self.redisPortHost = findKey('redisHostAndPort',config['pipeLine'])
        self.redisPortHost = list(self.redisPortHost)
        if len(self.redisPortHost) == 0 :
            print "Taking redis connection info from default config"
            self.redisPortHost = list(findKey('redisHostAndPort', config['defaultInputParams']))[0]
        else:
            self.redisPortHost = self.redisPortHost[0]
        self.connect()
    def connect(self):
        host = self.redisPortHost.split(':')[0]
        port = self.redisPortHost.split(':')[-1]
        try:
            self.conn = redis.StrictRedis(
                host= host,
                port=port,
                decode_responses=True,
                db=0)
            self.conn.ping()
        except Exception as ex:
            print 'Error:', ex
            exit('Failed to connect, terminating.')

    def execute(self,func,*args,**kwargs):
        key_pattern = kwargs["key_pattern"]
        key = kwargs["key"]
        if key is None:
            keys = self.conn.keys(key_pattern)
        else:
            keys = [key]
        output_dict = collections.OrderedDict()
        for key in keys:
            output_dict[key] = func(key, *args)
        return output_dict

    def hgetall(self, key_pattern="*", key=None):
        return self.execute(self.conn.hgetall, key_pattern=key_pattern, key=key)

    def lrange(self, key_pattern="*", key=None, start_index=0, end_index=-1):
        return self.execute(self.conn.lrange, start_index, end_index, key_pattern=key_pattern, key=key)

    def get(self, key_pattern="*", key=None):
        return self.execute(self.conn.hget, key_pattern=key_pattern, key=key)

    def flushdb(self):
        return self.redis_obj.flushdb()

    def zrange(self,key_pattern='*',key= None,start=0,end=-1):
        return self.execute(self.conn.zrange,start,end,key=key,key_pattern=key_pattern)

    def getIbFromRedis(self):
        allKeys = self.conn.keys('*')
        myDict = {}
        for k in allKeys :
            try :
                val = self.conn.zrange(k,0,-1)
            except redis.exceptions.ResponseError :
                print "Error converting key value pair of redis : %s -> %s " % ( k,val )
            #val = map(lambda x : x.split('_'),val)
            #val = map(lambda (x,y) : (x,int(y)),val)
            #val = reduce(lambda x,y : )
            myDict[k] = ','.join(val)
        return myDict

r = redisConnection()


m = r.zrange().items()[0:2]
print m
