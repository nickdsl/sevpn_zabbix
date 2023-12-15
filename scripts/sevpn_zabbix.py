from sevpn_api import SevpnAPI
import copy
import json
import subprocess
import pdb

class SevpnZabbix(SevpnAPI):
    '''
    SevpnZabbix - класс наследующий работу с API sevpn,
    но при этом обрабатывающий данные в формате, которые
    понятны Zabbix
    '''
    def __init__(self,ping_count:int = 0,
                 ping_count_min:int = 0,
                 ping_count_max:int = 0,
                 password:str="",
                 server_address:str="example.com",
                 proto:str="https",
                 port:int=443,
                 ssl_verify:bool = True,
                 rest_path:str="/api"):
        # вызываем конструктор базового класса
        super().__init__(password,
                 server_address,
                 proto,
                 port,
                 ssl_verify,
                 rest_path)
        # а это уже атрибут текущего класса
        self.__ping_count = ping_count
        self.__ping_count_min = ping_count_min
        self.__ping_count_max = ping_count_max
        pass

    def __convert_bool(self, input:dict):
        """
        Get input dict. Replace Bool True/False to Int 1/0
        :param input : dict:
        :return:
        """
        output_dict = input
        # select all keys and values
        for key, value in input.items():
            # if value type is boolean
            if isinstance(value, type(True)):
                # convert to integer
                output_dict[key] = int(value)
        # return result dict
        return output_dict


    def bridge_discovery(self):
        api_bridges = self.EnumLocalBridge()
        zabbix_json = { "data": [] }
        if api_bridges['error']:
            return zabbix_json
        
        for cur_bridge in api_bridges['data']['result']['LocalBridgeList']:
            bridge_converted = self.__convert_bool(cur_bridge)
            json_item = {}
            json_item["{#HUBNAME}"] = bridge_converted["HubNameLB_str"]
            json_item["{#IFNAME}"] = bridge_converted["DeviceName_str"]
            json_item["{#ACTIVE}"] = bridge_converted["Active_bool"]
            json_item["{#ONLINE}"] = bridge_converted["Online_bool"]
            json_item["{#TAPMODE}"] = bridge_converted["TapMode_bool"]
            zabbix_json["data"].append(json_item)
        return json.dumps(copy.deepcopy(zabbix_json))

    def bridge_support(self):
        result = self.GetBridgeSupport()
        result['data']['result'] = self.__convert_bool(result['data']['result'])
        return result
    
    def server_info(self):
        result = self.GetServerInfo()
        result['data']['result'] = self.__convert_bool(result['data']['result'])
        return result
    
    def server_status(self):
        result = self.GetServerStatus()
        result['data']['result'] = self.__convert_bool(result['data']['result'])
        return result
    
    def listener_discovery(self):
        result = self.EnumListener()
        zabbix_json = {"data": []}
        for cur_listener in result['data']['result']['ListenerList']:
            listener_converted = self.__convert_bool(cur_listener)
            json_item = {}
            json_item["{#PORT}"] = listener_converted["Ports_u32"]
            json_item["{#ENABLED}"] = listener_converted["Enables_bool"]
            zabbix_json["data"].append(json_item)
        return json.dumps(copy.deepcopy(zabbix_json))
    
    def bridge_stats(self):
        result = self.EnumLocalBridge()
        result_json = {}
        for cur_item in result['data']['result']['LocalBridgeList']:
            item_converted = self.__convert_bool(cur_item)
            json_item = {}
            json_item["Online_bool"] = item_converted["Online_bool"]
            json_item["Active_bool"] = item_converted["Active_bool"]
            cur_hub_name = item_converted["HubNameLB_str"]
            cur_dev_name = item_converted["DeviceName_str"]
            cur_tap_mode = item_converted["TapMode_bool"]
            if cur_hub_name not in result_json.keys():
                result_json[cur_hub_name] = {cur_dev_name: {str(cur_tap_mode): copy.deepcopy(json_item)}}
            elif cur_dev_name not in result_json[cur_hub_name].keys():
                result_json[cur_hub_name][cur_dev_name] = {str(cur_tap_mode): copy.deepcopy(json_item)}
            else:
                result_json[cur_hub_name][cur_dev_name][str(cur_tap_mode)] = copy.deepcopy(json_item)
        return json.dumps(result_json)
    
    def listener_stats(self):
        result = self.EnumListener()
        result_json = {}
        for cur_listener in result['data']['result']['ListenerList']:
            listener_converted = self.__convert_bool(cur_listener)
            json_item = {}
            json_item["Errors_bool"] = listener_converted["Errors_bool"]
            json_item["Enables_bool"] = listener_converted["Enables_bool"]
            result_json[str(cur_listener["Ports_u32"])] = json_item
        return json.dumps(copy.deepcopy(result_json))

    def hub_discovery(self):
        result = self.EnumHub()
        zabbix_json = { "data": [] }
        if result['error']:
            return zabbix_json
        for cur_item in result['data']['result']['HubList']:
            item_converted = self.__convert_bool(cur_item)
            json_item = {}
            json_item["{#HUBNAME}"] = item_converted["HubName_str"]
            json_item["{#ONLINE}"] = item_converted["Online_bool"]
            json_item["{#TYPE}"] = item_converted["HubType_u32"]
            json_item["{#TRAFFICFILLED}"] = item_converted["IsTrafficFilled_bool"]
            zabbix_json["data"].append(copy.deepcopy(json_item))
        return json.dumps(zabbix_json)
    
    # зачем дергать статус одного хаба, когда можно дергать статусы сразу всех???
    def get_hub_status(self, hubname:str = ""):
        result = self.GetHubStatus(hubname=hubname)
        return json.dumps(copy.deepcopy(result))
    
    def get_hub(self,hubname:str = ""):
        result = self.GetHub(hubname=hubname)
        return json.dumps(copy.deepcopy(result))
    
    def hub_stats(self):
        result_json = {}
        # get hub list
        fn_hubs_dict = self.EnumHub()
        fn_hub_list = fn_hubs_dict['data']['result']['HubList']
        for cur_item in fn_hub_list:
            cur_hub = self.GetHubStatus(cur_item["HubName_str"])
            item_converted = self.__convert_bool(cur_hub['data']["result"])
            hub_name = item_converted["HubName_str"]
            json_item = {}
            for key, value in item_converted.items():
                json_item[key] = value
            # additional query for special metrics
            # we need to get our dictionary by calling GetHub method = get_hub function
            fn_hub_dict = self.EnumHub()

            # convert any bool values to int
            cur_hub_converted = self.__convert_bool(fn_hub_dict['data']['result'])
            # iterate key, value
            for key, value in cur_hub_converted.items():
                # set new key - value pairs
                json_item[key] = value
            # for sequrity
            json_item["AdminPasswordPlainText_str"] = "It's my secret :)"
            # add our hub stats to main json
            result_json[hub_name] = copy.deepcopy(json_item)
        return json.dumps(result_json)
    
    def cascade_list(self, hubname:str = ""):
        result = self.EnumLink(hubname=hubname)
        json.dumps(copy.deepcopy(result))

    def get_cascade_status(self,hub_name:str = "", cascade_name:str = ""):
        result = self.GetLinkStatus(hubname=hub_name,accountname=cascade_name)
        return json.dumps(copy.deepcopy(result))
    
    def cascade_discovery(self):
        zabbix_json = { "data": [] }
        fn_hubs_dict = self.EnumHub()
        if fn_hubs_dict['error']:
            return zabbix_json
        fn_hub_list = fn_hubs_dict['data']['result']['HubList']
        for cur_hub_item in fn_hub_list:
            cur_hub_name = cur_hub_item["HubName_str"]
            cur_hub_cascades = self.EnumLink(hubname=cur_hub_name)
            
            for cur_item in cur_hub_cascades['data']["result"]["LinkList"]:
                json_item = {}
                item_converted = self.__convert_bool(cur_item)
                cascade_name = item_converted["AccountName_utf"]
                json_item["{#HUBNAME}"] = cur_hub_name
                json_item["{#CASCADENAME}"] = cascade_name
                json_item["{#ONLINE}"] = item_converted["Online_bool"]
                json_item["{#CONNECTED}"] = item_converted["Connected_bool"]
                json_item["{#HOSTNAME}"] = item_converted["Hostname_str"]
                json_item["{#TARGETHUB}"] = item_converted["TargetHubName_str"]
                zabbix_json["data"].append(copy.deepcopy(json_item))
        return json.dumps(zabbix_json)
    
    def internal_ping_discovery(self):
        """this is docstring"""
        my_links = json.loads(self.cascade_discovery())
        new_links = []
        for cur_link in my_links["data"]:
            cur_item = {}
            if cur_link["{#ONLINE}"]:
                cascade_name = cur_link["{#CASCADENAME}"].split(":")
                if len(cascade_name) > 1:
                    cur_item["{#ACCOUNT_NAME}"] = cascade_name[0]
                    cur_item["{#TARGET_HOST}"] = cascade_name[1]
                    cur_item["{#TARGETHUB}"] = cur_link["{#TARGETHUB}"]
                    cur_item["{#HUBNAME}"] = cur_link["{#HUBNAME}"]
                    cur_item["{#HOSTNAME}"] = cur_link["{#HOSTNAME}"]
                    new_links.append(copy.deepcopy(cur_item))
        my_links["data"] = new_links
        return json.dumps(copy.deepcopy(my_links))
    
    def external_ping_discovery(self):
        """this is docstring"""
        my_links = json.loads(self.cascade_discovery())
        new_links = []
        for cur_link in my_links["data"]:
            cur_item = {}
            if cur_link["{#ONLINE}"]:
                cur_item["{#TARGETHUB}"] = cur_link["{#TARGETHUB}"]
                cur_item["{#HUBNAME}"] = cur_link["{#HUBNAME}"]
                cur_item["{#HOSTNAME}"] = cur_link["{#HOSTNAME}"]
                new_links.append(copy.deepcopy(cur_item))
        my_links["data"] = new_links
        return json.dumps(copy.deepcopy(my_links))
    
    def cascade_stats_detailed(self):
        """
        This is doc string
        :return:
        """
        result_json = {}
        # get hub list
        fn_hubs_dict = self.EnumHub()
        fn_hub_list = fn_hubs_dict['data']['result']['HubList']
        for cur_hub_item in fn_hub_list:
            cur_hub_name = cur_hub_item["HubName_str"]
            cur_hub_cascades = self.EnumLink(cur_hub_name)
            json_item = {}
            # если при получении списка каскадов не возникло ошибки
            if not cur_hub_cascades['error']:
                # перебираем все каскады
                for cur_item in cur_hub_cascades['data']["result"]["LinkList"]:
                    # вычленияем имя каскада
                    cascade_name = cur_item["AccountName_utf"]
                    # получение статы каскада
                    cur_item_stat = json.loads(self.get_cascade_status(hub_name=cur_hub_name,
                                                                    cascade_name=cascade_name))
                    # проверяем  была ли ошибка про запросе статы по каскаду
                    if ((len(cur_item_stat['error']) == 0) and ('error' not in cur_item_stat['data'].keys())):
                        # конвертируем айтем
                        item_converted = self.__convert_bool(cur_item_stat['data']["result"])
                        for key, value in item_converted.items():
                            json_item[key] = value
                        if cur_hub_name not in result_json.keys():
                            result_json[cur_hub_name] = {cascade_name: copy.deepcopy(json_item)}
                        else:
                            result_json[cur_hub_name][cascade_name] = copy.deepcopy(json_item)
                
        return json.dumps(result_json)
    
    def cascade_stats(self):
        """
        This is doc string
        :return:
        """
        result_json = {}
        # get hub list
        fn_hubs_dict = self.EnumHub()
        fn_hub_list = fn_hubs_dict['data']['result']['HubList']
        for cur_hub_item in fn_hub_list:
            cur_hub_name = cur_hub_item["HubName_str"]
            cur_hub_cascades = self.EnumLink(hubname=cur_hub_name)
            for cur_item in cur_hub_cascades['data']["result"]["LinkList"]:
                json_item = {}
                cascade_name = cur_item["AccountName_utf"]
                item_converted = self.__convert_bool(cur_item)
                for key, value in item_converted.items():
                    json_item[key] = value
                if cur_hub_name not in result_json.keys():
                    result_json[cur_hub_name] = {cascade_name: copy.deepcopy(json_item)}
                else:
                    result_json[cur_hub_name][cascade_name] = copy.deepcopy(json_item)
        return json.dumps(result_json)
    
    def cascade_stat(self, p_hub_name:str = "", p_cascade_name:str = ""):
        """
        This is doc string
        :return:
        """
        result_json = {}
        # get hub list
        fn_hubs_dict = self.EnumHub()
        fn_hub_list = fn_hubs_dict['data']['result']['HubList']
        for cur_hub_item in fn_hub_list:
            cur_hub_name = cur_hub_item["HubName_str"]
            cur_hub_cascades = self.EnumLink(hubname=cur_hub_name)
            json_item = {}
            for cur_item in cur_hub_cascades['data']["result"]["LinkList"]:
                cascade_name = cur_item["AccountName_utf"]
                if (cur_hub_name == p_hub_name) and (cascade_name == p_cascade_name):
                    for key, value in cur_item.items():
                        json_item[key] = value
                    result_json = copy.deepcopy(json_item)
        return json.dumps(result_json)
    
    def user_discovery(self):
        """
        This is doc string
        :return:
        """
        zabbix_json = {"data": []}
        # get hub list
        fn_hubs = self.EnumHub()
        for cur_hub in fn_hubs['data']["result"]["HubList"]:
            cur_hub_name = cur_hub["HubName_str"]
            fn_users = self.EnumUser(hubname=cur_hub_name)
            for cur_item in fn_users['data']['result']['UserList']:
                item_converted = self.__convert_bool(cur_item)
                json_item = {}
                json_item["{#HUBNAME}"] = cur_hub_name
                json_item["{#USERNAME}"] = item_converted["Name_str"]
                json_item["{#GROUPNAME}"] = item_converted["GroupName_str"]
                json_item["{#REALNAME}"] = item_converted["Realname_utf"]
                json_item["{#NOTE}"] = item_converted["Note_utf"]
                json_item["{#AUTHTYPE}"] = item_converted["AuthType_u32"]
                json_item["{#DENYACCESS}"] = item_converted["DenyAccess_bool"]
                json_item["{#ISTRAFFICFILLED}"] = item_converted["IsTrafficFilled_bool"]
                json_item["{#ISEXPIRESFILLED}"] = item_converted["IsExpiresFilled_bool"]
                json_item["{#EXPIRESDATE}"] = item_converted["Expires_dt"]
                zabbix_json["data"].append(copy.deepcopy(json_item))
        return json.dumps(zabbix_json)
    
    def user_stats_detailed(self):
        """
        This is doc string
        :return:
        """
        result_json = {}
        # get hub list
        fn_hubs_dict = self.EnumHub()
        fn_hub_list = fn_hubs_dict['data']['result']['HubList']
        #print("fn_hub_list: {}".format(fn_hub_list))
        for cur_hub_item in fn_hub_list:
            cur_hub_name = cur_hub_item["HubName_str"]
            #print("Hub name: {}".format(cur_hub_name))
            cur_hub_users = self.EnumUser(hubname=cur_hub_name)
            json_item = {}
            for cur_item in cur_hub_users['data']["result"]["UserList"]:
                user_name = cur_item["Name_str"]
                #print("\tUser name: {}".format(user_name))
                cur_item_stat = self.GetUser(hubname=cur_hub_name,name=user_name)
                #print("\tCur item stat: {}".format(cur_item_stat))
                if not len(cur_item_stat['error']):
                    item_converted = self.__convert_bool(cur_item_stat['data']["result"])
                    for key, value in item_converted.items():
                        json_item[key] = value
                    if cur_hub_name not in result_json.keys():
                        result_json[cur_hub_name] = {user_name: copy.deepcopy(json_item)}
                    else:
                        result_json[cur_hub_name][user_name] = copy.deepcopy(json_item)
        return json.dumps(result_json)
    
    def user_stats(self):
        """
        This is doc string
        :return:
        """
        result_json = {}
        # get hub list
        fn_hubs_dict = self.EnumHub()
        fn_hub_list = fn_hubs_dict['data']['result']['HubList']
        for cur_hub_item in fn_hub_list:
            cur_hub_name = cur_hub_item["HubName_str"]
            cur_hub_users = self.EnumUser(hubname=cur_hub_name)
            json_item = {}
            for cur_item in cur_hub_users['data']["result"]["UserList"]:
                user_name = cur_item["Name_str"]
                item_converted = self.__convert_bool(cur_item)
                for key, value in item_converted.items():
                    json_item[key] = value
                if cur_hub_name not in result_json.keys():
                    result_json[cur_hub_name] = {user_name: copy.deepcopy(json_item)}
                else:
                    result_json[cur_hub_name][user_name] = copy.deepcopy(json_item)
        return json.dumps(result_json)
    
    def __ping_list(self, ip_list:list = [], ping_count:int = 0):
        """this is docstring"""
        try:
            # try to set int value from param
            ping_count = int(ping_count)
        except ValueError:
            # if we got not number value
            # we will set default value
            ping_count = self.__ping_count
        # if ping count > max or < min value
        if ping_count not in range(self.__ping_count_min, self.__ping_count_max+1):
            # we will set default value
            ping_count = self.__ping_count
        # result pings dict
        pings_dict = {}
        # generate fping command string (parallel ping to all camera ip's)
        ping_command = "fping -C {} -q ".format(ping_count) + " ".join(ip_list)
        # execute fping and read data (from stderr stream!)
        result = subprocess.run(ping_command.split(' '),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        # get data from stderr stream (decode from utf8 and split into list by '\n'
        result_output = result.stderr.decode('utf-8').split('\n')
        # remove last item (empty string)
        result_output.pop()
        # process lines from list
        for result_line in result_output:
            # exclude lines with 'duplicate for entry'
            if 'duplicate for' in result_line:
                continue
            # split line by space to list of values
            result_line_list = result_line.split(' ')
            # get filter empty values (strings)
            result_line_list = list(filter(lambda x: x != '', result_line_list))
            # get cam ip
            result_line_ip = result_line_list.pop(0)
            # get list of pings
            result_line_data = result_line_list[1:]
            # filter dashes. dash = packet loss
            result_line_pings = list(map(float,
                                        list(filter(lambda x: x != '-',
                                                    result_line_data))))
            if result_line_pings:
                # calculate packet loss %
                result_line_loss = ((len(result_line_data) - len(result_line_pings))
                                    / len(result_line_pings)) / 100
                # calculate ping average value
                result_line_avg = float("{0:.2f}".format(sum(result_line_pings) /
                                                        len(result_line_pings)))
                # add ip <-> ping stats item into dictionary
            else:
                result_line_loss = '100'
                result_line_avg = 0
                result_line_pings = [0]
            pings_dict[result_line_ip] = {"min": min(result_line_pings),
                                          "max": max(result_line_pings),
                                        "avg": result_line_avg,
                                        "loss": int(result_line_loss)
                                        }
        return json.dumps(pings_dict)
    
    # get ping statistics
    def get_ping(self, ping_count:int = 0):
        """this is docstring"""
        if ping_count == 0:
            ping_count = self.__ping_count
        # init ip list
        zbx_ips = []
        # result pings
        result_pings = {"external": {},
                        "internal": {}}
        # get hub list
        fn_hubs_dict = self.EnumHub()
        for cur_hub_item in fn_hubs_dict['data']['result']['HubList']:
            cur_hub_name = cur_hub_item["HubName_str"]
            cur_hub_cascades = self.EnumLink(hubname=cur_hub_name)
            for cur_item in cur_hub_cascades['data']["result"]["LinkList"]:
                # if cascade is up
                if cur_item["Connected_bool"] and cur_item["Online_bool"]:
                    if cur_item["Hostname_str"] not in zbx_ips:
                        zbx_ips.append(cur_item["Hostname_str"])
                        result_pings["external"][cur_item["Hostname_str"]] = {}
                    acc_name_splitted = cur_item["AccountName_utf"].split(':')
                    if len(acc_name_splitted) > 1:
                        if acc_name_splitted[1] not in zbx_ips:
                            result_pings["internal"][acc_name_splitted[1]] = {}
                            zbx_ips.append(acc_name_splitted[1])
        my_pings = json.loads(self.__ping_list(ip_list=zbx_ips, ping_count=ping_count))
        for cur_ip, cur_val in my_pings.items():
            if cur_ip not in result_pings["external"].keys():
                result_pings["internal"][cur_ip] = cur_val
            else:
                result_pings["external"][cur_ip] = cur_val
        # return result json
        return json.dumps(result_pings)
    pass