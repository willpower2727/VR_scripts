
#import math
import random
import viz
import itertools
'''
for z in [1,2,3,4,5,6,7,8,9,10]:
	test = random.randint(1,2)
	print(test)
'''
E = [2] * 20
F = [1] * 20

G = E+F
#G = [1,1,1,1,1,2,2,2,2,2]
#G = random.randint(1,2)
print(G)
test = random.shuffle(G)
print(G)
rcount = 0
print(G[rcount])
