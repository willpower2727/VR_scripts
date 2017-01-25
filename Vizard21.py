#test of json capabilities for writing data to file during VR routines.

import json
import viz
import sys
import io
import os.path
import time


data = ['hello',4,5,'test']
print data

mst = time.time()
mst2 = int(round(mst))
mststring = str(mst2)+'data.txt'
print(mststring)
file = open(mststring,'w+')
file.close()

file = open(mststring,'a')
for n in range(0,10):
	json.dump(data, file)

file.close()