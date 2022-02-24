import socket 
import datetime

FORMAT = 'ascii'

HELP = '''Commands:
	/help - Get this command list
	/quit - End the program
	/msg {username} {message} - send private message to an user
	/room-create {room name} - Creates a new room
	/room-msg {room name} {message} - send message to a chat room
	/room-rename {room name} {new name} - renames a room
	/room-add {room name} {username} - add an user to the room
	/room-del {room name} {username} - removes an user from the room
	/room-accept {room name} to accept a room invite
	/room-deny {room name} to decline room invite'''

COMMAND_LIST = ['/help','/quit', '/msg', '/room-create','/room-msg', 
	'/room-rename', '/room-add','/room-del', '/room-accept',
	'/room-deny']

USER = '0'
ROOM = '1'

# List of server response protocols---------------------------------------------

OFFLINE = '100'
ONLINE = '101'

# For users
USR_MSG = '21'							#Message from/to users
USR_OFFLINE = '22'
USR_READ_ACK = '23'
USR_NOT_FOUND = '24'

# For rooms 
ROOM_CREATE = '30'
ROOM_CREATE_ACK = '301'
ROOM_CREATE_DUP = '302'

ROOM_MSG = '31'					#Message to rooms
ROOM_MSG_ACK = '311'
ROOM_NOT_FOUND = '312'

MEMBER_ADD = '32'
MEMBER_ADD_ACK = '321'
MEMBER_ADD_DENY = '322'

MEMBER_DEL = '33'
MEMBER_DEL_ACK = '331'

ROOM_RENAME = '34'
ROOM_RENAME_ACK = '341'

ERROR = '40'
#-------------------------------------------------------------------------------

VERBOSE = ()

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
			if 1 in VERBOSE:
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

				read_ack = '{} {} {} {}'.format(USR_READ_ACK, getTime(), 
					sender,username)
				client.send(read_ack.encode(FORMAT))
				
			elif protocol == USR_OFFLINE:
				# 2: target (the offline client)
				target = splitted_msg[2]
				print_terminal = 'User [{}] is offline, last seen on {}'.format(
					target, convertDateTime(time))
				print(print_terminal)
				
			elif protocol == USR_READ_ACK:
				# 2: sender(this client), 3: target (the other user)
				print('User [{}] read the message sent at {}'.format(
					splitted_msg[3], convertLocalTime(time)))

			elif protocol == USR_NOT_FOUND:
				target = splitted_msg[2]
				print_terminal = 'User [{}] has never connected to server'.format(
					target)
				print(print_terminal)

			elif protocol == ROOM_CREATE_ACK:
				print_terminal = 'Room <{}> created'.format(splitted_msg[2])
				print(print_terminal)

			elif protocol == ROOM_CREATE_DUP:
				print_terminal = 'Name <{}> is taken'.format(splitted_msg[2])
				print(print_terminal)

			elif protocol == ROOM_MSG:
				# 2: sender, 3: target (the room), 4-:Content
				sender = splitted_msg[2]
				room_name = splitted_msg[3]
				content = ' '.join(splitted_msg[4:])
				print_terminal = '{} <{}> [{}] {}'.format(
					convertLocalTime(time),room_name, sender, content)
				print(print_terminal)

				reply = '{} {} {} {} {}'.format(ROOM_MSG_ACK, getTime(), 
					sender,room_name,username)
				client.send(reply.encode(FORMAT))

			elif protocol == ROOM_MSG_ACK:
				room_name = splitted_msg[3]
				receiver = splitted_msg[4]
				terminal_print = '<{}> User {} has read your message'\
					' from {}'.format(room_name, receiver,convertDateTime(time))
				print(terminal_print)

			elif protocol == ROOM_NOT_FOUND:
				room_name = splitted_msg[2]
				terminal_print = 'Room <{}> is not in database'.format(
					room_name)
				print(terminal_print)

			elif protocol == MEMBER_ADD:
				sender = splitted_msg[2]
				room_name = splitted_msg[3]
				terminal_print = 'User [{}] invited you to join <{}>, '\
					'type "/room-accept {}" to accept\n/room-deny {} '\
					'to decline'.format(sender, room_name, room_name, room_name)
				print(terminal_print)

			elif protocol == MEMBER_ADD_ACK:
				receiver = splitted_msg[2]
				room_name = splitted_msg[3]
				
				terminal_print = 'User [{}] accepted your invitation '\
					'to <{}>'.format(receiver,room_name)
				print(terminal_print)

			elif protocol == MEMBER_ADD_DENY:
				receiver = splitted_msg[2]
				room_name = splitted_msg[3]
				terminal_print = 'User [{}] declined your invitation '\
					'to <{}>'.format(receiver,room_name)
				print(terminal_print)

			elif protocol == MEMBER_DEL:
				sender = splitted_msg[2]
				room_name = splitted_msg[3]
				terminal_print = 'You are removed from <{}> by {}'.format(
					room_name,sender)
				print(terminal_print)

			elif protocol == MEMBER_DEL_ACK:
				room_name = splitted_msg[3]
				removed_user = splitted_msg[4]
				terminal_print = 'User [{}] is removed from <{}>'.format(
					removed_user,room_name)
				print(terminal_print)
			elif protocol == ERROR:
				msg = ' '.join(splitted_msg[2:])
				terminal_print = 'ERROR: {}'.format(msg)
				print(terminal_print)
			else:
				print(msg)
		except IOError:
			break
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
				elif command == '/quit':
					try:
						print('[{}] Closing program'.format(getLocalTime()))
						report = '{} {} {}'.format(OFFLINE,getTime(),username)
						client.send(report.encode(FORMAT))
						online = False
						client.shutdown(socket.SHUT_RDWR)
						client.close()
					except OSError as error:
						if str(error) == '[Errno 107] Transport endpoint '\
							'is not connected':
							pass
						else:
							print('{} Quit error: "{}"'.format(getLocalTime(),
								error))
					except Exception as error:
						print('{} Quit error: {}'.format(getLocalTime(),
								error))
					break

				elif command == '/room-create':
					if len(msg_split) != 2:
						print('Room name must be on word, you can use "_" '\
							'instead of spaces')
					else:
						room_name = msg_split[1]
						target_msg = '{} {} {} {}'.format(ROOM_CREATE, getTime(),
							username,room_name)
						client.send(target_msg.encode(FORMAT))

				elif command == '/room-accept':
					if len(msg_split) != 2:
						print('Room name must be on word, you can use "_" '\
							'instead of spaces')
					else:
						room_name = msg_split[1]
						target_msg = '{} {} {} {}'.format(MEMBER_ADD_ACK,
							getTime(),username,room_name)
						client.send(target_msg.encode(FORMAT))

				elif command == '/room-deny':
					if len(msg_split) != 2:
						print('Room name must be on word, you can use "_" '\
							'instead of spaces')
					else:
						room_name = msg_split[1]
						target_msg = '{} {} {} {}'.format(MEMBER_ADD_DENY, 
							getTime(),username,room_name)
						client.send(target_msg.encode(FORMAT))
				else:
					# Filter all wrong len here
					if len(msg_split) < 3:
						print("Please enter the correct command: see /help")
					else:

						target = msg_split[1]
						

						if command == '/msg':
							content = ' '.join(msg_split[2:])
							target_msg = formatMessage(USR_MSG, username, 
											target,content)
							client.send(target_msg.encode(FORMAT))
							print('Sent {}'.format(target_msg))
							
						elif command == '/room-msg':
							content = ' '.join(msg_split[2:])
							target_msg = formatMessage(ROOM_MSG, username, 
											target,content)
							client.send(target_msg.encode(FORMAT))
							print('Sent {}'.format(target_msg))

						elif command == '/room-rename':
							if len (msg_split) != 3:
								print('Room name must be on word, you can'\
									' use "_" instead of spaces')
								continue

							new_name = msg_split[2]
							target_msg = formatMessage(ROOM_RENAME, username, 
											target,new_name)
							client.send(target_msg.encode(FORMAT))
							print('Sent {}'.format(target_msg))

						elif command == '/room-add':
							if len (msg_split) != 3:
								print('Room name and username are one word each')
								continue

							new_member = msg_split[2]
							target_msg = formatMessage(MEMBER_ADD, username, 
											target,new_member)
							client.send(target_msg.encode(FORMAT))
							print('Sent {}'.format(target_msg))

						elif command == '/room-del':
							if len (msg_split) != 3:
								print('Room name and username are one word each')
								continue
							remove_user = msg_split[2]
							target_msg = formatMessage(MEMBER_DEL, username, 
											target,remove_user)
							client.send(target_msg.encode(FORMAT))
							print('Sent {}'.format(target_msg))
						else:
							print('Unimplimented')
