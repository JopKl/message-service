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

# List of server response protocols----------------------------------------------

# For users
USR = 21							#Message from users
USR_SEND_ACK = 22
USR_RECV_ACK = 23

# For rooms 
ROOM_MSG = 31					#Message to rooms
ROOM_MSG_SEND_ACK = 32
MEMBER_ADD_ACK = 33
MEMBER_DEL_ACK = 34
#-------------------------------------------------------------------------------

# Return UTC time stamp
def getTime():
	dt = datetime.datetime.now(datetime.timezone.utc)
	utc_time = dt.replace(tzinfo=datetime.timezone.utc)
	utc_timestamp = utc_time.timestamp()

	return utc_timestamp

def receive(client,username):
	while True:
		try:
			msg = client.recv(1024).decode(FORMAT)
			if msg == 'Username':
				client.send(username.encode(FORMAT))
			else:
				#handle cases here
				print(msg)
		except Exception as error:
			print("Connection error: " + str(error))
			client.close()
			break

def formatMessage(msg, username):
	# Message example 12345.123 sender_username /room-msg room_name hi
	#				  [0]		[1]       		[2.1]     [2.2]     [2.3]
	#				  time      username        command   target    detail
	formatted_msg = '{} {} {}'.format(getTime(), username, msg)
	return formatted_msg

def message(client,username):
	while True:
		msg = input()
		if msg[0] != '/':
			print('This is not a command, use /help to see possible commands')
		else:
			msg_split = msg.split()
			command = msg_split[0]
			# Length of msg_split is at least 1
			# All wrong cases of len 1 is avoided here
			if command not in COMMAND_LIST:
				print('Command not found, use /help to see possible commands')
			# The len of 1 can only be /help
			else:
				if command == '/help':
					print(HELP)
				else:
					# Filter all wrong len here
					if len(msg_split) < 3:
						print("Please enter the correct command: see /help")
					else:
						target_msg = formatMessage(msg, username)
						client.send(target_msg.encode(FORMAT))
						print('Sent {}'.format(target_msg))
