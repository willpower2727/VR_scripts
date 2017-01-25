#test of profiling

import cProfile
import re
import time
import viz
import pstats
from threading import Thread

def foo():
	for z in range(0,5):
		time.sleep(1)
		print("hello world")
		
def goo():
	for z in range(0,6):
		time.sleep(1)
		print("goodbye world")
		
def enable_thread_profiling():
	'''Monkey-patch Thread.run to enable global profiling.
	Each thread creates a local profiler; statistics are pooled
	to the global stats object on run completion.'''
	Thread.stats = None
	thread_run = Thread.run

	def profile_run(self):
		self._prof = cProfile.Profile()
		self._prof.enable()
		thread_run(self)
		self._prof.disable()

		if Thread.stats is None:
			Thread.stats = pstats.Stats(self._prof)
		else:
			Thread.stats.add(self._prof)

	Thread.run = profile_run

def get_thread_stats():
	stats = getattr(Thread, 'stats', None)
	if stats is None:
		raise ValueError, 'Thread profiling was not enabled,''or no threads finished running.'
	return stats

enable_thread_profiling()
#cProfile.run("C:\Program Files (x86)\WorldViz\Vizard4\bin\winviz.exe")
t1 = Thread(target=foo)
t2 = Thread(target=goo)
t1.start()
t2.start()
t1.join()
t2.join()
#cProfile.run('foo()')

get_thread_stats().print_stats()

