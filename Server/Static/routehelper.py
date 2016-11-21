import logging
from Static.models import Version
import Static.statichelper


"""
This file will handle all routed methods managing static data
All methods must follow the following standards:

Inputs - they will all take in only two inputs, 
    the userID (ignore if it doesn't make sense), and the JSON data
    
Outputs - they will pass back a formatted JSON response object
    which will detail the success or failure of the command
    as well as any other necessary information regarding the command.
"""
def getAllStaticData(userID, data):
	#TODO Determine if user needs other version's static data
	
	# Get most current version
	ver_id = Version.objects.latest('pk').id

	error = None
	
	# Get all of the classes
	logging.debug("Loading class data...")
	clsses = Static.statichelper.getClassData(ver_id)

	# Get all of the Leaders
	logging.debug("Loading leader data...")
	leaders = Static.statichelper.getLeaderData(ver_id)

	# Get all of the terrain information
	logging.debug("Loading terrain data...")
	terrains = Static.statichelper.getTerrainData(ver_id)

	# Get all of the terrain info
	response = {"Success": True, 
				"Classes":clsses,
				"Leaders":leaders,
				"Terrain":terrains}

	return response

	# Verify the unit was added
	if -1 > 0:
		response = {"Success": True}
	else:
		response = {"Success": False}

	return response