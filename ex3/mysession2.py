#!/usr/bin/python3
import reservationapi
import configparser
from exceptions import (
	BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
	SlotUnavailableError,ReservationLimitError, ServerError,
	ServiceUnavailableError, UnexpectedError)


def initAPI():
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
		continue

	return response

def errorAPI(message: str, errorCode: int=-1):
	print(message, end="")
	if (errorCode > 0):
		print(" (" + str(errorCode) + ")", end="")
	print()


def quit(services):
	print("Quitting application.")
	# releaseAllSlots(services)

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
	NUMTRIES = 3
	
	services = initAPI()
	releaseAllSlots(services)

	print("-- AutoWeddingPlannerXL --\n\nWelcome to our automatic client for booking your wedding needs!\nWe're going to have a quick look for which slots are available for the band and hotel.")

	bestSlot = -1
	for _ in range(NUMTRIES):
		slots = []
		for service in services:
			slots.append(allSlots(service))

		commonSlots = slots[0]
		for i in range(1, len(slots)):
			commonSlots = sorted([value for value in commonSlots if value in slots[i]])

		print("\nWe've identified the following slots which are available for both the band and hotel:")
		print(formatResponse(commonSlots))

		for i in range(len(commonSlots)):
			slot = commonSlots[i]

			isReserved = []
			for service in services:
				isReserved.append(reserveSlot(service, [slot]))

			if False in isReserved:
				for k in range(len(isReserved)):
					if (isReserved[k] == False):
						releaseSlot(service, [slot])

				time.sleep(1)
				continue

			break

		if ((bestSlot == -1) or (slot < bestSlot)):
			bestSlot = slot
			print("Slot " + str(bestSlot) + " has been successfuly reserved for both the band and hotel.")
		else:
			print("No better booking could be found on this try.")

		reservedSlots = []
		for service in services:
			reservedSlots.append(mySlots(service))

		if (2 in [len(reservedSlots[i]) for i in range(len(reservedSlots))]):
			for i in range(len(reservedSlots)):
				if (len(reservedSlots[i]) == 2):
					for j in range(len(reservedSlots[i])):
						if (reservedSlots[i][j] != bestSlot):
							releaseSlot(services[i], [reservedSlots[i][j]])

		if (i < NUMTRIES - 1):
			print("We can attempt to find you a better booking. Would you like us to do so? (y/n)")
			query = input("> ")
			if query.lower() in ["no", "n"]:
				break
			print("We will now try to find a better booking!")
			time.sleep(1)
		
	print("\nYour bookings for the band and hotel at slot " + str(bestSlot) + " have been confirmed.\nWe'd like to wish you the best for your wedding day!")

run()