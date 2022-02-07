from abc import ABC, abstractmethod
import json
import socket
from common.variables import *
import time
import logging
from pprint import pformat
from logs.log_config import log_decorator
import select

class ClientServer(ABC):
    """
    Абстрактный класс для создания Клиента или Сервера
    """

    def get_message(self,client):
        '''
        Утилита приёма и декодирования сообщения
        принимает байты выдаёт словарь, если приняточто-то другое отдаёт ошибку значения
        :param client:
        :return:
        '''

        encoded_response = client.recv(MAX_PACKAGE_LENGTH)
        if isinstance(encoded_response, bytes):
            json_response = encoded_response.decode(ENCODING)
            response = json.loads(json_response)
            if isinstance(response, dict):
                return response
            raise ValueError
        raise ValueError

    def send_message(self,sock, message):
        '''
        Утилита кодирования и отправки сообщения
        принимает словарь и отправляет его
        :param sock:
        :param message:
        :return:
        '''
        js_message = json.dumps(message)
        encoded_message = js_message.encode(ENCODING)
        sock.send(encoded_message)

    @abstractmethod
    def create_socket(self):
       '''
         Абстрактный метод для создания socket-а
       '''
       pass


class ClientSocket(ClientServer):
    def __init__(self):
        self.log=logging.getLogger('client')

    @log_decorator('client')
    def create_socket(self,server_address,server_port):
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        return transport

    @staticmethod
    @log_decorator('client')
    def process_ans(message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError

    @staticmethod
    @log_decorator('client')
    def create_presence(account_name='Guest'):
        '''
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        '''
        # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        return out

class ServerSocket(ClientServer):
    def __init__(self):
        self.log=logging.getLogger('server')

    @log_decorator('server')
    def create_socket(self,server_host,server_port):
        # Готовим сокет
        self.log.info('Сервер создает сокет')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((server_host, server_port))
        # Слушаем порт
        transport.listen(MAX_CONNECTIONS)
        self.log.info('Сокет создан')
        return transport

    @log_decorator('server')
    def process_client_message(self,message):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        self.log.info('Сервер обрабатывает сообщение клиента')
        self.log.info(pformat(message))
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    @log_decorator('server')
    def start_server(self,server_host,server_port):
        self.log.info("Сервер стартует")
        address = (server_host, server_port)
        all_clients = []
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(address)
            sock.listen(5)
            sock.settimeout(0.2)
            while True:
                try:
                    conn, addr = sock.accept()
                except OSError as err:
                    pass
                else:
                    print(f"Получен запрос на соединение от {str(addr)}")
                    all_clients.append(conn)
                finally:
                    wait = 0
                    clients_read = []
                    clients_write = []
                    try:
                        clients_read, clients_write, errors = \
                            select.select(all_clients, all_clients, [], wait)
                    except Exception:
                        pass

                    requests = self.read_requests(clients_read, all_clients)
                    #print(requests)
                    if requests:
                        # print(requests)
                        self.write_responses(requests, clients_write, all_clients)


    @log_decorator('server')
    def read_requests(self,read_clients, all_clients):
        """Чтение запросов из списка клиентов"""

        responses = {}

        for sock in read_clients:
            try:
                data = sock.recv(1024).decode('utf-8')
                responses[sock] = data
            except Exception:
                print(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
                all_clients.remove(sock)
            else:
                if data == '':
                    print(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
                    sock.close()
                    all_clients.remove(sock)
                elif(data):
                    print(f"Получено сообщение от {sock.fileno()} {sock.getpeername()} со значением {data}")

        return responses

    @log_decorator('server')
    def write_responses(self,requests, clients_write, all_clients):
        """Эхо-ответ сервера клиентам, от которых были запросы"""

        for sock in clients_write:
            for s in requests:
                try:
                    resp = requests[s]
                    # print(resp)
                    sock.send(resp.encode('utf-8'))
                except Exception:
                    # sock.fileno() - вернуть дескриптор файла сокетов (небольшое целое число)
                    # sock.getpeername() - получить IP-адрес и номер порта клиента
                    print(f"Клиент {sock.fileno()} {sock.getpeername()} отключился")
                    sock.close()
                    all_clients.remove(sock)
                else:
                    print(f"Отправлено сообщение  {sock.fileno()} {sock.getpeername()} со значением {resp}")