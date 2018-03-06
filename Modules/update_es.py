import elasticsearch
import json
import sys

def es_update(key, value):
    es_conn = elasticsearch.Elasticsearch ("192.168.112.52:6775")
    mydict = { "script": { "inline": "ctx._source.system.process.name=\""+key+"\"","lang": "painless"},
            "query": { "term": { "system.process.pid": value} }
        }
    body=json.dumps(mydict)
    es_conn.update_by_query('metricbeat-*',body=body)

pidfile = sys.argv[1]
for line in open(pidfile).readlines():
    line = line.strip('\n')
    if not line:
        continue
    array=line.split(',')
    process_name=array[1]
    pid_name=array[0]
    es_update(process_name, pid_name)