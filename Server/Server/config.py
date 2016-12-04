import logging

def startup():
	#Set the logging level default
	DEFAULT_LOG_LEVEL = logging.DEBUG
	logging.basicConfig(filename="trace.log", format='[%(asctime)s %(filename)10.10s:%(lineno)3.3s] %(levelname)5.5s %(message)s', datefmt='%m/%d/%y %I:%M:%S %p', level=logging.DEBUG)