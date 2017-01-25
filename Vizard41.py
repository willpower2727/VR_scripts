import threading
import vizact
import viz

#practice stopping looping threads with thread events

global stopevent1
global stopevent2
stopevent1 = threading.Event()
stopevent2 = threading.Event()

viz.go(
#viz.FULLSCREEN 
)

def thread1(arg1):
	stopper = arg1["two"]
	print(stopper)
	while (not arg1["two"].is_set()):
		print('thread1 runs')
	print('thread1 terminated')
	
def thread2(arg2,stopevent2):
	while (not stopevent2.is_set()):
		print('thread2 runs')
	print('thread2 terminated')
	
def raisestop(biggle):
	global stopevent1
	global stopevent2
	
	stopevent1.set()
	stopevent2.set()
	viz.quit()
	
args1 = {}
args1["one"] = 1
args1["two"] = stopevent1
t1 = threading.Thread(target=thread1,args=(args1,))
t2 = threading.Thread(target=thread2,args=(2,stopevent2))

#t1.setDaemon = True
#t2.setDaemon = True

t1.start()
t2.start()

#t1.join()
#t2.join()

vizact.onkeydown('q',raisestop,'biggle')