import signal
import socket
from client_functions import*
import threading
from functools import partial

PORT_IPV4 = 50000
PORT_IPV6 = 50001
HOST_IPV4 = '127.0.0.1'
HOST_IPV6 = '::1'

online = True
# Handle terminations (like ctrl+z, ctrl+c)
def terminate(self, signum, frame):
	print('[{}] Closing sockets, terminating program'.format(getLocalTime()))
	global online
	online = False
	report = '{} {} {}'.format(OFFLINE,getTime(),self[1])
	self[0].send(report.encode(FORMAT))
	self[0].shutdown(socket.SHUT_RDWR)
	self[0].close()

def main():
	IPV6_USE = False
	
	if socket.has_ipv6:
		use_ipv6 = input('Do you want to use ipv6? y/n\n')

		while use_ipv6 not in ('y','n'):
			use_ipv6 = input('Do you want to use ipv6? y/n\n')

		if use_ipv6 == 'y':
			IPV6_USE = True

	username = input("Enter your username: ")

	if not IPV6_USE:
		print('Creating an IPv4 socket')
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			client.connect((HOST_IPV4, PORT_IPV4))
		except socket.error() as error:
			print("IPV4 connection error: " + str(error))
	else:
		print('Creating an IPv6 socket')
		client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		#client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			client.connect((HOST_IPV6, PORT_IPV6))
		except socket.error() as error:
			print("IPV6 connection error: " + str(error))

	msg = client.recv(1024).decode(FORMAT)
	if msg == 'USERNAME':
		response = '{} {}'.format(getTime(), username)
		client.send(response.encode(FORMAT))

	database = {USER:{},ROOM:{}}

	receive_thread = threading.Thread(target=receive,args=(client,username))
	receive_thread.daemon = True
	receive_thread.start()

	message_thread = threading.Thread(target=message,args=(client,username,
											database))
	message_thread.daemon = True
	message_thread.start()

	user_tuple = (client, username)
	while online and message_thread.is_alive():
		# Ctrl + Z
		signal.signal(signal.SIGTSTP, partial(terminate, user_tuple))
		# Ctrl + C
		signal.signal(signal.SIGINT, partial(terminate, user_tuple))
		# 'kill -1' command
		signal.signal(signal.SIGHUP, partial(terminate, user_tuple))
		# 'kill -15' command
		signal.signal(signal.SIGTERM, partial(terminate, user_tuple))

if __name__ == "__main__": 
	main()