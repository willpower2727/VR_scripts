import viz
import vizshape
import time
import vizinfo
import random
import itertools
import socket
import sys
import io
import re
#import xml.etree.cElementTree as ElementTree
import threading
import Queue
import time
import json
import vizact
import struct
import array
import math
import vizlens
import oculus


	
HOST2 = 'BIOE-PC'
PORT2 = 4000
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Treadmill Socket created'
print 'Treadmill Socket now connecting'
s2.connect((HOST2,PORT2))
	
def serializepacket(speedR,speedL,accR,accL,theta):
	fmtpack = struct.Struct('>B 18h 27B')#should be 64 bits in length to work properly
	outpack = fmtpack.pack(0,speedR,speedL,0,0,accR,accL,0,0,theta,~speedR,~speedL,~0,~0,~accR,~accL,~0,~0,~theta,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
	return(outpack)
		
out = serializepacket(0,0,500,500,0)
s2.send(out)
s2.close()