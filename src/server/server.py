import socket
from server_functions import*

PORT_IPV4 = 50000
PORT_IPV6 = 50001
HOST_IPV4 = '127.0.0.1'
HOST_IPV6 = '::1'

IPV6 = False

def main():
	if IPV6 is False:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			server.bind((HOST_IPV4, PORT_IPV4))
		except Exception as error:
			print("IPV4 socket binding error: " + str(error))
	elif socket.has_ipv6():
		server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			server.bind((HOST_IPV6, PORT_IPV6))
		except Exception as error:
			print("IPV6 socket binding error: " + str(error))

	server.listen()

	client_data = {}
	msg_queue = queue.Queue()
	usr_queue = queue.Queue()

	receive_thread = threading.Thread(target=receive,
					args=(msg_queue,server))
	receive_thread.start()

	handle_thread = threading.Thread(target=handle,
					args=(client_data,msg_queue,usr_queue))
	handle_thread.start()

	while(True):
		if (31 or 30 or 9) in VERBOSE:
			print('[{}] Receiving new connections'.format(getLocalTime()))

		client, address = server.accept()
		print('Connected with ' + str(address))
		# Request and storing user name
		welcome_thread = threading.Thread(target=welcome,
							args=(client, address,usr_queue))
		welcome_thread.start()


if __name__ == "__main__":
	main()