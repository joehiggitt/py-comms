""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

import requests
import simplejson
import warnings
import time

from requests.exceptions import HTTPError
from exceptions import (
	BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
	SlotUnavailableError,ReservationLimitError)

class ReservationApi:
	def __init__(self, base_url: str, token: str, retries: int, delay: float, service: str=""):
		"""
		Create a new ReservationApi to communicate with a reservation server.

		base_url: The URL of the reservation API to communicate with
		token: The user's API token obtained from the control panel
		retries: The maximum number of attempts to make for each request
		delay: A delay to apply to each request to prevent server overload
		service: The string name of the service being interfaced
		"""
		self.base_url = base_url
		self.token    = token
		self.retries  = retries
		self.delay    = delay
		self.service  = service

	def get_service(self) -> str:
		return self.service


	def _reason(self, req: requests.Response) -> str:
		"""
		Obtains the reason associated with a response.

		req: The response object

		Returns: A string containing the reason for that response
		"""
		reason = ''

		# Try to get the JSON content, if possible, as that may contain a
		# more useful message than the status line reason
		try:
			json = req.json()
			reason = json['message']

		# A problem occurred while parsing the body - possibly no message
		# in the body (which can happen if the API really does 500,
		# rather than generating a "fake" 500), so fall back on the HTTP
		# status line reason
		except simplejson.errors.JSONDecodeError:
			if isinstance(req.reason, bytes):
				try:
					reason = req.reason.decode('utf-8')
				except UnicodeDecodeError:
					reason = req.reason.decode('iso-8859-1')
			else:
				reason = req.reason

		return reason


	def _headers(self) -> dict:
		"""
		Create the authorisation token header needed for API requests.

		Returns: A dictionary containg the header information
		"""
		return {"Authorization": "Bearer " + self.token}


	def _send_request(self, method: str, endpoint: str) -> list:
		"""
		Send a request to the reservation API and convert errors to appropriate exceptions.
	
		method: The HTTP method the request is being sent with
		endpoint: The end of the URL the request is being sent to

		Returns: A list containg the request HTTP status and the content of the response
		Raises: A HTTP-related error if one occurs
		"""
		url = self.base_url + "/reservation" + endpoint

		for i in range(self.retries):
			# Performs the request
			response = requests.request(method.upper(), url, headers=self._headers())
			# print(" status:", response.status_code)

			# Successful request
			if (response.status_code == 200):
				break

			# Client errors (4xx)
			elif ((response.status_code >= 400) and (response.status_code < 500)):
				if (response.status_code == 400):
					raise BadRequestError
				elif (response.status_code == 401):
					raise InvalidTokenError
				elif (response.status_code == 403):
					raise BadSlotError
				elif (response.status_code == 404):
					raise NotProcessedError
				elif (response.status_code == 409):
					raise SlotUnavailableError
				elif (response.status_code == 451):
					raise ReservationLimitError
				else:
					raise UnexpectedError("Unexpected 4xx error.")

			# Server errors (5xx)
			elif ((response.status_code >= 500) and (response.status_code < 600)):
				print("The server has temporarily become unavailable, we will try to process your request as soon as possible. Attempt " + str(i + 1))

			# Unexpected errors
			else:
				raise UnexpectedError("Unexpected error. You may need to restart the program.")

			time.sleep(self.delay)

		# Successful request
		if (response.status_code == 200):
			return response.json()

		# Prolonged server errors (5xx) - need raising
		elif ((response.status_code >= 500) and (response.status_code < 600)):
			if (response.status_code == 500):
				raise ServiceUnavailableError
			elif (response.status_code == 503):
				raise ServerError
			else:
				raise UnexpectedError("Persistent 5xx error.")

		# Unexpected errors
		else:
			raise UnexpectedError("Unexpected error. You may need to restart the program.")


	def get_slots_available(self) -> list:
		"""
		Obtains the list of slots currently available in the system.

		Returns: A list containing the available slots
		Raises: A HTTP-related error if one occurs
		"""
		response = self._send_request("GET", "/available")

		# Processes response into list format
		for i in range(len(response)):
			response[i] = int(response[i]["id"])
		
		return response

	def get_slots_held(self) -> list:
		"""
		Obtains the list of slots currently held by the client.

		Returns: A list containing the slots currently held by the client
		Raises: A HTTP-related error if one occurs
		"""
		response = self._send_request("GET", "")

		# Processes response into list format
		for i in range(len(response)):
			response[i] = int(response[i]["id"])

		return response

	def release_slot(self, slot_id: int) -> str:
		"""
		Releases a slot currently held by the client.

		slot_id: The ID of the slot to be released

		Returns: A message confirming that the slot has been deleted
		Raises: A HTTP-related error if one occurs
		"""
		response = self._send_request("DELETE", "/" + str(slot_id))
		response = response["message"]
		print(response)
		return response
		
	def reserve_slot(self, slot_id: int) -> int:
		"""
		Attempts to reserve a slot for the client.

		slot_id: The ID of the slot to be reserved

		Returns: The ID of the slot, confirming that it has been reserved
		Raises: A HTTP-related error if one occurs
		"""
		response = self._send_request("POST", "/" + str(slot_id))
		response = int(response["id"])
		return response
