from sevpn_api import SevpnAPI
import copy
import json

class SevpnZabbix(SevpnAPI):
    '''
    SevpnZabbix - класс наследующий работу с API sevpn,
    но при этом обрабатывающий данные в формате, которые
    понятны Zabbix
    '''
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
        
        for cur_bridge in api_bridges['data']['LocalBridgeList']:
            bridge_converted = self.__convert_bool(cur_bridge)
            json_item = {}
            json_item["{#HUBNAME}"] = bridge_converted["HubNameLB_str"]
            json_item["{#IFNAME}"] = bridge_converted["DeviceName_str"]
            json_item["{#ACTIVE}"] = bridge_converted["Active_bool"]
            json_item["{#ONLINE}"] = bridge_converted["Online_bool"]
            json_item["{#TAPMODE}"] = bridge_converted["TapMode_bool"]
            zabbix_json["data"].append(json_item)
        return json.dumps(copy.deepcopy(zabbix_json))

    pass