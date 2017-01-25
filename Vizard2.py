import viz
import vizshape
import time
import mmserver
import vizinfo

print "Time in seconds since the epoch: %s" %time.time()

viz.go(
)




grid = vizshape.addGrid()
panel1 = vizinfo.InfoPanel("""This is a test of the info panel""",align=viz.ALIGN_CENTER,fontSize=50,icon=False,key=None)

#time.sleep(3)

#viz.visible(0)