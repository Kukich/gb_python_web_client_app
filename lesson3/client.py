from ClientServer import ClientSocket
from common.variables import *
import sys
import json

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
client = ClientSocket()
transport = client.create_socket(server_host,server_port)
client.send_message(transport, ClientSocket.create_presence())
try:
    answer = ClientSocket.process_ans(client.get_message(transport))
    print(answer)
except (ValueError, json.JSONDecodeError):
    print('Не удалось декодировать сообщение сервера.')