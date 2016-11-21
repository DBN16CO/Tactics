import logging

"""
This class is used for any static untility functions that can be used
as general ways to simplify test methods
"""


def startTestLog(testName):
	logging.debug("")
	logging.debug("==========  Starting Test: " + str(testName) + " ==========")

def endTestLog(testName):
	logging.debug("========== Finishing Test: " + str(testName) + " ==========")