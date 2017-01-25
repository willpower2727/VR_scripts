import viz
import vizshape
import time
import vizinfo
import vizact

viz.go(

#viz.FULLSCREEN #run world in full screen
)


#ball = viz.addChild('vcc_female.cfg',color=(0.063,0.102,0.898),scale=[0.1,0.1,0.1])
#face = viz.add('morph_head.vzf',color=viz.YELLOW)
viz.MainView.setPosition(0, 0, -1.25)
#viz.MainView.setEuler(180,0,0)
#
#morph = vizact.morphTo(1,0.1,time=2)
#
#face.setMorph(1,3)
#face.addAction(morph)

#fire = viz.add('smoke_trail.osg',scale=[1,1,1])
fire = viz.add('dust2.osg',scale=[1,1,1])
#fire.setPosition(0.1,0.2,0)
fire.hasparticles()
#fire.enable(viz.EMITTERS)

#morph = vizact.morphTo(1,0.1,time=2)
#fire.addAction(morph)
#fire.setMorph(1,3)