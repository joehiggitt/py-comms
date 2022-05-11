"""
exceptions
~~~~~~~~~~
This module contains exceptions that are thrown by the ReservationApi
when the API responds with a non-200 or 5xx error
"""

from requests.exceptions import RequestException

# 400 error
class BadRequestError(RequestException):
	"""A 400 Bad Request error occurred."""

	def __init__(self):
		self.status_code = 400
		self.message = "Bad request."
		super().__init__(self.message)

# 401 error
class InvalidTokenError(RequestException):
	"""The API token was invalid or missing."""

	def __init__(self):
		self.status_code = 401
		self.message = "The API token was invalid or missing."
		super().__init__(self.message)

# 403 error
class BadSlotError(RequestException):
	"""The requested slot does not exist."""

	def __init__(self):
		self.status_code = 403
		self.message = "The slot provided does not exist."
		super().__init__(self.message)

# 404 error
class NotProcessedError(RequestException):
	"""The request has not been processed."""

	def __init__(self):
		self.status_code = 404
		self.message = "The request you sent has not been processed."
		super().__init__(self.message)

# 409 error
class SlotUnavailableError(RequestException):
	"""The requested slot is not available."""

	def __init__(self):
		self.status_code = 409
		self.message = "The slot provided is not available."
		super().__init__(self.message)

# 451 error
class ReservationLimitError(RequestException):
	"""The client already holds the maximum number of reservations."""

	def __init__(self):
		self.status_code = 451
		self.message = "You already hold the maximum number of reservations."
		super().__init__(self.message)


# 500 error
class ServerError(RequestException):
	"""The server has encountered an unexpected internal error."""

	def __init__(self):
		self.status_code = 500
		self.message = "There was an internal server error."
		super().__init__(self.message)

# 503 error
class ServiceUnavailableError(RequestException):
	"""The service is unavailable."""

	def __init__(self):
		self.status_code = 503
		self.message = "The service is currently unavailable."
		super().__init__(self.message)


# Other errors
class UnexpectedError(RequestException):
	"""An unexpected error has occured."""

	def __init__(self, message):
		self.message = message
		super().__init__(self.message)
