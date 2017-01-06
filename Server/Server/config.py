import logging
import string

# Log Level
DEFAULT_LOG_LEVEL = logging.DEBUG

# Number of days a login token is valid
LOGIN_TOKEN_EXPIRATION = 14

# How often celery workers execute the matchmaking logic (in seconds)
GAME_QUEUE_PROCESS_INTERVAL = 5

PASSWORD_POLICY = {
	'Min Length': 7,
	'Max Length': 100,
	'Requirements': {
		'Lowercase': [True, list(string.ascii_lowercase)],
		'Uppercase': [True, list(string.ascii_uppercase)],
		'Number': [True, [str(num) for num in range(0, 10)]],
		'Symbol': [False, ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '?', '.', '/', '"', ',']]
	}
}

def startup():
	"""
	Handles any necessary setup for the server including:\n
	- Setting the logging level for messages\n
	- Setting the logging format for messages
	"""
	# Set the logging level default
	logging.basicConfig(filename="trace.log", format='[%(asctime)s %(filename)10.10s:%(lineno)3.3s] %(levelname)5.5s %(message)s', datefmt='%m/%d/%y %I:%M:%S %p', level=DEFAULT_LOG_LEVEL)