import sys
import os
import time
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
import threading

LOGGER = logging.getLogger('client')
LOGGER.info('Запускаем клиента')
client_name = input('Введите имя пользователя: ')
try:
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    if server_port < 1024 or server_port > 65535:
        raise ValueError
except IndexError:
    server_host = DEFAULT_IP_ADDRESS
    server_port = DEFAULT_PORT
except ValueError:
    print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
    sys.exit(1)

print(f'Подключаемся к {server_host}:{server_port}')
try:
    client = ClientSocket()
    transport = client.create_socket(server_host,server_port)
    print(ClientSocket.create_presence(client_name))
    client.send_message(transport, ClientSocket.create_presence(client_name))
    answer = ClientSocket.process_ans(client.get_message(transport))
    print(answer)
except json.JSONDecodeError:
    print('Не удалось декодировать полученную Json строку.')
    LOGGER.error('Не удалось декодировать полученную Json строку.')
    sys.exit(1)
except (ConnectionRefusedError, ConnectionError):
    print(f'Не удалось подключиться к серверу {server_host}:{server_port}, '
        f'конечный компьютер отверг запрос на подключение.')
    LOGGER.critical(
        f'Не удалось подключиться к серверу {server_host}:{server_port}, '
        f'конечный компьютер отверг запрос на подключение.')
    sys.exit(1)
else:
    # Если соединение с сервером установлено корректно,
    # запускаем клиенский процесс приёма сообщний
    print('Запускаем!')
    receiver = threading.Thread(target=client.message_from_server, args=(transport, client_name))
    receiver.daemon = True
    receiver.start()
    print('Запущен процесс 1')
    # затем запускаем отправку сообщений и взаимодействие с пользователем.
    user_interface = threading.Thread(target=client.user_interactive, args=(transport, client_name))
    user_interface.daemon = True
    user_interface.start()
    print('Запущен процесс 2')
    LOGGER.debug('Запущены процессы')

    # Watchdog основной цикл, если один из потоков завершён,
    # то значит или потеряно соединение или пользователь
    # ввёл exit. Поскольку все события обработываются в потоках,
    # достаточно просто завершить цикл.
    while True:
        time.sleep(1)
        if receiver.is_alive() and user_interface.is_alive():
            continue
        break




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