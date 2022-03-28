import sys
from ex2utils import Client
import time


class Client(Client):

	def onConnect(self, socket):
		if (len(sys.argv) == 4):
			name = sys.argv[3].replace(" ", "")
			if (len(name) > 0):
				command = "RENAME " + name
				self.send(command.encode())

	def onMessage(self, socket, message):
		# *** process incoming messages here ***
		print("\r", end="")
		print(message, end="")
		print("\n> ", end="")
		return True



def error(code):
	if (code == 1):
		print("Incorrect usage of client. Use following format:\n    $ python3 " + str(sys.argv[0]) + " <ip address> <port> <screen name (optional)>")
	elif (code == 2):
		print("Server couldn't be found")
	sys.exit()


# Ensures that IP address and port are passed in
if (len(sys.argv) not in [3, 4]):
	error(1)

# Parse the IP address and port you wish to connect to.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create a client.
client = Client()

# Start server
try:
	client.start(ip, port)
except:
	error(2)

#send message to the server
# message = "MESSAGE ALL hello world"
# client.send(message.encode())

run = True
message = ""

while run:
	message = input()
	print("\033[A                             \033[A")
	client.send(message.encode())
	if (message.upper()[0:4] == "QUIT"):
		run = False
		print("\r", end="")

#stops client
client.stop()
