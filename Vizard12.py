# test of python Vicon server

import struct
import socket 
import sys

import Vicon_server2

#from Vicon_server_python import ViconReader
from Vicon_server2 import ViconReader

V = ViconReader()
print(V)
names = V.connect()

print('names')
print(names)
V.stream()


V.stop()

#print(names)