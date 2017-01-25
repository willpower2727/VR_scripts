import socket
import sys
#import struct
#import binascii
import io
import re
import viz
import threading
from xml.etree import ElementTree
import Queue


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
s.send('1')#as long as we are not sending "0" cpp server will return information. Otherwise the connection is closed

#declare global xml object "root"
global root


while 1:
    global root

    data = s.recv(50)#receive the initial message
    #print(data)#see what is in there
    #print("the length of the initial packet is: ")
    #print(len(data))
    data3 = data[:3]#get first 3 letters
    #print("data3 is: ")
    #print(data3)
    if (data3 == "New"):
        #get ready for new packet
        nextsizestring = data[3:]
#        print("incoming frame size is: ")
#        print(nextsizestring)
        nextsizestring2 = nextsizestring.rstrip('\0')
        nextsize = int(nextsizestring2,10)
#        print(type(nextsize))
        print("Next Packet is size: ")
        print(nextsize)
        s.send('b')#tell cpp we are ready for the packet
        databuf = ''
        while (sys.getsizeof(databuf) < nextsize):
            data = s.recv(nextsize)#data buffer as a python string
            databuf = databuf + data
#        databuf2 = re.sub(RE_XML_ILLEGAL, "?", databuf)
#        print("Size of data recieved is: ")
#        print(sys.getsizeof(databuf))
#        print(databuf)
        global root
        root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
        q.put(root)
        #find an element and print its' attribute
#        path = root.find("Time")
#        path = root.find("FrameNumber")
#        fn = path.attribute
#        print(path.attrib)
        
        #raise event so the vizard world can update
#        viz.sendEvent(Event0)

    elif (data3 != "New"):
        print("WARNING! TCP SYNCH HAS FAILED")
        break
    if not data: break#if not data then stop listening for more
#    print(data)
    s.send('b')#keep sending anything but zero to get more stuff
s.close()