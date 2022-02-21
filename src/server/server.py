import socket
from server_functions import*

PORT_IPV4 = 50000
PORT_IPV6 = 50001
HOST_IPV4 = '127.0.0.1'
HOST_IPV6 = '::1'

IPV6 = False

def main():
	if IPV6 is False:
		server_ip4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_ip4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			server_ip4.bind((HOST_IPV4, PORT_IPV4))
		except Exception as error:
			print("IPV4 socket binding error: " + str(error))
	elif socket.has_ipv6():
		server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			server.bind((HOST_IPV6, PORT_IPV6))
		except Exception as error:
			print("IPV6 socket binding error: " + str(error))

	server_ip4.listen()

	client_data = {}
	msg_queue = queue.Queue()
	usr_queue = queue.Queue()
	
	update_thread = threading.Thread(target=updateUsers, args=(client_data,
																usr_queue))
	update_thread.start()

	send_thread = threading.Thread(target=processQueue, args=(client_data,
		msg_queue))
	send_thread.start()

	receive(server_ip4, msg_queue,usr_queue)


if __name__ == "__main__":
	main()