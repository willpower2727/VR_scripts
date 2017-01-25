#development script to establish pythonic control of the bertec treadmill
#WDA 1/22/2015

import socket
import sys
import struct

HOST = 'BIOE-PC'
PORT = 4000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
print 'Socket now connecting'
s.connect((HOST,PORT))

def serializepacket(speedR,speedL,accR,accL,theta):
	fmtpack = struct.Struct('>B 18h 27B')
	outpack = fmtpack.pack(0,speedR,speedL,0,0,accR,accL,0,0,theta,~speedR,~speedL,~0,~0,~accR,~accL,~0,~0,~theta,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
	return(outpack)

#while 1:
out = serializepacket(500,1000,1000,1000,0)
print out
s.send(out)
s.close()

