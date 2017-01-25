import viz
import vizact
import vizshape
import random
import vizinfo
import viztask
import numpy
import csv


#Enable full screen anti-aliasing (FSAA) to smooth edges
viz.setMultiSample(4)

#Start World
viz.go(viz.FULLSCREEN)

def Create_Shape(Number,x_pace,y_pace,z_pace,set_Time) :
	#create an array of shapes
	shapes = []
#	ranges = ([-10,0],[1,11])
	X = list() #these will be saved to a file
	Y = list()
	Z = list()
	n = 0
	while (n<=Number):
		x = random.uniform(-4,4)
		y = random.uniform(-4,4)
		z = random.uniform(0,500)
		
		if (-3 <= x <= 3) and (-3 <= y <= 3):
			print('in exclusion range')
			print(n)
			pass
		else:
			shape = vizshape.addSphere(0.05,10,10)
			shape.setPosition([x,y,z])
			shape.color(1,1,1)
			shapes.append(shape)
			X.append(x)
			Y.append(y)
			Z.append(z)
			n += 1
			print(n)
	print('X:')
	print(X)
#	file = open('OpticFlow1.txt','w+')
#	csvw = csv.writer(file)
#	csvw.writerow(X)
#	csvw.writerow(Y)
#	csvw.writerow(Z)
#	file.close()
	
	viz.MainView.velocity(x_pace,y_pace,z_pace)
	
	#Generate Shapes
#	for i in range(Number):
#		#Generate random values for position and orientation
##		x = random.randint(-100,100)
##		y = random.randint(-100,100)
##		z = random.randint(-100,100)
#		x = random.uniform(-10,10)
#		y = random.uniform(-10,10)
#		z = random.uniform(0,500)
##		low,high = random.choice(ranges)
##		x = random.uniform(low,high)
#		#generate shapes
#
#		shape = vizshape.addSphere(0.1,10,10)
#		#shape.setScale(0.25,0.25,0.25)
#		shape.setPosition([x,y,z])
#		shape.color(1,1,1)
#	shapes.append(shape)

	#Move shapes
#	move = vizact.move(x_pace,y_pace,z_pace,set_Time)
#	#Loop through all shapes and move them
#	for shape in shapes:
#		shape.addAction(move)
		#return shapes
#		return shapes

#Calls create shape with the number of shapes needed to be made and
#the speed and time for the shapes to move at
Create_Shape(5000,0,0,10,100000)