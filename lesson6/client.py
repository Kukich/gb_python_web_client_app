import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from ClientServer import ClientSocket
from common.variables import *
import logging
import logs.log_config
import sys
import json
from pprint import pformat
LOGGER = logging.getLogger('client')
LOGGER.info('Запускаем клиента')
try:
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    if server_port < 1024 or server_port > 65535:
        raise ValueError
except IndexError:
    server_host = DEFAULT_IP_ADDRESS
    server_port = DEFAULT_PORT
except ValueError:
    LOGGER.critical('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
    sys.exit(1)

LOGGER.info(f'Подключаемся к {server_host}:{server_port}')
client = ClientSocket()
transport = client.create_socket(server_host,server_port)
LOGGER.info(f'Клиент отправил сообщение ')
msg = ClientSocket.create_presence()
LOGGER.info(pformat(msg))
client.send_message(transport,msg )
try:
    answer = ClientSocket.process_ans(client.get_message(transport))
except (ValueError, json.JSONDecodeError):
    LOGGER.error('Не удалось декодировать сообщение сервера.')
else:
    LOGGER.info("Сервер прислал ответ клиенту")
    LOGGER.info(pformat(answer))