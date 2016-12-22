import logging
import Game.maphelper

# Log Level
DEFAULT_LOG_LEVEL = logging.DEBUG

# Number of days a login token is valid
LOGIN_TOKEN_EXPIRATION = 14

def startup():
	"""
	Handles any necessary setup for the server including:\n
	- Setting the logging level for messages\n
	- Setting the logging format for messages\n
	- Loading all of the maps into memory
	"""
	# Set the logging level default
	logging.basicConfig(filename="trace.log", format='[%(asctime)s %(filename)10.10s:%(lineno)3.3s] %(levelname)5.5s %(message)s', datefmt='%m/%d/%y %I:%M:%S %p', level=DEFAULT_LOG_LEVEL)