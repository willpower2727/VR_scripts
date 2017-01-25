#import viz
#
#viz.setMultiSample(4)
#viz.fov(60)
#viz.go()
#
#gallery = viz.addChild('dojo.osgb')
'''
#Add some 3D text in the world
text_3D = viz.addText3D('Art Gallery',pos=[-2.5,1.5,5])
#Add 2D text in the world
text_2D_world = viz.addText('Bench',pos=[2, 0.6, 3.5],parent=viz.WORLD)
#Add 2D text to the screen
text_2D_screen = viz.addText('On the screen',parent=viz.SCREEN)
#Parent 3D text to an object
plant = viz.addChild('plant.osgb',pos=[-4,0,7.9])
text_object = viz.addText3D( 'plant',parent=plant,pos=[0.4,0.2,0])
'''

import random

global STEPNUM
STEPNUM =10 #must be even number!
#setup array of randomly picked steps
global randy
randy  = [1] * STEPNUM + [2] * STEPNUM # create list of 1's and 2's 
random.shuffle(randy)
print(randy)
print(randy.count(randy[0]) == len(randy))
for z in range(0,len(randy),3):
	temp = randy[z:z+3]
	print(temp)
	

