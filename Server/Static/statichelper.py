"""
.. module:: routeunithelper
   :synopsis: Handles any router commands received from the front end which \
   			  relate specifically to units in the game

.. moduleauthor:: Drew, Brennan, and Nick

"""
import logging
from Static.models import Ability, Action, Class, Leader, Leader_Ability, Map, Perk, Stat, Unit_Stat, Terrain, Terrain_Unit_Movement, Version

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
	logging.debug("There are " + str(len(all_ver_abil)) + " objects in ability for version " + str(version.name) + ".")

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
	logging.debug("There are " + str(len(all_ver_actions)) + " objects in action for version " + str(version.name) + ".")
	action_dict = {}

	# Add each action name to the list
	for actn in all_ver_actions:
		action_dict[actn.name] = actn.description

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
	logging.debug("There are " + str(len(all_ver_classes)) + " objects in class for version " + str(version.name) + ".")

	class_dict = {}

	# Add the name and descrption to the dictionary
	for clss in all_ver_classes:
		class_dict[clss.name] = {}
		class_dict[clss.name]["Description"] = clss.description
		class_dict[clss.name]["Price"]       = clss.price

		# Add The Stat information
		class_dict[clss.name]["Stats"] = {}
		all_ver_clss_stat = Unit_Stat.objects.filter(version=version, unit=clss)
		logging.debug("There are " + str(len(all_ver_clss_stat)) + " objects in Unit_Stat for class " 
			+ str(clss.name) + " version " + str(version.name) + ".")
		for unt_stt in all_ver_clss_stat:
			class_dict[clss.name]["Stats"][unt_stt.stat.name] = unt_stt.value

		# Add The Terrain information
		class_dict[clss.name]["Terrain"] = {}
		all_ver_clss_ter_mov = Terrain_Unit_Movement.objects.filter(version=version, unit=clss)
		logging.debug("There are " + str(len(all_ver_clss_ter_mov)) + " objects in Terrain_Unit_Movement for class " 
			+ str(clss.name) + " version " + str(version.name) + ".")
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
					"Abilities":["Steal","Agility Aura"],\n
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
	logging.debug("There are " + str(len(all_ver_leader_abils)) + " objects in leader for version " + str(version.name) + ".")
	leader_dict = {}

	# For each leader object
	for ldr_abil in all_ver_leader_abils:
		# Add the leader to the dictionary if it doesn't exist, including the description
		if not ldr_abil.leader.name in leader_dict:
			leader_dict[ldr_abil.leader.name] = {}
			leader_dict[ldr_abil.leader.name]["Abilities"] = []
			leader_dict[ldr_abil.leader.name]["Description"] = ldr_abil.leader.description

		# Add the specific hero's ability
		leader_dict[ldr_abil.leader.name]["Abilities"].append(ldr_abil.ability.name)

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
	logging.debug("There are " + str(len(all_ver_maps)) + " objects in map for version " + str(version.name) + ".")
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

# Gets the perk information for the specified version
# Returns a dictionary of the following form:
# {
# 	"Extra money":{
# 		"Description":"More $$$$$!",
# 		"Tier":1,
# 	},
# 	"Strong Arrows":{
# 		"Description":"You shoot stuff, it dies faster!",
# 		"Tier":2,
# 	},
# 	"Forest Fighter":{
# 		"Description":"You can now raise a wood elf army!",
# 		"Tier":3,
# 	},
# }
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
	logging.debug("There are " + str(len(all_ver_perks)) + " objects in perk for version " + str(version.name) + ".")

	perk_dict = {}

	# Add each action name to the list
	for perk in all_ver_perks:
		perk_dict[perk.name] = {}
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
	logging.debug("There are " + str(len(all_ver_stat)) + " objects in stat for version " + str(version.name) + ".")

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
	logging.debug("There are " + str(len(all_ver_terrain)) + " objects in terrain for version " + str(version.name) + ".")
	
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
	ver_dict["Unit_Count"] = version.unit_count

	return ver_dict
