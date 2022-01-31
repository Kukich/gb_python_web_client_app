import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
import unittest
import socket
from ClientServer import ServerSocket
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import *

server = ServerSocket()
transport = server.create_socket(DEFAULT_IP_ADDRESS,DEFAULT_PORT)
print(type(transport))
if(isinstance(transport,socket.socket)):
    print('ok')
else:
    print('not ok')