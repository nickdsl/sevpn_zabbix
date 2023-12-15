# Подключаем наш модуль где описан класс работающий с API
# и импортируем этот класс
from sevpn_zabbix import SevpnZabbix

sevpn_server = SevpnZabbix(password="mjjer36sYheKAtlNHjkQ",
                        server_address="162.55.101.144",port=992,
                        ssl_verify=False)

result = sevpn_server.user_stats()
print(result)
