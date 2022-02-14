import socket
import threading
from server_functions import*

PORT_IPV4 = 50000
PORT_IPV6 = 50001
HOST_IPV4 = '127.0.0.1'
HOST_IPV6 = '::1'

IPV6 = False

client_id = {}

def main():
	if IPV6 is False:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			server.bind((HOST_IPV4, PORT_IPV4))
		except socket.error() as error:
			print("IPV4 socket binding error: " + str(error))
	elif socket.has_ipv6():
		server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			server.bind((HOST_IPV6, PORT_IPV6))
		except socket.error() as error:
			print("IPV6 socket binding error: " + str(error))

	server.listen()

	receive(server, client_id)


if __name__ == "__main__":
	main()