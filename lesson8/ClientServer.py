from abc import ABC, abstractmethod
import json
import socket
import sys
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
        print(encoded_message)
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


    @log_decorator('client')
    def message_from_server(self,sock, my_username):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = self.get_message(sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    self.log.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                f'\n{message[MESSAGE_TEXT]}')
                else:
                    self.log.error(f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                self.log.critical(f'Потеряно соединение с сервером.')
                break

    @staticmethod
    @log_decorator('client')
    def create_exit_message(account_name):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    @log_decorator('client')
    def create_message(self,sock, account_name='Guest'):
        """
        Функция запрашивает кому отправить сообщение и само сообщение,
        и отправляет полученные данные на сервер
        :param sock:
        :param account_name:
        :return:
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        self.log.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            self.send_message(sock, message_dict)
            self.log.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            self.log.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @log_decorator('client')
    def user_interactive(self,sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                self.send_message(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                self.log.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def print_help(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

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
    def start_server(self,server_host,server_port):
        self.log.info("Сервер стартует")
        address = (server_host, server_port)
        # список клиентов , очередь сообщений
        all_clients = []
        messages = []
        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        names = dict()
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
                    if clients_read:
                        for client_with_message in clients_read:
                            try:
                                print("process_client_message")
                                self.process_client_message(self.get_message(client_with_message),
                                                       messages, client_with_message, all_clients, names)
                            except Exception:
                                self.log.info(f'Клиент {client_with_message.getpeername()} '
                                            f'отключился от сервера.')
                                all_clients.remove(client_with_message)
                    #print(requests)
                    # Если есть сообщения, обрабатываем каждое.
                    for i in messages:
                        try:
                            self.process_message(i, names, clients_write)
                        except Exception:
                            self.log.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                            all_clients.remove(names[i[DESTINATION]])
                            del names[i[DESTINATION]]
                    messages.clear()

    @log_decorator('server')
    def process_client_message(self,message, messages_list, client, clients, names):
        """
        Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
        проверяет корректность, отправляет словарь-ответ в случае необходимости.
        :param message:
        :param messages_list:
        :param client:
        :param clients:
        :param names:
        :return:
        """
        self.log.debug(f'Разбор сообщения от клиента : {message}')
        print(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                self.send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                self.send_message(client, response)
                clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            messages_list.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            self.send_message(client, response)
            return

    @log_decorator('server')
    def process_message(self,message, names, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        :param message:
        :param names:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            self.send_message(names[message[DESTINATION]], message)
            self.log.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                        f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            self.log.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')