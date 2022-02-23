import time
import im


serverName = "w81310jh"  # Default server name
initMessage = "\\online"  # Default opening message, informing other user that a new user is online
readyMessage = "\\ready"
quitMessage = "\\quit"
run = True


# Establishes connection with server
def connect(serverName):
	return im.IMServerProxy("https://web.cs.manchester.ac.uk/" + serverName + "/COMP28112_ex1/IMserver.php")

# Sends a message on the server by writing a to the current user's server variable
# If the user enters \quit, then the function returns a 1 to notify the protocol to quit
def sendMessage(server, userName):
	message = input(userName + ": ")
	server[userName] = message
	if (message == quitMessage):
		return 1
	return 0

# Outputs a message received from the server by reading the current value in the other user's server variable
# If a quit message has been received, then the function returns a 1 to notify the protocol to quit
def getMessage(server, userName):
	message = getStringFromServer(server, userName)
	if (message == quitMessage):
		return 1
	print(userName + ": " + message)
	return message

# Waits 0.1s, informing the user every 100 repetitions (10 seconds)
def wait(counts):
	counts[0] += 1
	if (counts[0] == 50):
		print("Waiting for other user...")
		counts[0] = 0
		counts[1] += 1
	if (counts[1] == 5):
		counts[1] = 0
		print("You've been waiting a while, would you like to quit? (y/n)")
		query = input("> ")
		if ((query.lower() == "n") or (query == quitMessage)):
			return [-1, -1]
	time.sleep(0.1)
	return counts

# Used to simplify code, since each message from server needs this process done to it
# Returns string representation with '\n's removed of the current value stored at 'userName'
def getStringFromServer(server, userName):
	return server[userName].decode().strip()


def ChatProtocol(server, user, otherUser, initMessage, onlineFirst):
	prevMessage = readyMessage  # Used to determine if a new message has been sent
	server["\\run"] = "1"  # Used to control when chat starts/ends
	quitSent = False

	counts = [0, 0]
	while (getStringFromServer(server, otherUser) != readyMessage):
		counts = wait(counts)
		if (counts[0] == -1):
			server[userName] = quitMessage
			server["\\run"] = "0"
			quitSent = True

	# If the current user was online first, they can send the first message
	# 'quit' is used to determine whether the program is exiting
	if onlineFirst:
		quit = sendMessage(server, user)
		if quit:
			server["\\run"] == "0"

	# Main body of protocol
	# While the chat is still running, the current user waits for a message and then can respond
	while int(server["\\run"]):
		# Waits for other user to send a message
		counts = [0, 0]
		while (getStringFromServer(server, otherUser) == prevMessage):
			counts = wait(counts)
			if (counts[0] == -1):
				server[userName] = quitMessage
				server["\\run"] = "0"
				quitSent = True

		# Displays message received from other user, checking if they have requested \quit
		prevMessage = getMessage(server, otherUser)
		if (prevMessage == 1):
			server["\\run"] = "0"
			continue

		# Sends current user's next message, checking if they have requested \quit
		quit = sendMessage(server, user)
		if quit:
			server["\\run"] = "0"
			quitSent = True

	if (not quitSent):
		server.clear()  # Server cleared by last user to leave to avoid errors when using server again
		print(otherUser + " has ended the chat.")
	else:
		print("You've ended the chat.")
	print("Connection Terminated")



# Gives the option to enter a custom university username to access a different server
print("Enter the server name you want to use (press enter to use the default)")
query = input("> ")
if (query != ""):
	serverName = query

# Attempts to connect to the server
server = connect(serverName)

print("If you know you are the first user to enter the chat, then it is a good idea to clear the server log to avoid both participants waiting for the other.")
print("Would you like to clear the previous server log? (y/n)")
query = input("> ")
if (query.lower() == "y"):
	server.clear()

# Asks for a username and ensures it is unique
loop = True
while loop:
	print("Enter your username")
	userName = input("> ")
	if (userName == "\\run"):
		print("That username is reserved for internal server functions.")
		continue
	keys = server.keys()
	loop = False
	for i in range(len(keys)):
		key = keys[i].decode()
		if ((key == userName) and (getStringFromServer(server, key) == initMessage)):
			print("Your username is already in use, please select a new one.")
			loop = True
			break


# Sets the current user's status to 'initMessage' (\online)
server[userName] = initMessage

# Establishes whether the current user was online first or not
# Who ever was online first sends first message
onlineFirst = True
keys = server.keys()
for i in range(len(keys) - 1):
	key = keys[i].decode()
	if (key != userName):
		if ((getStringFromServer(server, key) == initMessage) or (getStringFromServer(server, key) == readyMessage)):
			onlineFirst == False
		else:
			del server[key]

# Waits for another user to join server
counts = [0, 0]
while (len(server.keys()) < 3):
	counts = wait(counts)
	if (counts[0] == -1):
		server[userName] = quitMessage
		run = False
		server.clear()
		print("You've ended the chat.")

if (run == True):
	# Finds other user's username
	keys = server.keys()
	for i in range(len(keys) - 1):
		key = keys[i].decode()
		if ((key != userName) and ((getStringFromServer(server, key) == initMessage) or (getStringFromServer(server, key) == readyMessage))):
			otherUserName = keys[i].decode()
			break

	print("You are talking with " + otherUserName + ".")
	server[userName] = readyMessage

	ChatProtocol(server, userName, otherUserName, initMessage, onlineFirst)
