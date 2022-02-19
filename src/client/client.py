import socket
from client_functions import*
import threading

PORT_IPV4 = 50000
PORT_IPV6 = 50001
HOST_IPV4 = '127.0.0.1'
HOST_IPV6 = '::1'

IPV6 = False
online = {'User':[], 'Server':[]}

def main():

	username = input("Enter your username: ")

	if IPV6 is False:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			client.connect((HOST_IPV4, PORT_IPV4))
		except socket.error() as error:
			print("IPV4 connection error: " + str(error))
	elif socket.has_ipv6():
		client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			client.connect((HOST_IPV6, PORT_IPV6))
		except socket.error() as error:
			print("IPV6 connection binding error: " + str(error))

	receive_thread = threading.Thread(target=receive,args=(client,username))
	receive_thread.start()

	message_thread = threading.Thread(target=message,args=(client,username))
	message_thread.start()
	
if __name__ == "__main__": 
	main()