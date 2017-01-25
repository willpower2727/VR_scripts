import socket
import sys

HOST = 'localhost'   
PORT = 50008

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

#Bind socket to local host and port
#try:
#    s.bind((HOST, PORT))
#except socket.error as msg:
#    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
#    sys.exit()

#print 'Socket bind complete'

#Start listening on socket

#s.listen(10)
print 'Socket now connecting'
s.connect((HOST,PORT))
s.send('hello')
while 1:
    data = s.recv(1024)
    if not data: break
    print(data)
    s.send('hello')
conn.close()
#now keep talking with the client
#while 1:
#    
#    conn, addr = s.accept()
#    print 'Connected with ' + addr[0] + ':' + str(addr[1])
#    data = conn.recv(10000)
#    print(data)
s.close()