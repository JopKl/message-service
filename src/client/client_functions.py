import socket 
import datetime

FORMAT = 'ascii'

HELP = '''Commands:
	/help - Get this command list
	/msg {username} {message} - send private message to an user
	/room-msg {room name} {message} - send message to a chat room
	/room-rename {room name} {new name} - renames a room
	/room-add-usr {room name} {username} - add an user to the room
	/room-remove-usr {room name} {username} - removes an user from the room'''

COMMAND_LIST = ['/help', '/msg', '/room-msg', '/room-rename', '/room-add-usr',
	'/room-remove-usr']

USER = 0
ROOM = 1

# List of server response protocols---------------------------------------------

# For users
USR_MSG = '21'							#Message from/to users
USR_OFFLINE = '22'
USR_READ_ACK = '23'
USR_NOT_FOUND = '24'

# For rooms 
ROOM_MSG = '31'					#Message to rooms
MEMBER_ADD_ACK = '32'
MEMBER_DEL_ACK = '33'
#-------------------------------------------------------------------------------

# Return UTC time stamp
def getTime():
	dt = datetime.datetime.now(datetime.timezone.utc)
	utc_time = dt.replace(tzinfo=datetime.timezone.utc)
	utc_timestamp = utc_time.timestamp()
	return utc_timestamp

def getLocalTime():
	now = datetime.datetime.now()
	current_time = now.strftime("%H:%M:%S")
	return str(current_time)

def convertLocalTime(epoch_time):
	date_time = datetime.datetime.fromtimestamp(float(epoch_time))  
	local_time = date_time.strftime("%H:%M:%S")
	return local_time

def convertDateTime(epoch_time):
	date_time = datetime.datetime.fromtimestamp(float(epoch_time))  
	return date_time

def formatMessage(protocol, sender, target, content):
	formatted_msg = '{} {} {} {} {}'.format(protocol, getTime(), sender, 
											target, content)
	return formatted_msg

def receive(client,username):
	while True:
		try:
			msg = client.recv(1024).decode(FORMAT)
			if len(msg) == 0:
				continue
			print('[{}] Received length {}: {}'.format(getLocalTime(), 
				len(msg),msg))
			splitted_msg = msg.split()
			#Msg format:
			# 0: Protocol, 1:Time
			protocol = splitted_msg[0]
			time = float(splitted_msg[1])
			if protocol == USR_MSG:
				# 2: sender, 3: target (this client), 4-:Content
				sender = splitted_msg[2]
				content = ' '.join(splitted_msg[4:])
				print_terminal = '{} [{}]: {}'.format(convertLocalTime(time),
					sender, content)
				print(print_terminal)

				# read_ack = '{} {} {}'.format(USR_READ_ACK, getTime(), username)
				
				# client.send(read_ack.encode(FORMAT))
				
			elif protocol == USR_OFFLINE:
				# 2: target (the offline client)
				target = splitted_msg[2]
				print_terminal = 'User {} is offline, last seen on {}'.format(
					target, convertDateTime(time))
				print(print_terminal)
			# elif protocol == USR_READ_ACK:
			# 	pass
			elif protocol == USR_NOT_FOUND:
				target = splitted_msg[2]
				print_terminal = 'User {} has never connected to server'.format(
					target)
				print(print_terminal)
			else:
				print(msg)
		except Exception as error:
			print("Connection error: " + str(error))
			client.close()
			break

def printMsgList(database):
	user_list = database[USER]
	for user in user_list.keys():
		print('[User] {}'.format(user))

	room_list = database[ROOM]
	for room in room_list.keys():
		print('[Room] {}'.format(room))

def message(client,username,database):
	while True:

		#printMsgList(database)
		msg = input()
		
		if msg[0] != '/':
			print('This is not a command, use /help to see possible commands')
		else:
			msg_split = msg.split()
			command = msg_split[0]

			if command not in COMMAND_LIST:
				print('Command not found, use /help to see possible commands')
			else:
				if command == '/help':
					print(HELP)
				else:
					# Filter all wrong len here
					if len(msg_split) < 3:
						print("Please enter the correct command: see /help")
					else:

						target = msg_split[1]
						content = ' '.join(msg_split[2:])

						if command == '/msg':
							target_msg = formatMessage(USR_MSG, username, 
											target,content)
							client.send(target_msg.encode(FORMAT))
							print('Sent {}'.format(target_msg))

						else:
							print('Unimplimented')
