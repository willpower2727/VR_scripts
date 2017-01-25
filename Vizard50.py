import time

reftime = time.time()
print("ref time: ",reftime)
time.sleep(2)

print("elapsed time: ",time.time()-reftime)