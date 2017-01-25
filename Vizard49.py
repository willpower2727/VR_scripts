
import random
ranTar=[0, 2, -2, 6, -6, 10, -10] #CJS 12/17/2016
sets=1
global frodo
frodo = list()

print ranTar[0]
print frodo

for x in range(1,sets+1, 1):
	random.shuffle(ranTar)#mix up the order
	frodo = frodo+[ranTar[0]]
	frodo = frodo+[ranTar[1]]
	frodo = frodo+[ranTar[2]]
	frodo = frodo+[ranTar[3]]
	frodo = frodo+[ranTar[4]]
	frodo = frodo+[ranTar[5]]
	frodo = frodo+[ranTar[6]]
	print frodo
	
print frodo
print len(frodo)