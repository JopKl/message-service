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

USR_TEMPLATE = {0: None,	# Client's socket.Socket() object
				1 : True,	# Whether client is online or not
				2 : 0, 		# Last online time
				3 : []		# Buffer list of messages this client will receive
				}

# Server protocols

ANALYZE = 0

UPDATE_USR = 11					#Add/update user to database
CREATE_ROOM = 12					# Create chatroom

USR = 21							#Message from users
USR_SEND_ACK = 22
USR_RECV_ACK = 23

ROOM_MSG = 31					#Message to rooms
ROOM_MSG_SEND_ACK = 32
MEMBER_ADD_ACK = 33
MEMBER_DEL_ACK = 34

# Message queue structure:
# for each queue, add a tuple:
# 	(protocol, username, msg)

def printDatabase(client_id):
	print('++++++++++++++++++++')
	for usr in client_id.keys():
		print('{}:'.format(usr))
		for cat,val in client_id[usr].items():
			print('\t{}:  {}'.format(cat,val))
	print('++++++++++++++++++++')

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
	# queue example (username, socket(), sent time)
	#                [0]       [1]       [2]
	while not usr_queue.empty():

		user = usr_queue.get()
		username = user[0]
		client = user[1]
		time = user[2]

		if username not in client_data.keys():
			client_data[username] = USR_TEMPLATE
			if (11 or 10 or 9) in VERBOSE:
				print('[{}] adding user {} to database'.format(getLocalTime(), 
					username))
		if (11 or 10 or 9) in VERBOSE:
			print('[{}] Updating user {}'.format(getLocalTime(), username))
		#update socket instance
		client_data[username] [0] = client

		#update online status
		client_data[username] [1] = True

		#update online time
		client_data[username] [2] = time

def processQueue(client_data, msg_queue):
	while not msg_queue.empty():
		msg = msg_queue.get()
		time, sender, command, target, detail = msgBreakDown(msg)

		client_data[sender][2] = time
		if (11 or 10 or 9) in VERBOSE:
			print('[{}] processing message from {}'.format(getLocalTime(),
				sender))
		# Check if the target exists -------------------------------------------
		if target not in client_data.keys():
			client_data[sender][0].send('ERROR User does not exist'.encode(
																		FORMAT))
			continue
		# ----------------------------------------------------------------------
		
		if command == '/msg':
			target_client = client_data[target][0]
			sent_msg = getTargetMsg(USR, time, sender, detail)

			if client_data[target][1]:
				# If the usr is online, send message
				target_client.send(sent_msg.encode(FORMAT))
			else:
				# If the user if offline send to buffer
				client_data[target][3].append(sent_msg)

		elif command == '/room-msg':
			pass
		elif command == '/room-rename':
			pass
		elif command == '/room-add-usr':
			pass
		elif command == '/room-remove-usr':
			pass
		else:
			client_data[sender][0].send(
				'ERROR: Can not process command, please try again'.encode(FORMAT))
			continue
		
def processBuffer(client_data):
	if (11 or 10 or 9) in VERBOSE:
		print('\n[{}] Start handling the buffer------------'.format(getLocalTime()))
	for user, data in client_data.items():
		# If the user is online, send buffered data
		client = data[0]
		if data[1]:
			if (11 or 10 or 9) in VERBOSE:
				print('[{}] Processing buffer for {}'.format(getLocalTime(), user))
			for msg in data[3]:
				client.send(msg.encode(FORMAT))
			# Clear the buffer after sending all messages
			data[3].clear()
	if (11 or 10 or 9) in VERBOSE:
		print('[{}] Finished handling the buffer---------\n'.format(getLocalTime()))

def handle(client_data, msg_queue,usr_queue):
	while True:
		if not usr_queue.empty():
			updateUsers(client_data, usr_queue)

		if not msg_queue.empty():
			processQueue(client_data, msg_queue)

		processBuffer(client_data)
				
def receive(msg_queue,server):
	# Get messages
	while(True):
		if (21 or 20 or 9) in VERBOSE:
			print('[{}] Receiving new messages'.format(getLocalTime()))
		msg = server.recv(1024).decode(FORMAT)
		if len(msg.split) >= MESSAGE_MIN_LEN:
			msg_queue.put(msg)

def welcome(client, address,usr_queue):	
	# Get new connections
	try:
		if (32 or 30 or 9) in VERBOSE:
			print('[{}] Sending username confirmation to {}'.format(
				getLocalTime(), address))
		client.send('Username'.encode(FORMAT))
		username = client.recv(1024).decode(FORMAT)
	except Exception as error:
		print('[{}] Error receiving user {}'.format(getLocalTime(), address))

	print('[{}] Connected with {}'.format(getLocalTime(), username))

	if (32 or 30 or 9) in VERBOSE:
		print('[{}] Sending user to database'.format(getLocalTime()))

	usr_queue.put((username, client, getTime()))