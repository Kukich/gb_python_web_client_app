"""Unit-тесты клиента"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest
import socket
from ClientServer import ClientSocket
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import *


class TestClass(unittest.TestCase):
    '''
    Класс с тестами
    '''
    def setUp(self):
        """Выполнить настройку тестов (если необходимо)"""
        self.ClientSocket = ClientSocket()


    def test_def_presense(self):
        """Тест коректного запроса"""
        test = ClientSocket.create_presence()
        test[TIME] = 1.1  # время необходимо приравнять принудительно
                          # иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(ClientSocket.process_ans({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        """Тест корректного разбора 400"""
        self.assertEqual(ClientSocket.process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, ClientSocket.process_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()

#