# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import sys,json
if __name__ == "__main__":
    print "This is module, don't run it alone"
    sys.exit(1)
class SimpleQuery:
    params = dict()
    def __init__(self):
        self.params["includeTotal"] = '"true"';
        self.params["limit"] = '0';
    def set_limit(self,limit):
        self.params["limit"] = int(limit);
    def set_basic_filter(self,field,value):
        self.params["filters"] = '[{"type" : "EsmFieldFilter","field": {"name": "%s"},"operator": "EQUALS","values": [{    "type" : "EsmBasicValue","value" : "%s"}]}]' % (field,value)
    def set_complex_filter(self,field,value):
        sys.exit(100)
        self.params["filters"] = """
        [{
            "type" : "EsmFieldFilter",
            "field": {"name": "%s"},
            "operator": "IN",
            "values": [{
                "type" : "EsmBasicValue",
                "value" : "<25"
            }]
        }]
        """ % (field)

    def set_fields(self,fields):
        
        #: [{"name": "DSIDSigID"},{"name": "Rule.msg"},{"name": "AvgSeverity"}],
        p = "["
        for f in fields:
            p+='{"name": "%s"},' % (f)
        p = p[:-1]
        p += "]"
        self.params["fields"] = p
    def set_order(self,field,direction = 'ASCENDING'):
        self.params["order"] = '[{"direction": "%s","field": {"name": "%s"}}]' % (direction,field)
    def set_custom_time(self,start,end):
        self.params["timeRange"] = '"CUSTOM"'
        self.params["customStart"] = '"%s"' % (start)
        self.params["customEnd"] = '"%s"' % (end)
    def render(self):
        out = ""
        for key in self.params:
            out+='"%s" : %s,' % (key,self.params[key])
        out = '{"config": {%s}}' % (out[:-1])
        try:
            json.loads(out)
        except:
            print 'blad w json'
            sys.exit(1)
        return out
