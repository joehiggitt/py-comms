#!/usr/bin/python3
import reservationapi
import configparser
from exceptions import (
	BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
	SlotUnavailableError,ReservationLimitError, ServerError,
	ServiceUnavailableError, UnexpectedError)
import time


def initAPI() -> list:
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

	return [hotel, band]

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
	NUMTRIES = 3
	services = initAPI()

	print("-- AutoWeddingPlannerXL --\n\nWelcome to our automatic client for booking your wedding needs!")

	# Gets all reserved slots for each service
	reservedSlots = []
	for service in services:
		reservedSlots.append(mySlots(service))

	print("We're just checking which slots you already have reserved (if any).")

	# Finds the common slots between all services
	commonSlots = reservedSlots[0]
	for i in range(1, len(reservedSlots)):
		commonSlots = sorted([value for value in commonSlots if value in reservedSlots[i]])

	# Finds if a potential 'best' slot has already been reserved and initilises bestSlot to that
	bestSlot = -1
	if (len(commonSlots) > 0):
		for i in range(len(commonSlots)):
			if ((bestSlot == -1) or (commonSlots[i] < bestSlot)):
				bestSlot = commonSlots[i]
	# Otherwise sets to -1 (indicating not set) and releases all currently reserved slots
	else:
		releaseAllSlots(services)

	# Attempts to find better reservation NUMTRIES times
	for _ in range(NUMTRIES):
		print("\nWe're going to have a quick look for which slots are available for the band and hotel.")

		# Gets all available slots for each service
		slots = []
		for service in services:
			slots.append(allSlots(service))

		# Finds the common slots between all services
		commonSlots = slots[0]
		for i in range(1, len(slots)):
			commonSlots = sorted([value for value in commonSlots if value in slots[i]])

		print("\nWe've identified the following slots which are available for both the band and hotel:")
		print(formatResponse(commonSlots))

		# Attempts to reserve 'best' slot
		for i in range(len(commonSlots)):
			slot = commonSlots[i]

			# Reserves current earliest slot at given service
			isReserved = []
			for service in services:
				isReserved.append(reserveSlot(service, slot))

			# If can't reserved slot, releases all other reserved slots with current index
			if False in isReserved:
				for k in range(len(isReserved)):
					if (isReserved[k] == False):
						releaseSlot(service, slot)
				time.sleep(1)
				continue

			# Exits as soon as same slots have been reserved for all services
			break

		# Checks whether the slot reserved is the 'best'
		if ((bestSlot == -1) or (slot < bestSlot)):
			bestSlot = slot
			print("Slot " + str(bestSlot) + " has been successfuly reserved for both the band and hotel.")
		else:
			print("No better booking could be found on this try.")

		# Gets all reserved slots for each service
		reservedSlots = []
		for service in services:
			reservedSlots.append(mySlots(service))

		# Releases the less 'best' slot if 2 slots currently booked
		if (2 in [len(reservedSlots[i]) for i in range(len(reservedSlots))]):
			for i in range(len(reservedSlots)):
				if (len(reservedSlots[i]) == 2):
					for j in range(len(reservedSlots[i])):
						if (reservedSlots[i][j] != bestSlot):
							releaseSlot(services[i], reservedSlots[i][j])

		# Queries whether client wishes to attempt better booking
		if (i < NUMTRIES - 1):
			print("We can attempt to find you a better booking. Would you like us to do so? (y/n)")
			query = input("> ")
			if query.lower() in ["no", "n"]:
				break
			print("We will now try to find a better booking!")
			time.sleep(1)
		
	print("\nYour bookings for the band and hotel at slot " + str(bestSlot) + " have been confirmed.\nWe'd like to wish you the best for your wedding day!")


run()
