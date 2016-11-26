import logging
from Static.models import Action, Class, Hero_Ability, Leader, Map, Perk, Stat, Terrain, Version

# Gets the action information for the specified version
# Returns a dictionary of the following form:
# {
# 	"Attack":"Attacks a unit.", 
# 	"Heal":"Heals a unit.", 
# 	"Wait":"Does nothing."
# }
def getActionData(ver_id):
	# Gets all action objects for specified version
	all_ver_actions = Action.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_actions)) + " objects in action for version " + str(ver_id) + ".")
	action_dict = {}

	# Add each action name to the list
	for actn in all_ver_actions:
		action_dict[actn.name] = actn.description

	return action_dict

# Gets the class information for the specified version
# Returns an array of the following form:
# {
# 	"Archer":"An archer guy.",
# 	"Mage":"A ranged mage caster man.",
# 	"Flier":"It's a bird, it's a plane, it's a flier!"
# }
def getClassData(ver_id):
	# Gets all class objects for specified version
	class_ids_names = getClassDict(ver_id)
	logging.debug("There are " + str(len(class_ids_names)) + " objects in class for version " + str(ver_id) + ".")
	class_dict = {}

	# Remove all ID keys from the dictionary and add a description
	for cls_id in class_ids_names.keys():
		cls_name = class_ids_names[cls_id]
		class_dict[cls_name] = Class.objects.get(pk=cls_id).description

	return class_dict

# Gets the leader information for the specified version
# Returns a dictionary of the following form:
# {
# 	'Assassin':{
# 		"Abilities":["Steal","Agility Aura"],
# 		"Descripton":"He kills things real good.".
# 	}
# 	'General':{
# 		"Abilities":["Defense Aura"],
# 		"Description":"He's good at not taking damage",
# 	}
# }
def getLeaderData(ver_id):
	# Get all the ability objects and their IDs
	ability_dict = getHeroAbilDict(ver_id)

	# Get all the leader objects for the specified version
	all_ver_leaders = Leader.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_leaders)) + " objects in leader for version " + str(ver_id) + ".")
	leader_dict = {}

	# For each leader object
	for ldr in all_ver_leaders:
		# Add the leader to the dictionary if it doesn't exist, including the description
		if not ldr.name in leader_dict:
			leader_dict[ldr.name] = {}
			leader_dict[ldr.name]["Abilities"] = []
			leader_dict[ldr.name]["Description"] = ldr.description

		# Ensure the ability exists in the ability dictionary
		if not ldr.ability_id in ability_dict:
			logging.error("The hero ability dictionary was missing a class (id=" + str(ldr.ability_id) + ").")
			ability_dict[ldr.ability_id]["Abilites"] = Leader.objects.get(ldr.ability_id).name

		# Add the specific hero's ability
		leader_dict[ldr.name]["Abilities"].append(ability_dict[ldr.ability_id])

	return leader_dict

# Gets the map information for the specified version
# Returns a dictionary of the following form:
# {
# 	"Map 1 Name": "0,1 1,1 1,1 0,1n0,2 0,2 0,1 0,1n0,2 0,2 0,1 0,1n0,1 1,1 1,1 0,1",
# 	"All Grass":  "0,1 1,1 0,1 0,1n0,1 1,1 0,1 0,1n0,1 1,1 0,1 0,1n0,1 1,1 0,1 0,1",
# }
# For the map data, 
# there are n-delimited lines, for each line,
# there are space-delimited tokens, for each token,
# there are comma-delimited fields, 
# the first being whether or not a unit can be initially placed there
# the second being the ID of the terrain type
# These IDs will match the data sent in the terrain object
def getMapData(ver_id):
	# Get all map names and file paths for that version
	all_ver_maps = Map.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_maps)) + " objects in map for version " + str(ver_id) + ".")
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
def getPerkData(ver_id):
	# Get all the perk objects for the current version
	all_ver_perks = Perk.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_perks)) + " objects in perk for version " + str(ver_id) + ".")

	perk_dict = {}

	# Add each action name to the list
	for perk in all_ver_perks:
		perk_dict[perk.name] = {}
		perk_dict[perk.name]["Description"] = perk.description
		perk_dict[perk.name]["Tier"] = perk.tier

	return perk_dict

# Gets the stat information for the specified version
# Returns a dictionary of thie following form:
# {"HP":
# 	{
# 		"Archer":10,
# 		"Flier":10,
# 	},
#  "Move":
#  	{
#  		"Archer":5,
#  		"Flier":8,
#  	},
# }
def getStatData(ver_id):
	# Get all the stats for that version
	all_ver_stat = Stat.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_stat)) + " objects in stat for version " + str(ver_id) + ".")

	class_dict = getClassDict(ver_id)

	stat_dict = {}

	# Add all the stats
	for stt in all_ver_stat:
		# If the specified stat has yet to be encountered
		if not stt.name in stat_dict:
			stat_dict[stt.name] = {}

		# Ensure that the specified unit(class) ID exists in the dictionary input
		if not stt.unit_id in class_dict:
			logging.error("The passed class dictionary was missing a class (id=" + str(stt.unit_id) + ").")
			class_dict[stt.unit_id] = Class.objects.get(stt.unit_id).name

		# If the specified class doesn't exist in the specific stat dict
		if not class_dict[stt.unit_id] in stat_dict[stt.name]:
			stat_dict[stt.name][class_dict[stt.unit_id]] = stt.value
		else:
			logging.error("Duplicate unit class for stat type.")

	return stat_dict

# Gets the terrain information for the specified version
# Returns a dictionary of thie following form:
# {"Grass":
# 	[
# 	"Units":
# 		{
# 			"Archer":1,	// 1 is move consumed moving over grass for archer
# 			"Flier":1,
# 		},
# 	"ID":1,
# 	],	
#  "Forest":
#  [
#  	"Units":
#  		{
#  			"Archer":2,
#  			"Flier":1,
#  		},
#  	"ID":2.
#  ],
# }
def getTerrainData(ver_id):
	# Get all the terrains for that version
	all_ver_terrain = Terrain.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_terrain)) + " objects in terrain for version " + str(ver_id) + ".")
	class_dict = getClassDict(ver_id)
	terrain_dict = {}

	# Add all the terrains
	for ter in all_ver_terrain:
		# If the specified terrain has yet to be encountered
		if not ter.name in terrain_dict:
			terrain_dict[ter.name] = {}
			terrain_dict[ter.name]["ID"] = ter.id
			terrain_dict[ter.name]["Units"] = {}

		# Ensure that the specified unit(class) ID exists in the dictionary input
		if not ter.unit_id in class_dict:
			logging.error("The passed class dictionary was missing a class (id=" + str(ter.unit_id) + ").")
			class_dict[ter.unit_id] = Class.objects.get(ter.unit_id).name

		# If the specified class doesn't exist in the specific terrain dict
		if not class_dict[ter.unit_id] in terrain_dict[ter.name]["Units"]:
			terrain_dict[ter.name]["Units"][class_dict[ter.unit_id]] = ter.move
		else:
			logging.error("Duplicate unit class for terrain type.")

	return terrain_dict

"""
All internal helper classes for this 'Class' below this line
"""
# Gets the class information for the specified version including the ID
def getClassDict(ver_id):
	# Get all the classes for that version
	all_ver_classes = Class.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_classes)) + " objects in class for version " + str(ver_id) + ".")

	class_dict = {}

	# Add each class name to the dictionary
	for clss in all_ver_classes:
		class_dict[clss.id] = clss.name

	return class_dict

# Gets the hero ability information for the specified version including the ID
def getHeroAbilDict(ver_id):
	# Get all the classes for that version
	all_ver_hero_abil = Hero_Ability.objects.filter(version_id=ver_id)
	logging.debug("There are " + str(len(all_ver_hero_abil)) + " objects in hero_abil for version " + str(ver_id) + ".")


	hero_abil_dict = {}

	# Add each hero ability name to the dictionary
	for hb in all_ver_hero_abil:
		hero_abil_dict[hb.id] = hb.name

	return hero_abil_dict