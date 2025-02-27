import sys
from ex2utils import Server


class Server(Server):
	def onStart(self):
		"""
		Called when the server has started.
		Initiates list of sockets.
		"""
		print("Server has started")
		self._sockets = []


	def onStop(self):
		"""
		Called when the server has terminated.
		Cleans-up list of sockets.
		"""
		print("Server has stopped")
		self._sockets.clear()


	def onConnect(self, socket):
		"""
		Called when a socket connects to the server.
		Adds socket to the list of sockets and broadcasts the connection.

		socket: The socket to connect to the server.
		"""
		# Adds user to socket list and gets index
		newUserRef = self.addSocket(socket, "user" + str(len(self._sockets)))
		name = self._sockets[newUserRef][0]

		# Outputs new connection to server
		print(name + " is trying to connect")
		print("Server has " + str(len(self._sockets)) + " active connections")

		# Sends new user connection info, help info and the current user list
		connectInfo = "Server has been found, please enter a suitable user name using the JOIN command"
		self.sendToSocket(newUserRef, connectInfo)


	def onDisconnect(self, socket):
		"""
		Called when a socket disconnects to the server.
		Removes socket from the list of socket and broadcasts the disconnection.

		socket: The socket to disconnect from the server.
		"""
		# Gets socket name and index
		userRef = self.getSocket(socket)
		name = self._sockets[userRef][0]

		# Sends user disconnection info
		disconnectInfo = "You've left the server"
		self.sendToSocket(userRef, disconnectInfo)

		# Alerts other users that a new user has connected
		disconnectInfo = name + " has disconnected"
		self.sendToAllOtherSockets(userRef, disconnectInfo)

		# Removes socket from socket list
		self.removeSocket(userRef)

		# Outputs disconnection to server
		print(name + " has disconnected")
		print("Server has " + str(len(self._sockets)) + " active connections")


	def onMessage(self, socket, message):
		"""
		Called when a server message is received.
		Parses command and parameters from the server messasge, executing the corresponding command if authorised.

		socket: The socket which has sent the server message.
		message: The server message.
		Returns: True if the connection hasn't been terminated, False if it has.
		"""
		# Parses server message for command and parameters and gets socket index
		(command, sep, parameters) = message.strip().partition(" ")
		userRef = self.getSocket(socket)

		if (userRef != -1):
			name = self._sockets[userRef][0]
			authorised = self._sockets[userRef][2]

			# Executes corresponding command
			if (command.upper() == "HELP"):
				print("HELP command - " + name)
				self.help(userRef)

			elif (command.upper() == "USERS"):
				print("USERS command - " + name)
				self.users(userRef)

			elif (command.upper() == "JOIN"):
				if not authorised:
					print("JOIN command - " + name)
					newName = parameters.replace(" ", "")
					if (newName == ""):
						self.error(userRef, 2)
					else:
						self.join(userRef, newName)
				else:
					self.error(userRef, 1)

			elif (command.upper() == "RENAME"):
				if authorised:
					print("RENAME command - " + name)
					newName = parameters.replace(" ", "")
					if (newName == ""):
						self.error(userRef, 3)
					else:
						self.rename(userRef, newName)
				else:
					self.error(userRef, 1)

			elif (command.upper() == "MESSAGE"):
				if authorised:
					print("MESSAGE command - " + name)
					(target, sep, content) = parameters.strip().partition(" ")
					if ((target == "") or (content == "")):
						self.error(userRef, 4)
					else:
						self.message(userRef, target, content)
				else:
					self.error(userRef, 1)

			elif (command.upper() == "QUIT"):
				print("QUIT command - " + name)
				return self.quit(userRef)

			else:
				print("Invalid command")
				self.error(userRef, 5)

		return True


	def addSocket(self, socket, name):
		"""
		Adds a socket to the server.

		socket: The socket which is being added to the server.
		name: The screen name that the new socket will use.
		Returns: The index of the new socket.
		"""
		self._sockets.append([name, socket, False])
		print(self._sockets[len(self._sockets) - 1][0] + " added to server")
		return len(self._sockets) - 1  # Returns new index

	def renameSocket(self, userRef, newName, isJoin=False):
		"""
		Updates a socket's screen name.

		userRef: The index of the socket to update the screen name of.
		newName: The new screen name of the socket.
		isJoin: True if user is joining the server, False otherwise. Is False by default.
		Returns: True if socket successfully renamed, False otherwise.
		"""
		oldName = self._sockets[userRef][0]

		if ((self.getSocketByName(newName) == -1) and (newName.lower() not in ["all", "everyone"])):
			self._sockets[userRef][0] = newName
			if isJoin:
				self._sockets[userRef][2] = True
			return True

		self.error(userRef, 6)
		return False

	def sendToSocket(self, userRef, message):
		"""
		Sends a message to a socket.

		userRef: The index of the socket.
		message: The message to be sent.
		"""
		self._sockets[userRef][1].send(message.encode())
		print("Message sent to " + str(self._sockets[userRef][0]))

	def sendToAllOtherSockets(self, userRef, message):
		"""
		Sends a message to all sockets except the current socket.

		userRef: The index of the current socket.
		message: The message to be sent.
		"""
		for socRef in range(len(self._sockets)):
			if (socRef != userRef):
				self.sendToSocket(socRef, message)

	def getSocket(self, socket):
		"""
		Gets the index for a socket currently connected to the server.

		socket: The socket reference.
		Returns: The index of the socket.
		"""
		for socRef in range(len(self._sockets)):
			if (self._sockets[socRef][1] == socket):
				print(self._sockets[socRef][0] + " found")
				return socRef
		print(str(socket) + " not found")
		return -1

	def getSocketByName(self, name):
		"""
		Gets the index for a socket currently connected to the server.

		name: Screen name of the socket.
		Returns: The index of the socket.
		"""
		for socRef in range(len(self._sockets)):
			if (self._sockets[socRef][0] == name):
				print(name + " found")
				return socRef
		print(name + " not found")
		return -1

	def removeSocket(self, userRef):
		"""
		Removes a socket from the server.

		userRef: The index of the socket being removed.
		Returns: True if socket successfully removed, False if socket couldn't be removed.
		"""
		if ((userRef >= 0) or (userRef < len(self._sockets))):
			print(self._sockets[userRef][0] + " removed from server")
			del self._sockets[userRef]
			return True
		print(self._sockets[userRef][0] + " couldn't be removed from server")
		return False


	def help(self, userRef):
		"""
		Sends a list of available commands to a user.

		userRef: The index of the socket to send the information to.
		"""
		helpInfo = "\nAvailable Commands:"
		if (self._sockets[userRef][2] == True):
			helpInfo += "\n    HELP                                  - Get list of available commands"
			helpInfo += "\n    USERS                                 - Get a list of all users currently online"
			helpInfo += "\n    RENAME <new name>                     - Change your screen name"
			helpInfo += "\n    MESSAGE <recipient> <message content> - Send a message to the recipient (use ALL to send a message to everyone)"
			helpInfo += "\n    QUIT                                  - Quit the chat server"
		else:
			helpInfo += "\n    HELP            - Get list of available commands"
			helpInfo += "\n    USERS           - Get a list of all users currently online"
			helpInfo += "\n    JOIN <new name> - Join the chat server with a unique screen name"
			helpInfo += "\n    QUIT            - Quit the chat server"
		self.sendToSocket(userRef, helpInfo)

	def users(self, userRef):
		"""
		Sends a list of the current online user names.

		userRef: The index of the socket to send the information to.
		"""
		num = len(self._sockets)
		if (num == 0):
			usersInfo = "\nThere are no other active users"
		else:
			usersInfo = "\nCurrent Active Users:"
			for i in range(num):
				usersInfo += "\n    " + self._sockets[i][0]
				if (i == userRef):
					usersInfo += " (You)"
		self.sendToSocket(userRef, usersInfo)

	def join(self, userRef, newName):
		"""
		Updates a socket's screen name.

		userRef: The index of the socket to update the screen name of.
		newName: The new screen name of the socket.
		Returns: True if socket successfully renamed, False otherwise.
		"""
		isUpdated = self.renameSocket(userRef, newName, True)

		if isUpdated:
			self.sendToSocket(userRef, "You've successfully joined the server as " + newName)
			self.help(userRef)
			self.users(userRef)

			self.sendToAllOtherSockets(userRef, newName + " has joined")

	def rename(self, userRef, newName):
		"""
		Updates a socket's screen name.

		userRef: The index of the socket to update the screen name of.
		newName: The new screen name of the socket.
		"""
		oldName = self._sockets[userRef][0]

		isUpdated = self.renameSocket(userRef, newName)

		if isUpdated:
			self.sendToSocket(userRef, "Your screen name has been changed to " + newName)
			self.sendToAllOtherSockets(userRef, oldName + " has changed their name to " + newName)
		
	def message(self, userRef, target, content):
		"""
		Sends a message to a user or a group of users.
		
		userRef: The index of the socket which is sending the message.
		target: The target socket or sockets of the message.
		content: The content of the message.
		"""
		name = self._sockets[userRef][0]
		
		# Sends message to all users
		if (target.lower() in ["all", "everyone"]):
			print("Sending to everyone")

			message = name + ": " + content
			self.sendToAllOtherSockets(userRef, message)
			self.sendToSocket(userRef, message)

		# Sends message to target user
		else:
			print("Sending to " + target)
			message = name + " (Private): " + content

			targetSocket = self.getSocketByName(target)
			if (targetSocket == -1):
				self.error(userRef, 7)
				return

			self.sendToSocket(targetSocket, message)

			message = name + " (" + target + "): " + content
			self.sendToSocket(userRef, message)
		
	def quit(self, userRef):
		"""
		Initiates a connection termination.

		userRef: The index of the socket which is disconnecting.
		Returns: False to initiate disconnection.
		"""
		quitInfo = "You have successfully left the chat server."
		self.sendToSocket(userRef, quitInfo)
		return False

	def error(self, userRef, code):
		"""
		Sends a usage error message to the user.

		userRef: The index of the socket to send the message to.
		code: The error code.
		"""
		errorInfo = "\n"
		if (code == 1):
			errorInfo += "You do not have access to that command. For a list of available commands, enter HELP."
		elif (code == 2):
			errorInfo += "Incorrect usage of JOIN command. Use following format:\n    JOIN <new name>"
		elif (code == 3):
			errorInfo += "Incorrect usage of RENAME command. Use following format:\n    RENAME <new name>"
		elif (code == 4):
			errorInfo += "Incorrect usage of MESSAGE command. Use following format:\n    MESSAGE <recipient> <message content>"
		elif (code == 5):
			errorInfo += "Unrecognised command entered - check your spelling. For a list of available commands, enter HELP."
		elif (code == 6):
			errorInfo += "New name entered is unavailable - try a different name. For a list of active users, enter USERS."
		elif (code == 7):
			errorInfo += "Unrecognised name entered - check your spelling. For a list of active users, enter USERS."
		else:
			return

		self.sendToSocket(userRef, errorInfo)



def error(code):
	"""
	Sends a server error message to the user.

	code: The error code.
	"""
	if (code == 1):
		print("Incorrect usage of server. Use following format:\n    $ python3 " + str(sys.argv[0]) + " <ip address> <port>")
	elif (code == 2):
		print("IP address or port couldn't be found.")
	sys.exit()


# Ensures that IP address and port are passed in
if (len(sys.argv) != 3):
	error(1)

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create the server
server = Server()

# Start server
try:
	server.start(ip, port)
except:
	error(2)
