import sys
from ex2utils import Server

class Server(Server):

	def onStart(self):
		print("Server has started")

	def onStop(self):
		print("Server has stopped")

	def onConnect(self, socket):
		print("Server has connected")

	def onMessage(self, socket, message):
		print("Message has been recieved")
		return True

	def onDisconnect(self, socket):
		print("Server has disconnected")

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = Server()

# Start server
server.start(ip, port)
