import sys
from ex2utils import Server

class Server(Server):
	numConnections = 0
	userName = "Joe"

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
		print(socket + " has connected")
		self.inc()
		print("Server has " + str(self.getNum()) + " active connections")

	def onMessage(self, socket, message):
		print("Message has been recieved")

		(command, sep, parameters) = message.strip().partition(" ")

		if (command.upper() == "MESSAGE"):
			print("Message command")
			(target, sep, content) = parameters.strip().partition(" ")
			if ((target == "") or (content == "")):
				Server.error(socket, 1)
				return True
			if (target == "all"):
				print("everyone")
			else:
				print(target)

			socket.send((Server.userName + ": " + content).encode())
			print(content)

		elif (command.upper() == "QUIT"):
			print("QUIT command")
			if (content != ""):
				print("No content required")
		else:
			print("Invalid command")

		return True

	def onDisconnect(self, socket):
		print(socket + " has disconnected")
		self.dec()
		print("Server has " + str(self.getNum()) + " active connections")

	def error(socket, code):
		if (code == 1):
			socket.send("Incorrect usage of MESSAGE command. Use following format:\n\tMESSAGE <recipient> <message content>".encode())

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = Server()

# Start server
server.start(ip, port)
