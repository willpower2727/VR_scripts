import time
import ctypes

#for x in range(1,10,1):
#	foo = time.clock()
#	print id(foo)

a = time.clock()
time.sleep(1)
a2 = time.clock()

print a-a2