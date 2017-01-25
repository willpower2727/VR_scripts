import viz

viz.go()

room = viz.addChild('HMRL8.osgb')
room.setPosition(0,0,0)
room.setEuler(90,270,0)
room.setScale(0.01,0.01,0.01)
#room.disable(viz.LIGHTING)

mylight = viz.addLight() 
mylight.enable() 
mylight.position(0, 3, 0) 
mylight.spread(180) 
mylight.intensity(50) 

mylight2 = viz.addLight() 
mylight2.enable() 
mylight2.position(0, 3, 2) 
mylight2.spread(180) 
mylight2.intensity(50) 

mylight3 = viz.addLight() 
mylight3.enable() 
mylight3.position(0, 3, 1) 
mylight3.spread(180) 
mylight3.intensity(50) 

#man = viz.addChild('robot.osgb')
#man.color(1,0,0)
#man.setPosition(0,0,0)
#man.disable(viz.LIGHTING)

#armBone = man.getBone('Bip001 L Forearm') 