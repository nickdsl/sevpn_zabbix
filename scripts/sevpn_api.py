'''
SoftEtherVPN API module
'''

import requests
import urllib3
import json
import pdb

class SevpnAPI():
    def __init__(self,
                 password="",
                 server_address="example.com",
                 proto="https",
                 port="443",
                 ssl_verify = True,
                 rest_path="/api"):
        '''
        Initialize SevpnAPI object
        '''
        self.__server_address = server_address
        self.__proto = proto
        self.__port = port
        self.__ssl_verify = ssl_verify
        self.__password = password
        self.__rest_path = rest_path
        pass

    def __execute_request(self,method="post",rest_path="",
                          params={},headers={}):
        '''
        Execute common web request
        '''
        # проверки
        # params - влидный словарь
        # headers - валидный словарь
        result = { "data": {}, "error": {} }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if method == "post":
            # тут возможно нужно try catch на случай если сервер недоступен
            req_result = requests.post(url=self.__proto +
                                  "://" +
                                  self.__server_address +
                                  ":" + self.__port +
                                  rest_path,data=json.dumps(params), headers=headers, verify=self.__ssl_verify)
            # здесь надо проверить код ответа результата
            if req_result.ok:
                # здесь у нас код ответа < 400, скорее всего все хорошо
                result['data'] = req_result.text
            else:
                # а здесь у нас не все хорошо
                result['error'] = req_result.text
        return result

    def __get_entity(self,method="",params={}):
        '''
        Метод запрашивает произвольную сущность через API
        '''
        req_params = { "jsonrpc": "2.0", "id": "rpc_call_id", "method": "" }
        req_params['method'] = method
        req_params['params'] = params
        req_headers = {
            "X-VPNADMIN-HUBNAME": "",
            "X-VPNADMIN-PASSWORD": self.__password }
        
        ent_result = self.__execute_request(params=req_params,
                                                   headers=req_headers,
                                                   rest_path=self.__rest_path)
        return ent_result

    def Test(self,test_value=0): # ok
        '''
        Test RPC function. Input any integer value to the IntValue_u32 field. Then the server will 
        convert the integer to the string, and return the string in the StrValue_str field.
        '''
        method = "Test" # according official API value
        params = { "IntValue_u32": test_value }
        return self.__get_entity(method=method,params=params)
    
    def EnumLocalBridge(self): # ok
        '''
        Get List of Local Bridge Connection. 
        Use this to get a list of the currently defined Local Bridge connections. 
        You can get the Local Bridge connection Virtual Hub name and the bridge destination 
        Ethernet device (network adapter) name or tap device name, as well as the operating status.
        '''
        method = "EnumLocalBridge" # according official API value
        params = {}
        return self.__get_entity(method=method,params=params)
    
    def GetBridgeSupport(self): # ok
        '''
        Get whether the localbridge function is supported on the current system.
        '''
        method = "GetBridgeSupport" # according official API value
        params = {}
        return self.__get_entity(method=method,params=params)
    
    def GetServerInfo(self): # ok
        '''
        Get server information. This allows you to obtain the server information of the currently 
        connected VPN Server or VPN Bridge. Included in the server information are the version number, 
        build number and build information. You can also obtain information on the current server 
        operation mode and the information of operating system that the server is operating on.
        '''
        method = "GetServerInfo" # according official API value
        params = {}
        return self.__get_entity(method=method,params=params)
    
    def GetServerStatus(self): # ok
        '''
        Get Current Server Status. This allows you to obtain in real-time the current status of the 
        currently connected VPN Server or VPN Bridge. You can get statistical information on data 
        communication and the number of different kinds of objects that exist on the server. 
        You can get information on how much memory is being used on the current computer by the OS.
        '''
        method = "GetServerStatus" # according official API value
        params = {}
        return self.__get_entity(method=method,params=params)
    
    def EnumListener(self): # ok
        '''
        Get List of TCP Listeners. This allows you to get a list of TCP listeners registered on the 
        current server. You can obtain information on whether the various TCP listeners have a status 
        of operating or error. To call this API, you must have VPN Server administrator privileges.
        '''
        method = "EnumListener" # according official API value
        params = {}
        return self.__get_entity(method=method,params=params)
    
    def EnumHub(self):  # ok
        '''
        Get List of Virtual Hubs. Use this to get a list of existing Virtual Hubs on the VPN Server. 
        For each Virtual Hub, you can get the following information: Virtual Hub Name, Status, Type, 
        Number of Users, Number of Groups, Number of Sessions, Number of MAC Tables, Number of 
        IP Tables, Number of Logins, Last Login, and Last Communication. Note that when connecting 
        in Virtual Hub Admin Mode, if in the options of a Virtual Hub that you do not have 
        administrator privileges for, the option Don't Enumerate this Virtual Hub for Anonymous Users 
        is enabled then that Virtual Hub will not be enumerated. If you are connected in 
        Server Admin Mode, then the list of all Virtual Hubs will be displayed. When connecting to 
        and managing a non-cluster-controller cluster member of a clustering environment, only the 
        Virtual Hub currently being hosted by that VPN Server will be displayed. When connecting to a 
        cluster controller for administration purposes, all the Virtual Hubs will be displayed.
        '''
        method = "EnumHub" # according official API value
        params = {}
        return self.__get_entity(method=method,params=params)
    
    def GetHubStatus(self,hubname=""): # ok
        '''
        Get Current Status of Virtual Hub. Use this to get the current status of the Virtual Hub 
        currently being managed. You can get the following information: Virtual Hub Type, Number of 
        Sessions, Number of Each Type of Object, Number of Logins, Last Login, Last Communication, 
        and Communication Statistical Data.
        '''
        method = "GetHubStatus" # according official API value
        params = { "HubName_str": hubname }
        return self.__get_entity(method=method,params=params)
    
    def GetHub(self,hubname=""): # ok
        '''
        Get the Virtual Hub configuration. You can call this API to get the current configuration 
        of the specified Virtual Hub. To change the configuration of the Virtual Hub, call the 
        SetHub API.
        '''
        method = "GetHub" # according official API value
        params = { "HubName_str": hubname }
        return self.__get_entity(method=method,params=params)
    
    def EnumLink(self,hubname=""): # ok
        '''
        Get List of Cascade Connections. Use this to get a list of Cascade Connections that are 
        registered on the currently managed Virtual Hub. By using a Cascade Connection, you can 
        connect this Virtual Hub by Layer 2 Cascade Connection to another Virtual Hub that is 
        operating on the same or a different computer. [Warning About Cascade Connections] By 
        connecting using a Cascade Connection you can create a Layer 2 bridge between multiple 
        Virtual Hubs but if the connection is incorrectly configured, a loopback Cascade Connection 
        could inadvertently be created. When using a Cascade Connection function please design the 
        network topology with care. You cannot execute this API for Virtual Hubs of VPN Servers 
        operating as a cluster.
        '''
        method = "EnumLink" # according official API value
        params = { "HubName_str": hubname }
        return self.__get_entity(method=method,params=params)
    
    def GetLinkStatus(self,hubname="",accountname=""): # ok
        '''
        Get Current Cascade Connection Status. When a Cascade Connection registered on the 
        currently managed Virtual Hub is specified and that Cascade Connection is currently online, 
        use this to get its connection status and other information. You cannot execute this API 
        for Virtual Hubs of VPN Servers operating as a cluster.
        '''
        method = "GetLinkStatus" # according official API value
        params = { "HubName_Ex_str": hubname,
                  "AccountName_utf": accountname }
        return self.__get_entity(method=method,params=params)
    
    def EnumUser(self,hubname=""): # ok
        '''
        Get List of Users. Use this to get a list of users that are registered on the security 
        account database of the currently managed Virtual Hub. This API cannot be invoked on VPN 
        Bridge. You cannot execute this API for Virtual Hubs of VPN Servers operating as a member 
        server on a cluster.
        '''
        method = "EnumUser" # according official API value
        params = { "HubName_str": hubname }
        return self.__get_entity(method=method,params=params)
    
    def GetUser(self,hubname="",name=""): # ok
        '''
        Get User Settings. Use this to get user settings information that is registered on the 
        security account database of the currently managed Virtual Hub. The information that 
        you can get using this API are User Name, Full Name, Group Name, Expiration Date, Security 
        Policy, and Auth Type, as well as parameters that are specified as auth type attributes and 
        the statistical data of that user. To get the list of currently registered users, use the 
        EnumUser API. This API cannot be invoked on VPN Bridge. You cannot execute this API for 
        Virtual Hubs of VPN Servers operating as a member server on a cluster.
        '''
        method = "GetUser" # according official API value
        params = {
            "HubName_str": hubname,
            "Name_str": name
        }
        return self.__get_entity(method=method,params=params)
    
    pass