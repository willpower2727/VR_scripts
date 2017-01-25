'''
from random import choice
def added1(lst, bank):
    if len(bank) == 0:
        return lst
    selection = choice(bank)
    lst.append(selection)
    bank.remove(selection)
    if selection == 1:
        return added11(lst, bank)
    return added2(lst, bank)

def added11(lst,bank):
    if len(bank) == 0:
        return lst
    bank.remove(2)
    lst.append(2)
    return added2(lst, bank)

def added2(lst, bank):
    if len(bank) == 0:
        return lst
    selection = choice(bank)
    lst.append(selection)
    bank.remove(selection)
    if selection == 2:
        return added22(lst, bank)
    return added1(lst, bank)

def added22(lst,bank):
    if len(bank) == 0:
        return lst
    bank.remove(1)
    lst.append(1)
    return added1(lst, bank)

def start(lst, bank):
    bank_bkp = bank[:]
    while True:
        try:
            if len(bank) == 0:
                return lst
            selection = choice(bank)
            lst.append(selection)
            bank.remove(selection)
            if selection == 1:
                return added1(lst, bank)
            return added2(lst, bank)
        except:
            # retry
            bank = bank_bkp[:]
            lst = []


print start([], [1] * 10 + [2] * 10)
'''




'''
sequences = []
for n in range(2**20):
    b = bin(n)[2:].zfill(20)
    if b.count('1') == 10:
        sequences.append(b)
print(sequences)
'''

import random
from itertools import groupby

sequences = []
order = [1, 0] * 10

while len(sequences) < 10:
    random.shuffle(order)

    if order in sequences:
        continue

    if all(len(list(group)) < 4 for _, group in groupby(order)):
        sequences.append(order[:])
print(sequences)



################################################
'''
import random
randy = []

ones = [1] * 10
twos = [2] * 10

for i in range(14):
    if len(randy) > 3 and randy[i-1] == randy[i-2] == randy[i-3]:
        randy.append(ones.pop() if randy[i-1] == 1 else twos.pop())
    else:
        randy.append(random.choice([ones, twos]).pop())
print(randy)
'''
'''
import random
from operator import itemgetter

#randy = [ [item,amount], ... ]
randy  = [[1,10],[2,10]]

#This turns the above list into the same format of your 'randy'
itemList = [j for k in[([i[0]]*i[1])for i in randy]for j in k]  

randomList = [-1]  #This stops the check from causing problems at the start
for i in range(len(itemList)):
    while True:
        newChoice = random.choice( itemList )
        if len(set(randomList[-3:]+[newChoice]))-1: #Checks the last 2 values plus the new value aren't all the same
            randomList.append( newChoice )
            break
shuffledList = randomList[1:]
print shuffledList
'''

