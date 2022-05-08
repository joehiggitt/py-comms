#!/usr/bin/python3

import reservationapi
import configparser
from exceptions import (
	BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
	SlotUnavailableError,ReservationLimitError)

def initAPI():
	# Load the configuration file containing the URLs and keys
	config = configparser.ConfigParser()
	config.read("api.ini")

	# Create an API object to communicate with the hotel API
	hotel = reservationapi.ReservationApi(config['hotel']['url'],
										  config['hotel']['key'],
										  int(config['global']['retries']),
										  float(config['global']['delay']))

	# Create an API object to communicate with the band API
	band = reservationapi.ReservationApi(config['band']['url'],
										 config['band']['key'],
										 int(config['global']['retries']),
										 float(config['global']['delay']))

	return hotel, band


def allSlots(service):
	try:
		response = hotel.get_slots_available()

	except BadRequestError:
		response = [400, "Bad request"]
	except InvalidTokenError:
		response = [401, "The API token was invalid or missing."]
	except BadSlotError:
		response = [403, "SlotId does not exist."]
	except NotProcessedError:
		response = [404, "The request has not been processed."]
	except SlotUnavailableError:
		response = [409, "Slot is not available."]
	except ReservationLimitError:
		response = [451, "The client already holds the maximum number of reservations."]

	return response

def mySlots(service):
	try:
		response = hotel.get_slots_held()
		
	except BadRequestError:
		response = [400, "Bad request"]
	except InvalidTokenError:
		response = [401, "The API token was invalid or missing."]
	except BadSlotError:
		response = [403, "SlotId does not exist."]
	except NotProcessedError:
		response = [404, "The request has not been processed."]
	except SlotUnavailableError:
		response = [409, "Slot is not available."]
	except ReservationLimitError:
		response = [451, "The client already holds the maximum number of reservations."]

	return response

def reserveSlot(service, parameters: list):
	try:
		slotId = int(parameters[0])
		response = service.reserve_slot(slotId)
		
	except ValueError:
		response = [000, "The slot ID provided was not valid."]
	except BadRequestError:
		response = [400, "Bad request"]
	except InvalidTokenError:
		response = [401, "The API token was invalid or missing."]
	except BadSlotError:
		response = [403, "SlotId does not exist."]
	except NotProcessedError:
		response = [404, "The request has not been processed."]
	except SlotUnavailableError:
		response = [409, "Slot is not available."]
	except ReservationLimitError:
		response = [451, "The client already holds the maximum number of reservations."]

	return response	

def releaseSlot(service, parameters: list):
	try:
		slotId = int(parameters[0])
		response = service.release_slot(slotId)
		
	except ValueError:
		response = [000, "The slot ID provided was not valid."]
	except BadRequestError:
		response = [400, "Bad request"]
	except InvalidTokenError:
		response = [401, "The API token was invalid or missing."]
	except BadSlotError:
		response = [403, "SlotId does not exist."]
	except NotProcessedError:
		response = [404, "The request has not been processed."]
	except SlotUnavailableError:
		response = [409, "Slot is not available."]
	except ReservationLimitError:
		response = [451, "The client already holds the maximum number of reservations."]

	return response	


hotel, band = initAPI()

while True:
	parameters = input("> ").split()
	try:
		command = parameters.pop(0)
	except IndexError:
		print("Desired command must be provided.")
		continue

	# Exits client
	if (command.upper() == "QUIT"):
		print("Exiting")
		break

	try:
		service = parameters.pop(0)
	except IndexError:
		print("Desired service must be required.")
		continue

	if (service.upper() == "HOTEL"):
		service = hotel
	elif (service.upper() == "BAND"):
		service = band
	else:
		print("Service provided is invalid.")
		continue

	response = []
	# Executes corresponding command
	if (command.upper() == "ALLSLOTS"):
		response = allSlots(service)

	elif (command.upper() == "MYSLOTS"):
		response = mySlots(service)

	elif (command.upper() == "RESERVESLOT"):
		response = reserveSlot(service, parameters)

	elif (command.upper() == "RELEASESLOT"):
		response = releaseSlot(service, parameters)

	else:
		print("Command provided is invalid.")

	print(response)
