import logging
from Static.models import Version
import Static.statichelper


"""
This file will handle all routed methods managing static data
All methods must follow the following standards:

Inputs - they will all take in only one input: the JSON data
    
Outputs - they will pass back a formatted JSON response object
    which will detail the success or failure of the command
    as well as any other necessary information regarding the command.
"""
def getAllStaticData(data):
	#TODO Determine if user needs other version's static data

	error_list = []

	# Get the most current version's info
	version = Version.objects.latest('pk')
	ver_id = version.id
	version_name = version.name

	# Get all of the actions
	logging.debug("Loading Action data...")
	actions = Static.statichelper.getActionData(ver_id)
	if actions == None or len(actions) == 0:
		error_list.append("Actions")

	# Get all of the classes
	logging.debug("Loading Class data...")
	classes = Static.statichelper.getClassData(ver_id)
	if classes == None or len(classes) == 0:
		error_list.append("Classes")

	# Get all of the Hero Abilities
	logging.debug("Loading Hero Ability data...")
	hero_abil = Static.statichelper.getHeroAbilData(ver_id)
	if hero_abil == None or len(hero_abil) == 0:
		error_list.append("Hero_Abils")

	# Get all of the Leaders
	logging.debug("Loading Leader data...")
	leaders = Static.statichelper.getLeaderData(ver_id)
	if leaders == None or len(leaders) == 0:
		error_list.append("Leaders")

	# Get all of the maps
	logging.debug("Loading Map data...")
	maps = Static.statichelper.getMapData(ver_id)
	if maps == None or len(maps) == 0:
		error_list.append("Maps")

	# Get all of the perks
	logging.debug("Loading Perk data...")
	perks = Static.statichelper.getPerkData(ver_id)
	if perks == None or len(perks) == 0:
		error_list.append("Perks")

	# Get all of the stat information
	logging.debug("Loading Stat data...")
	stats = Static.statichelper.getStatData(ver_id)
	if stats == None or len(stats) == 0:
		error_list.append("Stats")

	# Get all of the terrain information
	logging.debug("Loading Terrain data...")
	terrain = Static.statichelper.getTerrainData(ver_id)
	if terrain == None or len(terrain) == 0:
		error_list.append("Terrain")

	if len(error_list) == 0:
		# Get all of the terrain info
		response = {"Success": True, 
					"Version": version_name,
					"Actions": actions,
					"Classes": classes,
			 	 "Hero_Abils": hero_abil,
					"Leaders": leaders,
					"Maps"   : maps,
					"Perks"  : perks,
					"Stats"  : stats,
					"Terrain": terrain}
	else:
		error = "The following tables could not be loaded: "
		for err in error_list:
			error += err + ", "
		error = error.strip(" ").strip(",")
		response = {"Success": False,
					"Error": error}

	return response