import sys
import os
import argparse
sys.path.append(os.path.join(os.getcwd(), '..'))
from ClientServer import ClientSocket
from common.variables import *
import logging
import logs.log_config
import sys
import json
import socket
from pprint import pformat
LOGGER = logging.getLogger('client')
LOGGER.info('Запускаем клиента')
parser = argparse.ArgumentParser(description='Запуск клиента сокет сервера')
parser.add_argument('-t', action="store")
my_namespace = parser.parse_args()
client_type = ""
if(my_namespace.t == 'send'):
    client_type = my_namespace.t
    print(f'Используется клиент для записи')
    LOGGER.info(f'Используется клиент для записи')
elif(my_namespace.t == 'receive'):
    client_type = my_namespace.t
    print(f'Используется клиент для чтения')
    LOGGER.info(f'Используется клиент для чтения')

#try:
#    server_host = sys.argv[1]
#    server_port = int(sys.argv[2])
#    if server_port < 1024 or server_port > 65535:
#        raise ValueError
#except IndexError:
#    server_host = DEFAULT_IP_ADDRESS
#    server_port = DEFAULT_PORT
#except ValueError:
#    LOGGER.critical('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
#    sys.exit(1)

#LOGGER.info(f'Подключаемся к {server_host}:{server_port}')

ADDRESS = (DEFAULT_IP_ADDRESS, DEFAULT_PORT)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(ADDRESS)
    while True:
        if(client_type == 'send'):
            msg = input('Ваше сообщение: ')
            if msg == 'exit':
                sock.close()
                break
            sock.send(msg.encode('utf-8'))
        if(client_type == 'receive'):
            data = sock.recv(1024).decode('utf-8')
            if(data == ''):
                sock.close()
                break
            elif(data):
                print(f"Пришло сообщение: {data}")





#client = ClientSocket()
#transport = client.create_socket(server_host,server_port)
#LOGGER.info(f'Клиент отправил сообщение ')
#msg = ClientSocket.create_presence()
#LOGGER.info(pformat(msg))
#client.send_message(transport,msg )
#try:
#    answer = ClientSocket.process_ans(client.get_message(transport))
#except (ValueError, json.JSONDecodeError):
#    LOGGER.error('Не удалось декодировать сообщение сервера.')
#else:
#    LOGGER.info("Сервер прислал ответ клиенту")
#    LOGGER.info(pformat(answer))