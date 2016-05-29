# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
if __name__ == "__main__":
    print "This is module, don't run it alone"
    sys.exit(1)
import xml.parsers.expat
import base64
import sys,time,string
import httplib,urllib,ssl
import json
import getpass
from collections import deque

class xp ():
    def __init__(self):
        self.key = 'sessionID'
        self.store = dict()
    def start_element(self,key, attrs):
        self.key = key       
        self.attr = attrs
    def char_data(self,data):
        if self.key == 'sessionID' :
            self.store[self.key] = data #epr(data)  
            self.key = None
    def get(self,name):
        return self.store[name]
#
# @version 0.2
# @author Arek macak
#
class API():
    conn = None
    sessionID = None
    host = '0.0.0.0'
    result_table = deque()
    def __init__(self,host,port = 443):
        #context = ssl._create_unverified_context()#ssl.create_default_context()
        self.host = host
        #self.conn = httplib.HTTPSConnection(host,port,None,None,None,None,None,context)
        self.conn = httplib.HTTPSConnection(host,port,timeout=30)
       
        print 'Creating new API instance for host: ',host,':',port

    def login(self):
        if sys.platform.startswith("win32"):
            fileName = sys.path[0]+'\\.sessID'
        else:
            fileName = sys.path[0]+'/.sessID'
        try:
            fp = open(fileName,'r')
            content = fp.read()
            sessID, hostIP = string.split(content,'|')
            if hostIP != self.host :
                raise Exception('Lack of session ID, please login first')
            self.setSessionID(sessID)
            fp.close()
            return True
        except:
            login = str(raw_input('User login:'))
            password = str(raw_input('Password:'))
            
            
            self.auth = base64.b64encode('%s:%s' % (login,password))
            if not self.conn :
                raise Exception('Lack of established connection');
            headers = {"Content-type":"application/json","Authorization" : "Basic %s" % (self.auth)}
            params = None
            self.conn.request('POST','/rs/esm/login',params,headers)
            res = self.conn.getresponse();
            if res.status != 201 :
                print res.status, res.reason
                print res.read().strip()
                sys.exit(1)
            #login with success
            xres = res.read().strip()
            myParser = xp()          
            p = xml.parsers.expat.ParserCreate()
            p.StartElementHandler = myParser.start_element
            p.CharacterDataHandler = myParser.char_data
            p.Parse(xres,1)
            self.sessionID = myParser.get('sessionID')
            fp = open(fileName,'w')
            fp.write(self.sessionID+'|'+self.host)
            fp.close()
        #return self.sessionID
        return True
        
    def logout(self):
        if not self.conn :
            raise Exception('Lack of established connection');
        headers = {"Content-type":"application/json","Authorization" : "Session %s" % (self.sessionID)}
        params = None
        self.conn.request('POST','/rs/esm/userLogout',params,headers)
        res = self.conn.getresponse();
        print res.status, res.reason
        print res.read().strip()
    def setSessionID(self,sessID):
       
        self.sessionID = sessID
    def caseGetCase(self,caseID):
        params = '{"id" : {"value" : %s}}' % (caseID)
        try:
            a = self.q('caseGetCaseDetail',params)
        except Exception as er:	
            return (er[1],er[0])
        res = json.loads(a)
        return (0,res['return'])
    def caseGetCaseList(self):
        a = self.q('caseGetCaseList')
        print a
        res = json.loads(a)
        return (0,res['return'])
    def getVersion(self):      
        res = json.loads(self.q('getVersion'))
        return res['return']
    def search(self):
        return self.q('getVersion')
    def qryGetStatus(self,resultID):
        if resultID not in self.result_table:
            self.result_table.append(resultID)
        params = '{"resultID" : {"value" : %s}}' % (resultID)
        res = json.loads(self.q('qryGetStatus',params))
        return res['return']
    def clean(self):
        for key in self.result_table:
            #print 'trying to close:',key
            self.qryClose(key)
        self.result_table.clear()
    def qryGetResults(self,resultID,startPos = 0,numRows = 100):
        params = '{"resultID" : {"value" : %s}}' % (resultID)
        res = json.loads(self.q('qryGetResults?startPos=%d&numRows=%d&reverse=false' % (startPos,numRows),params))
        return res['return']
    def qryClose(self,resultID):
        params = '{"resultID" : {"value" : %s}}' % (resultID)
        self.q('qryClose',params)
    def caseGetCaseDetail(self,caseID):        
        try:
            res = json.loads(self.q('caseGetCaseDetail','{"id": {"value": %d}}' % caseID))
            return res['return']
        except:
            return None
        
    def q(self,command,params = None,headers = None):  
        if not self.conn :
            raise Exception('Lack of established connection');
        if headers is None :
            headers = {"Content-type":"application/json","Authorization" : "Session %s" % (self.sessionID)}
        self.conn.request('POST',('/rs/esm/%s' % (command)),params,headers)
        res = self.conn.getresponse();
        if res.status != 200 :
            raise Exception(res.read(),res.status)
        return res.read().strip()
    def qget(self,command,headers = None):  
        if not self.conn :
            raise Exception('Lack of established connection');
        if headers is None :
            headers = {"Content-type":"application/json","Authorization" : "Session %s" % (self.sessionID)}
        self.conn.request('GET',('/rs/esm/%s' % (command)),None,headers)
        res = self.conn.getresponse();
        if res.status != 200 :
            raise Exception(res.reason,res.status)
        return res.read().strip()
    def get_device_tree_extended(self):
        try :
            response = self.q('grpGetDeviceTreeEx?displayID=0&hideDisabledDevices=true')
        except Exception as er:				
            error_info = 'Error getting list of devices:\n %s'%er
            return (1, error_info)
        #print response
        a = json.loads(response);
        return (0, a['return'])    
    def get_device_tree(self):
        try :
            response = self.q('grpGetDeviceTree?displayID=0&hideDisabledDevices=false')
        except Exception as er:				
            error_info = 'Error getting list of devices:\n %s'%er
            return (1, error_info)
        a = json.loads(response);
        
        return (0, a['return'])    
    def get_device_list(self, type_of_devs=[]):
        '''
        Description: This procedure get the list of devices added to the SIEM architecture

        Input:
                                Optional type = type is a list wich filter the type of devices to get information from.

        Output:
                                List object with the id of the device (the id corresponds with the IPSID), IPSID is an
                                interesting value to filter out information when logs are obtained, type and name of the
                                device
        '''
        if not type_of_devs:
            type_of_devs = ["IPS","POLICY","RECEIVER","THIRD_PARTY","DBM", "DBM_DB", "DBM_AGENT",\
                "VA", "IPSVIPS", "ESM", "APM","APMVIPS","ELM","ELMREC","LOCALESM",\
                "RISK","ASSET","RISKMANAGER","RISKAGENT","EPO","EPO_APP","NSM",\
                "NSM_SENSOR","NSM_INTERFACE","MVM","OTHER","UNKNOWN"]
        payload = '{"types": %s}' % ('["' + ('","'.join(type_of_devs)) +  '"]')
        try:
            response = self.q('devGetDeviceList?filterByRights=false',payload)
        except Exception as er:				
            error_info = 'Error getting list of devices:\n %s'%er
            return (1, error_info)
        a = json.loads(response);
        return (0, a['return'])    
