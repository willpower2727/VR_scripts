import numpy as np
import random

f = open('C:\Users\Gelsey Torres-Oviedo\Downloads\SLPdist.csv','r')

lines = f.readlines()
dist = np.zeros((len(lines),1))
dist = [0]*len(lines)
f.close()
f = open('C:\Users\Gelsey Torres-Oviedo\Downloads\SLPdist.csv','r')
for z in range(0,len(lines)):
	temp = f.readline()
	temp = temp.replace('\n','')
#	print(temp)

	dist[z] = float(temp)
#line1 = line1.replace('\n','')
#line2 = line1.split(',')
print('line1 ',dist)
print('pick: ',random.choice(dist))