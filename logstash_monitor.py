import logging,os,yaml
import requests,json
log = logging.getLogger()
logging.basicConfig(level=logging.ERROR)
config=os.path.join(os.path.dirname(__file__),"logstash_config.yml")
prometheus=os.path.join(os.path.dirname(__file__),"logstash.prom")
ml=[]
with open(config,'r') as f:
    r=f.read()
    y=yaml.load(r)
    yl = []
    for i  in  y.get("logstash_server"):
        yl.append((y.get("logstash_server").get(i)))
    e=y.get('env')
def get_logstash_info(hostname, port):
    metrics=[]
    uri_list = [  "jvm","process","pipeline"]
    for uri in uri_list:
        r = requests.get(url="http://" + hostname + ".mynextev.net:" + str(port) + "/_node/stats/" + uri + "?pretty")
        metrics.append(json.dumps(r.json()))
    return metrics

def DictFormat(Dict,First_key=None):
    for k in Dict:
        if isinstance(Dict[k],dict):
            if First_key != None:
                DictFormat(Dict[k],First_key=First_key+'_'+k)
            else:
                DictFormat(Dict[k],First_key=k)
        else:
            if First_key != None:
                if type(Dict[k]) == int or type(Dict[k])==float:
                    ml.append({First_key+'_'+k:Dict[k]})
            else:
                if type(Dict[k]) == int or type(Dict[k]) == float:
                    ml.append({k:Dict[k]})
    return ml
if __name__ == '__main__':
    with open(prometheus,'w+') as  f:
        for y in yl:
            r = get_logstash_info(y[0].get('hostname'), y[1].get('port'))
            for i in r:
                ml.clear()
                res = DictFormat(json.loads(i))
                for l in res:
                    tags='''Department="SWC",Owner="sqe-se",Project="elk-logstash",Team="SQE",env="{}", hostname="{}"'''.format(e,y[0].get('hostname'))
                    f.writelines("logstash_" + list(l.keys())[0]+ "{" +tags + "}" + " " + str(list(l.values())[0] ))
                    f.writelines("\n")
