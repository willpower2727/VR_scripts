import viz
import vizact
import vizmat
import socket
import sys
import threading 
from xml.dom import minidom
import math
import time #This line added by WDA 3/18/2014
import vizshape #This line added by WDA 3/18/2014
import vizinfo #This line added by WDA 3/21/2014
#global data #this line added by WDA 12/19/2013
global starttime
starttime = 0

# Generate IDs for the custom events that are triggered by this module.
CONNECTED_EVENT = viz.getEventID('CONNECTED_EVENT')
DISCONNECTED_EVENT = viz.getEventID('DISCONNECTED_EVENT')
CALIBRATION_FILE_GENERATED_EVENT = viz.getEventID('CALIBRATION_FILE_GENERATED_EVENT')
SCALAR_VALUE_RECEIVED_EVENT = viz.getEventID('SCALAR_VALUE_RECEIVED_EVENT')
VECTOR_VALUE_RECEIVED_EVENT = viz.getEventID('VECTOR_VALUE_RECEIVED_EVENT')
QUAT_VALUE_RECEIVED_EVENT = viz.getEventID('QUAT_VALUE_RECEIVED_EVENT')

# This is the maximum number of objects that we'll allow to be put into the scene.
MAX_OBJECTS = 4000;

# This is the name of the calibration file we will generate.
CALIBRATION_FILE_NAME = 'calibration.acd'

# Create a global variable to hold the IP port.
ipPort = int(0)

# Create a list for holding the objects.
objs = []

# Create dictionaries for holding the output variable states.
scalars = {}
vectors = {}
quats = {}

def sendScalarValue(scalarName, scalarValue):

	# Declare globals.
	global scalars
	
	# Update the dictionary with the new value.
	scalars[scalarName] = scalarValue

def sendVectorValue(vectorName, vectorValue):

	# Declare globals.
	global vectors

	# Update the dictionary with the new value.
	vectors[vectorName] = vectorValue

def sendQuatValue(quatName, quatValue):

	# Declare globals.
	global quats
	
	# Update the dictionary with the new value.
	quats[quatName] = quatValue

def sendFrame(conn):
	
	# Declare globals.
	global scalars
	global vectors
	global quats
	
	# Assemble the output frame.
	msg = '<frame>\n'
	for name, scalar in scalars.items():
		msg += '<var name=\"'
		msg += name
		msg += '\" val=\"'
		msg += str(scalar)
		msg += '\">\n</var>\n'
	for name, vector in vectors.items():
		msg += '<var name=\"'
		msg += name
		msg += '\" x=\"'
		msg += str(vector.getX())
		msg += '\" y=\"'
		msg += str(vector.getY())
		msg += '\" z=\"'
		msg += str(vector.getZ())
		msg += '\">\n</var>\n'
	for name, quat in quats.items():
		msg += '<var name=\"'
		msg += name
		msg += '\" qw=\"'
		msg += str(quat.getW())
		msg += '\" qx=\"'
		msg += str(quat.getX())
		msg += '\" qy=\"'
		msg += str(quat.getY())
		msg += '\" qz=\"'
		msg += str(quat.getZ())
		msg += '\">\n</var>\n'
	msg += '</frame>'
	
	# Send the output frame.
	msglen = len(msg)
	totalsent = 0
	while totalsent < msglen:
		sent = conn.send(msg[totalsent:])
		if sent == 0:
			raise RuntimeError("socket connection broken")
		totalsent = totalsent + sent
		
# Create a function dedicated to handling TCP/IP communications.  This will run in a separate thread, since it contains blocking calls.
def serverProc():

	# Declare globals.
	global ipPort
	global objs
	global starttime#added by WDA 4/7/2014
	# Initialize the variables that will be used to receive calibration information.
	height = 1.0
	heightReceived = False	
	head = vizmat.Transform() # back-of-head position and gagnon orientation, both relative to original head sensor
	headposReceived = False
	headoriReceived = False
	lhand = vizmat.Transform() # left wrist position and gagnon orientation, both relative to original left hand sensor
	lhandposReceived = False
	lhandoriReceived = False
	rhand = vizmat.Transform() # right wrist position and gagnon orientation, both relative to original right hand sensor
	rhandposReceived = False
	rhandoriReceived = False
	lfoot = vizmat.Transform() # left ankle position and gagnon orientation, both relative to original left foot sensor
	lfootposReceived = False
	lfootoriReceived = False
	rfoot = vizmat.Transform() # right ankle position and gagnon orientation, both relative to original right foot sensor
	rfootposReceived = False
	rfootoriReceived = False
	waist = vizmat.Transform() # L5S1 position and gagnon orientation, both relative to original sacrum sensor
	waistposReceived = False
	waistoriReceived = False	
	fileCreated = False

	# Create a socket.
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Associate the socket with a port.
	host = '' # this can be left blank on the server side
	sock.bind((host, ipPort))

	# Wait for the client to initiate a connection.
	sock.listen(1)# "1" indicates a backlog of 1 attempt is kept
	conn, addr = sock.accept() # conn is a new socket, addr is the client's address

	# Indicate that a connection was made.
	viz.sendEvent(CONNECTED_EVENT)

	# Create a buffer to store the received data packets.
	inbuf = ''
	
	#*****************************************************************************************************
	#code added by WDA 3/18/2014 to time the length of data stream from TMM and stop displaying or executing biofeedback commands 
	#if the time is close to the end of the data stream
	#global maxtime
	#global starttime
	#global grid
	#grid = vizshape.addGrid()
	#starttime = 0
	#maxtime = 9 #this can be updated depending on what is specified in TMM
	global waitpanel
	waitpanel = vizinfo.InfoPanel("""Trial restarting, please stand by...""",align=viz.ALIGN_CENTER,fontSize=50,icon=False,key=None)
	#waitpanel.visible(0)
	#panel1 = vizinfo.InfoPanel(INSTRUCTIONS,align=viz.ALIGN_CENTER,fontSize=22,icon=False,key=None)
	#*****************************************************************************************************
	
	# Continuously read packets from the client, until they disconnect.
	while(1):

		# Wait for the next packet of data (up to 4096 bytes).  By default, this call will block until new data is available.
		try:
			data = conn.recv(4096)
		except:
			print 'client disconnected'
			break
			
			
		#print(data)
		global starttime
		#**************************************************************************
		
		if (data == '<begstr rate="50.000000">\n</begstr>'):
			starttime = time.time()
			#print('Starting time is...\n')
			#print(starttime)
			
			
		if ((time.time()-starttime) > 298):#wait 300 seconds to restart
			#grid.visible(1)
			#print('visible time is...\n')
			#print(time.time())	
			waitpanel.visible(1)
			viz.visible(0)
			#mmserver.sendScalarValue('RightBeltSpeed',0)#make sure that treadmill is stopped, WARNING if treadmill remote control is enabled this will stop the treadmill! And it will not start again automatically
			#mmserver.sendScalarValue('LeftBeltSpeed',0)
		else:
			#grid.visible(0)
			waitpanel.visible(0)
			viz.visible(1)

			
		#**************************************************************************
		#################################################################################################
		#These lines added by WDA 12/19/2013
		#they blank the screen when TMM is changing from one trial to the next
		#print(data)
		#print('*************')
		
		#if (data == '<addobj i="0" model="sphere.x" sx="0.000000" sy="0.000000" sz="0.000000" red="1.000000" green="1.000000" blue="1.000000" x="0.000000" y="0.000000" z="0.000000" qw="1.000000" qx="0.000000" qy="0.000000" qz="0.000000" o="0.000000">\n</addobj>'):
		'''
		if (data == '<remobj>\n</remobj><remobj>\n</remobj><addobj i="0" model="sphere.x" sx="0.000000" sy="0.000000" sz="0.000000" red="1.000000" green="1.000000" blue="1.000000" x="0.000000" y="0.000000" z="0.000000" qw="1.000000" qx="0.000000" qy="0.000000" qz="0.000000" o="0.000000">\n</addobj>') | (data == '<begstr rate="50.000000">\n</begstr>') | (data == '<endstr>\n</endstr><remobj>\n</remobj>') | (data == '<remobj>\n</remobj><addobj i="0" model="sphere.x" sx="0.000000" sy="0.000000" sz="0.000000" red="1.000000" green="1.000000" blue="1.000000" x="0.000000" y="0.000000" z="0.000000" qw="1.000000" qx="0.000000" qy="0.000000" qz="0.000000" o="0.000000">\n</addobj>'):
			viz.visible(0)
			print(time.time())
		else:
			viz.visible(1)
			'''
		#################################################################################################

		# If this is the end of data (meaning the client disconnected), break from loop.
		if not data:
			print 'client disconnected'
			break

		# Add the new data to the buffer.
		inbuf += data

		# Process the records in the buffer until there are no more left.
		while (1):

			# 
			addobj_index = inbuf.find('</addobj>')
			remobj_index = inbuf.find('</remobj>')
			updobj_index = inbuf.find('</updobj>')
			updvar_index = inbuf.find('</updvar>')
			begstr_index = inbuf.find('</begstr>')
			endstr_index = inbuf.find('</endstr>')

			# Break from the loop if there are no more records.
			if (addobj_index == -1) and (remobj_index == -1) and (updobj_index == -1) and (updvar_index == -1) and (begstr_index == -1) and (endstr_index == -1):
				break;

			# Calculate the length of the first record in the buffer.
			if (addobj_index == -1):
				addobj_recordlength = 1000000
			else:
				addobj_recordlength = addobj_index + len('</addobj>')
			if (remobj_index == -1):
				remobj_recordlength = 1000000
			else:
				remobj_recordlength = remobj_index + len('</remobj>')
			if (updobj_index == -1):
				updobj_recordlength = 1000000
			else:
				updobj_recordlength = updobj_index + len('</updobj>')
			if (updvar_index == -1):
				updvar_recordlength = 1000000
			else:
				updvar_recordlength = updvar_index + len('</updvar>')
			if (begstr_index == -1):
				begstr_recordlength = 1000000
			else:
				begstr_recordlength = begstr_index + len('</begstr>')
			if (endstr_index == -1):
				endstr_recordlength = 1000000
			else:
				endstr_recordlength = endstr_index + len('</endstr>')
			recordlength = min(addobj_recordlength, remobj_recordlength, updobj_recordlength, updvar_recordlength, begstr_recordlength, endstr_recordlength)

			# Extract the record from the buffer.
			record = inbuf[0 : recordlength]

			# Delete the record from the buffer.
			inbuf = inbuf[recordlength : len(inbuf)]

			# 
			if (recordlength == addobj_recordlength):

				# 
				invalid = False

				# 
				indexstart = record.find(' i=\"')
				if (indexstart != -1):
					indexstart += len(' i=\"')
					indexend = record.find('\"', indexstart)
					index = int(record[indexstart : indexend])
					if (index < 0) or (index >= MAX_OBJECTS):
						continue
				else:
					continue

				# 
				while (len(objs) < index):
					objs.append([])

				# 
				modelstart = record.find(' model=\"')
				if (modelstart != -1):
					modelstart += len(' model=\"')
					modelend = record.find('\"', modelstart)
					model = record[modelstart : modelend]
				else:
					continue

				# 
				sxstart = record.find(' sx=\"')
				if (sxstart != -1):
					sxstart += len(' sx=\"')
					sxend = record.find('\"', sxstart)
					sx = float(record[sxstart : sxend])
				else:
					sx = 1.0

				# 
				systart = record.find(' sy=\"')
				if (systart != -1):
					systart += len(' sy=\"')
					syend = record.find('\"', systart)
					sy = float(record[systart : syend])
				else:
					sy = 1.0

				# 
				szstart = record.find(' sz=\"')
				if (szstart != -1):
					szstart += len(' sz=\"')
					szend = record.find('\"', szstart)
					sz = float(record[szstart : szend])
				else:
					sz = 1.0

				# 
				redstart = record.find(' red=\"')
				if (redstart != -1):
					redstart += len(' red=\"')
					redend = record.find('\"', redstart)
					red = float(record[redstart : redend])
				else:
					red = 0.0

				# 
				greenstart = record.find(' green=\"')
				if (greenstart != -1):
					greenstart += len(' green=\"')
					greenend = record.find('\"', greenstart)
					green = float(record[greenstart : greenend])
				else:
					green = 0.0

				# 
				bluestart = record.find(' blue=\"')
				if (bluestart != -1):
					bluestart += len(' blue=\"')
					blueend = record.find('\"', bluestart)
					blue = float(record[bluestart : blueend])
				else:
					blue = 0.0

				# 
				imagestart = record.find(' image=\"')
				if (imagestart != -1):
					imagestart += len(' image=\"')
					imageend = record.find('\"', imagestart)
					image = record[imagestart : imageend]
				else:
					image = ''

				# 
				if (image != ''):

					# 
					obj = viz.add(model, scale=[sx,sy,sz], cache=viz.CACHE_NONE)
					map = viz.add(image)
					obj.texture(map)

				# 
				else:

					# 
					obj = viz.add(model, color=[red,green,blue], scale=[sx,sy,sz], cache=viz.CACHE_NONE)

				# Place the object away from view.
				obj.setPosition([0, 1000, -1000])

				# The object's collision envelope will be the bounding sphere of the ball.
				obj.collideSphere(density=1000) # give the object a very high density, so that nothing else pushes it around

				# Manually negate the force of gravity.
				radius = obj.getBoundingSphere().radius
				obj.applyForce([0, (4.0 / 3.0) * math.pi * radius * radius * radius * 1000 * 9.8 * 0.189, 0], 1000000)

				# 
				obj.visible(viz.OFF)

				# Add the object to the list.
				if (index == len(objs)):
					objs.append([obj])
				else:
					objs[index] = [obj]

				# 
				xstart = record.find(' x=\"')
				if (xstart != -1):
					xstart += len(' x=\"')
					xend = record.find('\"', xstart)
					if (record[xstart : xend] == 'NaN'):
						invalid = True
					x = float(record[xstart : xend])
				else:
					x = None

				# 
				ystart = record.find(' y=\"')
				if (ystart != -1):
					ystart += len(' y=\"')
					yend = record.find('\"', ystart)
					if (record[ystart : yend] == 'NaN'):
						invalid = True
					y = float(record[ystart : yend])
				else:
					y = None

				# 
				zstart = record.find(' z=\"')
				if (zstart != -1):
					zstart += len(' z=\"')
					zend = record.find('\"', zstart)
					if (record[zstart : zend] == 'NaN'):
						invalid = True
					z = float(record[zstart : zend])
				else:
					z = None

				# 
				qwstart = record.find(' qw=\"')
				if (qwstart != -1):
					qwstart += len(' qw=\"')
					qwend = record.find('\"', qwstart)
					if (record[qwstart : qwend] == 'NaN'):
						invalid = True
					qw = float(record[qwstart : qwend])
				else:
					qw = None

				# 
				qxstart = record.find(' qx=\"')
				if (qxstart != -1):
					qxstart += len(' qx=\"')
					qxend = record.find('\"', qxstart)
					if (record[qxstart : qxend] == 'NaN'):
						invalid = True
					qx = float(record[qxstart : qxend])
				else:
					qx = None

				# 
				qystart = record.find(' qy=\"')
				if (qystart != -1):
					qystart += len(' qy=\"')
					qyend = record.find('\"', qystart)
					if (record[qystart : qyend] == 'NaN'):
						invalid = True
					qy = float(record[qystart : qyend])
				else:
					qy = None

				# 
				qzstart = record.find(' qz=\"')
				if (qzstart != -1):
					qzstart += len(' qz=\"')
					qzend = record.find('\"', qzstart)
					if (record[qzstart : qzend] == 'NaN'):
						invalid = True
					qz = float(record[qzstart : qzend])
				else:
					qz = None

				# 
				vxstart = record.find(' vx=\"')
				if (vxstart != -1):
					vxstart += len(' vx=\"')
					vxend = record.find('\"', vxstart)
					if (record[vxstart : vxend] == 'NaN'):
						invalid = True
					vx = float(record[vxstart : vxend])
				else:
					vx = None

				# 
				vystart = record.find(' vy=\"')
				if (vystart != -1):
					vystart += len(' vy=\"')
					vyend = record.find('\"', vystart)
					if (record[vystart : vyend] == 'NaN'):
						invalid = True
					vy = float(record[vystart : vyend])
				else:
					vy = None

				# 
				vzstart = record.find(' vz=\"')
				if (vzstart != -1):
					vzstart += len(' vz=\"')
					vzend = record.find('\"', vzstart)
					if (record[vzstart : vzend] == 'NaN'):
						invalid = True
					vz = float(record[vzstart : vzend])
				else:
					vz = None

				# 
				avxstart = record.find(' avx=\"')
				if (avxstart != -1):
					avxstart += len(' avx=\"')
					avxend = record.find('\"', avxstart)
					if (record[avxstart : avxend] == 'NaN'):
						invalid = True
					avx = float(record[avxstart : avxend])
				else:
					avx = None

				# 
				avystart = record.find(' avy=\"')
				if (avystart != -1):
					avystart += len(' avy=\"')
					avyend = record.find('\"', avystart)
					if (record[avystart : avyend] == 'NaN'):
						invalid = True
					avy = float(record[avystart : avyend])
				else:
					avy = None

				# 
				avzstart = record.find(' avz=\"')
				if (avzstart != -1):
					avzstart += len(' avz=\"')
					avzend = record.find('\"', avzstart)
					if (record[avzstart : avzend] == 'NaN'):
						invalid = True
					avz = float(record[avzstart : avzend])
				else:
					avz = None

				# 
				ostart = record.find(' o=\"')
				if (ostart != -1):
					ostart += len(' o=\"')
					oend = record.find('\"', ostart)
					if (record[ostart : oend] == 'NaN'):
						invalid = True
					opacity = float(record[ostart : oend])
				else:
					opacity = None

				# 
				if (invalid):
					continue

				# Disable dynamics if the object's velocity is zero (to prevent drift).
				if (((vx == 0) and (vy == 0) and (vz == 0)) or (vx == None) or (vy == None) or (vz == None)) and (((avx == 0) and (avy == 0) and (avz == 0)) or (avx == None) or (avy == None) or (avz == None)):
					objs[index][0].disable(viz.DYNAMICS) # unfortunately, this prevents us from giving the object a velocity!!!

				# Set the object's position.
				if (x != None) and (y != None) and (z != None):
					objs[index][0].setPosition([- y, z, x]) # update the position based on the rearranged world axes (see demo.py, line 35)

				# Set the object's orientation.
				if (qw != None) and (qx != None) and (qy != None) and (qz != None):
					objs[index][0].setQuat([qy, - qz, - qx, qw]) # update the orientation based on the rearranged world axes (see demo.py, line 35)

				# Set the object's opacity.
				if (opacity == 0.0):
					objs[index][0].visible(viz.OFF)
				else:
					objs[index][0].visible(viz.ON)

				# Set the object's velocity.
				if (vx != None) and (vy != None) and (vz != None):
					objs[index][0].setVelocity([- vy, vz, vx]) # update the velocity based on the rearranged world axes (see demo.py, line 35)

				# Set the object's angular velocity.
				if (avx != None) and (avy != None) and (avz != None):
					objs[index][0].setAngularVelocity([- avy, avz, avx]) # update the angular velocity based on the rearranged world axes (see demo.py, line 35)

				continue

			# 
			if (recordlength == remobj_recordlength):

				# 
				i = 0
				while (i < len(objs)):

					# 
					if objs[i] == []:
						i = i + 1
						continue

					# 
					objs[i][0].visible(viz.OFF)
					objs[i][0].setVelocity([0, 0, 0])
					objs[i][0].setAngularVelocity([0, 0, 0])
					objs[i][0].setPosition([0, 1000, -1000])

					# 
					i = i + 1

				# 
				objs = []

				continue

			# 
			if (recordlength == updobj_recordlength):

				# 
				invalid = False

				# 
				indexstart = record.find(' i=\"')
				if (indexstart != -1):
					indexstart += len(' i=\"')
					indexend = record.find('\"', indexstart)
					index = int(record[indexstart : indexend])
					if (index < 0) or (index >= len(objs)) or (objs[index] == []):
						continue
				else:
					continue

				# 
				xstart = record.find(' x=\"')
				if (xstart != -1):
					xstart += len(' x=\"')
					xend = record.find('\"', xstart)
					if (record[xstart : xend] == 'NaN'):
						invalid = True
					x = float(record[xstart : xend])
				else:
					x = None

				# 
				ystart = record.find(' y=\"')
				if (ystart != -1):
					ystart += len(' y=\"')
					yend = record.find('\"', ystart)
					if (record[ystart : yend] == 'NaN'):
						invalid = True
					y = float(record[ystart : yend])
				else:
					y = None

				# 
				zstart = record.find(' z=\"')
				if (zstart != -1):
					zstart += len(' z=\"')
					zend = record.find('\"', zstart)
					if (record[zstart : zend] == 'NaN'):
						invalid = True
					z = float(record[zstart : zend])
				else:
					z = None

				# 
				qwstart = record.find(' qw=\"')
				if (qwstart != -1):
					qwstart += len(' qw=\"')
					qwend = record.find('\"', qwstart)
					if (record[qwstart : qwend] == 'NaN'):
						invalid = True
					qw = float(record[qwstart : qwend])
				else:
					qw = None

				# 
				qxstart = record.find(' qx=\"')
				if (qxstart != -1):
					qxstart += len(' qx=\"')
					qxend = record.find('\"', qxstart)
					if (record[qxstart : qxend] == 'NaN'):
						invalid = True
					qx = float(record[qxstart : qxend])
				else:
					qx = None

				# 
				qystart = record.find(' qy=\"')
				if (qystart != -1):
					qystart += len(' qy=\"')
					qyend = record.find('\"', qystart)
					if (record[qystart : qyend] == 'NaN'):
						invalid = True
					qy = float(record[qystart : qyend])
				else:
					qy = None

				# 
				qzstart = record.find(' qz=\"')
				if (qzstart != -1):
					qzstart += len(' qz=\"')
					qzend = record.find('\"', qzstart)
					if (record[qzstart : qzend] == 'NaN'):
						invalid = True
					qz = float(record[qzstart : qzend])
				else:
					qz = None

				# 
				vxstart = record.find(' vx=\"')
				if (vxstart != -1):
					vxstart += len(' vx=\"')
					vxend = record.find('\"', vxstart)
					if (record[vxstart : vxend] == 'NaN'):
						invalid = True
					vx = float(record[vxstart : vxend])
				else:
					vx = None

				# 
				vystart = record.find(' vy=\"')
				if (vystart != -1):
					vystart += len(' vy=\"')
					vyend = record.find('\"', vystart)
					if (record[vystart : vyend] == 'NaN'):
						invalid = True
					vy = float(record[vystart : vyend])
				else:
					vy = None

				# 
				vzstart = record.find(' vz=\"')
				if (vzstart != -1):
					vzstart += len(' vz=\"')
					vzend = record.find('\"', vzstart)
					if (record[vzstart : vzend] == 'NaN'):
						invalid = True
					vz = float(record[vzstart : vzend])
				else:
					vz = None

				# 
				avxstart = record.find(' avx=\"')
				if (avxstart != -1):
					avxstart += len(' avx=\"')
					avxend = record.find('\"', avxstart)
					if (record[avxstart : avxend] == 'NaN'):
						invalid = True
					avx = float(record[avxstart : avxend])
				else:
					avx = None

				# 
				avystart = record.find(' avy=\"')
				if (avystart != -1):
					avystart += len(' avy=\"')
					avyend = record.find('\"', avystart)
					if (record[avystart : avyend] == 'NaN'):
						invalid = True
					avy = float(record[avystart : avyend])
				else:
					avy = None

				# 
				avzstart = record.find(' avz=\"')
				if (avzstart != -1):
					avzstart += len(' avz=\"')
					avzend = record.find('\"', avzstart)
					if (record[avzstart : avzend] == 'NaN'):
						invalid = True
					avz = float(record[avzstart : avzend])
				else:
					avz = None

				# 
				ostart = record.find(' o=\"')
				if (ostart != -1):
					ostart += len(' o=\"')
					oend = record.find('\"', ostart)
					if (record[ostart : oend] == 'NaN'):
						invalid = True
					opacity = float(record[ostart : oend])
				else:
					opacity = None

				# 
				if (invalid):
					objs[index][0].visible(viz.OFF)
					objs[index][0].setVelocity([0, 0, 0])
					objs[index][0].setAngularVelocity([0, 0, 0])
					objs[index][0].setPosition([0, 1000, -1000])
					continue

				# Disable dynamics if the object's velocity is zero (to prevent drift).
				if (vx != None) and (vy != None) and (vz != None):
					if (vx == 0) and (vy == 0) and (vz == 0) and (((avx == 0) and (avy == 0) and (avz == 0)) or (avx == None) or (avy == None) or (avz == None)):
						objs[index][0].disable(viz.DYNAMICS) # unfortunately, this prevents us from giving the object a velocity!!!
					else:
						objs[index][0].enable(viz.DYNAMICS)

				# Set the object's position.
				if (x != None) and (y != None) and (z != None):
					objs[index][0].setPosition([- y, z, x]) # update the position based on the rearranged world axes (see demo.py, line 35)

				# Set the object's orientation.
				if (qw != None) and (qx != None) and (qy != None) and (qz != None):
					objs[index][0].setQuat([qy, - qz, - qx, qw]) # update the orientation based on the rearranged world axes (see demo.py, line 35)

				# Set the object's opacity.
				if (opacity == 0.0):
					objs[index][0].visible(viz.OFF)
				else:
					objs[index][0].visible(viz.ON)

				# Set the object's velocity.
				if (vx != None) and (vy != None) and (vz != None):
					objs[index][0].setVelocity([- vy, vz, vx]) # update the velocity based on the rearranged world axes (see demo.py, line 35)

				# Set the object's angular velocity.
				if (avx != None) and (avy != None) and (avz != None):
					objs[index][0].setAngularVelocity([- avy, avz, avx]) # update the angular velocity based on the rearranged world axes (see demo.py, line 35)

				continue

			# 
			if (recordlength == updvar_recordlength):

				# 
				invalid = False

				# 
				namestart = record.find(' name=\"')
				if (namestart != -1):
					namestart += len(' name=\"')
					nameend = record.find('\"', namestart)
					name = record[namestart : nameend]
				else:
					continue

				# 
				valstart = record.find(' val=\"')
				if (valstart != -1):
					valstart += len(' val=\"')
					valend = record.find('\"', valstart)
					if (record[valstart : valend] == 'NaN'):
						invalid = True
					val = float(record[valstart : valend])
				else:
					val = None

				# 
				xstart = record.find(' x=\"')
				if (xstart != -1):
					xstart += len(' x=\"')
					xend = record.find('\"', xstart)
					if (record[xstart : xend] == 'NaN'):
						invalid = True
					x = float(record[xstart : xend])
				else:
					x = None

				# 
				ystart = record.find(' y=\"')
				if (ystart != -1):
					ystart += len(' y=\"')
					yend = record.find('\"', ystart)
					if (record[ystart : yend] == 'NaN'):
						invalid = True
					y = float(record[ystart : yend])
				else:
					y = None

				# 
				zstart = record.find(' z=\"')
				if (zstart != -1):
					zstart += len(' z=\"')
					zend = record.find('\"', zstart)
					if (record[zstart : zend] == 'NaN'):
						invalid = True
					z = float(record[zstart : zend])
				else:
					z = None

				# 
				qwstart = record.find(' qw=\"')
				if (qwstart != -1):
					qwstart += len(' qw=\"')
					qwend = record.find('\"', qwstart)
					if (record[qwstart : qwend] == 'NaN'):
						invalid = True
					qw = float(record[qwstart : qwend])
				else:
					qw = None

				# 
				qxstart = record.find(' qx=\"')
				if (qxstart != -1):
					qxstart += len(' qx=\"')
					qxend = record.find('\"', qxstart)
					if (record[qxstart : qxend] == 'NaN'):
						invalid = True
					qx = float(record[qxstart : qxend])
				else:
					qx = None

				# 
				qystart = record.find(' qy=\"')
				if (qystart != -1):
					qystart += len(' qy=\"')
					qyend = record.find('\"', qystart)
					if (record[qystart : qyend] == 'NaN'):
						invalid = True
					qy = float(record[qystart : qyend])
				else:
					qy = None

				# 
				qzstart = record.find(' qz=\"')
				if (qzstart != -1):
					qzstart += len(' qz=\"')
					qzend = record.find('\"', qzstart)
					if (record[qzstart : qzend] == 'NaN'):
						invalid = True
					qz = float(record[qzstart : qzend])
				else:
					qz = None

				# 
				if (val != None):
					viz.sendEvent(SCALAR_VALUE_RECEIVED_EVENT, name, val, invalid)
					
				# 
				if (x != None) and (y != None) and (z != None):
					viz.sendEvent(VECTOR_VALUE_RECEIVED_EVENT, name, vizmat.Vector(x, y, z), invalid)
					
				# 
				if (qx != None) and (qy != None) and (qz != None) and (qw != None):
					viz.sendEvent(QUAT_VALUE_RECEIVED_EVENT, name, vizmat.Quat(qx, qy, qz, qw), invalid)
					
				#
				if (name == 'height'):
					if (val != None) and not invalid:
						height = val
						heightReceived = True
				if (name == 'headpos'):
					if (x != None) and (y != None) and (z != None) and not invalid:
						head.setPosition(x, y, z)
						headposReceived = True
				if (name == 'headori'):
					if (qx != None) and (qy != None) and (qz != None) and (qw != None) and not invalid:
						head.setQuat(qx, qy, qz, qw)
						headoriReceived = True
				if (name == 'lhandpos'):
					if (x != None) and (y != None) and (z != None) and not invalid:
						lhand.setPosition(x, y, z)
						lhandposReceived = True
				if (name == 'lhandori'):
					if (qx != None) and (qy != None) and (qz != None) and (qw != None) and not invalid:
						lhand.setQuat(qx, qy, qz, qw)
						lhandoriReceived = True
				if (name == 'rhandpos'):
					if (x != None) and (y != None) and (z != None) and not invalid:
						rhand.setPosition(x, y, z)
						rhandposReceived = True
				if (name == 'rhandori'):
					if (qx != None) and (qy != None) and (qz != None) and (qw != None) and not invalid:
						rhand.setQuat(qx, qy, qz, qw)
						rhandoriReceived = True
				if (name == 'lfootpos'):
					if (x != None) and (y != None) and (z != None) and not invalid:
						lfoot.setPosition(x, y, z)
						lfootposReceived = True
				if (name == 'lfootori'):
					if (qx != None) and (qy != None) and (qz != None) and (qw != None) and not invalid:
						lfoot.setQuat(qx, qy, qz, qw)
						lfootoriReceived = True
				if (name == 'rfootpos'):
					if (x != None) and (y != None) and (z != None) and not invalid:
						rfoot.setPosition(x, y, z)
						rfootposReceived = True
				if (name == 'rfootori'):
					if (qx != None) and (qy != None) and (qz != None) and (qw != None) and not invalid:
						rfoot.setQuat(qx, qy, qz, qw)
						rfootoriReceived = True
				if (name == 'waistpos'):
					if (x != None) and (y != None) and (z != None) and not invalid:
						waist.setPosition(x, y, z)
						waistposReceived = True
				if (name == 'waistori'):
					if (qx != None) and (qy != None) and (qz != None) and (qw != None) and not invalid:
						waist.setQuat(qx, qy, qz, qw)
						waistoriReceived = True
					
				continue

			# 
			if (recordlength == begstr_recordlength):

				# 
				ratestart = record.find(' rate=\"')
				if (ratestart != -1):
					ratestart += len(' rate=\"')
					rateend = record.find('\"', ratestart)
					rate = float(record[ratestart : rateend])
				else:
					rate = 100.0

				# 
				timerAction = vizact.ontimer(1.0 / rate, sendFrame, conn)

				continue

			# 
			if (recordlength == endstr_recordlength):

				# 
				timerAction.setEnabled(0)

				continue

		if ((not fileCreated) and
		heightReceived and		
		headposReceived and
		headoriReceived and
		lhandposReceived and
		lhandoriReceived and
		rhandposReceived and
		rhandoriReceived and
		lfootposReceived and
		lfootoriReceived and
		rfootposReceived and
		rfootoriReceived and
		waistposReceived and
		waistoriReceived):



			"""
			
			# This section of code calculates and prints the constants needed to generate the ACD file, below.  Enable it whenever you need to re-calculate these constants.
			
			# The following values came from the ACD file generated by the WorldViz demo script (they are specific to the Tracker data files being streamed)
			_scale = 0.9663251042366028
			_headSlotShift = vizmat.Vector(0.0, 0.11595901250839233, 0.10339678615331649)
			_postHeadSlotShift = vizmat.Vector(9.265440041862972e-07, -1.5260990138631314, 0.026110843022639937)
			_head = vizmat.Transform()
			_head.setPosition(0, 0, 0) # NOTE: no head transform is actually created by the demo script, so we use the default (null) transform
			_head.setQuat(0, 0, 0, 1)
			_lhand = vizmat.Transform()
			_lhand.setPosition(0.06000851077752778, -0.05043161687481801, -0.04489803957285976)
			_lhand.setQuat(-0.03970563852288436, 0.11751048080399891, -0.07945901194920552, 0.9890910041934015)
			_rhand = vizmat.Transform()
			_rhand.setPosition(-0.03351221794850022, -0.03763446141878202, -0.0917197021922278)
			_rhand.setQuat(0.0722467251445279, 0.15193692026407063, 0.05966842736120879, 0.9839386473245935)
			_lfoot = vizmat.Transform()
			_lfoot.setPosition(0.03736702885550927, 0.01166855814013569, 0.012684188711086876)
			_lfoot.setQuat(0.24746426557274506, -0.4839058967159169, -0.5389117816995869, 0.6435608886258092)
			_rfoot = vizmat.Transform()
			_rfoot.setPosition(-0.1329175263525768, -0.021413405930371485, -0.031831728281038134)
			_rfoot.setQuat(-0.5557093596181519, 0.6515733870600422, 0.2093636409441593, -0.47202338887662193)
			_waist = vizmat.Transform()
			_waist.setPosition(-0.050999047460052904, -0.1934826272365303, -0.0806388067586582)
			_waist.setQuat(0.14321237387319605, -0.6495453140802693, 0.7249593560031711, 0.17892745490029624)

			# Calculate the scale constant.
			print 'scale'
			print _scale / height
			
			# Calculate the headSlotShift constant.
			print 'headSlotShift'
			print _headSlotShift / _scale
			
			# Calculate the postHeadSlotShift constant.
			print 'postHeadSlotShift'
			print _postHeadSlotShift / _scale
			
			# Calculate the head constants, by reversing the calculations that generate the head entry in the ACD file.
			headpos = head.getPosition()
			newheadpos = vizmat.Vector(- headpos[1], headpos[2], headpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			headori = head.getQuat()
			newheadori = vizmat.Quat(headori[1], - headori[2], - headori[0], headori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newhead = vizmat.Transform()
			newhead.setPosition(newheadpos)
			newhead.setQuat(newheadori)
			t0 = _head * newhead.inverse()
			print 'head'
			v0 = vizmat.Vector(t0.getPosition())
			v0 /= _scale
			print v0
			print t0.getQuat()

			# Calculate the lhand constants, by reversing the calculations that generate the lhand entry in the ACD file.
			lhandpos = lhand.getPosition()
			newlhandpos = vizmat.Vector(- lhandpos[1], lhandpos[2], lhandpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			lhandori = lhand.getQuat()
			newlhandori = vizmat.Quat(lhandori[1], - lhandori[2], - lhandori[0], lhandori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newlhand = vizmat.Transform()
			newlhand.setPosition(newlhandpos)
			newlhand.setQuat(newlhandori)
			t1 = _lhand * newlhand.inverse()
			print 'lhand'
			v1 = vizmat.Vector(t1.getPosition())
			v1 /= _scale
			print v1
			print t1.getQuat()

			# Calculate the rhand constants, by reversing the calculations that generate the rhand entry in the ACD file.
			rhandpos = rhand.getPosition()
			newrhandpos = vizmat.Vector(- rhandpos[1], rhandpos[2], rhandpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			rhandori = rhand.getQuat()
			newrhandori = vizmat.Quat(rhandori[1], - rhandori[2], - rhandori[0], rhandori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newrhand = vizmat.Transform()
			newrhand.setPosition(newrhandpos)
			newrhand.setQuat(newrhandori)
			t2 = _rhand * newrhand.inverse()
			print 'rhand'
			v2 = vizmat.Vector(t2.getPosition())
			v2 /= _scale
			print v2
			print t2.getQuat()

			# Calculate the lfoot constants, by reversing the calculations that generate the lfoot entry in the ACD file.
			lfootpos = lfoot.getPosition()
			newlfootpos = vizmat.Vector(- lfootpos[1], lfootpos[2], lfootpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			lfootori = lfoot.getQuat()
			newlfootori = vizmat.Quat(lfootori[1], - lfootori[2], - lfootori[0], lfootori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newlfoot = vizmat.Transform()
			newlfoot.setPosition(newlfootpos)
			newlfoot.setQuat(newlfootori)
			t3 = _lfoot * newlfoot.inverse()
			print 'lfoot'
			v3 = vizmat.Vector(t3.getPosition())
			v3 /= _scale
			print v3
			print t3.getQuat()

			# Calculate the rfoot constants, by reversing the calculations that generate the rfoot entry in the ACD file.
			rfootpos = rfoot.getPosition()
			newrfootpos = vizmat.Vector(- rfootpos[1], rfootpos[2], rfootpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			rfootori = rfoot.getQuat()
			newrfootori = vizmat.Quat(rfootori[1], - rfootori[2], - rfootori[0], rfootori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newrfoot = vizmat.Transform()
			newrfoot.setPosition(newrfootpos)
			newrfoot.setQuat(newrfootori)
			t4 = _rfoot * newrfoot.inverse()
			print 'rfoot'
			v4 = vizmat.Vector(t4.getPosition())
			v4 /= _scale
			print v4
			print t4.getQuat()

			# Calculate the waist constants, by reversing the calculations that generate the waist entry in the ACD file.
			waistpos = waist.getPosition()
			newwaistpos = vizmat.Vector(- waistpos[1], waistpos[2], waistpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			waistori = waist.getQuat()
			newwaistori = vizmat.Quat(waistori[1], - waistori[2], - waistori[0], waistori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newwaist = vizmat.Transform()
			newwaist.setPosition(newwaistpos)
			newwaist.setQuat(newwaistori)
			t5 = _waist * newwaist.inverse()
			print 'waist'
			v5 = vizmat.Vector(t5.getPosition())
			v5 /= _scale
			print v5
			print t5.getQuat()

			# ===== End of code which calculates the ACD file constants =====

			"""



			scale = height * 0.536847280131 # constant was calculated in previous section
			
			tposeOffsetDict = {}
			
			headpos = head.getPosition()
			newheadpos = vizmat.Vector(- headpos[1], headpos[2], headpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			headori = head.getQuat()
			newheadori = vizmat.Quat(headori[1], - headori[2], - headori[0], headori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newhead = vizmat.Transform()
			newhead.setPosition(newheadpos)
			newhead.setQuat(newheadori)
			mat0 = vizmat.Transform()
			v0 = vizmat.Vector(0.03768091225915562, 0.00520704002280954, -0.004513399444144898) # offset vector from back-of-head (calculated in previous section)
			v0 *= scale
			mat0.setPosition(v0)
			mat0.setQuat(-0.0010360015401329485, 0.60775790350056, 0.7941171805446106, 0.002676003978181243) # offset quaternion from rearranged Gagnon orientation (calculated in previous section)
			mat0.postMult(newhead)
			tposeOffsetDict['head'] = mat0

			lhandpos = lhand.getPosition()
			newlhandpos = vizmat.Vector(- lhandpos[1], lhandpos[2], lhandpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			lhandori = lhand.getQuat()
			newlhandori = vizmat.Quat(lhandori[1], - lhandori[2], - lhandori[0], lhandori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newlhand = vizmat.Transform()
			newlhand.setPosition(newlhandpos)
			newlhand.setQuat(newlhandori)
			mat1 = vizmat.Transform()
			v1 = vizmat.Vector(-0.08108926911420497, 0.04026489832562692, 0.012562662154315493) # offset vector from wrist (calculated in previous section)
			v1 *= scale
			mat1.setPosition(v1)
			mat1.setQuat(0.038498714147931705, -0.05405255295210779, 0.9977932340915838, -0.00219830147458306) # offset quaternion from rearranged Gagnon orientation (calculated in previous section)
			mat1.postMult(newlhand)
			tposeOffsetDict['lhand'] = mat1
			
			rhandpos = rhand.getPosition()
			newrhandpos = vizmat.Vector(- rhandpos[1], rhandpos[2], rhandpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			rhandori = rhand.getQuat()
			newrhandori = vizmat.Quat(rhandori[1], - rhandori[2], - rhandori[0], rhandori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newrhand = vizmat.Transform()
			newrhand.setPosition(newrhandpos)
			newrhand.setQuat(newrhandori)
			mat2 = vizmat.Transform()
			v2 = vizmat.Vector(0.0520969709831759, 0.04006913738265312, -0.035232159679672956) # offset vector from wrist (calculated in previous section)
			v2 *= scale
			mat2.setPosition(v2)
			mat2.setQuat(-0.22735621039832238, 0.05797292360699827, 0.972012769649862, -0.01180971461871437) # offset quaternion from rearranged Gagnon orientation (calculated in previous section)
			mat2.postMult(newrhand)
			tposeOffsetDict['rhand'] = mat2
			
			lfootpos = lfoot.getPosition()
			newlfootpos = vizmat.Vector(- lfootpos[1], lfootpos[2], lfootpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			lfootori = lfoot.getQuat()
			newlfootori = vizmat.Quat(lfootori[1], - lfootori[2], - lfootori[0], lfootori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newlfoot = vizmat.Transform()
			newlfoot.setPosition(newlfootpos)
			newlfoot.setQuat(newlfootori)
			mat3 = vizmat.Transform()
			v3 = vizmat.Vector(0.023834091873879998, -0.005907334728276722, -0.0027331686936446645) # offset vector from ankle (calculated in previous section)
			v3 *= scale
			mat3.setPosition(v3)
			mat3.setQuat(0.37639683443525523, -0.5458311084143318, -0.4490128974636277, 0.598983507306853) # offset quaternion from rearranged Gagnon orientation (calculated in previous section)
			mat3.postMult(newlfoot)
			tposeOffsetDict['lfoot'] = mat3

			rfootpos = rfoot.getPosition()
			newrfootpos = vizmat.Vector(- rfootpos[1], rfootpos[2], rfootpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			rfootori = rfoot.getQuat()
			newrfootori = vizmat.Quat(rfootori[1], - rfootori[2], - rfootori[0], rfootori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newrfoot = vizmat.Transform()
			newrfoot.setPosition(newrfootpos)
			newrfoot.setQuat(newrfootori)
			mat4 = vizmat.Transform()
			v4 = vizmat.Vector(-0.12314111505754202, -0.010255339202402576, -0.018621471060804362) # offset vector from ankle (calculated in previous section)
			v4 *= scale
			mat4.setPosition(v4)
			mat4.setQuat(-0.4878957140114658, 0.6010917536635552, 0.3726417207318329, -0.5116489264104175) # offset quaternion from rearranged Gagnon orientation (calculated in previous section)
			mat4.postMult(newrfoot)
			tposeOffsetDict['rfoot'] = mat4

			waistpos = waist.getPosition()
			newwaistpos = vizmat.Vector(- waistpos[1], waistpos[2], waistpos[0]) # update the offset vector based on the sensor's rearranged axes (see demo.py, line 36)
			waistori = waist.getQuat()
			newwaistori = vizmat.Quat(waistori[1], - waistori[2], - waistori[0], waistori[3]) # update the offset quaternion based on the sensor's rearranged axes (see demo.py, line 36)
			newwaist = vizmat.Transform()
			newwaist.setPosition(newwaistpos)
			newwaist.setQuat(newwaistori)
			mat5 = vizmat.Transform()
			v5 = vizmat.Vector(-0.006262284488095274, 0.0018985604843519306, 0.14041834073821596) # offset vector from L5S1 (calculated in previous section)
			v5 *= scale
			mat5.setPosition(v5)
			mat5.setQuat(-0.0002853961799667005, 0.707115782316091, 0.707097500395364, -0.0005602527566433574) # offset quaternion from rearranged Gagnon orientation (calculated in previous section)
			mat5.postMult(newwaist)
			tposeOffsetDict['waist'] = mat5

			data = viz.Data()
			data.scale = [scale, scale, scale]
			v6 = vizmat.Vector(0, 0.12, 0.107) # calculated in previous section
			v6 *= scale
			data._headSlotShift = v6
			v7 = vizmat.Vector(0, -1.579281, 0.027021) # calculated in previous section
			v7 *= scale
			data._postHeadSlotShift = v7
			data._tposeOffsetDict = tposeOffsetDict
			import pickle
			with open(CALIBRATION_FILE_NAME, 'wb') as file:
				pickle.dump(data, file)

			fileCreated = True

			viz.sendEvent(CALIBRATION_FILE_GENERATED_EVENT, CALIBRATION_FILE_NAME)

	# Close the socket.
	conn.close()

	# Indicate that the client disconnected.
	viz.sendEvent(DISCONNECTED_EVENT)

def waitForConnection(port):

	# Declare globals.
	global ipPort
	global starttime

	
	# Save the IP port number in the global variable.
	ipPort = port
	
	# Run the communications routine in a separate thread.
	threading.Thread(target = serverProc).start()
