import socket 
import threading

FORMAT = 'ascii'

def handle(client, client_id):
	while True:
		try:
			msg = client.recv(1024).decode(FORMAT)
			#handle sends here
			print("Received from {}: {}".format(client_id[client], msg))
			client.send(('Received: {}'.format(msg)).encode(FORMAT))
		except:
			client_id.pop(client)
			break

def receive(server, client_id):
	while True:
		client, address = server.accept()
		print('Connected with ' + str(address))

		# Request and storing user name
		client.send('Username'.encode(FORMAT))
		username = client.recv(1024).decode(FORMAT)
		client_id[client] = username

		print('User {} connected'.format(username))
		client.send('Connected to server'.encode(FORMAT))

		thread = threading.Thread(target=handle, args=(client,client_id))
		thread.start()


