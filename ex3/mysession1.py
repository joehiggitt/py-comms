#!/usr/bin/python3
import reservationapi
import configparser
from exceptions import (
	BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
	SlotUnavailableError,ReservationLimitError, ServerError,
	ServiceUnavailableError, UnexpectedError)
import time


def initAPI() -> dict:
	"""
	Initialises the ReservationAPI objects and returns a reference to them.

	Returns: Dictionary with references to 'HOTEL' and 'BAND' objects
	"""
	# Load the configuration file containing the URLs and keys
	config = configparser.ConfigParser()
	config.read("api.ini")

	# Create an API object to communicate with the hotel API
	hotel = reservationapi.ReservationApi(config['hotel']['url'],
										  config['hotel']['key'],
										  int(config['global']['retries']),
										  float(config['global']['delay']),
										  "hotel")

	# Create an API object to communicate with the band API
	band = reservationapi.ReservationApi(config['band']['url'],
										 config['band']['key'],
										 int(config['global']['retries']),
										 float(config['global']['delay']),
										 "band")

	return {"HOTEL": hotel, "BAND": band}

def callAPIMethod(method, parameters: list=[]):
	"""
	Calls a ReservationAPI method passed in to the function, passing in additional parameters if required.
	Catches any client-side errors and reports them.

	method: An ReservationAPI method
	parameters: A list of parameters to pass into method

	Returns: The response from the method call
	"""
	response = None

	# Attempts to call the API method
	try:
		if (len(parameters) == 0):
			response = method()
		else:
			response = method(parameters[0])

	# Catches all HTTP errors and displays an appropriate error message
	except (BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
		SlotUnavailableError, ReservationLimitError, ServerError,
		ServiceUnavailableError) as e:
		print(errorAPI(e.message, e.status_code))

	return response

def errorAPI(message: str, errorCode: int=-1) -> str:
	"""
	Generates an error message.

	message: The content of the error
	errorCode: The HTTP error code (Optional)

	Returns: A string representation of the error
	"""
	errorInfo = message
	if (errorCode > 0):
		errorInfo += " (" + str(errorCode) + ")"
	return errorInfo + "\n"
	

def getHelp() -> str:
	"""
	Generates help information.

	Returns: A string representation of the help information
	"""
	helpInfo = "Available Commands:"
	helpInfo += "\n    HELP                            - Get list of available commands"
	helpInfo += "\n    ALLSLOTS <service>              - Returns a list of available slots from that service"
	helpInfo += "\n    MYSLOTS <service>               - Returns a list of slots you've reserved from that service"
	helpInfo += "\n    RESERVESLOT <service> <slot id> - Reserves a slot from that service that is available (Max: 2 per service)"
	helpInfo += "\n    RELEASESLOT <service> <slot id> - Releases a slot from that service that you've reserved"
	helpInfo += "\n    QUIT                            - Quit the chat server"
	helpInfo += "\n<service> must be either HOTEL or BAND"
	helpInfo += "\n<slot id> must be a valid slot between 1 and 500"
	return helpInfo

def allSlots(service: reservationapi.ReservationApi) -> list:
	"""
	Gets all the available slots from the given service.

	service: The service being called (ReservationAPI object)

	Returns: A list of all available slots
	"""
	response = callAPIMethod(service.get_slots_available)
	if (response == None):
		return []

	return response
	
def mySlots(service) -> list:
	"""
	Gets all the slots currently reserved by this client on the given service.

	service: The service being called (hotel or band object)

	Returns: A list of current-client reserved slots
	"""
	response = callAPIMethod(service.get_slots_held)
	if (response == None):
		return []

	return response
	
def reserveSlot(service, slotId: int) -> bool:
	"""
	Reserves a slot on the given service.

	service: The service being called (hotel or band object)
	slotId: The slot ID

	Returns: True if slot reserved, false otherwise
	"""
	response = callAPIMethod(service.reserve_slot, [slotId])
	if (response == None):
		return False

	# Checks whether the reservation was successful
	isReserved = False
	if (response == slotId):
		isReserved = True

	return isReserved

def releaseSlot(service, slotId: int) -> str:
	"""
	Releases a slot on the given service that the current client already has reserved.

	service: The service being called (hotel or band object)
	slotId: The slot ID

	Returns: A string confirmation from the server
	"""
	response = callAPIMethod(service.release_slot, [slotId])
	if (response == None):
		return

	return response

def releaseAllSlots(services: list):
	"""
	Releases all slot son the given service that the current client already has reserved.

	services: A list containing all the services (ReservationAPI objects)
	parameters: A list containing the slot ID in the first index position
	"""
	for service in services:
		slots = mySlots(service)

		# Releases all slots found for the current service
		for i in range(len(slots)):
			releaseSlot(service, slots[i])
			time.sleep(1)

def formatResponse(slots: list, num: int=10) -> str:
	"""
	Generates a string representation of a slot list.

	slots: A list of slot IDs
	num: Number of items per line

	Returns: A string representation of the slots
	"""
	text = "    "
	for i in range(len(slots)):
		text += str(slots[i])
		if (i < len(slots) - 1):
			text += ", "
		if (i % num == 9):
			text += "\n    "
	return text


def run():
	"""
	Runs the client.
	"""
	services = initAPI()

	print("-- WeddingPlannerXL --\n\nWelcome to our handy client for booking your wedding needs!")
	print(getHelp())

	# Main program loop
	while True:
		# Gets next command input
		parameters = input("\n> ").split()
		print()

		# Attempts to parse command
		try:
			command = parameters.pop(0)
		except IndexError:
			print("Desired command must be provided.")
			continue

		# Commands requiring no parameters
		if (command.upper() == "QUIT"):
			# Performs quit procedure
			print("Quitting application.")
			# releaseAllSlots(list(services.values()))
			return

		elif (command.upper() == "HELP"):
			text = getHelp()

		else:
			# Attempts to parse service
			try:
				service = services[parameters.pop(0).upper()]
			except IndexError:
				print("A service must be provided.")
				continue
			except KeyError:
				print("Service provided is invalid.")
				continue

			# Commands requiring service
			if (command.upper() == "ALLSLOTS"):
				response = allSlots(service)

				if (len(response) == 0):
					text = "No slots available currently."
				else:
					text = "Available Slots:\n" + formatResponse(response)

			elif (command.upper() == "MYSLOTS"):
				response = mySlots(service)

				if (len(response) == 0):
					text = "You haven't reserved any slots yet."
				else:
					text = "My Slots:\n" + formatResponse(response)

			else:
				try:
					slotId = int(parameters[0])		
				except (ValueError, IndexError):
					print("The slot ID provided was not valid.")
					continue

				# Commands requiring service and slot ID
				if (command.upper() == "RESERVESLOT"):
					isReserved = reserveSlot(service, slotId)

					if (isReserved == False):
						text = "Unfortunately, the slot couldn't be reserved."
					else:
						text = "Slot " + str(slotId) + " has been successfuly reserved."

				elif (command.upper() == "RELEASESLOT"):
					text = releaseSlot(service, slotId)

				else:
					print("Command provided is invalid.")
					continue

		print(text)

run()
