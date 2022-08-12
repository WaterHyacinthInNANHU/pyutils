"""
A simple script that: reads arbitrary
input from one socket and writes it to
another socket.

Allows two clients to connect.
Runs on port 9999 by default.
Original Author: https://github.com/devrajpalit
"""
import socket
import select
import sys

class Connection(object):
	""" Connection handeler for each connected client. """

	def __init__(self, client_socket, client_adress):
		""" Instantiates a Connection class object, which
			is used to read and write to connections.
			write to them.

			:param client_socket: A socket object.
			:param client_adress: Adress of client connection.
		"""
		self.sock = client_socket
		self.addrs = client_adress


	def recieve_data(self):
		""" Reads data from socket """
		data = self.sock.recv(1000)
		return data

	def send_data(self, data):
		""" Sends data over the socket object.

			:param data: The string to be sent.
		"""
		self.sock.sendall(data)


class PeerRelayServer(object):
	""" Server to read from one socket and write to other. """
	def __init__(self, host: list, port: int):
		""" Instantiates a Server class object, which
			is used to accept client connections and
			relay data between them.
		"""
		self.sock_map = {} # between socket and Connection object
		self.servers = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(2)]
		# Enable re-use of socket address
		for server in self.servers:
			server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			for idx, server in enumerate(self.servers):
				server.bind((host[idx], port))
		except Exception as e:
			print('Unable to bind, server will now quit.')
			sys.exit(1)
		print ('Server running on port: %s ...' % port)
		
	def accept_connections(self):
		""" Accepts connections for 2 clients
			and instantiates corresponding
			Connection objects.
		"""
		for server in self.servers:
			server.listen(2)
		try:
			sock_one, address_one = self.servers[0].accept()
			print ('Connected to first client: ', address_one)
			sock_two, address_two = self.servers[1].accept()
			print ('Connected to second client: ', address_two)
			first_connection = Connection(sock_one, address_one)
			self.sock_map[sock_one] = first_connection
			second_connection = Connection(sock_two, address_two)
			self.sock_map[sock_two] = second_connection
		except KeyboardInterrupt:
			print ('Server has been stopped.')

	def run(self):
		""" Main function that will relay connections.

			Checks which socket is readable among
			connected clients. Then reads data from
			one socket and writes to another.
		"""
		print('Waiting for connection...')
		self.accept_connections() # connecting both clients
		all_client_socks = self.sock_map.keys()
		while True:
			readable_sockets, writeable_sockets, error_sockets = \
			select.select(all_client_socks, all_client_socks, [])
			for r_socket in readable_sockets:
				sender = self.sock_map[r_socket]
				for s in all_client_socks:
					if s != r_socket: # s will be socket other than sender
						reciever = self.sock_map[s]
				try:
					data = sender.recieve_data()
				except socket.error as e:
					print ("Error receiving data: %s" % e)
					# sys.exit(1)
					return e
				if not data:
					# The connection on sender end is dead / socket has closed
					writeable_sockets[0].close() #closing reciever socket
					print ("Lost connection, server will exit")
					# sys.exit(1)
					return None
				try:
					reciever.send_data(data)
				except socket.error as e:
					# The connection on reciever end is dead / socket has closed
					readable_sockets[0].close() #closing sender socket
					print ("Unable to send data %s" % e)
					print ("Server will exit")
					# sys.exit(1)
					return e

	def reset(self):
		for server in self.servers:
			server.close()


if __name__ == "__main__":
	if len(sys.argv) == 1:
		port = 9999
	elif len(sys.argv) == 2:
		try:
			port = int(sys.argv[1])
		except ValueError as e:
			print ('Invalid port number. Server will try running on port 9999')
			port = 9999
	server = PeerRelayServer('127.0.0.1', port)
 
