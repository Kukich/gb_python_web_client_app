"""Unit-тесты клиента"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest
import socket
from ClientServer import ServerSocket
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import *

class TestClass(unittest.TestCase):
    '''
    Класс с тестами
    '''

    def setUp(self):
        """Выполнить настройку тестов (если необходимо)"""
        self.ServerSocket = ServerSocket()
        self.err_dict = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
        self.ok_dict = {RESPONSE: 200}

    def test_create_socket(self):
        transport = self.ServerSocket.create_socket(DEFAULT_IP_ADDRESS,DEFAULT_PORT)
        self.assertIsInstance(transport,socket.socket,'Wrong type of object in return of create_socket')

    def test_no_action(self):
        """Ошибка если нет действия"""
        self.assertEqual(self.ServerSocket.process_client_message(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_wrong_action(self):
        """Ошибка если неизвестное действие"""
        self.assertEqual(self.ServerSocket.process_client_message(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_time(self):
        """Ошибка, если  запрос не содержит штампа времени"""
        self.assertEqual(self.ServerSocket.process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_user(self):
        """Ошибка - нет пользователя"""
        self.assertEqual(self.ServerSocket.process_client_message(
            {ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)

    def test_unknown_user(self):
        """Ошибка - не Guest"""
        self.assertEqual(self.ServerSocket.process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}}), self.err_dict)

    def test_ok_check(self):
        """Корректный запрос"""
        self.assertEqual(self.ServerSocket.process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)


if __name__ == '__main__':
    unittest.main()

#