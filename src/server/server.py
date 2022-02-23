import socket
from server_functions import*

PORT_IPV4 = 50000
PORT_IPV6 = 50001
HOST_IPV4 = '127.0.0.1'
HOST_IPV6 = '::1'

IPV6_CAPABLE = False

def main():
	
	server_ip4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ip4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		server_ip4.bind((HOST_IPV4, PORT_IPV4))
		server_ip4.listen()
		print('[{}] Opened ipv4 socket and listening for connections'.format(
			getLocalTime()))
	except Exception as error:
		print("IPV4 socket binding error: " + str(error))

	if socket.has_ipv6:
		IPV6_CAPABLE = True
		server_ip6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		server_ip6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			server_ip6.bind((HOST_IPV6, PORT_IPV6))
			server_ip6.listen()
			print('[{}] Opened ipv6 socket and listening for connections'.format(
				getLocalTime()))
		except Exception as error:
			print("IPV6 socket binding error: " + str(error))


	client_data = {}
	msg_queue = queue.Queue()
	usr_queue = queue.Queue()
	
	update_thread = threading.Thread(target=updateUsers, args=(client_data,
																usr_queue))
	update_thread.daemon = True
	update_thread.start()

	send_thread = threading.Thread(target=processQueue, args=(client_data,
		msg_queue,usr_queue))
	send_thread.daemon = True
	send_thread.start()

	online = True
	ipv4_receive_thread = threading.Thread(target=receive,args=(server_ip4, 
										msg_queue,usr_queue,online))
	ipv4_receive_thread.daemon = True
	ipv4_receive_thread.start()

	ipv6_receive_thread = threading.Thread(target=receive,args=(server_ip6, 
										msg_queue,usr_queue,online))
	ipv6_receive_thread.daemon = True
	ipv6_receive_thread.start()

	exit = input()
	while exit != 'quit':
		exit = input()


if __name__ == "__main__":
	main()