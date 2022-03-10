import time, sys
import im


DEFAULT_SERVER = "w81310jh"  # Default server name

# Declares the global server and user code variables
Server = 0
UserCode = 0

# Defines server and user states for the FSM
ServerStates = {"init": "0", "run": "1", "quit": "2"}
UserStates = {"init": "0", "online": "1", "ready": "2", "waiting": "3", "quit": "4"}

# Defines the names of the user slots on the server
UserCodes = ["user1", "user2"]


# Establishes connection with server, returning an error if the server name can't be found
def serverConnect(serverName):
	try:
		server = im.IMServerProxy("https://web.cs.manchester.ac.uk/" + serverName + "/COMP28112_ex1/IMserver.php")
	except:
		print("Error - " + serverName + " can't be found")
		sys.exit()

	print(serverName + " found and connected successfully")
	serverInit(server)
	return server

# Ensures the server is set up correctly for chat system, performing a reset otherwise
def serverInit(server):
	global UserCodes

	# Reset performed if the current server state is quit (meaning the server isn't currently being used)
	if (int(server["state"] == int(ServerStates["quit"]))):
		serverReset(server)

	# Reset also performed if the server is not configured correctly
	keys = server.keys()
	if ((len(keys) == 8) and (keys[0].decode() == "state")):
		j = 1
		for i in range(len(UserCodes)):
			if ((keys[j].decode() == UserCodes[i] + "state") and (keys[j + 1].decode() == UserCodes[i] + "name") and (keys[j + 2].decode() == UserCodes[i] + "message")):
				j += 3
				continue
			serverReset(server)
			return
		return
	serverReset(server)

# Allows a new user to join the server by assigning them to one of the two user slots on the server
def serverJoin(server, userName):
	global ServerStates, UserStates, UserCodes

	# Users can only join if the server isn't currently running a chat and there is a free slot
	if (Server["state"] != ServerStates["run"]):
		for i in range(len(UserCodes)):
			if ((int(Server[UserCodes[i] + "state"]) == int(UserStates["init"])) or (int(Server[UserCodes[i] + "state"]) == int(UserStates["quit"]))):
				# Assigns a user to a slot
				Server[UserCodes[i] + "state"] = UserStates["online"]
				Server[UserCodes[i] + "name"] = userName
				# print(UserCodes[i] + " => online 1")
				return UserCodes[i]
	return -1

# Resets the server and adds the necessary states
def serverReset(server):
	global ServerStates, UserStates, UserCodes
	print("Running a server reset")
	server.clear()
	server["state"] = ServerStates["init"]
	for i in range(len(UserCodes)):
		server[UserCodes[i] + "state"] = UserStates["init"]
		server[UserCodes[i] + "name"] = ""
		server[UserCodes[i] + "message"] = ""

# Propogates a quit message through the server, ending the current session and cleaning resources
def serverQuit(server):
	global ServerStates, UserStates
	for i in range(len(UserCodes)):
		server[UserCodes[i] + "state"] = UserStates["quit"]
		server[UserCodes[i] + "name"] = ""
		server[UserCodes[i] + "message"] = ""

# Used to simplify code, since each string from server requires this process to be usable
# Returns the decoded string representation with '\n's removed for the string located in the requested user indexes
def serverGetString(server, userCode, index):
	global UserCodes
	if ((userCode in UserCodes) and (index in ["state", "name", "message"])):
		return server[userCode + index].decode().strip()


# Checks the users states that a start can occur, which is where there are two online users
def checkForStart():
	global Server, ServerStates, UserStates, UserCodes
	start = False
	for i in range(len(UserCodes)):
		if (int(Server[UserCodes[i] + "state"]) == int(UserStates["online"])):
			start = True
	return start

# Checks the user states for a quit
# Returns 0 for no quit, 1 for a quit by current user and -1 for a quit by other user
def checkForQuit():
	global Server, UserStates, UserCodes, UserCode
	quit = False
	for i in range(len(UserCodes)):
		if (int(Server[UserCodes[i] + "state"]) == int(UserStates["quit"])):
			quit = True
			break
	if (quit):
		if (UserCodes[i] == UserCode):
			return 1
		return -1
	return 0


# Indicates that one user is quitting the chat, triggering the termination process
def quit():
	global Server, UserStates, UserCode
	Server[UserCode + "message"] = ""
	# print(UserCode + " => quit 2")
	Server[UserCode + "state"] = UserStates["quit"]
	Server["state"] = ServerStates["quit"]

# Sends a message on the server by writing a to the current user's assigned message index
# If the user enters \quit, then the function calls quit() to begin the termination process
def sendMessage(message):
	global Server, UserStates, UserCode
	if (message == "\\quit"):
		quit()
		return
	Server[UserCode + "message"] = message
	# print(UserCode + " => waiting 3")
	Server[UserCode + "state"] = UserStates["waiting"]
	time.sleep(0.5)

# Outputs a message received from the other user by reading the current value in that user's assigned message index
def getMessage(otherUserCode):
	global Server, UserStates, UserCode
	message = serverGetString(Server, otherUserCode, "message")
	# print(UserCode + " => ready 4")
	Server[UserCode + "state"] = UserStates["ready"]
	time.sleep(0.5)
	return message

# Waits 0.1s, informing the user every 100 repetitions (10 seconds)
# Users are given the opportunity to quit every 600 repetitions (60 seconds) to avoid an infinite wait
def wait(counts):
	global UserStates
	counts[0] += 1
	if (counts[0] == 50):
		print("Waiting for other user...")
		counts[0] = 0
		counts[1] += 1
	if (counts[1] == 6):
		counts[1] = 0
		print("You've been waiting a while, would you like to quit? (y/n)")
		query = input("> ")
		if ((query.lower() in ["y", "yes", "ok", "okay"]) or (query == "\\quit")):
			quit()
	time.sleep(0.1)
	return counts


def ChatProtocol():
	global Server, ServerStates, UserStates, UserCode, DEFAULT_SERVER

	# Gives the option to enter a custom university username to access a different server
	print("Enter the server name you want to use (press enter to use the default)")
	query = input("> ")
	serverName = DEFAULT_SERVER
	if (query != ""):
		serverName = query

	# Attempts to connect to the server
	Server = serverConnect(serverName)

	# Allows for a user to clean up the server if the server wasn't correctly cleaned after the previous chat
	print("If you know you are the first user to enter the chat, then it is a good idea to clear the server log to avoid both participants waiting for the other.")
	print("Would you like to clear the previous server log? (y/n)")
	query = input("> ")
	if (query.lower() in ["y", "yes", "ok", "okay"]):
		serverReset(Server)

	# Asks for a username
	print("Enter your username")
	userName = input("> ")

	# Attempts to join the user to the server
	UserCode = serverJoin(Server, userName)
	if (UserCode == -1):
		print("Unfortunately the chat server is currently full")
		return
	print("You've successfully joined the chat server as " + serverGetString(Server, UserCode, "name"))
	
	temp = UserCodes.copy()
	temp.remove(UserCode)
	otherUserCode = temp[0]

	# Waits for another user to join server
	counts = [0, 0]
	while ((int(Server[otherUserCode + "state"]) == int(UserStates["init"])) or (int(Server[otherUserCode + "state"]) == int(UserStates["quit"]))):
		counts = wait(counts)
		quit = checkForQuit()
		if (quit != 0):
			serverQuit(Server)
			print("You've ended the chat\nConnection Terminated")
			return

	# Determines who joined server first, and therefore sends the first message
	if (UserCode == UserCodes[0]):
		# print(UserCode + " => ready 5")
		Server[UserCode + "state"] = UserStates["ready"]
	else:
		# print(UserCode + " => waiting 6")
		Server[UserCode + "state"] = UserStates["waiting"]
	Server["state"] = ServerStates["run"]

	print("You are talking with " + serverGetString(Server, otherUserCode, "name") + ".")

	# Main body of protocol
	# While the chat is still running, the current user waits for a message and then can respond
	while (int(Server["state"]) == int(ServerStates["run"])):
		# Waits for other user to send a message, before recieving it
		if (int(Server[UserCode + "state"]) == int(UserStates["waiting"])):
			counts = [0, 0]
			while (int(Server[otherUserCode + "state"]) == int(UserStates["ready"])):
				counts = wait(counts)

				# Checks for quit
				quit = checkForQuit()
				if abs(quit):
					break

			# Checks for quit
			quit = checkForQuit()
			if abs(quit):
				break

			# Displays message received from other user, checking if they have requested a quit
			message = getMessage(otherUserCode)
			print(serverGetString(Server, otherUserCode, "name") + ": " + message)

		# Sends current user's next message, checking if they have requested \quit
		if (int(Server[UserCode + "state"]) == int(UserStates["ready"])):
			message = input(serverGetString(Server, UserCode, "name") + ": ")
			sendMessage(message)

			# Checks for quit
			quit = checkForQuit()
			if abs(quit):
				break

	# Ends chat and cleans up server
	quit = checkForQuit()
	if (quit == 1):
		print("You've ended the chat")
	elif (quit == -1):
		print(serverGetString(Server, otherUserCode, "name") + " has ended the chat")
		serverQuit(Server)
	print("Connection Terminated")



ChatProtocol()