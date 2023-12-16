"""
This is doc string
"""
# sys
import sys
# config parser
import configparser
# working with json
import json
# Подключаем наш модуль где описан класс работающий с API
# и импортируем этот класс
from sevpn_zabbix import SevpnZabbix

# config file
CURRENT_CONFIG_NAME = "sevpn.ini"
# get current script path and split by /
CURRENT_CONFIG = sys.argv[0].split('/')
# we got list. delete last item (script file name)
CURRENT_CONFIG.pop()
# add config file name
CURRENT_CONFIG.append(CURRENT_CONFIG_NAME)
# generate string: config file path
CURRENT_CONFIG = "/".join(CURRENT_CONFIG)
# init settings variable
SEVPN_SETTINGS = configparser.ConfigParser()
# try to read config file
try:
    SEVPN_SETTINGS.read(CURRENT_CONFIG)
except IOError:
    print('Cannot read: ' + CURRENT_CONFIG)
    exit()

# server url
SERVER_PROTO = SEVPN_SETTINGS["SERVER"]['PROTO']
SERVER_HOST = SEVPN_SETTINGS["SERVER"]['HOST']
SERVER_PORT = SEVPN_SETTINGS["SERVER"]['PORT']
ADMIN_PASS = SEVPN_SETTINGS["SERVER"]["ADMIN_PASS"]
# valid commands
VALID_COMMANDS = SEVPN_SETTINGS["SERVER"]["COMMANDS"].split(',')

# max ping count (1 try = 1 second, zabbix has 30 sec max timeout. Default: 3
# i choose 15 as maximum
PING_COUNT_MAX = int(SEVPN_SETTINGS["PING"]["MAX"])
# minimum ping tries
PING_COUNT_MIN = int(SEVPN_SETTINGS["PING"]["MAX"])
# default - average value
PING_COUNT_DEFAULT = int((PING_COUNT_MAX + PING_COUNT_MIN)/2)

# boolean flag
EXIT_NOW = False

# if we have 1 argument
if len(sys.argv) == 1:
    # script executed without any params
    # activate exit_now flag
    EXIT_NOW = True
    print("Script parameter not set")
# if we got wrong parameter
elif sys.argv[1] not in VALID_COMMANDS:
    print("Wrong script parameter: {}".format(sys.argv[1]))
    EXIT_NOW = True
# if we got exit_now = True
if EXIT_NOW:
    # print default message
    print("Usage: python3 {} ".format(sys.argv[0]) + "|".join(VALID_COMMANDS))
    # exit with errors
    exit(1)

# we need to create a callable expression
# we have our set of methods in VALID_COMMANDS list
# our commands has dots in their names, but our functions has underlines
# we need to replace all '.' to '_' and then add any parameters and call it (evaluate)
# 1. step. split our method name to list of spring. (split character: '.')
METHOD = sys.argv[1].split('.')
# 2. step. we need to generate our function name. concatenate our string list with '_' symbol
METHOD = "_".join(METHOD)

sevpn_server = SevpnZabbix(ping_count=PING_COUNT_DEFAULT,
                           ping_count_max=PING_COUNT_MAX,
                           ping_count_min=PING_COUNT_MIN,
                           password=ADMIN_PASS,
                        server_address=SERVER_HOST,
                        port=int(SERVER_PORT),
                        proto=SERVER_PROTO,
                        ssl_verify=False)

# перебираем методы ветвлением (не придумал как лучше)
if METHOD == "server_info":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.server_info())
    pass
elif METHOD == "server_status":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.server_status())
    pass
elif METHOD == "listener_discovery":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.listener_discovery())
    pass
elif METHOD == "listener_stats":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.listener_stats())
    pass
elif METHOD == "hub_discovery":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.hub_discovery())
    pass
elif METHOD == "hub_stats":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.hub_stats())
    pass
elif METHOD == "bridge_support":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.bridge_support())
    pass
elif METHOD == "bridge_stats":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.bridge_stats())
    pass
elif METHOD == "bridge_discovery":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.bridge_discovery())
    pass
elif METHOD == "cascade_discovery":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.cascade_discovery())
    pass
elif METHOD == "cascade_stats":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.cascade_stats())
    pass
elif METHOD == "user_discovery":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.user_discovery())
    pass
elif METHOD == "user_stats":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.user_stats())
    pass
elif METHOD == "get_ping":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.get_ping())
    pass
elif METHOD == "internal_ping_discovery":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.internal_ping_discovery())
    pass
elif METHOD == "external_ping_discovery":
    # подготовка к вызову метода
    # вызов метода
    result = json.dumps(sevpn_server.external_ping_discovery())
    pass

print(result)

# exit
exit(0)