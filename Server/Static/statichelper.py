"""
.. module:: routeunithelper
   :synopsis: Handles any router commands received from the front end which
   			  relate specifically to units in the game

.. moduleauthor:: Drew, Brennan, and Nick

"""
import copy, logging
from Static.models import Version, Ability, Action, Class, Class_Action, Leader_Ability, Map, Perk, Stat, Unit_Stat, Terrain, Terrain_Unit_Movement

static_data = {}
static_data_il = {}

def getAllStaticData(version=None):
	"""
	Gets the static data object by loading all static data from the database.
	If the static data already exists, simply pull out the part for the version requested.

	:rtype: Dictionary
	:return: An object loaded with all static data, in simplified version:\n
			{\n
				"Version"   : <getVersionData results>,\n
				"Abilities" : <getAbilityData results>,\n
				"Actions"   : <getActionData results>,\n
				"Classes"   : <getClassData results>,\n
				"Leaders"   : <getLeaderData results>,\n
				"Maps"      : <getMapData results>,\n
				"Perks"     : <getPerkData results>,\n
				"Stats"     : <getStatData results>,\n
				"Terrain"   : <getTerrainData results>\n
			}
	"""
	if version == None:
		version = Version.objects.latest('pk')

	if not version.name in static_data:
		static_data[version.name] = loadAllStaticData(version)

		if "Error" in static_data[version.name]:
			logging.info("Reloading Static data failed.")
			return static_data.pop(version.name, None)

	return static_data[version.name]

def getAllStaticDataIL(version=None):
	"""
	Gets the static data object by loading all static data from the database.
	If the static data already exists, simply pull out the part for the version requested.
	Different from 'getAllStaticData' in that all of the model objects have been removed
	from the dictionary.

	:rtype: Dictionary
	:return: An object loaded with all static data, in simplified version:\n
			{\n
				"Version"   : <getVersionData results>,\n
				"Abilities" : <getAbilityData results>,\n
				"Actions"   : <getActionData results>,\n
				"Classes"   : <getClassData results>,\n
				"Leaders"   : <getLeaderData results>,\n
				"Maps"      : <getMapData results>,\n
				"Perks"     : <getPerkData results>,\n
				"Stats"     : <getStatData results>,\n
				"Terrain"   : <getTerrainData results>\n
			}
	"""
	if version == None:
		version = Version.objects.latest('pk')

	if not version.name in static_data_il:
		response = copy.deepcopy(getAllStaticData(version))

		if "Error" in response:
			logging.info("Reloading Static data failed.")
			return response

		for actn in response["Actions"]:
			response["Actions"][actn].pop("Object", None)

		for clss in response["Classes"]:
			response["Classes"][clss].pop("Object", None)

		for perk in response["Perks"]:
			response["Perks"][perk].pop("Object", None)

		for leader in response["Leaders"]:
			response["Leaders"][leader]["Abilities"] = response["Leaders"][leader]["Abilities"].keys()

		static_data_il[version.name] = response

	return static_data_il[version.name]

def loadAllStaticData(version=None):
	"""
	Loads all static data by calling all of the remaining functions of this class

	:type version: Version
	:param version: The version for which the data needs to be loaded

	:rtype: Dictionary
	:return: An object loaded with all static data, in simplified version:\n
			{\n
				"Version"   : <getVersionData results>,\n
				"Abilities" : <getAbilityData results>,\n
				"Actions"   : <getActionData results>,\n
				"Classes"   : <getClassData results>,\n
				"Leaders"   : <getLeaderData results>,\n
				"Maps"      : <getMapData results>,\n
				"Perks"     : <getPerkData results>,\n
				"Stats"     : <getStatData results>,\n
				"Terrain"   : <getTerrainData results>\n
			}
	"""
	if version == None:
		version = Version.objects.latest('pk')

	error_list = []

	# Get the selected version's info, or most current if none provided
	logging.debug("Loading Version data...")
	version_info = getVersionData(version)
	logging.debug("Using latest version: " + str(version.name))

	# Get all of the Abilities
	logging.debug("Loading Ability data...")
	abilities = getAbilityData(version)
	if abilities == None or len(abilities) == 0:
		error_list.append("Abilities")

	# Get all of the actions
	logging.debug("Loading Action data...")
	actions = getActionData(version)
	if actions == None or len(actions) == 0:
		error_list.append("Actions")

	# Get all of the classes
	logging.debug("Loading Class data...")
	classes = getClassData(version)
	if classes == None or len(classes) == 0:
		error_list.append("Classes")

	# Get all of the Leaders
	logging.debug("Loading Leader data...")
	leaders = getLeaderData(version)
	if leaders == None or len(leaders) == 0:
		error_list.append("Leaders")

	# Get all of the maps
	logging.debug("Loading Map data...")
	maps = getMapData(version)
	if maps == None or len(maps) == 0:
		error_list.append("Maps")

	# Get all of the perks
	logging.debug("Loading Perk data...")
	perks = getPerkData(version)
	if perks == None or len(perks) == 0:
		error_list.append("Perks")

	# Get all of the stat information
	logging.debug("Loading Stat data...")
	stats = getStatData(version)
	if stats == None or len(stats) == 0:
		error_list.append("Stats")

	# Get all of the terrain information
	logging.debug("Loading Terrain data...")
	terrain = getTerrainData(version)
	if terrain == None or len(terrain) == 0:
		error_list.append("Terrain")

	if len(error_list) == 0:
		# Get all of the terrain info
		data = {
			"Version"  : version_info,
			"Abilities": abilities,
			"Actions"  : actions,
			"Classes"  : classes,
			"Leaders"  : leaders,
			"Maps"     : maps,
			"Perks"    : perks,
			"Stats"    : stats,
			"Terrain"  : terrain
		}
	else:
		error = "The following tables could not be loaded: "
		for err in error_list:
			error += err + ", "
		error = error.strip(" ").strip(",")
		return {"Error": error}

	return data

def getAbilityData(version):
	"""
	Gets the ability information for the specified version

	:type version: Version
	:param version: The version of ability data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"Steal":"Steals stuff from that other guy.. tricky",\n
				"Extra Range":"Provides nearby ranged units an additional attack range"\n
			 }\n
	"""
	# Get all the classes for that version
	all_ver_abil = Ability.objects.filter(version=version)
	logging.debug("There are {0} objects in ability for version {1}.".format(len(all_ver_abil), version.name))

	abil_dict = {}

	# Add each hero ability name to the dictionary
	for hb in all_ver_abil:
		abil_dict[hb.name] = hb.description

	return abil_dict

def getActionData(version):
	"""
	Gets the action information for the specified version

	:type version: Version
	:param version: The version of action data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"Attack":"Attacks a unit.",\n
			 	"Heal":"Heals a unit.",\n
			 	\n"Wait":"Does nothing."\n
			 }
	"""
	# Gets all action objects for specified version
	all_ver_actions = Action.objects.filter(version=version)
	logging.debug("There are {0} objects in action for version {1}.".format(len(all_ver_actions), version.name))
	action_dict = {}

	# Add each action name to the list
	for actn in all_ver_actions:
		action_dict[actn.name] = {}
		action_dict[actn.name]["Object"]      = actn
		action_dict[actn.name]["Description"] = actn.description

	return action_dict

def getClassData(version):
	"""
	Gets the class information for the specified version

	:type version: Version
	:param version: The version of class data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"Archer":    {\n
			 		"AttackType":<Magical, Physical, Heal>,\n
					"Description":"Ranged unit with low armor.  Good at defeating Fliers.",\n
					"Stats": {\n
						"HP":10.0, "Move": 6.0, "Agility": 8.5, "Intelligence": 4.0, "Strength": 7.0, "Luck": 7.0,\n
					},\n
					"Terrain": {\n
						"G": 1.0, "F": 2.0, "W":99.0, "M": 4.0, "R": 1.0,\n
					},\n
				},\n
				"Mage": {\n
					...\n
				},\n
			 }\n
	"""
	# Gets all class objects for specified version
	all_ver_classes = Class.objects.filter(version=version)
	logging.debug("There are {0} objects in class for version {1}.".format(len(all_ver_classes), version.name))

	class_dict = {}

	# Add the name and descrption to the dictionary
	for clss in all_ver_classes:
		class_dict[clss.name] = {}
		class_dict[clss.name]["Object"]      = clss
		class_dict[clss.name]["AttackType"]  = clss.attack_type
		class_dict[clss.name]["Description"] = clss.description
		class_dict[clss.name]["Price"]       = clss.price

		# Add the Action information
		class_dict[clss.name]["Actions"] = {}
		for action in Action.objects.filter(version=version):
			if Class_Action.objects.filter(clss=clss, action=action, version=version).first() == None:
				class_dict[clss.name]["Actions"][action.name] = False
			else:
				class_dict[clss.name]["Actions"][action.name] = True

		# Add The Stat information
		class_dict[clss.name]["Stats"] = {}
		all_ver_clss_stat = Unit_Stat.objects.filter(version=version, unit=clss)
		logging.debug("There are {0} objects in Unit_Stat for class {1} version {2}.".format(len(all_ver_clss_stat), clss.name, version.name))
		for unt_stt in all_ver_clss_stat:
			class_dict[clss.name]["Stats"][unt_stt.stat.name] = unt_stt.value

		# Add The Terrain information
		class_dict[clss.name]["Terrain"] = {}
		all_ver_clss_ter_mov = Terrain_Unit_Movement.objects.filter(version=version, unit=clss)
		logging.debug("There are {0} objects in Terrain_Unit_Movement for class	{1} version {2}.".format(len(all_ver_clss_ter_mov), clss.name, version.name))
		for unt_ter_mov in all_ver_clss_ter_mov:
			class_dict[clss.name]["Terrain"][unt_ter_mov.terrain.shortname] = unt_ter_mov.move

	return class_dict

def getLeaderData(version):
	"""
	Gets the leader information for the specified version

	:type version: Version
	:param version: The version of leader data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"Assassin":{\n
					"Abilities":{"Steal":<steal obj>,"Agility Aura":<agility obj>},\n
					"Descripton":"He kills things real good.".\n
				}\n
				"General":{\n
					"Abilities":["Defense Aura"],\n
					"Description":"He's good at not taking damage",\n
				}\n
			 }\n
	"""
	# Get all the leader objects for the specified version
	all_ver_leader_abils = Leader_Ability.objects.filter(version=version)
	logging.debug("There are {0} objects in leader for version {1}.".format(len(all_ver_leader_abils), version.name))
	leader_dict = {}

	# For each leader object
	for ldr_abil in all_ver_leader_abils:
		# Add the leader to the dictionary if it doesn't exist, including the description
		if not ldr_abil.leader.name in leader_dict:
			leader_dict[ldr_abil.leader.name] = {}
			leader_dict[ldr_abil.leader.name]["Abilities"] = {}
			leader_dict[ldr_abil.leader.name]["Description"] = ldr_abil.leader.description

		# Add the specific hero's ability
		leader_dict[ldr_abil.leader.name]["Abilities"][ldr_abil.ability.name] = ldr_abil

	return leader_dict

def getMapData(version):
	"""
	Gets the map information for the specified version

	:type version: Version
	:param version: The version of map data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"Map 1 Name": "0,1 1,1 1,1 0,1n0,2 0,2 0,1 0,1n0,2 0,2 0,1 0,1n0,1 1,1 1,1 0,1",\n
				"All Grass":  "0,1 1,1 0,1 0,1n0,1 1,1 0,1 0,1n0,1 1,1 0,1 0,1n0,1 1,1 0,1 0,1",\n
			 }\n
			 Note: For the map data, there are n-delimited lines, for each line,
			 there are space-delimited tokens, for each token, there are comma-delimited fields,
			 the first being whether or not a unit can be initially placed there
			 the second being the shortname of the terrain type.
			 These shornamess will match the key data sent in the terrain object
	"""
	# Get all map names and file paths for that version
	all_ver_maps = Map.objects.filter(version=version)
	logging.debug("There are {0} objects in map for version {1}.".format(len(all_ver_maps), version.name))
	map_dict = {}

	# For each map object in the database
	for mp in all_ver_maps:
		# Open each map file for processing
		with open(mp.file_path) as map_file:
			map_as_list = map_file.readlines()

		# Create a string representation of the map file
		map_string = ""
		for map_line in map_as_list:
			map_line_strip = map_line.strip()
			map_string += map_line_strip + "n"

		# Add the map text to the dictionary
		map_dict[mp.name] = map_string

	return map_dict

def getPerkData(version):
	"""
	Gets the perk information for the specified version

	:type version: Version
	:param version: The version of perk data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"Extra money":{\n
					"Description":"More $$$$$!",\n
					"Tier":1,\n
				},\n
				"Strong Arrows":{\n
					"Description":"You shoot stuff, it dies faster!",\n
					"Tier":2,\n
				},\n
				"Forest Fighter":{\n
					"Description":"You can now raise a wood elf army!",\n
					"Tier":3,\n
				},\n
			 }\n
	"""
	# Get all the perk objects for the current version
	all_ver_perks = Perk.objects.filter(version=version)
	logging.debug("There are {0} objects in perk for version {1}.".format(len(all_ver_perks), version.name))

	perk_dict = {}

	# Add each action name to the list
	for perk in all_ver_perks:
		perk_dict[perk.name] = {}
		perk_dict[perk.name]["Object"] = perk
		perk_dict[perk.name]["Description"] = perk.description
		perk_dict[perk.name]["Tier"] = perk.tier

	return perk_dict

def getStatData(version):
	"""
	Gets the stat information for the specified version

	:type version: Version
	:param version: The version of stat data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"HP":{\n
					"Description":"Health points, duh"\n
				},\n
				"Move":{\n
					"Description":"How far you can move.",\n
				},\n
			 }
	"""
	# Get all the stats for that version
	all_ver_stat = Stat.objects.filter(version=version)
	logging.debug("There are {0} objects in stat for version {1}.".format(len(all_ver_stat), version.name))

	stat_dict = {}

	# Add all the stats
	for stt in all_ver_stat:

		# Create a dictionary entry with the shortname as the key and populate it
		stat_dict[stt.name] = {}
		stat_dict[stt.name]["Description"] = stt.description

	return stat_dict

def getTerrainData(version):
	"""
	Gets the terrain information for the specified version

	:type version: Version
	:param version: The version of terrain data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"G":{ // The shortname in the table\n
					"Description":"Grasssssy."\n
					"DisplayName":"Grass"\n
				},\n
				"F":{\n
					"Description":"Trees! Trees everywhere!",\n
					"DisplayName":"Forest"\n
				},\n
			 }
	"""
	# Get all the terrains for that version
	all_ver_terrain = Terrain.objects.filter(version=version)
	logging.debug("There are {0} objects in terrain for version {1}.".format(len(all_ver_terrain), version.name))

	terrain_dict = {}

	# Add all the terrains
	for ter in all_ver_terrain:

		# Create a dictionary entry with the shortname as the key and populate it
		terrain_dict[ter.shortname] = {}
		terrain_dict[ter.shortname]["Description"] = ter.description
		terrain_dict[ter.shortname]["DisplayName"] = ter.name

	return terrain_dict

def getVersionData(version):
	"""
	Gets the terrain information for the specified version

	:type version: Version
	:param version: The version of terrain data requested

	:rtype: Dictionary
	:return: Returns a dictionary of the following form:\n
			 {\n
			 	"Name":"1.0",\n
				"Price_Max":1000,\n
				"Unit_Count":8,\n
			 }
	"""
	ver_dict = {}

	ver_dict["Name"]       = version.name
	ver_dict["Price_Max"]  = version.price_max
	ver_dict["Unit_Min"] = version.unit_min
	ver_dict["Unit_Max"] = version.unit_max

	return ver_dict
