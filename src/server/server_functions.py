import queue
import socket 
import threading
import datetime

# Encoding format
FORMAT = 'ascii'
MESSAGE_MIN_LEN = 5

# Debugging message
# 0 : None
# x = 0 : All in family
# 1x : Print things related to handle()
# 	11 : related to handle()
# 2x : Print things related to receive()
#	21 : In receive()
# 3x : Print things related to welcome()
#	31 : Receving connections
#	32 : welcoming users
# 9 : Print all
VERBOSE = (32, 21)


# List of server response protocols---------------------------------------------

OFFLINE = 0
ONLINE = 1

UPDATE_USR = 11					#Add/update user to database
CREATE_ROOM = 12					# Create chatroom

# For users
USR_MSG = '21'							#Message from/to users
USR_OFFLINE = '22'
USR_READ_ACK = '23'

# For rooms 
ROOM_MSG = '31'					#Message to rooms
MEMBER_ADD_ACK = '32'
MEMBER_DEL_ACK = '33'
#-------------------------------------------------------------------------------



def printDatabase(client_data):
	print('[{}]------------------------'.format(getLocalTime()))
	for usr, data in client_data.items():
		print('\t{}:'.format(usr))
		print('\tAddress: {}'.format(data[0]))	
		print('\tOnline: {}'.format(data[1]))
		print('\tLast online: {}'.format(data[2]))
		print('.....................')
	print('----------------------------')

def getLocalTime():
	now = datetime.datetime.now()
	current_time = now.strftime("%H:%M:%S")
	return str(current_time)

# Return UTC time stamp
def getTime():
	dt = datetime.datetime.now(datetime.timezone.utc)
	utc_time = dt.replace(tzinfo=datetime.timezone.utc)
	utc_timestamp = utc_time.timestamp()

	return utc_timestamp

# Return message to client in formatted form
def getTargetMsg(protocol,time, sender, msg_detail):
	# Example msg string
	# '11 1234,123  sender_name hi'
	#  [0][1]       [2]         [3]
	msg = '{} {} {} {}'.format(str(protocol),time,sender, msg_detail)
	return msg

def msgBreakDown(msg):
	# Message example 12345.123 sender_username /room-msg room_name hi
	#				  [0]		[1]       		[2]       [3]       [4]
	#				  time      username        command   target    detail
	splitted_msg = msg.split()

	time = float(splitted_msg[0])
	sender = splitted_msg[1]
	command = splitted_msg[2]
	target = splitted_msg[3]
	detail = splitted_msg[4]

	return time, sender, command, target, detail

def updateUsers(client_data,usr_queue):
	while True:
		if not usr_queue.empty():
			user = usr_queue.get()
			status = user[0]
			username = user[1]
			time = float(user[2])

			if status == ONLINE:
				client = user[3]

				if username not in client_data.keys():
					print('[{}] {} is not in database, adding now'.format(
						getLocalTime(),username))
					client_data[username] = {0: None,1 : True,	2 : 0}

					print('\nTest 1~~~~~~~~~~~~~~~~~~~~~~~')
					printDatabase(client_data)
					print('\nTest 1~~~~~~~~~~~~~~~~~~~~~~~')

					if (11 or 10 or 9) in VERBOSE:
						print('[{}] Adding user {} to database'.format(
							getLocalTime(), username))

				if (11 or 10 or 9) in VERBOSE:
					print('[{}] Updating user {}'.format(getLocalTime(), 
						username))
				
				# update socket instance
				client_data[username] [0] = client

				print('\n Test2~~~~~~~~~~~~~~~~~~~~~~~')
				printDatabase(client_data)
				print('\n Test2~~~~~~~~~~~~~~~~~~~~~~~')
				# update online status
				client_data[username] [1] = True
				# update online time
				client_data[username] [2] = time
			else:
				# update offline status
				client_data[username] [1] = False
				# update last online time
				client_data[username] [2] = time

			print('\nAfter adding {}:'.format(username))
			printDatabase(client_data)

def processQueue(client_data, msg_queue):
	offline_queue = queue.Queue()
	while True:
		if not msg_queue.empty():
			current_msg = msg_queue.get()
			splitted_msg = current_msg.split()
			protocol = splitted_msg[0]
			# time = splitted_msg[1]
			# sender = splitted_msg[2]
			target = splitted_msg[3]
			# content = splitted_msg[4]

			if protocol == USR_MSG:
				# If the recipient is onine
				if client_data[target][1]:
					client = client_data[target][0]
					try:
						client.send(current_msg.encode(FORMAT))
					except Exception as error:
						print('[{}] {}'.format(getLocalTime(), error))
						offline_queue.put(current_msg)
					
				else:
					offline_queue.put(current_msg)
			else:
				print('[{}] Unimplemented: {}'.format(getLocalTime(),
													current_msg))
				continue

		
def processBuffer(client_data):
	pass

def handle(client,username,msg_queue,usr_queue):
	while True:
		try:
			message = client.recv(1024).decode(FORMAT)
			msg_queue.put(message)
		except:
			usr_queue.put((OFFLINE, username, getTime()))
			client.close()
			break

	pass
				
def receive(server, msg_queue,usr_queue):
	# Get messages and create new client threads
	while(True):
		if (31 or 30 or 9) in VERBOSE:
			print('[{}] Receiving new connections'.format(getLocalTime()))

		client, address = server.accept()
		print('Connected with ' + str(address))

		try:
			client.send('USERNAME'.encode(FORMAT))
			response = client.recv(1024).decode(FORMAT)
		except Exception as error:
			print('[{}] Error receiving user {}'.format(getLocalTime(), 
				address))

		resp = response.split()
		time = resp[0]
		username = resp[1]
		usr_queue.put((ONLINE, username, time, client))

		print('[{}] Connected with {}'.format(getLocalTime(), username))
		
		client_thread = threading.Thread(target=handle,args=(client, username,
														msg_queue,usr_queue))
		client_thread.start()


def welcome(client, address,usr_queue):	
	# Get new connections
	pass