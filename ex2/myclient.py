import sys
from ex2utils import Client
import time


class Client(Client):

	def onConnect(self, socket):
		"""
		Called when a socket connects to the server.
		If the user provided a name when starting the server, their name is attempted to be changed.

		socket: The socket to connect to the server.
		"""
		if (len(sys.argv) == 4):
			name = sys.argv[3].replace(" ", "")
			if (len(name) > 0):
				command = "JOIN " + name
				self.send(command.encode())

	def onMessage(self, socket, message):
		"""
		Called when a server message is received.
		Prints the message recieved to the client, removing the previous line (so input lines are hidden).

		socket: The socket which has sent the server message.
		message: The server message.
		Returns: True.
		"""
		print("\r", end="")
		print(message, end="")
		print("\n> ", end="")
		return True



def error(code):
	"""
	Sends a client error message to the user.

	code: The error code.
	"""
	if (code == 1):
		print("Incorrect usage of client. Use following format:\n    $ python3 " + str(sys.argv[0]) + " <ip address> <port> <screen name (optional)>")
	elif (code == 2):
		print("Server couldn't be found with provided IP address or port.")
	sys.exit()


# Ensures that IP address and port are passed in
if (len(sys.argv) not in [3, 4]):
	error(1)

# Parse the IP address and port you wish to connect to.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create a client.
client = Client()

# Start client server connection
try:
	client.start(ip, port)
except:
	error(2)

run = True
message = ""

# 
while run:
	message = input()
	print("\033[A                             \033[A")
	client.send(message.encode())
	if (message.upper()[0:4] == "QUIT"):
		run = False
		print("\r", end="")

# Stops client
client.stop()
