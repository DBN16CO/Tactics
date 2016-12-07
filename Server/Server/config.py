import logging

def startup():
	"""
	Handles any necessary setup for the server including:\n
	- Setting the logging level for messages\n
	- Setting the logging format for messages\n
	"""
	# Set the logging level default
	DEFAULT_LOG_LEVEL = logging.DEBUG
	logging.basicConfig(filename="trace.log", format='[%(asctime)s %(filename)10.10s:%(lineno)3.3s] %(levelname)5.5s %(message)s', datefmt='%m/%d/%y %I:%M:%S %p', level=logging.DEBUG)