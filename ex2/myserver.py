import sys
from ex2utils import Server

class Server(Server):
	numConnections = 0

	def getNum(self):
		return Server.numConnections

	def inc(self):
		Server.numConnections += 1

	def dec(self):
		Server.numConnections -= 1


	def onStart(self):
		print("Server has started")

	def onStop(self):
		print("Server has stopped")

	def onConnect(self, socket):
		print("Server has connected")
		self.inc()
		print("Server has " + str(self.getNum()) + " active connections")

	def onMessage(self, socket, message):
		print("Message has been recieved")
		return True

	def onDisconnect(self, socket):
		print("Server has disconnected")
		self.dec()
		print("Server has " + str(self.getNum()) + " active connections")

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = Server()

# Start server
server.start(ip, port)
