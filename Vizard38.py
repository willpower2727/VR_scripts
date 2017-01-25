#test of iterating dict keys in for loop

data = {}
data["HMD1"] = [0,2,3]
data["HMD2"] = [5,6,4]
data["not"] = 1237659398
data["HMD3"] = [1,1,1]

def dummyfun(vargin):
	print(vargin)
	return vargin
	


for f in range(1,4,1):
	out = dummyfun(data["HMD{}".format(f)])