#rev 2 is to test V2P R3, which abandons xml as the serialization method over TCP. Now a simple string is 

import socket
import sys
import io
import re
#import xml.etree.cElementTree as ElementTree
import viz
import threading
import Queue
import time
import json
import vizact
import struct
import vizshape

viz.go(
viz.FULLSCREEN
)
vizshape.addGrid()

def UpdateViz(root,q,savestring,q3):
    timeold = time.time()
    RHS = 0
    LHS = 0

    while not endflag.isSet():
        root = q.get()
        tempdat = root.split(',')

        FrameNum = int(tempdat[0])
        Rfz = float(tempdat[2])
        Lfz = float(tempdat[3])
        RHIPY = float(tempdat[4])
        LHIPY = float(tempdat[5])
        RANKY = float(tempdat[6])
        LANKY = float(tempdat[7])
#		savestring = [int(fnn[0]),Rz,Lz,RHS,LHS]
        savestring = [FrameNum,Rfz,Lfz,RHIPY,LHIPY,RANKY,LANKY]
#		print(sys.getsizeof(savestring))
        q3.put(savestring)
#		print(q3.qsize())
    print("data has all been gotten")

def runclient(root,q):
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
    while not endflag.isSet():
    #    global root
        data = s.recv(8)#receive the initial message
        data3 = data[:3]#get first 3 letters
        if (data3 == "New"):
            #get ready for new packet
            nextsizestring = data[3:]
            nextsizestring2 = nextsizestring.rstrip('\0')
            nextsize = int(nextsizestring2,10)
    #        print(type(nextsize))
#            print("Next Packet is size: ")
#            print(nextsize)
            s.send('b')#tell cpp we are ready for the packet
            databuf = ''
            while (sys.getsizeof(databuf) < nextsize+21):
                data = s.recv(nextsize)#data buffer as a python string
                databuf = databuf + data
    #        databuf2 = re.sub(RE_XML_ILLEGAL, "?", databuf)
    #        print("Size of data recieved is: ")
    #        print(sys.getsizeof(databuf))
#            print(databuf)
            root = databuf
#            print(root)
    #        root = ElementTree.ElementTree(ElementTree.fromstring(databuf))#create the element tree
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
    
def savedata(savestring,q3):
    #initialize the file
    mst = time.time()
    mst2 = int(round(mst))
    mststring = str(mst2)+'StrideTime.txt'
    print("Data file created named:")
    print(mststring)
    file = open(mststring,'w+')
    json.dump(['FrameNumber','Rfz','Lfz','RHIPY','LHIPY','RANKY','LANKY'],file)
    file.close()

    file = open(mststring,'a')#reopen for appending only
    print('file is open for appending')
    while not endflag.isSet():
#		print(q3.empty())
        savestring = q3.get()#look in the queue for data to write
#		print(savestring)
        q3.task_done()
        if savestring is None:
            continue
        else:
            json.dump(savestring, file)
    print("savedata stop flag raised, finishing...")
    while 1:
        try:
            savestring = q3.get(False,2)
        except:
            savestring = 'g'
#		print(savestring)
        if savestring  == 'g':
            break
            print("data finished write to file")
        else:
            json.dump(savestring, file)
            print("data still writing to file")

    print("savedata finished writing")
    file.close()

	
endflag = threading.Event()
#endflag.clear()
def raisestop(sign):
    print("stop flag raised")
    endflag.set()
    t1.join()
    t2.join()
    t4.join()
    viz.quit()

root = ''#empty string
savestring = ''
q = Queue.Queue()#initialize the queue
q3 = Queue.Queue()#intialize another queue for saving data
#create threads for client
t1 = threading.Thread(target=runclient,args=(root,q))
t2 = threading.Thread(target=UpdateViz,args=(root,q,savestring,q3))
t4 = threading.Thread(target=savedata,args=(savestring,q3))

t1.daemon = True
t2.daemon = True
t4.daemon = True
#start the threads
t1.start()
t2.start()
t4.start()

print("\n")
print("press 'q' to stop")
print("\n")

vizact.onkeydown('q',raisestop,'y')
