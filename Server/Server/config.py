import logging

def startup():
	#Set the logging level default
	DEFAULT_LOG_LEVEL = logging.DEBUG
	logging.basicConfig(filename="trace.log", format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)