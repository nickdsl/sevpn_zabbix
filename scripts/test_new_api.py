# Подключаем наш модуль где описан класс работающий с API
# и импортируем этот класс
from sevpn_api import SevpnAPI
import pdb

sevpn_server = SevpnAPI(password="dtnthdujkjdt",
                        server_address="192.168.7.180",
                        ssl_verify=False)

test_result = sevpn_server.EnumHub()
print(test_result['data'])
print(test_result['error'])