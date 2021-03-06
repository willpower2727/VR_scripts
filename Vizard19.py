﻿import socket
import sys
import io
import re
from xml.etree import ElementTree
import viz
import threading
import Queue

viz.go()#start worldviz

def UpdateViz(root,q):#thread to update WorldViz objects
	while 1:
		root = q.get()#pull xml from the queue
		
		# parse xml...
		
		#update Worldviz objects...
	
def runclient(root,q):#client to receive xml from c++ server
	
	#illegal characters to remove from string later before going to xml
	RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
					 u'|' + \
					 u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
					  (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
					   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
					   unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))
	HOST = 'localhost'   
	PORT = 50008
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print 'Socket created'
	print 'Socket now connecting'
	s.connect((HOST,PORT))
	s.send('1')
	while 1:
		data = s.recv(50)#receive the initial message
		data3 = data[:3]#get first 3 letters
		if (data3 == "New"):#this means there is a new frame ready to send
			nextsizestring = data[3:]
			nextsizestring2 = nextsizestring.rstrip('\0')
			nextsize = int(nextsizestring2,10)#this is the size of the next xml string
			print("Next Packet is size: ")
			print(nextsize)
			s.send('b')#tell cpp we are ready for the packet
			databuf = ''#intialize a buffer
			while (sys.getsizeof(databuf) < nextsize + 21):#receive until we have the entire xml string
				data = s.recv(nextsize)
				databuf = databuf + data
			root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree from xml
			q.put(root)#place the xml into the queue
		elif (data3 != "New"):
			print("WARNING! TCP SYNCH HAS FAILED")
			break
		if not data: break
		s.send('b')
	s.close()


root = ''#initialize as empty string
q = Queue.Queue()
#create thread for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q))
#start the threads
t1.start()
t2.start()
