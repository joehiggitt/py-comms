#!/usr/bin/python3
import reservationapi
import configparser
from exceptions import (
	BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
	SlotUnavailableError,ReservationLimitError, ServerError,
	ServiceUnavailableError, UnexpectedError)


def initAPI() -> dict:
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
	response = None
	try:
		if (len(parameters) == 0):
			response = method()
		else:
			response = method(parameters[0])

	# Catches all HTTP errors and displays an appropriate error message
	except (BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
		SlotUnavailableError, ReservationLimitError, ServerError,
		ServiceUnavailableError) as e:
		errorAPI(e.message, e.status_code)

	return response

def errorAPI(message: str, errorCode: int=-1):
	print(message, end="")
	if (errorCode > 0):
		print(" (" + str(errorCode) + ")", end="")
	print()


def quit(services):
	print("Quitting application.")
	# releaseAllSlots(services)

def getHelp() -> str:
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

def allSlots(service) -> list:
	response = callAPIMethod(service.get_slots_available)
	if (response == None):
		return []

	return response
	
def mySlots(service) -> list:
	response = callAPIMethod(service.get_slots_held)
	if (response == None):
		return []

	return response
	
def reserveSlot(service, parameters: list) -> bool:
	try:
		slotId = int(parameters[0])		
	except (ValueError, IndexError):
		errorAPI("The slot ID provided was not valid.")
		return False

	response = callAPIMethod(service.reserve_slot, [slotId])
	if (response == None):
		return False

	isReserved = False
	if (response == slotId):
		isReserved = True

	return isReserved

def releaseSlot(service, parameters: list) -> str:
	try:
		slotId = int(parameters[0])		
	except (ValueError, IndexError):
		errorAPI("The slot ID provided was not valid.")
		return

	response = callAPIMethod(service.release_slot, [slotId])
	if (response == None):
		return

	return response

def releaseAllSlots(services):
	for service in services:
		slots = mySlots(service)
		while (len(slots) > 0):
			releaseSlot(service, [slots[0]])
			slots = mySlots(service)

def formatResponse(slots: list, num: int=10) -> str:
	text = "    "
	for i in range(len(slots)):
		text += str(slots[i])
		if (i < len(slots) - 1):
			text += ", "
		if (i % num == 9):
			text += "\n    "
	return text


def run():
	services = initAPI()

	print("-- WeddingPlannerXL --\n\nWelcome to our handy client for booking your wedding needs!")
	print(getHelp())

	while True:
		parameters = input("\n> ").split()
		print()

		try:
			command = parameters.pop(0)
		except IndexError:
			print("Desired command must be provided.")
			continue

		# Exits client
		if (command.upper() == "QUIT"):
			quit(list(services.values()))
			break

		elif (command.upper() == "HELP"):
			print(getHelp())
			continue

		try:
			service = services[parameters.pop(0).upper()]
		except IndexError:
			print("A service must be provided.")
			continue
		except KeyError:
			print("Service provided is invalid.")
			continue

		# Executes corresponding command
		if (command.upper() == "ALLSLOTS"):
			response = allSlots(service)

			if (len(response) == 0):
				print("No slots available currently.")
			else:
				print("Available Slots:")
				print(formatResponse(response))

		elif (command.upper() == "MYSLOTS"):
			response = mySlots(service)

			if (len(response) == 0):
				print("You haven't reserved any slots yet.")
			else:
				print("My Slots:")
				print(formatResponse(response))

		elif (command.upper() == "RESERVESLOT"):
			isReserved = reserveSlot(service, parameters)

			if (isReserved == False):
				print("Unfortunately, the slot couldn't be reserved.")
			else:
				print("Slot " + parameters[0] + " has been successfuly reserved.")

		elif (command.upper() == "RELEASESLOT"):
			response = releaseSlot(service, parameters)
			print(response)

		else:
			print("Command provided is invalid.")


run()
