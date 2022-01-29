from abc import ABC, abstractmethod
import json
import socket
from common.variables import *
import time


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

    def create_socket(self,server_address,server_port):
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        return transport

    @staticmethod
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
    def create_socket(self,server_host,server_port):
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((server_host, server_port))
        # Слушаем порт
        transport.listen(MAX_CONNECTIONS)
        return transport

    def process_client_message(self,message):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def start_server(self,transport):
        while True:
            client, client_address = transport.accept()
            try:
                message_from_cient = self.get_message(client)
                print(message_from_cient)
                # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
                response = self.process_client_message(message_from_cient)
                self.send_message(client, response)
                client.close()
            except (ValueError, json.JSONDecodeError):
                print('Принято некорретное сообщение от клиента.')
                client.close()