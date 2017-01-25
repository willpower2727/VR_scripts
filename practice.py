
from numpy import matrix
from numpy import linalg
A = matrix( [[1,2,3],[11,12,13],[21,22,23]])
steplengthR = 0.5
steplengthL = 0.4


steplength_matrix = ([steplengthR, steplengthL])

print A
print steplength_matrix

a=[[1,1],[2,1],[3,1]]
b=[[1,2],[2,2],[3,2]]

print a[2][0]
print a
c =a[2][0] + a[1][0]
print c

global R
R = 0
print steplengthR

multi_array = []
for i in xrange(5):
    list2 = []
    for j in xrange(6):
        list3 = []
        for k in xrange(7):
            list3.append(0)
        list2.append(list3)
    multi_array.append(list2)