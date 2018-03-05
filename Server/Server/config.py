import logging
import string
import datetime

# Log Level
DEFAULT_LOG_LEVEL = logging.DEBUG

# Number of days a login token is valid
LOGIN_TOKEN_EXPIRATION = 14

# How often celery workers execute the matchmaking logic (in seconds)
GAME_QUEUE_PROCESS_INTERVAL = 5
GAME_QUEUE_LOG_NAME = 'matchmaking.log'
GAME_QUEUE_LOG_LEVEL = logging.DEBUG

# How often celery workers upload logs to google drive (in seconds)
UPLOAD_LOGS_INTERVAL = 86400

# How often celery workers process asynchronous messages from the queue (in seconds)
MESSAGE_QUEUE_INTERVAL = 10
MESSAGE_QUEUE_LOG_NAME = 'message_queue.log'
MESSAGE_QUEUE_LOG_LEVEL = logging.DEBUG

# Number of seconds until an async message expires (30 seconds)
MESSAGE_EXPIRATION = 30

# Password policy configuration
# Note: the requirements lists contain a boolean (whether or not to actively require that particular requirement) and also the valid list
PASSWORD_POLICY = {
	'Min Length': 7,
	'Max Length': 100,
	'Requirements': {
		'Lowercase': [True, list(string.ascii_lowercase)],
		'Uppercase': [False, list(string.ascii_uppercase)],
		'Number': [False, [str(num) for num in range(0, 10)]],
		'Symbol': [False, ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '?', '.', '/', '"', ',']]
	}
}

START_DATETIME = datetime.datetime.now()

def startup():
	"""
	Handles any necessary setup for the server including:\n
	- Setting the logging level for messages\n
	- Setting the logging format for messages
	"""
	# Set the logging level default
	logging.basicConfig(filename="trace.log", format='[%(asctime)s %(filename)10.10s:%(lineno)3.3s] %(levelname)5.5s %(message)s', datefmt='%m/%d/%y %I:%M:%S %p', level=DEFAULT_LOG_LEVEL)