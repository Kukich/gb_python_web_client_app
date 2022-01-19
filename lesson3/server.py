'''
  Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
  Сначала обрабатываем порт:
  server.py -p 8079 -a 192.168.1.2
  :return:
'''

import argparse
from ClientServer import ServerSocket
from common.variables import *

parser = argparse.ArgumentParser(description='Запуск сокет сервера')
parser.add_argument('-a', action="store")
parser.add_argument('-p', action="store")
my_namespace = parser.parse_args()
server_host = DEFAULT_IP_ADDRESS
server_port = DEFAULT_PORT
if(my_namespace.a is not None):
    server_host = my_namespace.a
    print(f'Используется  сервер {server_host}')
else:
    print(f'Не введен хост : используется дефолтный хост {DEFAULT_IP_ADDRESS}')
if(my_namespace.p is not None):
    server_port = my_namespace.p
    if(int(server_port)< 1024 or int(server_port) > 65535):
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        exit(1)
    print(f'Используется  порт {server_port}')
else:
    print(f'Не введен порт : используется дефолтный порт {DEFAULT_PORT}')

serv = ServerSocket()
transport = serv.create_socket(server_host,server_port)
serv.start_server(transport)

