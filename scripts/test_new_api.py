# Подключаем наш модуль где описан класс работающий с API
# и импортируем этот класс
from sevpn_zabbix import SevpnZabbix

sevpn_server = SevpnZabbix(password="dtnthdujkjdt",
                        server_address="192.168.7.180",
                        ssl_verify=False)

result = sevpn_server.bridge_discovery()
print(result)
