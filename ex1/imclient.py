import time, sys
import im


DEFAULT_SERVER = "w81310jh"  # Default server name
ADMIN_PASSWORD = "admin"
ATTEMPTS = 5
WAIT_1 = 100
WAIT_2 = 6

# Declares the global server and user code variables
Server = 0
UserCode = 0

# Defines server and user states for the FSM
ServerStates = {"init": 0, "run": 1, "quit": 2}
UserStates = {"init": 0, "online": 1, "ready": 2, "waiting": 3, "quit": 4}

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
	if (int(server["state"]) == ServerStates["quit"]):
		serverReset(server)
		return

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

# Resets the server and adds the necessary states
def serverReset(server):
	global ServerStates, UserStates, UserCodes
	server.clear()
	server["state"] = str(ServerStates["init"])
	for i in range(len(UserCodes)):
		server[UserCodes[i] + "state"] = str(UserStates["init"])
		server[UserCodes[i] + "name"] = ""
		server[UserCodes[i] + "message"] = ""

# Allows a new user to join the server by assigning them to one of the two user slots on the server
def serverJoin(server, username):
	global ServerStates, UserStates, UserCodes

	# Users can only join if the server isn't currently running a chat and there is a free slot
	if (Server["state"] != ServerStates["run"]):
		for i in range(len(UserCodes)):
			if ((int(Server[UserCodes[i] + "state"]) == UserStates["init"]) or (int(Server[UserCodes[i] + "state"]) == UserStates["quit"])):
				# Assigns a user to a slot
				Server[UserCodes[i] + "state"] = str(UserStates["online"])
				Server[UserCodes[i] + "name"] = username
				return UserCodes[i]
	return -1

# Propogates a quit message through the server, ending the current session and cleaning resources
def serverQuit(server):
	global ServerStates, UserStates
	for i in range(len(UserCodes)):
		server[UserCodes[i] + "state"] = str(UserStates["quit"])
		server[UserCodes[i] + "name"] = ""
		server[UserCodes[i] + "message"] = ""
	Server["state"] = str(ServerStates["quit"])

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
		if (int(Server[UserCodes[i] + "state"]) == UserStates["online"]):
			start = True
	return start

# Checks the user states for a quit
# Returns 0 for no quit, 1 for a quit by current user and -1 for a quit by other user
def checkForQuit():
	global Server, UserStates, UserCodes, UserCode
	quit = False
	for i in range(len(UserCodes)):
		if (int(Server[UserCodes[i] + "state"]) == UserStates["quit"]):
			quit = True
			break
	if (quit):
		if (UserCodes[i] == UserCode):
			return 1
		return -1
	return 0


# Sends a message on the server by writing a to the current user's assigned message index
# If the user enters \quit, then the function calls quit() to begin the termination process
def sendMessage(message):
	global Server, UserStates, UserCode
	if (message == "\\quit"):
		quit()
		return
	Server[UserCode + "message"] = message
	Server[UserCode + "state"] = str(UserStates["waiting"])
	time.sleep(0.25)

# Outputs a message received from the other user by reading the current value in that user's assigned message index
def getMessage(otherUserCode):
	global Server, UserStates, UserCode
	message = serverGetString(Server, otherUserCode, "message")
	Server[UserCode + "state"] = str(UserStates["ready"])
	time.sleep(0.25)
	return message


# Indicates that one user is quitting the chat, triggering the termination process
def quit():
	global Server, UserStates, UserCode
	Server[UserCode + "message"] = ""
	Server[UserCode + "state"] = str(UserStates["quit"])

# Waits 0.1s, informing the user every 100 repetitions (10 seconds)
# Users are given the opportunity to quit every 600 repetitions (60 seconds) to avoid an infinite wait
def wait(counts):
	global UserStates, WAIT_1, WAIT_2
	counts[0] += 1
	if (counts[0] == WAIT_1):
		print("Waiting for other user...")
		counts[0] = 0
		counts[1] += 1
	if (counts[1] == WAIT_2):
		counts[1] = 0
		print("You've been waiting a while, would you like to quit? (y/n)")
		query = input("> ")
		if ((query.lower() in ["y", "yes", "ok", "okay"]) or (query == "\\quit")):
			quit()
	time.sleep(0.1)
	return counts


def ChatProtocol():
	global Server, ServerStates, UserStates, UserCode, DEFAULT_SERVER, ADMIN_PASSWORD, ATTEMPTS

	# Gives the option to enter a custom university username to access a different server
	print("Enter the server name you want to use (press enter to use the default)")
	query = input("> ")
	serverName = DEFAULT_SERVER
	if (query != ""):
		serverName = query

	# Attempts to connect to the server
	Server = serverConnect(serverName)

	# Allows for a user to clean up the server if the server wasn't correctly cleaned after the previous chat
	if (int(Server["state"]) != ServerStates["init"]):
		print("\nWould you like to clear the previous server log? (y/n)\nIt is likely that a chat is ongoing, and doing this would cause that chat to be terminated unexpectedly")
		query = input("> ")
		if (query.lower() in ["y", "yes", "ok", "okay"]):
			accessGranted = False

			# Gives the user a number of attempts to input the correct password
			for i in range(ATTEMPTS):
				print("This is a restricted operation - please enter the admin password")
				password = input("> ")
				if (password == ADMIN_PASSWORD):
					accessGranted = True
					break
				if (i + 1 == ATTEMPTS):
					print("The password you entered is incorrect, you have run out of attempts - the server won't be cleaned")
				elif (i + 2 == ATTEMPTS):
					print("The password you entered is incorrect, you have 1 attempt left")
				else:
					print("The password you entered is incorrect, you have " + str(ATTEMPTS - (i + 1)) + " attempts left")
			if accessGranted:
				print("Password accepted, the server has been cleaned")
				serverReset(Server)

	# Asks for a username
	print("\nEnter your username")
	userName = input("> ")

	# Attempts to join the user to the server
	UserCode = serverJoin(Server, userName)
	if (UserCode == -1):
		print("Unfortunately the chat server is currently full")
		return
	print("You've successfully joined the chat server as " + serverGetString(Server, UserCode, "name") + ", finding the other user...")
	
	# Gets other user's code
	temp = UserCodes.copy()
	temp.remove(UserCode)
	otherUserCode = temp[0]

	run = True
	while (run == True):
		# Waits for another user to join server
		counts = [0, 0]
		while ((int(Server[otherUserCode + "state"]) == UserStates["init"]) or (int(Server[otherUserCode + "state"]) == UserStates["quit"])):
			counts = wait(counts)
			quit = checkForQuit()
			if (quit != 0):
				serverQuit(Server)
				print("You've ended the chat\nConnection Terminated")
				return

		# Determines who joined server first, and therefore sends the first message
		if (UserCode == UserCodes[0]):
			Server[UserCode + "state"] = str(UserStates["ready"])
		else:
			Server[UserCode + "state"] = str(UserStates["waiting"])
		Server["state"] = str(ServerStates["run"])

		print("\nYou are talking with " + serverGetString(Server, otherUserCode, "name") + ".\n")

		# Main body of protocol
		# While the chat is still running, the current user waits for a message and then can respond
		while (int(Server["state"]) == ServerStates["run"]):
			# Waits for other user to send a message, before recieving it
			if (int(Server[UserCode + "state"]) == UserStates["waiting"]):
				counts = [0, 0]
				while (int(Server[otherUserCode + "state"]) == UserStates["ready"]):
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
			if (int(Server[UserCode + "state"]) == UserStates["ready"]):
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
			run = False
		elif (quit == -1):
			print(serverGetString(Server, otherUserCode, "name") + " has ended the chat, would you like to quit? (y/n)")
			query = input("> ")
			if ((query.lower() in ["y", "yes", "ok", "okay"]) or (query == "\\quit")):
				serverQuit(Server)
				run = False
			else:
				Server[otherUserCode + "state"] = str(UserStates["init"])
				Server["state"] = str(ServerStates["init"])
				print("Waiting for a new user...")

		if not run:
			print("Connection Terminated")


ChatProtocol()