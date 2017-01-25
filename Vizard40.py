import viz
import vizact

viz.setMultiSample(4)
viz.fov(60)
viz.go()

#demo of exchanging head and animating avatars
female = viz.addAvatar('vcc_female.cfg')
female.setPosition([-0.5,0.6,2.3])
female.setEuler([180,0,0])
female.state(6)
#female.face('biohead_talk.vzf')
female.face('HILLARY.vzf')

male = viz.addAvatar('vcc_male.cfg')
male.setPosition([0.5,0.6,2.3])
male.setEuler([180,0,0])
male.state(4)
male.face('BILL.vzf')

speech = vizact.speak('jfk.wav') 

#morphing_face = female.face('HILLARY.vzf')
#morphing_face2 = male.face('BILL.vzf')

vizact.onkeydown(' ', female.addAction, speech)
vizact.onkeydown('c', male.addAction, speech)
