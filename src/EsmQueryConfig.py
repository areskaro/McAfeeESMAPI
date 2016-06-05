# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import sys,json
if __name__ == "__main__":
    print "This is module, don't run it alone"
    sys.exit(1)
class EsmFieldFilterElement :
    element_name = ''
    element_type = 'EsmBasicValue'
    element_operator = 'IN'
    def __init__(self,element_name,element_type = 'EsmBasicValue'):
        self.element_name = element_name;
        self.element_type = element_type;
    def value(self,value):
        self.element_values = value
        return self
    def values(self,values):
        self.element_values = ','.join(values)
        return self
    
    def operator(self,operator):
        operator_list = ['IN','NOT_IN','DOES_NOT_EQUAL','EQUALS','CONTAINS','DOES_NOT_CONTAIN']
        if not operator in operator_list:
            raise Exception('Unknown operator; acceptable one: IN, NOT_IN, EQUALS')
        self.element_operator = operator
        return self
    def render(self):
        return """{
            "type" : "EsmFieldFilter",
            "field": {"name": "%s"},
            "operator": "%s",
            "values": [{
                "type" : "%s",
                "value" : "%s"
            }]
        }""" % (self.element_name,self.element_operator,self.element_type,self.element_values)
class SimpleQuery:
    params = dict()
    def __init__(self):
        self.params["includeTotal"] = '"true"';
        self.params["limit"] = '0';
        self.params["filters"] = [];
    def set_limit(self,limit):
        self.params["limit"] = int(limit);
    def addNewFilter(self,element_name,element_type = 'EsmBasicValue'):
        a = EsmFieldFilterElement(element_name,element_type)
        self.params["filters"].append(a)
        return a
        
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
    def set_defined_time(self,defName):
        '''
        Accepted Values:
            CUSTOM
            LAST_MINUTE
            LAST_10_MINUTES
            LAST_30_MINUTES
            LAST_HOUR
            CURRENT_DAY
            PREVIOUS_DAY
            LAST_24_HOURS
            LAST_2_DAYS
            LAST_3_DAYS
            CURRENT_WEEK
            PREVIOUS_WEEK
            CURRENT_MONTH
            PREVIOUS_MONTH
            CURRENT_QUARTER
            PREVIOUS_QUARTER
            CURRENT_YEAR
            PREVIOUS_YEAR
        '''
        self.params["timeRange"] = '"%s"' % (defName)
    def render(self):
        out = ""
        for key in self.params:
            if key == 'filters' : 
                
                out+='"filters" : ['
                for skey in self.params[key]:
                    out+="%s," % (skey.render())
                if len(self.params[key]) > 0:
                    out = out[:-1]
                out+='],'
            else:
                out+='"%s" : %s,' % (key,self.params[key])
        out = '{"config": {%s}}' % (out[:-1])
        try:
            json.loads(out)
        except:
            print 'blad w json'
            sys.exit(1)
        return out
        
