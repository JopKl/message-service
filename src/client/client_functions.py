from curses import REPORT_MOUSE_POSITION
import socket 
import threading

FORMAT = 'ascii'

HELP = '''Commands:
	/help - Get this command list
	/usr {username} {message} - send private message to an user
	/room-msg {room name} {message} - send message to a chat room
	/room-rename {room name} {new name} - renames a room
	/room-add-usr {room name} {username} - add an user to the room
	/room-remove-usr {room name} {username} - removes an user from the room
	/room-delete {room name} - removes a room'''

COMMAND_LIST = ['/help', '/usr', '/room-msg', '/room-rename', '/room-add-usr',
	'/room-remove-usr', '/room-delete']

def receive(client,username):
	while True:
		try:
			msg = client.recv(1024).decode(FORMAT)
			if msg == 'Username':
				client.send(username.encode(FORMAT))
			else:
				#handle cases here
				print(msg)
		except socket.error() as error:
			print("Connection error: " + str(error))
			client.close()
			break

def message(client,username,online):
	while True:
		msg = input()
		if msg[0] != '/':
			print('This is not a command, use /help to see possible commands')
		else:
			command = msg.split()[0]
			if command not in COMMAND_LIST:
				print('Command not found, use /help to see possible commands')
			else:
				if command == '/help':
					print(HELP)
				else:
					client.send(msg.encode(FORMAT))




